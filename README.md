# 🎤 ScoreMyBars

An AI-powered rap lyric analyzer that breaks down lyrics into sections, scores them on cleverness, rhyme density, wordplay, and radio hit potential, and displays results in a beautiful dashboard.

## ✨ Features

- **AI-Powered Analysis**: Uses OpenAI GPT to analyze lyrics with context-aware scoring
- **Section Breakdown**: Automatically parses lyrics into verses, choruses, intros, and outros
- **Multi-Dimensional Scoring**: 
  - Cleverness (wordplay, metaphors, cultural references)
  - Rhyme Density (rhyme patterns and complexity)
  - Wordplay (puns, double entendres, creative language)
  - Radio Hit Potential (catchiness, commercial appeal)
- **Billboard Hot 100 Comparison**: Compare your lyrics to actual chart-topping hits by genre
- **Song Metadata**: Add song title, artist name, and get AI-generated descriptions
- **Sub-Genre Detection**: Automatic prediction of sub-genres (drill, trap, conscious rap, etc.)
- **Export Functionality**: Download analysis as PDF reports or PNG images
- **Beautiful UI**: Modern, responsive design with real-time feedback

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/njayco/scoremybars.git
   cd scoremybars
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

5. **Run the application**
   ```bash
   python3 app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5001`

## 📋 Requirements

Install the required packages:

```bash
pip install flask python-dotenv openai reportlab pillow pronouncing
```

Or use the requirements.txt file:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

1. **Enter Your Lyrics**: Paste your rap lyrics into the text area
2. **Add Song Info**: Optionally add song title and artist name
3. **Select Genre**: Choose a genre for Billboard comparison
4. **Analyze**: Click "Analyze My Bars" to get your scores
5. **Review Results**: See detailed breakdown by section
6. **Export**: Download PDF reports or PNG images of your analysis

## 🏗️ Project Structure

```
ScoreMyBars/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── static/              # Static assets
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   ├── js/
│   │   └── main.js      # Frontend JavaScript
│   └── images/
│       └── mic.png      # App icon
├── templates/
│   └── index.html       # Main HTML template
└── utils/               # Utility modules
    ├── ai_scorer.py     # AI analysis and scoring
    ├── lyric_parser.py  # Lyric parsing and sectioning
    └── rhyme_engine.py  # Rhyme pattern analysis
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required for AI analysis)
- `SECRET_KEY`: Flask secret key for session management

### API Keys

To get the full AI-powered analysis, you'll need an OpenAI API key:
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Create an API key
3. Add it to your `.env` file

**Note**: The app works without an API key using rule-based scoring, but AI analysis provides much better results.

## 🎨 Features in Detail

### AI Analysis
- **Context-Aware Scoring**: AI considers genre, style, and cultural context
- **Billboard Comparison**: Compares your lyrics to actual chart-topping hits
- **Sub-Genre Detection**: Identifies specific rap sub-genres
- **Theme Analysis**: Extracts key themes and lyrical content
- **Mood Detection**: Analyzes emotional tone and energy

### Export Options
- **PDF Reports**: Professional, formatted reports with all analysis data
- **PNG Images**: Shareable images perfect for social media
- **Comprehensive Data**: Includes scores, breakdowns, suggestions, and metadata

### Billboard Integration
- **Genre-Specific Comparison**: Compare to hits in your chosen genre
- **Top Songs Reference**: See what #1 hits look like in your genre
- **Scoring Context**: Understand how your scores compare to chart success

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the AI analysis capabilities
- The rap community for inspiration and feedback
- All contributors who help improve ScoreMyBars

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Issues](https://github.com/njayco/scoremybars/issues) page
2. Create a new issue with detailed information
3. Include your Python version and error messages

---

**Made with ❤️ for the rap community** 