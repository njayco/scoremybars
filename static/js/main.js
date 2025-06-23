// =============================================================================
// ScoreMyBars - Main JavaScript File
// =============================================================================
// This file handles all the frontend functionality including:
// - User interactions (buttons, forms)
// - API calls to the backend
// - Rendering results on the page
// - Export and sharing functionality

// Wait for the HTML page to fully load before running our JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Get references to important HTML elements
    // These are the elements we'll interact with on the page
    const lyricsInput = document.getElementById('lyrics');        // Text area for lyrics
    const analyzeBtn = document.getElementById('analyzeBtn');     // "Analyze My Bars" button
    const sampleBtn = document.getElementById('sampleBtn');       // "Load Sample Lyrics" button
    const resultsSection = document.getElementById('resultsSection'); // Results container
    const resultsDashboard = document.getElementById('resultsDashboard'); // Where results are displayed
    const genreSelect = document.getElementById('genreSelect');   // Genre selection dropdown
    const genreDescription = document.getElementById('genreDescription'); // Genre description text
    const songTitleInput = document.getElementById('songTitle');  // Song title input
    const artistNameInput = document.getElementById('artistName'); // Artist name input

    // Global variable to store the latest analysis results for export
    let currentAnalysisData = null;

    // =============================================================================
    // GENRE SELECTION FUNCTIONALITY
    // =============================================================================
    
    // Load available genres when page loads
    loadGenres();
    
    // When user changes genre selection
    genreSelect.addEventListener('change', () => {
        updateGenreDescription();
    });
    
    /**
     * Load available genres from the server
     */
    async function loadGenres() {
        try {
            const response = await fetch('/genres');
            const data = await response.json();
            
            if (data.success && data.genres) {
                // Clear loading option
                genreSelect.innerHTML = '';
                
                // Add genre options
                data.genres.forEach(genre => {
                    const option = document.createElement('option');
                    option.value = genre.key;
                    option.textContent = genre.name;
                    genreSelect.appendChild(option);
                });
                
                // Set default selection and description
                if (data.genres.length > 0) {
                    genreSelect.value = 'hip_hop_rap'; // Default to hip-hop/rap
                    updateGenreDescription();
                }
            }
        } catch (error) {
            console.error('Error loading genres:', error);
            // Fallback to basic options
            genreSelect.innerHTML = `
                <option value="hip_hop_rap">Hip-Hop/Rap</option>
                <option value="pop">Pop</option>
                <option value="r_b">R&B/Soul</option>
            `;
        }
    }
    
    /**
     * Update genre description based on selected genre
     */
    function updateGenreDescription() {
        const selectedOption = genreSelect.options[genreSelect.selectedIndex];
        if (selectedOption) {
            const genreKey = selectedOption.value;
            const genreName = selectedOption.textContent;
            
            // Update description based on genre
            const descriptions = {
                'hip_hop_rap': 'Compare your lyrics to Billboard Hot 100 hip-hop hits like "Old Town Road" and "God\'s Plan"',
                'pop': 'Compare your lyrics to Billboard Hot 100 pop hits like "Blinding Lights" and "Levitating"',
                'r_b': 'Compare your lyrics to Billboard Hot 100 R&B hits with smooth vocals and emotional depth',
                'country': 'Compare your lyrics to Billboard Hot 100 country hits with storytelling elements',
                'electronic_dance': 'Compare your lyrics to Billboard Hot 100 EDM hits with dance beats and energy',
                'rock': 'Compare your lyrics to Billboard Hot 100 rock hits with guitar-driven sound'
            };
            
            genreDescription.textContent = descriptions[genreKey] || 
                `Compare your lyrics to Billboard Hot 100 hits in the ${genreName} genre`;
        }
    }

    // =============================================================================
    // SAMPLE LYRICS FUNCTIONALITY
    // =============================================================================
    
    // When user clicks "Load Sample Lyrics" button
    sampleBtn.addEventListener('click', async () => {
        try {
            // Make a request to our backend to get sample lyrics
            const response = await fetch('/sample');
            const data = await response.json();
            
            // Put the sample lyrics in the text area
            lyricsInput.value = data.lyrics;
            
            // Populate sample song metadata
            songTitleInput.value = "Sample Track";
            artistNameInput.value = "Demo Artist";
            
            lyricsInput.focus(); // Put cursor in the text area
        } catch (error) {
            console.error('Error loading sample lyrics:', error);
            
            // If the API call fails, use hardcoded sample lyrics as backup
        const sample = `[Verse 1]\nI'm in the studio, cooking up the heat\nEvery bar I spit, got the crowd on their feet\nMetaphors so deep, they can't compete\nWordplay so fresh, it's a lyrical treat\n\n[Chorus]\nScore my bars, let's see what you got\nAI analysis, give it all you've got\nFrom the cleverness to the radio spot\nThis is hip-hop, and we're taking the top`;
        lyricsInput.value = sample;
        songTitleInput.value = "Sample Track";
        artistNameInput.value = "Demo Artist";
        lyricsInput.focus();
        }
    });

    // =============================================================================
    // LYRIC ANALYSIS FUNCTIONALITY
    // =============================================================================
    
    // When user clicks "Analyze My Bars" button
    analyzeBtn.addEventListener('click', async () => {
        // Get the lyrics from the text area and remove extra spaces
        const lyrics = lyricsInput.value.trim();
        const selectedGenre = genreSelect.value;
        const songTitle = songTitleInput.value.trim();
        const artistName = artistNameInput.value.trim();
        
        // Check if user actually entered lyrics
        if (!lyrics) {
            alert('Please paste or type your rap lyrics first!');
            return;
        }
        
        // Check if user selected a genre
        if (!selectedGenre) {
            alert('Please select a genre to compare your lyrics against!');
            return;
        }

        // Show loading state to let user know something is happening
        resultsSection.classList.remove('hidden'); // Make results section visible
        resultsDashboard.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Analyzing your bars compared to Billboard Hot 100 hits...</p>
                <p class="loading-details">Generating song description, comparing to ${genreSelect.options[genreSelect.selectedIndex].textContent} hits, analyzing sections, and scoring your lyrics...</p>
            </div>
        `;

        try {
            console.log('Sending lyrics to server:', lyrics.substring(0, 100) + '...'); // Debug log
            console.log('Selected genre:', selectedGenre); // Debug log
            console.log('Song title:', songTitle); // Debug log
            console.log('Artist name:', artistName); // Debug log
            
            // Send the lyrics to our backend for analysis
            const response = await fetch('/analyze', {
                method: 'POST', // Use POST method to send data
                headers: {
                    'Content-Type': 'application/json', // Tell server we're sending JSON
                },
                body: JSON.stringify({ 
                    lyrics,
                    genre: selectedGenre,
                    song_title: songTitle,
                    artist_name: artistName
                }) // Convert lyrics to JSON and send
            });

            console.log('Response status:', response.status); // Debug log
            
            // Check if the response is ok (status 200-299)
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Get the analysis results from the server
            const data = await response.json();
            console.log('Received data:', data); // Debug log

            // Check if the analysis was successful
            if (data.success) {
                // Store the analysis data globally for export
                currentAnalysisData = data;
                renderResults(data); // Display the results on the page
            } else {
                throw new Error(data.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('Analysis error details:', error); // Detailed error log
            
            // Show error message to user
            resultsDashboard.innerHTML = `
                <div class="error">
                    <h3>❌ Analysis Failed</h3>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <p><strong>Type:</strong> ${error.name}</p>
                    <p>Please check your lyrics and try again.</p>
                    <p><small>If this keeps happening, try refreshing the page.</small></p>
                </div>
            `;
        }
    });

    // =============================================================================
    // RESULTS RENDERING FUNCTIONS
    // =============================================================================
    
    /**
     * Main function that renders all the analysis results on the page
     * @param {Object} data - The analysis results from the server
     */
    function renderResults(data) {
        // Extract all the data we need from the server response
        const { 
            sections, 
            overall_scores, 
            genre_prediction, 
            popularity_prediction, 
            suggestions, 
            total_bars,
            selected_genre,
            billboard_comparison,
            song_metadata
        } = data;

        // Create the HTML for the results dashboard
        resultsDashboard.innerHTML = `
            <div class="results-container">
                <!-- Song Information Section -->
                <div class="song-info-section">
                    <h3>🎵 Song Information</h3>
                    <div class="song-details">
                        <div class="song-title-artist">
                            <h4>${song_metadata.title || 'Untitled'}</h4>
                            <p class="artist-name">by ${song_metadata.artist || 'Unknown Artist'}</p>
                        </div>
                        <div class="song-description">
                            <h5>AI-Generated Description:</h5>
                            <p>${song_metadata.description.description}</p>
                        </div>
                        <div class="song-analysis">
                            <div class="analysis-grid">
                                <div class="analysis-item">
                                    <strong>Sub-Genre:</strong> ${song_metadata.description.sub_genre}
                                </div>
                                <div class="analysis-item">
                                    <strong>Mood:</strong> ${song_metadata.description.mood}
                                </div>
                                <div class="analysis-item">
                                    <strong>Target Audience:</strong> ${song_metadata.description.target_audience}
                                </div>
                                <div class="analysis-item">
                                    <strong>Lyrical Style:</strong> ${song_metadata.description.lyrical_style}
                                </div>
                            </div>
                            <div class="themes-section">
                                <strong>Key Themes:</strong>
                                <div class="themes-list">
                                    ${song_metadata.description.themes.map(theme => `<span class="theme-tag">${theme}</span>`).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Billboard Comparison Context -->
                <div class="billboard-context">
                    <h3>🏆 Billboard Hot 100 Comparison</h3>
                    <p><strong>Genre:</strong> ${selected_genre.name}</p>
                    <p>${billboard_comparison.description}</p>
                    ${billboard_comparison.top_songs.length > 0 ? `
                        <div class="top-songs">
                            <h4>Top Billboard Hits in ${selected_genre.name}:</h4>
                            <ul>
                                ${billboard_comparison.top_songs.map(song => `
                                    <li><strong>${song.title}</strong> by ${song.artist} (Peak: #${song.peak_position}, ${song.weeks_at_1} weeks at #1)</li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>

                <!-- Overall Summary Section -->
                <div class="overall-summary">
                    <h3>🎯 Overall Analysis</h3>
                    <div class="summary-stats">
                        <div class="stat">
                            <span class="stat-value">${total_bars}</span>
                            <span class="stat-label">Total Bars</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${sections.length}</span>
                            <span class="stat-label">Sections</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${genre_prediction}</span>
                            <span class="stat-label">Predicted Genre</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">${popularity_prediction.level}</span>
                            <span class="stat-label">Popularity</span>
                        </div>
                    </div>
                </div>

                <!-- Overall Scores Section -->
                <div class="overall-scores">
                    <h3>📊 Overall Scores (vs. Billboard ${selected_genre.name})</h3>
                    <div class="score-grid">
                        ${renderScoreCard('Cleverness', overall_scores.cleverness, '🎯')}
                        ${renderScoreCard('Rhyme Density', overall_scores.rhyme_density, '🎵')}
                        ${renderScoreCard('Wordplay', overall_scores.wordplay, '🎭')}
                        ${renderScoreCard('Radio Hit', overall_scores.radio_score, '📻')}
                    </div>
                </div>

                <!-- Section Breakdown -->
                <div class="section-breakdown">
                    <h3>📝 Section Breakdown</h3>
                    ${sections.map((section, index) => renderSection(section, index)).join('')}
                </div>

                <!-- Improvement Suggestions -->
                <div class="suggestions">
                    <h3>💡 Improvement Suggestions</h3>
                    <div class="suggestions-list">
                        ${suggestions.map(suggestion => `<p>• ${suggestion}</p>`).join('')}
                    </div>
                </div>

                <!-- Export Options -->
                <div class="export-options">
                    <h3>📤 Export Results</h3>
                    <div class="export-buttons">
                        <button onclick="exportResults('pdf')" class="export-btn pdf">📄 Export as PDF</button>
                        <button onclick="exportResults('image')" class="export-btn image">🖼️ Export as Image</button>
                        <button onclick="shareResults()" class="export-btn share">📱 Share Results</button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Creates a score card for displaying individual scores
     * @param {string} label - The name of the score (e.g., "Cleverness")
     * @param {number} score - The score value (0-100)
     * @param {string} emoji - The emoji to display
     * @returns {string} HTML for the score card
     */
    function renderScoreCard(label, score, emoji) {
        // Determine the CSS class based on the score
        const scoreClass = score >= 80 ? 'excellent' : score >= 60 ? 'good' : score >= 40 ? 'average' : 'poor';
        
        return `
            <div class="score-card ${scoreClass}">
                <div class="score-emoji">${emoji}</div>
                <div class="score-label">${label}</div>
                <div class="score-value">${score}</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${score}%"></div>
                </div>
            </div>
        `;
    }

    /**
     * Renders a single section (verse, chorus, etc.) with its analysis
     * @param {Object} section - The section data from the server
     * @param {number} index - The index of this section
     * @returns {string} HTML for the section
     */
    function renderSection(section, index) {
        // Extract data from the section
        const { type, text, bar_count, scores, rhyme_analysis, highlights } = section;
        
        return `
            <div class="section-card">
                <div class="section-header">
                    <h4>${type} (${bar_count} bars)</h4>
                    <div class="section-scores">
                        ${Object.entries(scores).map(([key, value]) => 
                            `<span class="mini-score ${getScoreClass(value)}">${key}: ${value}</span>`
                        ).join('')}
                    </div>
                </div>
                
                <div class="section-content">
                    <div class="lyrics-display">
                        ${text.split('\n').map(line => 
                            `<div class="lyric-line">${highlightRhymes(line, rhyme_analysis)}</div>`
                        ).join('')}
                    </div>
                    
                    <div class="section-analysis">
                        <div class="rhyme-pattern">
                            <strong>Rhyme Pattern:</strong> ${rhyme_analysis.pattern || 'AABB'}
                        </div>
                        <div class="highlights">
                            <strong>Highlights:</strong> ${highlights.join(', ')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Highlights rhyming words in a line of lyrics
     * @param {string} line - A single line of lyrics
     * @param {Object} rhymeAnalysis - The rhyme analysis data
     * @returns {string} HTML with highlighted rhyming words
     */
    function highlightRhymes(line, rhymeAnalysis) {
        // Simple rhyme highlighting - in a real implementation, this would be more sophisticated
        if (rhymeAnalysis.rhymes && rhymeAnalysis.rhymes.length > 0) {
            let highlightedLine = line;
            rhymeAnalysis.rhymes.forEach(rhyme => {
                const regex = new RegExp(`\\b${rhyme.word}\\b`, 'gi');
                highlightedLine = highlightedLine.replace(regex, `<span class="rhyme-highlight">${rhyme.word}</span>`);
            });
            return highlightedLine;
        }
        return line;
    }

    /**
     * Determines the CSS class for a score based on its value
     * @param {number} score - The score value
     * @returns {string} CSS class name
     */
    function getScoreClass(score) {
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'average';
        return 'poor';
    }

    // =============================================================================
    // EXPORT AND SHARING FUNCTIONALITY
    // =============================================================================
    
    /**
     * Exports analysis results as PDF or image
     * This function is made available globally so it can be called from HTML buttons
     * @param {string} type - The export type ('pdf' or 'image')
     */
    window.exportResults = async (type) => {
        try {
            // Check if we have analysis data to export
            if (!currentAnalysisData) {
                alert('No analysis data available. Please analyze some lyrics first.');
                return;
            }

            // Send export request to the server
            const response = await fetch('/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: type,
                    analysis_data: currentAnalysisData
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Create a download link and trigger the download
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = data.filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                console.log(`Export successful: ${data.filename}`);
                
                // Show success message
                const exportType = data.filename.endsWith('.txt') ? 'Text file' : 
                                 data.filename.endsWith('.pdf') ? 'PDF' : 'Image';
                alert(`${exportType} export successful! File: ${data.filename}`);
            } else {
                alert('Export failed: ' + data.error);
            }
        } catch (error) {
            console.error('Export error:', error);
            alert('Export failed. Please try again.');
        }
    };

    /**
     * Shares results using the Web Share API or copies link to clipboard
     * This function is made available globally so it can be called from HTML buttons
     */
    window.shareResults = async () => {
        try {
            // Check if we have analysis data to share
            if (!currentAnalysisData) {
                alert('No analysis data available. Please analyze some lyrics first.');
                return;
            }

            // First, generate an image of the results
            console.log('🖼️ Generating image for sharing...');
            const response = await fetch('/export', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: 'image',
                    analysis_data: currentAnalysisData
                })
            });

            const data = await response.json();
            
            if (!data.success) {
                alert('Failed to generate shareable image: ' + data.error);
                return;
            }

            // Convert base64 to blob
            const base64Data = data.download_url.split(',')[1];
            const blob = await fetch(`data:image/png;base64,${base64Data}`).then(res => res.blob());
            
            // Create a file from the blob
            const file = new File([blob], data.filename, { type: 'image/png' });

            // Check if the browser supports the Web Share API
            if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
                try {
                    await navigator.share({
                        title: 'ScoreMyBars Analysis Results',
                        text: `Check out my ${currentAnalysisData.song_metadata?.title || 'lyrics'} analysis from ScoreMyBars!`,
                        files: [file]
                    });
                    console.log('✅ Shared successfully via Web Share API');
                } catch (shareError) {
                    console.log('Web Share API failed, falling back to download:', shareError);
                    // Fallback to download
                    downloadImage(data.download_url, data.filename);
                }
            } else {
                // Fallback: download the image and show instructions
                downloadImage(data.download_url, data.filename);
                alert('Image downloaded! You can now share it manually.');
            }
        } catch (error) {
            console.error('Share error:', error);
            alert('Sharing failed. The image has been downloaded instead.');
        }
    };

    /**
     * Downloads an image from a data URL
     * @param {string} dataUrl - The data URL of the image
     * @param {string} filename - The filename to save as
     */
    function downloadImage(dataUrl, filename) {
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log(`✅ Image downloaded: ${filename}`);
    }

    // =============================================================================
    // KEYBOARD SHORTCUTS
    // =============================================================================
    
    // Add keyboard shortcuts for better user experience
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter or Cmd+Enter to analyze lyrics
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'Enter') {
                e.preventDefault(); // Prevent default behavior
                analyzeBtn.click(); // Trigger the analyze button
            }
        }
    });
}); 