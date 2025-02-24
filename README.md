# AnkiBot - German Vocabulary Flashcard Generator

AnkiBot is a tool that automatically generates Anki flashcards for German vocabulary learning using OpenAI's language models. It creates high-quality, context-rich flashcards with example sentences and audio pronunciations.

## Features

- **Automated Flashcard Creation**: Generate complete Anki cards from a simple list of German words
- **Smart Article Addition**: Automatically adds correct articles to German nouns
- **Example Sentences**: Creates natural example sentences using each word
- **Audio Pronunciation**: Includes audio pronunciation of the German sentences
- **Bidirectional Learning**: Creates both German→English and English→German cards
- **Batch Processing**: Efficiently processes words in batches to reduce API calls
- **Flexible Input**: Import words from command-line arguments or text files

## Installation

### Prerequisites

- Python 3.7 or higher
- An OpenAI API key with access to GPT-4o and TTS models

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ankibot.git
   cd ankibot
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Create an `.env` and add your API key `OPENAI_API_KEY=your_api_key_here`
   - Or set it as an environment variable: `export OPENAI_API_KEY=your_api_key_here`

## Usage

### Basic Usage

Generate a deck with default words:

```
python main.py
```

### Using Your Own Words

Specify words directly:

```
python main.py --words Hund Katze Maus Buch Tisch
```

Or use a text file (one word per line):

```
python main.py --file my_words.txt
```

### Additional Options

```
python main.py --help
```

Output:
```
usage: main.py [-h] [--words WORDS [WORDS ...]] [--file FILE] [--output OUTPUT] [--one-direction] [--batch-size BATCH_SIZE]

Generate Anki flashcards for German vocabulary learning.

options:
  -h, --help            show this help message and exit
  --words WORDS [WORDS ...], -w WORDS [WORDS ...]
                        List of German words to include in the deck
  --file FILE, -f FILE  Path to a text file containing German words, one per line
  --output OUTPUT, -o OUTPUT
                        Output file name for the Anki deck
  --one-direction, -1   Only create German to English cards (default: bidirectional)
  --batch-size BATCH_SIZE, -b BATCH_SIZE
                        Number of words to process in each API batch (default: 5)
```

## Importing into Anki

1. Open Anki on your computer
2. Click "File" → "Import"
3. Select the generated `.apkg` file
4. The deck will be imported with all cards, audio, and formatting

## How It Works

AnkiBot uses OpenAI's language models to:

1. Add correct articles to German nouns
2. Generate context-rich example sentences for each word
3. Translate the words and sentences to English
4. Create audio pronunciations for the German sentences

All of this information is assembled into Anki flashcards with optimized templates for language learning.

## Cost Considerations

This tool uses the OpenAI API, which charges based on usage:

- GPT-4o for generating sentences and translations
- TTS-1 for audio generation

A 50-word deck costs approximately $0.05-0.010 to generate as of 24.02.2025.
## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

- OpenAI for providing the API services
- genanki library for Anki deck generation
