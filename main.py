import os
import genanki
import json
import random
import argparse
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file if it exists
load_dotenv()

def get_api_key():
    """Get the OpenAI API key from environment variable or prompt user if not found"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Please enter your OpenAI API key: ")
        # Save to environment variable for current session
        os.environ["OPENAI_API_KEY"] = api_key
    return api_key

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=get_api_key())


def add_articles(words):
    """Add articles to German nouns using OpenAI API"""
    words_str = ", ".join(words)
    print(f"Processing {len(words)} words to add articles where needed...")
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a language learning bot. For each word given, if the word is a noun, you output the word with the correct definite article in front of it. If the word is not a noun, you output the word as is. Return your response as a JSON object with a key 'words_with_articles' containing an array of the processed words."},
            {"role": "user", "content": f"Add articles to these words: {words_str}"}
        ])
    
    response_json = json.loads(completion.choices[0].message.content)
    return response_json["words_with_articles"]


def generate_german_examples_batch(words, batch_size=5):
    """Process words in batches to reduce API calls"""
    all_results = []
    total_batches = (len(words) + batch_size - 1) // batch_size
    
    for i in range(0, len(words), batch_size):
        batch = words[i:i+batch_size]
        batch_str = json.dumps(batch)
        current_batch = i // batch_size + 1
        
        print(f"Processing batch {current_batch}/{total_batches} with {len(batch)} words...")
        
        # Create a single completion for multiple words
        completion = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": """You are a language learning assistant that helps with German vocabulary.
For each German word in the provided list, you will:
1. Create a short German sentence (A2 level) using the word
2. Provide the English translation of the word
3. Provide the English translation of the sentence
Return your response as a JSON object with a key 'word_data' containing an array of objects, each with the keys 'word', 'german_sentence', 'english_word', and 'english_sentence'."""},
                {"role": "user", "content": f"Process these German words: {batch_str}"}
            ]
        )
        
        response_json = json.loads(completion.choices[0].message.content)
        all_results.extend(response_json["word_data"])
        
        # Print progress
        processed_so_far = min(i + batch_size, len(words))
        print(f"Processed {processed_so_far}/{len(words)} words")
    
    return all_results


def generate_audio(text, filename, voice="alloy"):
    """Generate audio for a text using OpenAI's text-to-speech API"""
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    response.stream_to_file(filename)
    return filename


def create_anki_deck(words_list, output_file="german_vocabulary.apkg", bidirectional=True):
    """Create an Anki deck from a list of German words"""
    # Define the model for the Anki cards - German to English
    german_to_english_model = genanki.Model(
        1091735104,
        'German to English',
        fields=[
            {'name': 'German Word'},
            {'name': 'German Sentence'},
            {'name': 'English Word'},
            {'name': 'English Sentence'},
            {'name': 'German Audio'}
        ],
        templates=[
            {
                'name': 'German to English',
                'qfmt': '{{German Word}}<br><br>{{German Sentence}}<br>{{German Audio}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{English Word}}<br><br>{{English Sentence}}',
            },
        ]
    )

    # Define the model for the Anki cards - English to German
    english_to_german_model = genanki.Model(
        2091735105,
        'English to German',
        fields=[
            {'name': 'English Word'},
            {'name': 'English Sentence'},
            {'name': 'German Word'},
            {'name': 'German Sentence'},
            {'name': 'German Audio'}
        ],
        templates=[
            {
                'name': 'English to German',
                'qfmt': '{{English Word}}<br><br>{{English Sentence}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{German Word}}<br><br>{{German Sentence}}<br>{{German Audio}}',
            },
        ]
    )

    # Create a new deck
    my_deck = genanki.Deck(
        2059400110,
        'German Vocabulary'
    )

    print(f"Starting process with {len(words_list)} German words")

    # Add articles to nouns
    words_with_articles = add_articles(words_list)
    
    # Process words in batches to reduce API calls
    processed_words = generate_german_examples_batch(words_with_articles)
    media_files = []
    all_notes = []

    print(f"\nGenerating audio files and creating Anki cards...")

    # Generate cards for each processed word
    for word_data in processed_words:
        word = word_data["word"]
        german_sentence = word_data["german_sentence"]
        english_word = word_data["english_word"]
        english_sentence = word_data["english_sentence"]
        
        # Create audio for the German sentence
        audio_filename = f"{word.replace(' ', '_')}.mp3"
        generate_audio(german_sentence, audio_filename)
        media_files.append(audio_filename)
        
        # Create German to English note
        german_to_english_note = genanki.Note(
            model=german_to_english_model,
            fields=[
                word, 
                german_sentence, 
                english_word, 
                english_sentence, 
                f"[sound:{audio_filename}]"
            ]
        )
        all_notes.append(german_to_english_note)
        
        # Create English to German note if bidirectional learning is enabled
        if bidirectional:
            english_to_german_note = genanki.Note(
                model=english_to_german_model,
                fields=[
                    english_word, 
                    english_sentence, 
                    word, 
                    german_sentence, 
                    f"[sound:{audio_filename}]"
                ]
            )
            all_notes.append(english_to_german_note)

    # Randomize the order of notes
    random.shuffle(all_notes)

    # Add all shuffled notes to the deck
    for note in all_notes:
        my_deck.add_note(note)

    # Create a package with the deck
    my_package = genanki.Package(my_deck)
    my_package.media_files = media_files
    my_package.write_to_file(output_file)

    # Delete the audio files
    for file in media_files:
        if os.path.exists(file):
            os.remove(file)

    card_count = len(all_notes)
    print(f"\nProcess complete! Created {card_count} flashcards in total.")
    if bidirectional:
        print(f"- {card_count//2} German to English cards")
        print(f"- {card_count//2} English to German cards")
    else:
        print(f"- {card_count} German to English cards")
    print(f"Deck saved as {output_file}")
    print("All cards have been shuffled in a single deck.")


def load_words_from_file(file_path):
    """Load words from a text file, one word per line"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def main():
    """Main function to handle command-line arguments and run the program"""
    parser = argparse.ArgumentParser(description='Generate Anki flashcards for German vocabulary learning.')
    
    # Add arguments
    parser.add_argument('--words', '-w', nargs='+', help='List of German words to include in the deck')
    parser.add_argument('--file', '-f', help='Path to a text file containing German words, one per line')
    parser.add_argument('--output', '-o', default='german_vocabulary.apkg', help='Output file name for the Anki deck')
    parser.add_argument('--one-direction', '-1', action='store_true', help='Only create German to English cards (default: bidirectional)')
    parser.add_argument('--batch-size', '-b', type=int, default=5, help='Number of words to process in each API batch (default: 5)')
    
    args = parser.parse_args()
    
    # Default word list if no words or file provided
    default_words = [
        "Haus", "Familie", "Arbeit", "Schule", "Essen", "Trinken", "Zeit", "Tag", "Nacht",
        "Frühstück", "Mittagessen", "Abendessen"
    ]
    
    words_list = []
    
    # Get words from file if provided
    if args.file:
        try:
            words_list = load_words_from_file(args.file)
            print(f"Loaded {len(words_list)} words from {args.file}")
        except Exception as e:
            print(f"Error loading words from file: {e}")
            return
    
    # Get words from command line arguments if provided
    elif args.words:
        words_list = args.words
    
    # Use default words if no words provided
    else:
        print("No words provided. Using default word list.")
        words_list = default_words
    
    # Create the Anki deck
    create_anki_deck(
        words_list=words_list,
        output_file=args.output,
        bidirectional=not args.one_direction
    )


if __name__ == "__main__":
    main()