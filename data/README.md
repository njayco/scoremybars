# 📊 Data Folder - Sample Data and Reference Files

This folder contains sample data and reference files that help the application work properly. These files provide examples and rules for the analysis system.

## 📁 Folder Structure

```
data/
├── sample_lyrics.txt      # 📝 Example lyrics for testing
└── scoring_data.json      # 📊 Scoring rules and criteria
```

## 📝 Sample Data

### **sample_lyrics.txt** - Example Lyrics
**What it is**: A collection of sample rap lyrics that users can load to test the app.

**Purpose**:
- Helps users see how the app works without writing their own lyrics
- Provides a good example of proper formatting
- Shows different section types (verse, chorus, bridge, etc.)

**Content Structure**:
```
[Intro]
Yo, this is ScoreMyBars
Let's see what you got

[Verse 1]
I'm in the studio, cooking up the heat
Every bar I spit, got the crowd on their feet
...

[Chorus]
Score my bars, let's see what you got
AI analysis, give it all you've got
...
```

**How it's used**:
1. User clicks "Load Sample Lyrics" button
2. JavaScript calls `/sample` API endpoint
3. Server reads this file and returns the content
4. JavaScript puts the lyrics in the text area

---

## 📊 Reference Data

### **scoring_data.json** - Analysis Rules
**What it is**: A JSON file that defines how the scoring system works and what different genres look like.

**Purpose**:
- Provides reference data for genre classification
- Defines scoring criteria and thresholds
- Helps the AI understand what to look for

**Key Sections**:

1. **Genres**:
   ```json
   {
     "drill": {
       "description": "Dark, aggressive UK drill style",
       "characteristics": ["dark themes", "aggressive delivery"],
       "scoring_weights": {
         "cleverness": 0.3,
         "rhyme_density": 0.4,
         "wordplay": 0.2,
         "radio_score": 0.1
       }
     }
   }
   ```
   - Defines different rap genres
   - Lists characteristics of each genre
   - Sets scoring weights for each genre

2. **Scoring Criteria**:
   ```json
   {
     "cleverness": {
       "excellent": {
         "range": [80, 100],
         "description": "Exceptional metaphors, unique perspectives",
         "examples": ["complex metaphors", "double entendres"]
       }
     }
   }
   ```
   - Defines what makes a score "excellent", "good", "average", or "poor"
   - Provides examples of what to look for
   - Sets score ranges for each category

3. **Popularity Predictions**:
   ```json
   {
     "viral": {
       "range": [85, 100],
       "description": "High potential for viral success",
       "characteristics": ["catchy", "memorable", "shareable"]
     }
   }
   ```
   - Helps predict how popular a song might be
   - Based on scoring results
   - Provides marketing insights

---

## 🔄 How These Files Are Used

### In the Application:

1. **sample_lyrics.txt**:
   - Loaded by the `/sample` API endpoint in `app.py`
   - Used to demonstrate app functionality
   - Helps users understand proper formatting

2. **scoring_data.json**:
   - Referenced by `ai_scorer.py` for scoring rules
   - Used for genre classification
   - Provides context for AI analysis

### File Access:
- **Python**: Files are read using standard file operations
- **JavaScript**: Files are accessed through API endpoints
- **Security**: Files are not directly accessible from the web

---

## 🎯 For Beginners

**Think of these files like reference books**:
- **sample_lyrics.txt** = A cookbook with example recipes
- **scoring_data.json** = A rulebook that defines standards

**Key Learning Points**:
- Data files provide examples and rules
- JSON is a format for storing structured data
- These files make the app more intelligent and user-friendly
- They can be updated without changing the main code

**File Formats**:
- **.txt**: Plain text file (human-readable)
- **.json**: Structured data format (machine-readable)

**Why We Use These**:
- **Consistency**: Everyone gets the same examples
- **Flexibility**: Easy to update without changing code
- **Maintainability**: Rules and examples are separate from logic
- **User Experience**: Helps users understand how to use the app 