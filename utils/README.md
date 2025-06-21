# 🛠️ Utils Folder - Helper Functions

This folder contains the core logic that powers ScoreMyBars. Each file has a specific job in analyzing rap lyrics.

## 📁 Files Overview

### 1. **lyric_parser.py** - Text Structure Analyzer
**What it does**: Takes raw lyrics and breaks them into organized sections.

**Key Functions**:
- `parse_lyrics(text)`: Main function that processes the entire lyrics
- `_detect_sections(lines)`: Finds verse, chorus, bridge, etc.
- `_count_bars(text)`: Counts how many bars are in each section
- `_clean_text(text)`: Removes extra spaces and formatting

**How it works**:
1. Splits lyrics into lines
2. Looks for section markers like `[Verse 1]`, `[Chorus]`
3. Groups lines into sections
4. Counts bars in each section
5. Returns organized data structure

**Example Input**:
```
[Verse 1]
I'm in the studio, cooking up the heat
Every bar I spit, got the crowd on their feet

[Chorus]
Score my bars, let's see what you got
AI analysis, give it all you've got
```

**Example Output**:
```python
[
    {
        'type': 'Verse 1',
        'text': 'I\'m in the studio...',
        'bar_count': 2
    },
    {
        'type': 'Chorus', 
        'text': 'Score my bars...',
        'bar_count': 2
    }
]
```

---

### 2. **rhyme_engine.py** - Rhyme Detection System
**What it does**: Finds rhyming words and patterns in lyrics.

**Key Functions**:
- `analyze_rhymes(text)`: Main function that analyzes all rhyme aspects
- `_analyze_end_rhymes(lines)`: Finds rhymes at the end of lines
- `_analyze_internal_rhymes(lines)`: Finds rhymes within lines
- `_detect_rhyme_scheme(lines)`: Determines rhyme pattern (AABB, ABAB, etc.)
- `_words_rhyme(word1, word2)`: Checks if two words rhyme

**How it works**:
1. Uses the `pronouncing` library to get word pronunciations
2. Compares ending sounds to find rhymes
3. Identifies different types of rhymes:
   - End rhymes (last words of lines)
   - Internal rhymes (within the same line)
   - Multi-syllabic rhymes (complex rhyming)
   - Slant rhymes (near rhymes)

**Example Output**:
```python
{
    'end_rhymes': {
        'rhyme_pairs': [(0, 1, 'heat', 'feet')],
        'rhyme_density': 0.5
    },
    'internal_rhymes': [...],
    'rhyme_scheme': 'AABB',
    'rhyme_density': 0.3
}
```

---

### 3. **ai_scorer.py** - Scoring Engine
**What it does**: Scores lyrics on different criteria using AI or rules.

**Key Functions**:
- `score_section(section)`: Scores a single section of lyrics
- `get_highlights(text)`: Finds standout lines
- `predict_genre(analysis_results)`: Predicts the genre
- `predict_popularity(scores)`: Estimates popularity potential
- `generate_suggestions(scores, results)`: Creates improvement tips

**Scoring Categories**:
1. **Cleverness (0-100)**: Metaphors, double entendres, unique angles
2. **Rhyme Density (0-100)**: How well words rhyme together
3. **Wordplay (0-100)**: Puns, punchlines, clever word usage
4. **Radio Score (0-100)**: Commercial appeal and catchiness

**How it works**:
1. **AI Mode** (if OpenAI API is available):
   - Sends lyrics to GPT-4 for analysis
   - Gets detailed scores and feedback
   
2. **Rule-based Mode** (fallback):
   - Uses predefined rules to score lyrics
   - Looks for specific patterns and indicators
   - Provides basic scoring when AI is unavailable

**Example Output**:
```python
{
    'cleverness': 85.0,
    'rhyme_density': 78.0,
    'wordplay': 92.0,
    'radio_score': 65.0
}
```

---

## 🔄 How They Work Together

1. **lyric_parser.py** breaks down the raw lyrics into sections
2. **rhyme_engine.py** analyzes the rhyme patterns in each section
3. **ai_scorer.py** scores each section and provides insights
4. All results are combined in `app.py` and sent to the frontend

## 🎯 For Beginners

- **lyric_parser.py** is like a librarian organizing books by category
- **rhyme_engine.py** is like a music teacher identifying patterns
- **ai_scorer.py** is like a judge giving scores and feedback

Each file has a single responsibility and works independently, making the code easier to understand and maintain. 