# 📄 Templates Folder - HTML Pages

This folder contains the HTML files that define the structure of the website. HTML is like the skeleton of the website - it defines what elements are on the page and how they're organized.

## 📁 Folder Structure

```
templates/
├── index.html             # 🏠 Main page (the only page we have)
└── components/            # 📦 Reusable HTML parts (future use)
```

## 🏠 Main Page

### **index.html** - The Home Page
**What it does**: Defines the structure of the main page that users see.

**Key Sections**:

1. **Document Head**:
   ```html
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>ScoreMyBars - AI Rap Lyric Analyzer</title>
       <link rel="stylesheet" href="/static/css/style.css">
       <link rel="icon" href="/static/images/mic.png">
   </head>
   ```
   - Sets up the page title and character encoding
   - Links to our CSS file for styling
   - Sets the favicon (browser tab icon)
   - Makes it mobile-friendly

2. **Header Section**:
   ```html
   <header>
       <h1>🎤 ScoreMyBars</h1>
       <p class="subtitle">Paste your rap lyrics and let AI break down your bars.</p>
   </header>
   ```
   - Contains the app title and description
   - Uses emojis for visual appeal

3. **Main Content**:
   ```html
   <main>
       <section class="lyric-input-section">
           <label for="lyrics">Paste or type your rap lyrics:</label>
           <textarea id="lyrics" rows="10" placeholder="[Verse 1]\nI'm in the studio..."></textarea>
           <div class="input-actions">
               <button id="analyzeBtn">Analyze My Bars</button>
               <button id="sampleBtn" class="secondary">Load Sample Lyrics</button>
           </div>
       </section>
       
       <section id="resultsSection" class="results-section hidden">
           <h2>Results Dashboard</h2>
           <div id="resultsDashboard">
               <!-- Results will be inserted here by JavaScript -->
           </div>
       </section>
   </main>
   ```
   - **Lyric Input**: Text area where users paste their lyrics
   - **Action Buttons**: "Analyze My Bars" and "Load Sample Lyrics"
   - **Results Section**: Hidden by default, shown when analysis is complete

4. **Footer**:
   ```html
   <footer>
       <p>Built with ❤️ for the hip-hop community &bull; <a href="https://github.com/njayco/pursuit" target="_blank">GitHub</a></p>
   </footer>
   ```
   - Credits and links

5. **JavaScript Loading**:
   ```html
   <script src="/static/js/main.js"></script>
   ```
   - Loads our JavaScript file at the end of the page

---

## 🔗 How HTML Works with Other Files

### HTML + CSS Relationship
- HTML defines **what** is on the page
- CSS defines **how** it looks
- CSS classes like `lyric-input-section` and `results-section` are styled in `style.css`

### HTML + JavaScript Relationship
- HTML provides the **structure**
- JavaScript adds **interactivity**
- JavaScript can find elements using `getElementById()` and modify them
- Example: `document.getElementById('lyrics')` finds the textarea

### HTML + Flask Relationship
- Flask uses `render_template('index.html')` to serve this page
- Flask can pass data to the HTML (though we don't do this much in our app)
- The HTML is processed by Flask's template engine

---

## 🎯 Key HTML Concepts Used

### 1. **Semantic Elements**
- `<header>`: Page header
- `<main>`: Main content
- `<section>`: Content sections
- `<footer>`: Page footer

### 2. **Form Elements**
- `<textarea>`: Multi-line text input for lyrics
- `<button>`: Clickable buttons
- `<label>`: Labels for form elements

### 3. **CSS Classes**
- `hidden`: Hides elements (controlled by CSS)
- `secondary`: Different button styling
- `lyric-input-section`: Groups related elements

### 4. **IDs**
- `lyrics`: Unique identifier for the textarea
- `analyzeBtn`: Unique identifier for the analyze button
- `resultsDashboard`: Where JavaScript inserts results

---

## 🔄 Dynamic Content

**How Results Are Displayed**:
1. User clicks "Analyze My Bars"
2. JavaScript sends lyrics to server
3. Server returns analysis data
4. JavaScript creates HTML for the results
5. JavaScript inserts this HTML into `resultsDashboard`

**Example of Dynamic Content**:
```html
<!-- This gets created by JavaScript -->
<div class="score-card excellent">
    <div class="score-emoji">🎯</div>
    <div class="score-label">Cleverness</div>
    <div class="score-value">85</div>
    <div class="score-bar">
        <div class="score-fill" style="width: 85%"></div>
    </div>
</div>
```

---

## 🎯 For Beginners

**Think of HTML like building blocks**:
- Each HTML tag is like a building block
- You stack them together to create a structure
- CSS makes them look pretty
- JavaScript makes them interactive

**Key Learning Points**:
- HTML is the foundation of every website
- It's a markup language (not a programming language)
- Tags come in pairs: `<tag>` and `</tag>`
- Attributes provide additional information: `id="lyrics"`
- Classes allow CSS styling: `class="button secondary"`

**Common HTML Tags**:
- `<div>`: Container/box
- `<p>`: Paragraph
- `<h1>`, `<h2>`, etc.: Headings
- `<button>`: Clickable button
- `<textarea>`: Text input area
- `<a>`: Links 