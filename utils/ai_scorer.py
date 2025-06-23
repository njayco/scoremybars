import os
import openai
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class AIScorer:
    """AI-powered scoring engine for rap lyrics with Billboard Hot 100 comparison"""
    
    def __init__(self):
        self.client = None
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                # Clear any problematic environment variables that might cause the proxies error
                env_vars_to_clear = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
                for var in env_vars_to_clear:
                    if var in os.environ:
                        del os.environ[var]
                
                # Try to create OpenAI client with minimal configuration
                self.client = openai.OpenAI(api_key=api_key)
                
                # Test the client with a simple call
                self.client.models.list()
                print("✅ OpenAI client initialized successfully")
            except Exception as e:
                print(f"OpenAI client initialization failed: {e}")
                print("Falling back to rule-based scoring only")
                self.client = None
        else:
            print("No OpenAI API key found. Using rule-based scoring only.")
        
        # Load Billboard Hot 100 data for comparison
        self.billboard_data = self._load_billboard_data()
        
        # Scoring criteria
        self.scoring_criteria = {
            'cleverness': {
                'description': 'Metaphors, double entendres, unique angles, cultural references',
                'factors': ['metaphor_density', 'double_entendres', 'unique_perspective', 'cultural_references']
            },
            'rhyme_density': {
                'description': 'Rhyme density, multi-syllabic rhymes, internal rhyme, rhyme scheme complexity',
                'factors': ['end_rhymes', 'internal_rhymes', 'multi_syllabic', 'rhyme_scheme']
            },
            'wordplay': {
                'description': 'Puns, flips, punchlines, literary devices, word manipulation',
                'factors': ['puns', 'punchlines', 'literary_devices', 'word_manipulation']
            },
            'radio_score': {
                'description': 'Simplicity, hook potential, vibe, replay value, commercial appeal',
                'factors': ['hook_potential', 'simplicity', 'replay_value', 'commercial_appeal']
            }
        }
    
    def _load_billboard_data(self) -> Dict[str, Any]:
        """Load Billboard Hot 100 data from JSON file"""
        try:
            with open('data/billboard_hot100_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: Billboard data file not found, using fallback data")
            return self._get_fallback_billboard_data()
    
    def _get_fallback_billboard_data(self) -> Dict[str, Any]:
        """Fallback Billboard data if file is not found"""
        return {
            "genres": {
                "hip_hop_rap": {
                    "name": "Hip-Hop/Rap",
                    "top_songs": [
                        {
                            "title": "Old Town Road",
                            "artist": "Lil Nas X",
                            "peak_position": 1,
                            "scores": {"cleverness": 85, "rhyme_density": 90, "wordplay": 88, "radio_score": 95}
                        }
                    ]
                }
            },
            "scoring_weights": {
                "hip_hop_rap": {"cleverness": 0.25, "rhyme_density": 0.30, "wordplay": 0.25, "radio_score": 0.20}
            }
        }
    
    def get_available_genres(self) -> List[Dict[str, str]]:
        """Get list of available genres for user selection"""
        genres = []
        for genre_key, genre_data in self.billboard_data.get('genres', {}).items():
            genres.append({
                'key': genre_key,
                'name': genre_data.get('name', genre_key.replace('_', ' ').title()),
                'description': genre_data.get('description', '')
            })
        return genres
    
    def score_section(self, section: Dict[str, Any], selected_genre: str = 'hip_hop_rap') -> Dict[str, float]:
        """
        Score a section of lyrics using Billboard Hot 100 comparison
        
        Args:
            section (Dict): Section data with text and metadata
            selected_genre (str): User-selected genre for comparison
            
        Returns:
            Dict: Scores for each category (0-100) compared to Billboard hits
        """
        if not self.client:
            # Use Billboard comparison scoring
            return self._billboard_comparison_scoring(section, selected_genre)
        
        try:
            # Create prompt for AI analysis with Billboard context
            prompt = self._create_billboard_scoring_prompt(section, selected_genre)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert music analyst comparing lyrics to Billboard Hot 100 hits. Analyze the given lyrics and provide scores (0-100) for four categories: cleverness, rhyme_density, wordplay, and radio_score. Compare to actual Billboard #1 hits in the specified genre."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            scores = self._parse_ai_scores(ai_response)
            
            return scores
            
        except Exception as e:
            print(f"AI scoring failed: {e}")
            return self._billboard_comparison_scoring(section, selected_genre)
    
    def _billboard_comparison_scoring(self, section: Dict[str, Any], selected_genre: str) -> Dict[str, float]:
        """Score lyrics by comparing to Billboard Hot 100 hits in the selected genre"""
        text = section['text'].lower()
        lines = text.split('\n')
        words = text.split()
        
        # Get genre-specific scoring weights
        genre_weights = self.billboard_data.get('scoring_weights', {}).get(selected_genre, {
            'cleverness': 0.25,
            'rhyme_density': 0.25,
            'wordplay': 0.25,
            'radio_score': 0.25
        })
        
        # Get top songs in this genre for comparison
        genre_data = self.billboard_data.get('genres', {}).get(selected_genre, {})
        top_songs = genre_data.get('top_songs', [])
        
        # Calculate base scores
        base_scores = self._calculate_base_scores(text, lines, words)
        
        # Compare to Billboard hits and adjust scores
        adjusted_scores = self._compare_to_billboard_hits(base_scores, top_songs, selected_genre)
        
        return adjusted_scores
    
    def _calculate_base_scores(self, text: str, lines: List[str], words: List[str]) -> Dict[str, float]:
        """Calculate base scores using rule-based analysis"""
        # Cleverness scoring
        cleverness_score = 50.0
        metaphor_indicators = ['like', 'as', 'metaphor', 'simile', 'compare', 'imagine', 'picture']
        cultural_references = ['money', 'fame', 'success', 'struggle', 'hustle', 'grind']
        
        for indicator in metaphor_indicators:
            if indicator in text:
                cleverness_score += 8
        
        for reference in cultural_references:
            if reference in text:
                cleverness_score += 5
        
        # Rhyme density scoring
        rhyme_score = 50.0
        if len(lines) > 1:
            last_words = [line.split()[-1] if line.split() else '' for line in lines]
            rhyme_count = 0
            for i in range(len(last_words) - 1):
                if last_words[i] and last_words[i+1]:
                    if last_words[i][-2:] == last_words[i+1][-2:]:
                        rhyme_count += 1
            
            rhyme_score = min(100, 50 + (rhyme_count * 12))
        
        # Wordplay scoring
        wordplay_score = 50.0
        pun_indicators = ['play', 'word', 'double', 'meaning', 'flip', 'switch']
        for indicator in pun_indicators:
            if indicator in text:
                wordplay_score += 10
        
        # Radio score
        radio_score = 50.0
        hook_indicators = ['hook', 'catchy', 'repeat', 'chorus', 'memorable']
        simple_words = len([w for w in words if len(w) <= 4])
        if len(words) > 0:
            simplicity_ratio = simple_words / len(words)
            radio_score += simplicity_ratio * 30
        
        for indicator in hook_indicators:
            if indicator in text:
                radio_score += 8
        
        return {
            'cleverness': min(100, cleverness_score),
            'rhyme_density': rhyme_score,
            'wordplay': min(100, wordplay_score),
            'radio_score': min(100, radio_score)
        }
    
    def _compare_to_billboard_hits(self, base_scores: Dict[str, float], top_songs: List[Dict], genre: str) -> Dict[str, float]:
        """Compare base scores to Billboard hits and adjust accordingly"""
        if not top_songs:
            return base_scores
        
        # Calculate average Billboard scores for this genre
        billboard_averages = {
            'cleverness': 0,
            'rhyme_density': 0,
            'wordplay': 0,
            'radio_score': 0
        }
        
        for song in top_songs:
            song_scores = song.get('scores', {})
            for key in billboard_averages:
                billboard_averages[key] += song_scores.get(key, 75)
        
        # Calculate averages
        num_songs = len(top_songs)
        for key in billboard_averages:
            billboard_averages[key] = billboard_averages[key] / num_songs
        
        # Adjust scores based on Billboard comparison
        adjusted_scores = {}
        for key in base_scores:
            base_score = base_scores[key]
            billboard_avg = billboard_averages[key]
            
            # If base score is close to Billboard average, boost it
            if abs(base_score - billboard_avg) < 10:
                adjusted_scores[key] = min(100, base_score + 10)
            # If base score is much lower, keep it low
            elif base_score < billboard_avg - 20:
                adjusted_scores[key] = base_score
            # If base score is higher, give it a small boost
            else:
                adjusted_scores[key] = min(100, base_score + 5)
        
        return adjusted_scores
    
    def _create_billboard_scoring_prompt(self, section: Dict[str, Any], selected_genre: str) -> str:
        """Create a detailed prompt for AI scoring with Billboard context"""
        section_type = section['type']
        text = section['text']
        bar_count = section['bar_count']
        
        # Get genre information
        genre_data = self.billboard_data.get('genres', {}).get(selected_genre, {})
        genre_name = genre_data.get('name', selected_genre)
        top_songs = genre_data.get('top_songs', [])
        
        # Create Billboard context
        billboard_context = ""
        if top_songs:
            billboard_context = f"\n\nBillboard Hot 100 Context for {genre_name}:\n"
            for song in top_songs[:3]:  # Show top 3 songs
                billboard_context += f"- '{song['title']}' by {song['artist']} (Peak: #{song['peak_position']}, {song['weeks_at_1']} weeks at #1)\n"
                billboard_context += f"  Scores: Cleverness {song['scores']['cleverness']}, Rhyme {song['scores']['rhyme_density']}, Wordplay {song['scores']['wordplay']}, Radio {song['scores']['radio_score']}\n"
        
        prompt = f"""
Analyze this {section_type} section and score it (0-100) compared to Billboard Hot 100 hits in the {genre_name} genre.

Section Type: {section_type}
Number of Bars: {bar_count}
Lyrics:
{text}

{billboard_context}

Scoring Criteria (compare to Billboard #1 hits):
1. Cleverness (0-100): Metaphors, double entendres, unique angles, cultural references
2. Rhyme Density (0-100): End rhymes, internal rhymes, multi-syllabic rhymes, rhyme scheme complexity
3. Wordplay (0-100): Puns, punchlines, literary devices, word manipulation techniques
4. Radio Score (0-100): Hook potential, simplicity, replay value, commercial appeal

Return only a JSON object like this:
{{
    "cleverness": 85,
    "rhyme_density": 78,
    "wordplay": 92,
    "radio_score": 65,
    "billboard_comparison": "This compares favorably to [song name] in terms of [specific aspect]"
}}
"""
        return prompt
    
    def _parse_ai_scores(self, ai_response: str) -> Dict[str, float]:
        """Parse AI response to extract scores"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group())
                
                # Ensure all required scores are present and within range
                required_scores = ['cleverness', 'rhyme_density', 'wordplay', 'radio_score']
                for score_type in required_scores:
                    if score_type not in scores:
                        scores[score_type] = 50.0
                    else:
                        scores[score_type] = max(0, min(100, float(scores[score_type])))
                
                return scores
            else:
                raise ValueError("No JSON found in AI response")
                
        except Exception as e:
            print(f"Failed to parse AI scores: {e}")
            return {
                'cleverness': 50.0,
                'rhyme_density': 50.0,
                'wordplay': 50.0,
                'radio_score': 50.0
            }
    
    def get_highlights(self, text: str) -> List[str]:
        """Get highlights and standout lines from the text based on cleverness, wordplay, and rhyme density"""
        if not self.client:
            # Use rule-based highlighting when AI is not available
            return self._rule_based_highlights(text)
        
        try:
            prompt = f"""
Analyze these lyrics and identify 3-5 standout lines or phrases that demonstrate:
- Clever wordplay and metaphors
- Strong rhyme patterns
- Effective punchlines
- Memorable hooks
- Cultural references or clever angles

Lyrics:
{text}

Return only a JSON array of strings with the highlights.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music lyric analyst. Identify standout lines and return them as a JSON array."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content.strip()
            highlights = self._parse_highlights(ai_response)
            return highlights
            
        except Exception as e:
            print(f"Failed to get highlights: {e}")
            return self._rule_based_highlights(text)
    
    def _rule_based_highlights(self, text: str) -> List[str]:
        """Generate highlights using rule-based analysis based on cleverness, wordplay, and rhyme density"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return ["No lyrics found to analyze"]
        
        # Filter out section headers and very short lines
        filtered_lines = []
        for line in lines:
            # Skip section headers (lines in brackets) and very short lines
            if (not line.startswith('[') and 
                not line.endswith(']') and 
                len(line) > 5 and 
                not line.isupper()):  # Skip all-caps lines
                filtered_lines.append(line)
        
        if not filtered_lines:
            return ["No meaningful lyrics found to analyze"]
        
        # Score each line based on different criteria
        line_scores = []
        
        for i, line in enumerate(filtered_lines):
            # Calculate scores for this line
            cleverness_score = self._score_line_cleverness(line)
            wordplay_score = self._score_line_wordplay(line)
            rhyme_score = self._score_line_rhyme(line, filtered_lines, i)
            
            # Combined score (weighted average)
            combined_score = (cleverness_score * 0.4) + (wordplay_score * 0.4) + (rhyme_score * 0.2)
            
            line_scores.append({
                'line': line,
                'index': i,
                'cleverness': cleverness_score,
                'wordplay': wordplay_score,
                'rhyme': rhyme_score,
                'combined': combined_score
            })
        
        # Sort by combined score and get top highlights
        line_scores.sort(key=lambda x: x['combined'], reverse=True)
        
        # Generate highlight descriptions
        highlights = []
        for i, score_data in enumerate(line_scores[:5]):  # Top 5 lines
            line = score_data['line']
            cleverness = score_data['cleverness']
            wordplay = score_data['wordplay']
            rhyme = score_data['rhyme']
            combined = score_data['combined']
            
            # Determine what makes this line stand out
            strengths = []
            if cleverness > 75:
                strengths.append("clever metaphor")
            elif cleverness > 65:
                strengths.append("good metaphor")
                
            if wordplay > 75:
                strengths.append("strong wordplay")
            elif wordplay > 65:
                strengths.append("good wordplay")
                
            if rhyme > 75:
                strengths.append("excellent rhyme")
            elif rhyme > 65:
                strengths.append("good rhyme")
            
            # Create highlight description
            if strengths:
                if combined > 80:
                    highlight = f"\"{line}\" - Outstanding {', '.join(strengths)}"
                elif combined > 70:
                    highlight = f"\"{line}\" - Strong {', '.join(strengths)}"
                else:
                    highlight = f"\"{line}\" - Good {', '.join(strengths)}"
            else:
                if combined > 70:
                    highlight = f"\"{line}\" - Well-crafted line with balanced elements"
                else:
                    highlight = f"\"{line}\" - Solid lyrical content"
            
            highlights.append(highlight)
        
        if not highlights:
            highlights = ["No standout lines identified in this section"]
        
        return highlights[:5]  # Limit to 5 highlights
    
    def _score_line_cleverness(self, line: str) -> float:
        """Score a line for cleverness (metaphors, cultural references, unique angles)"""
        line_lower = line.lower()
        score = 50.0  # Base score
        
        # Metaphor indicators
        metaphor_indicators = ['like', 'as', 'metaphor', 'simile', 'compare', 'imagine', 'picture', 'seems', 'appears']
        for indicator in metaphor_indicators:
            if indicator in line_lower:
                score += 10
        
        # Cultural references
        cultural_indicators = ['money', 'fame', 'success', 'struggle', 'hustle', 'grind', 'dream', 'goal', 'life', 'death', 'love', 'hate']
        for indicator in cultural_indicators:
            if indicator in line_lower:
                score += 5
        
        # Unique perspective indicators
        unique_indicators = ['never', 'always', 'only', 'just', 'really', 'actually', 'truly', 'honestly']
        for indicator in unique_indicators:
            if indicator in line_lower:
                score += 3
        
        # Word complexity (longer, more sophisticated words)
        words = line.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        if avg_word_length > 6:
            score += 15
        
        return min(100, score)
    
    def _score_line_wordplay(self, line: str) -> float:
        """Score a line for wordplay (puns, double meanings, clever word usage)"""
        line_lower = line.lower()
        score = 50.0  # Base score
        
        # Pun indicators
        pun_indicators = ['play', 'word', 'double', 'meaning', 'flip', 'switch', 'turn', 'change']
        for indicator in pun_indicators:
            if indicator in line_lower:
                score += 12
        
        # Alliteration (repeated consonant sounds)
        words = line.split()
        if len(words) > 2:
            alliteration_count = 0
            for i in range(len(words) - 1):
                if words[i] and words[i+1]:
                    if words[i][0].lower() == words[i+1][0].lower():
                        alliteration_count += 1
            score += alliteration_count * 8
        
        # Assonance (repeated vowel sounds)
        vowels = 'aeiou'
        vowel_patterns = []
        for word in words:
            word_vowels = ''.join(c for c in word.lower() if c in vowels)
            if len(word_vowels) > 1:
                vowel_patterns.append(word_vowels)
        
        if len(vowel_patterns) > 1:
            for i in range(len(vowel_patterns) - 1):
                if vowel_patterns[i] == vowel_patterns[i+1]:
                    score += 10
        
        # Repetition for emphasis
        word_counts = {}
        for word in words:
            word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1
        
        for word, count in word_counts.items():
            if count > 1 and len(word) > 2:
                score += count * 5
        
        return min(100, score)
    
    def _score_line_rhyme(self, line: str, all_lines: List[str], line_index: int) -> float:
        """Score a line for rhyme quality (end rhymes, internal rhymes)"""
        score = 50.0  # Base score
        
        # End rhyme with adjacent lines
        if line_index > 0:
            prev_line = all_lines[line_index - 1]
            if self._lines_rhyme(line, prev_line):
                score += 20
        
        if line_index < len(all_lines) - 1:
            next_line = all_lines[line_index + 1]
            if self._lines_rhyme(line, next_line):
                score += 20
        
        # Internal rhyme within the line
        words = line.split()
        if len(words) > 3:
            internal_rhymes = 0
            for i in range(len(words) - 1):
                for j in range(i + 1, len(words)):
                    if self._words_rhyme(words[i], words[j]):
                        internal_rhymes += 1
            score += internal_rhymes * 8
        
        # Multi-syllabic rhyme detection
        if len(words) > 2:
            for i in range(len(words) - 1):
                if self._is_multi_syllabic_rhyme(words[i], words[i+1]):
                    score += 15
        
        return min(100, score)
    
    def _lines_rhyme(self, line1: str, line2: str) -> bool:
        """Check if two lines rhyme at the end"""
        words1 = line1.split()
        words2 = line2.split()
        
        if not words1 or not words2:
            return False
        
        return self._words_rhyme(words1[-1], words2[-1])
    
    def _words_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words rhyme"""
        # Simple rhyme detection based on ending sounds
        word1_clean = ''.join(c for c in word1.lower() if c.isalpha())
        word2_clean = ''.join(c for c in word2.lower() if c.isalpha())
        
        if len(word1_clean) < 2 or len(word2_clean) < 2:
            return False
        
        # Check last 2-3 characters for rhyme
        for length in [3, 2]:
            if len(word1_clean) >= length and len(word2_clean) >= length:
                if word1_clean[-length:] == word2_clean[-length:]:
                    return True
        
        return False
    
    def _is_multi_syllabic_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words form a multi-syllabic rhyme"""
        # Simple multi-syllabic detection (words with similar ending patterns)
        word1_clean = ''.join(c for c in word1.lower() if c.isalpha())
        word2_clean = ''.join(c for c in word2.lower() if c.isalpha())
        
        if len(word1_clean) < 4 or len(word2_clean) < 4:
            return False
        
        # Check for longer rhyming patterns (4+ characters)
        for length in [4, 5]:
            if len(word1_clean) >= length and len(word2_clean) >= length:
                if word1_clean[-length:] == word2_clean[-length:]:
                    return True
        
        return False
    
    def _parse_highlights(self, ai_response: str) -> List[str]:
        """Parse AI response to extract highlights"""
        try:
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                highlights = json.loads(json_match.group())
                if isinstance(highlights, list):
                    return highlights[:5]  # Limit to 5 highlights
            return ["No highlights found"]
        except Exception as e:
            print(f"Failed to parse highlights: {e}")
            return ["Error parsing highlights"]
    
    def predict_genre(self, analysis_results: List[Dict[str, Any]], selected_genre: str = "hip_hop_rap") -> str:
        """
        Return the selected genre instead of predicting it
        
        Args:
            analysis_results (List): Analysis results from sections
            selected_genre (str): User-selected genre
            
        Returns:
            str: The selected genre (not a prediction)
        """
        # Get genre information for proper display
        genre_data = self.billboard_data.get('genres', {}).get(selected_genre, {})
        genre_name = genre_data.get('name', selected_genre.replace('_', ' ').title())
        
        return genre_name
    
    def predict_popularity(self, overall_scores: Dict[str, float]) -> Dict[str, Any]:
        """Predict popularity potential based on scores"""
        radio_score = overall_scores.get('radio_score', 50)
        cleverness = overall_scores.get('cleverness', 50)
        wordplay = overall_scores.get('wordplay', 50)
        
        # Calculate popularity score
        popularity_score = (radio_score * 0.5) + (cleverness * 0.3) + (wordplay * 0.2)
        
        # Determine popularity level
        if popularity_score >= 80:
            level = "High"
            description = "Strong commercial potential with viral appeal"
        elif popularity_score >= 60:
            level = "Medium"
            description = "Good potential for niche success"
        else:
            level = "Low"
            description = "More suited for underground/niche audiences"
        
        return {
            'score': round(popularity_score, 1),
            'level': level,
            'description': description,
            'viral_potential': radio_score > 70,
            'critical_appeal': cleverness > 75
        }
    
    def generate_suggestions(self, overall_scores: Dict[str, float], analysis_results: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on scores"""
        suggestions = []
        
        # Analyze each score category
        if overall_scores.get('cleverness', 0) < 60:
            suggestions.append("Add more metaphors and cultural references to increase cleverness")
        
        if overall_scores.get('rhyme_density', 0) < 60:
            suggestions.append("Incorporate more internal rhymes and complex rhyme schemes")
        
        if overall_scores.get('wordplay', 0) < 60:
            suggestions.append("Include more puns and punchlines to enhance wordplay")
        
        if overall_scores.get('radio_score', 0) < 60:
            suggestions.append("Simplify some lines and add more hook-like phrases for radio appeal")
        
        # Add positive feedback
        if overall_scores.get('cleverness', 0) > 80:
            suggestions.append("Excellent use of metaphors and clever wordplay!")
        
        if overall_scores.get('rhyme_density', 0) > 80:
            suggestions.append("Strong rhyme patterns and flow!")
        
        if len(suggestions) == 0:
            suggestions.append("Great work! Your lyrics show strong balance across all categories.")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def generate_song_description(self, lyrics: str, song_title: str = "", artist_name: str = "", selected_genre: str = "hip_hop_rap") -> Dict[str, Any]:
        """
        Generate AI-powered song description and sub-genre prediction
        
        Args:
            lyrics (str): The song lyrics
            song_title (str): Song title (optional)
            artist_name (str): Artist name (optional)
            selected_genre (str): User-selected genre for analysis
            
        Returns:
            Dict: Song description, sub-genre prediction, and themes
        """
        if not self.client:
            # Use rule-based analysis when AI is not available
            return self._rule_based_song_description(lyrics, song_title, artist_name, selected_genre)
        
        try:
            # Get genre information for context
            genre_data = self.billboard_data.get('genres', {}).get(selected_genre, {})
            genre_name = genre_data.get('name', selected_genre.replace('_', ' ').title())
            
            prompt = f"""
Analyze these lyrics and provide a comprehensive song description and sub-genre prediction within the {genre_name} genre.

Song Title: {song_title or "Untitled"}
Artist: {artist_name or "Unknown Artist"}
Selected Genre: {genre_name}
Lyrics:
{lyrics}

Please provide:
1. A detailed song description (2-3 sentences) that correctly identifies this as a {genre_name} song
2. Sub-genre prediction within {genre_name} (e.g., for country: Mainstream Country, Outlaw Country, Country Pop, etc.)
3. Key themes and topics
4. Mood and tone analysis
5. Target audience

IMPORTANT: The song should be described as a {genre_name} song, not hip-hop or rap, unless {genre_name} is actually hip-hop/rap.

Return only a JSON object like this:
{{
    "description": "A detailed description of the song's content and style as a {genre_name} song",
    "sub_genre": "predicted sub-genre within {genre_name}",
    "themes": ["theme1", "theme2", "theme3"],
    "mood": "mood description",
    "target_audience": "target audience description",
    "lyrical_style": "description of lyrical approach"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert music analyst specializing in {genre_name} music. Analyze lyrics to determine sub-genres within {genre_name}, themes, and provide detailed descriptions. Always identify the song as {genre_name}, not hip-hop or rap unless the selected genre is actually hip-hop/rap."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            ai_response = response.choices[0].message.content.strip()
            return self._parse_song_description(ai_response)
            
        except Exception as e:
            print(f"AI song description failed: {e}")
            return self._rule_based_song_description(lyrics, song_title, artist_name, selected_genre)
    
    def _rule_based_song_description(self, lyrics: str, song_title: str, artist_name: str, selected_genre: str) -> Dict[str, Any]:
        """Generate song description using rule-based analysis"""
        lyrics_lower = lyrics.lower()
        words = lyrics_lower.split()
        
        # Get genre information
        genre_data = self.billboard_data.get('genres', {}).get(selected_genre, {})
        genre_name = genre_data.get('name', selected_genre.replace('_', ' ').title())
        
        # Sub-genre detection based on selected genre and lyrical content
        sub_genre = self._detect_sub_genre(lyrics_lower, words, selected_genre)
        
        # Theme detection
        themes = self._detect_themes(lyrics_lower, words)
        
        # Mood detection
        mood = self._detect_mood(lyrics_lower, words)
        
        # Generate description
        description = self._generate_description(lyrics, song_title, artist_name, sub_genre, themes, genre_name)
        
        return {
            "description": description,
            "sub_genre": sub_genre,
            "themes": themes,
            "mood": mood,
            "target_audience": self._determine_target_audience(sub_genre, themes, selected_genre),
            "lyrical_style": self._analyze_lyrical_style(lyrics_lower, words)
        }
    
    def _detect_sub_genre(self, lyrics: str, words: List[str], selected_genre: str) -> str:
        """Detect sub-genre based on selected genre and lyrical content"""
        
        # Genre-specific sub-genre detection
        if selected_genre == "country":
            # Country sub-genres
            country_indicators = {
                'Mainstream Country': ['country', 'rural', 'small town', 'pickup truck', 'dirt road', 'farm', 'ranch'],
                'Outlaw Country': ['outlaw', 'rebel', 'prison', 'jail', 'criminal', 'law', 'justice'],
                'Country Pop': ['pop', 'radio', 'hit', 'chart', 'mainstream', 'commercial'],
                'Bluegrass': ['bluegrass', 'banjo', 'fiddle', 'mandolin', 'acoustic', 'traditional'],
                'Country Rock': ['rock', 'guitar', 'electric', 'band', 'concert', 'stage']
            }
        elif selected_genre == "hip_hop_rap":
            # Hip-hop sub-genres (existing logic)
            drill_indicators = ['drill', 'opps', 'opposition', 'gang', 'violence', 'shoot', 'gun', 'dead', 'kill', 'blood', 'war']
            drill_count = sum(1 for word in words if any(indicator in word for indicator in drill_indicators))
            
            trap_indicators = ['trap', 'dope', 'drugs', 'money', 'cash', 'bands', 'racks', 'hundreds', 'thousands', 'million']
            trap_count = sum(1 for word in words if any(indicator in word for indicator in trap_indicators))
            
            conscious_indicators = ['conscious', 'awareness', 'social', 'justice', 'equality', 'freedom', 'rights', 'change', 'revolution']
            conscious_count = sum(1 for word in words if any(indicator in word for indicator in conscious_indicators))
            
            boom_bap_indicators = ['knowledge', 'wisdom', 'intellectual', 'philosophy', 'metaphor', 'simile', 'complex', 'sophisticated']
            boom_bap_count = sum(1 for word in words if any(indicator in word for indicator in boom_bap_indicators))
            
            alternative_indicators = ['alternative', 'experimental', 'unique', 'different', 'creative', 'artistic', 'abstract']
            alternative_count = sum(1 for word in words if any(indicator in word for indicator in alternative_indicators))
            
            counts = {
                'Drill': drill_count,
                'Trap': trap_count,
                'Conscious': conscious_count,
                'Boom Bap': boom_bap_count,
                'Alternative': alternative_count
            }
            
            max_genre = max(counts, key=counts.get)
            return max_genre if counts[max_genre] > 0 else 'Mainstream Hip-Hop'
            
        elif selected_genre == "pop":
            # Pop sub-genres
            pop_indicators = {
                'Mainstream Pop': ['pop', 'radio', 'hit', 'chart', 'mainstream', 'commercial'],
                'Pop Rock': ['rock', 'guitar', 'band', 'electric', 'concert'],
                'Electropop': ['electronic', 'synth', 'digital', 'computer', 'electric'],
                'Teen Pop': ['teen', 'young', 'school', 'crush', 'first love', 'innocent'],
                'Adult Contemporary': ['adult', 'mature', 'sophisticated', 'romantic', 'love']
            }
        elif selected_genre == "r_b":
            # R&B sub-genres
            r_b_indicators = {
                'Contemporary R&B': ['r&b', 'soul', 'smooth', 'romantic', 'love'],
                'Neo Soul': ['neo', 'soul', 'conscious', 'spiritual', 'jazz'],
                'Alternative R&B': ['alternative', 'experimental', 'unique', 'different'],
                'Hip-Hop Soul': ['hip-hop', 'rap', 'urban', 'street', 'gritty']
            }
        elif selected_genre == "electronic_dance":
            # EDM sub-genres
            edm_indicators = {
                'Mainstream EDM': ['edm', 'electronic', 'dance', 'club', 'party'],
                'House': ['house', 'groove', 'rhythm', 'beat', 'dance'],
                'Dubstep': ['dubstep', 'bass', 'heavy', 'intense', 'drop'],
                'Trance': ['trance', 'melodic', 'atmospheric', 'dreamy', 'ethereal']
            }
        elif selected_genre == "rock":
            # Rock sub-genres
            rock_indicators = {
                'Mainstream Rock': ['rock', 'guitar', 'band', 'electric', 'concert'],
                'Alternative Rock': ['alternative', 'indie', 'underground', 'experimental'],
                'Hard Rock': ['hard', 'heavy', 'metal', 'aggressive', 'power'],
                'Classic Rock': ['classic', 'vintage', 'retro', 'timeless', 'legendary']
            }
        else:
            # Default to mainstream for unknown genres
            return f"Mainstream {selected_genre.replace('_', ' ').title()}"
        
        # For country and other genres, use the appropriate indicators
        if selected_genre == "country":
            counts = {}
            for sub_genre, indicators in country_indicators.items():
                counts[sub_genre] = sum(1 for word in words if any(indicator in word for indicator in indicators))
            max_genre = max(counts, key=counts.get)
            return max_genre if counts[max_genre] > 0 else 'Mainstream Country'
        elif selected_genre == "pop":
            counts = {}
            for sub_genre, indicators in pop_indicators.items():
                counts[sub_genre] = sum(1 for word in words if any(indicator in word for indicator in indicators))
            max_genre = max(counts, key=counts.get)
            return max_genre if counts[max_genre] > 0 else 'Mainstream Pop'
        elif selected_genre == "r_b":
            counts = {}
            for sub_genre, indicators in r_b_indicators.items():
                counts[sub_genre] = sum(1 for word in words if any(indicator in word for indicator in indicators))
            max_genre = max(counts, key=counts.get)
            return max_genre if counts[max_genre] > 0 else 'Contemporary R&B'
        elif selected_genre == "electronic_dance":
            counts = {}
            for sub_genre, indicators in edm_indicators.items():
                counts[sub_genre] = sum(1 for word in words if any(indicator in word for indicator in indicators))
            max_genre = max(counts, key=counts.get)
            return max_genre if counts[max_genre] > 0 else 'Mainstream EDM'
        elif selected_genre == "rock":
            counts = {}
            for sub_genre, indicators in rock_indicators.items():
                counts[sub_genre] = sum(1 for word in words if any(indicator in word for indicator in indicators))
            max_genre = max(counts, key=counts.get)
            return max_genre if counts[max_genre] > 0 else 'Mainstream Rock'
    
    def _detect_themes(self, lyrics: str, words: List[str]) -> List[str]:
        """Detect themes in the lyrics"""
        themes = []
        
        theme_indicators = {
            'Success': ['success', 'win', 'victory', 'champion', 'king', 'boss', 'leader'],
            'Struggle': ['struggle', 'hardship', 'pain', 'suffering', 'difficult', 'challenge'],
            'Money': ['money', 'cash', 'wealth', 'rich', 'million', 'billion', 'dollar'],
            'Love': ['love', 'heart', 'romance', 'relationship', 'girl', 'woman', 'baby'],
            'Violence': ['violence', 'fight', 'war', 'gun', 'shoot', 'kill', 'blood'],
            'Social Issues': ['social', 'justice', 'equality', 'rights', 'freedom', 'change'],
            'Lifestyle': ['lifestyle', 'luxury', 'cars', 'jewelry', 'fashion', 'designer'],
            'Motivation': ['motivation', 'inspire', 'dream', 'goal', 'ambition', 'aspire']
        }
        
        for theme, indicators in theme_indicators.items():
            if any(indicator in lyrics for indicator in indicators):
                themes.append(theme)
        
        return themes[:5]  # Limit to top 5 themes
    
    def _detect_mood(self, lyrics: str, words: List[str]) -> str:
        """Detect the mood of the lyrics"""
        positive_words = ['happy', 'joy', 'success', 'win', 'love', 'good', 'great', 'amazing', 'wonderful']
        negative_words = ['sad', 'pain', 'hate', 'anger', 'fear', 'death', 'violence', 'struggle']
        aggressive_words = ['fight', 'war', 'attack', 'destroy', 'kill', 'violence', 'anger']
        
        positive_count = sum(1 for word in words if any(pos in word for pos in positive_words))
        negative_count = sum(1 for word in words if any(neg in word for neg in negative_words))
        aggressive_count = sum(1 for word in words if any(agg in word for agg in aggressive_words))
        
        if aggressive_count > positive_count and aggressive_count > negative_count:
            return "Aggressive and confrontational"
        elif positive_count > negative_count:
            return "Positive and uplifting"
        elif negative_count > positive_count:
            return "Dark and introspective"
        else:
            return "Balanced and reflective"
    
    def _generate_description(self, lyrics: str, song_title: str, artist_name: str, sub_genre: str, themes: List[str], genre_name: str) -> str:
        """Generate a song description"""
        line_count = len(lyrics.split('\n'))
        word_count = len(lyrics.split())
        
        artist_text = f" by {artist_name}" if artist_name else ""
        title_text = song_title if song_title else "This track"
        
        theme_text = ", ".join(themes[:3]) if themes else "various themes"
        
        description = f"{title_text}{artist_text} is a {sub_genre.lower()} {genre_name} song that explores {theme_text}. "
        
        if line_count > 20:
            description += "The song features extensive lyrical content with multiple verses and choruses. "
        elif line_count > 10:
            description += "The track presents a moderate-length composition with balanced structure. "
        else:
            description += "The song offers a concise, focused lyrical approach. "
        
        description += f"With approximately {word_count} words, it demonstrates a {self._get_complexity_level(word_count)} lyrical complexity."
        
        return description
    
    def _get_complexity_level(self, word_count: int) -> str:
        """Determine lyrical complexity level"""
        if word_count > 200:
            return "high"
        elif word_count > 100:
            return "moderate"
        else:
            return "straightforward"
    
    def _determine_target_audience(self, sub_genre: str, themes: List[str], selected_genre: str) -> str:
        """Determine target audience based on sub-genre, themes, and selected genre"""
        
        # Genre-specific target audience determination
        if selected_genre == "country":
            if "Outlaw" in sub_genre:
                return "Country music fans, typically 25-45, who appreciate traditional and rebellious themes"
            elif "Pop" in sub_genre:
                return "Mainstream country and pop fans, 18-35, with crossover appeal"
            elif "Bluegrass" in sub_genre:
                return "Traditional country and bluegrass enthusiasts, 30-60"
            else:
                return "Mainstream country music fans, 25-50, with broad appeal"
                
        elif selected_genre == "hip_hop_rap":
            if sub_genre == 'Drill':
                return "Young urban audience, typically 16-25"
            elif sub_genre == 'Trap':
                return "Mainstream hip-hop fans, 18-35"
            elif sub_genre == 'Conscious':
                return "Socially aware listeners, 20-40"
            elif sub_genre == 'Boom Bap':
                return "Hip-hop purists and intellectuals, 25-45"
            elif sub_genre == 'Alternative':
                return "Experimental music fans, 18-35"
            else:
                return "General hip-hop audience, 16-40"
                
        elif selected_genre == "pop":
            if "Teen" in sub_genre:
                return "Teenage and young adult audience, 13-25"
            elif "Adult Contemporary" in sub_genre:
                return "Adult listeners, 25-45, seeking sophisticated pop music"
            elif "Electropop" in sub_genre:
                return "Young adult audience, 18-30, who enjoy electronic elements"
            else:
                return "Mainstream pop audience, 15-40, with broad demographic appeal"
                
        elif selected_genre == "r_b":
            if "Neo Soul" in sub_genre:
                return "Soul music enthusiasts, 25-45, who appreciate conscious themes"
            elif "Alternative" in sub_genre:
                return "Experimental R&B fans, 20-35, seeking unique sounds"
            elif "Hip-Hop Soul" in sub_genre:
                return "Urban music fans, 18-35, who enjoy hip-hop and R&B fusion"
            else:
                return "Contemporary R&B fans, 20-40, with romantic and emotional appeal"
                
        elif selected_genre == "electronic_dance":
            if "House" in sub_genre:
                return "Club and dance music enthusiasts, 18-35"
            elif "Dubstep" in sub_genre:
                return "Bass music fans, 18-30, who enjoy heavy electronic sounds"
            elif "Trance" in sub_genre:
                return "Electronic music purists, 20-40, who appreciate melodic and atmospheric sounds"
            else:
                return "EDM and dance music fans, 18-35, with festival and club appeal"
                
        elif selected_genre == "rock":
            if "Alternative" in sub_genre:
                return "Indie and alternative rock fans, 20-40"
            elif "Hard Rock" in sub_genre:
                return "Heavy rock and metal fans, 18-35"
            elif "Classic Rock" in sub_genre:
                return "Rock music enthusiasts, 30-60, who appreciate timeless rock"
            else:
                return "Mainstream rock fans, 20-45, with broad rock appeal"
        else:
            # Default for unknown genres
            return f"General {selected_genre.replace('_', ' ')} music fans, 18-45"
    
    def _analyze_lyrical_style(self, lyrics: str, words: List[str]) -> str:
        """Analyze the lyrical style and approach"""
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length > 8:
            style = "Sophisticated vocabulary with complex word choices"
        elif avg_word_length > 6:
            style = "Moderate complexity with accessible language"
        else:
            style = "Direct and straightforward lyrical approach"
        
        # Check for repetition
        unique_words = len(set(words))
        repetition_ratio = unique_words / len(words) if words else 1
        
        if repetition_ratio < 0.6:
            style += " with significant repetition for emphasis"
        elif repetition_ratio < 0.8:
            style += " with moderate repetition"
        else:
            style += " with varied vocabulary"
        
        return style
    
    def _parse_song_description(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response to extract song description"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                description_data = json.loads(json_match.group())
                
                # Ensure all required fields are present
                required_fields = ['description', 'sub_genre', 'themes', 'mood', 'target_audience', 'lyrical_style']
                for field in required_fields:
                    if field not in description_data:
                        description_data[field] = "Not specified"
                
                return description_data
            else:
                raise ValueError("No JSON found in AI response")
                
        except Exception as e:
            print(f"Failed to parse AI song description: {e}")
            return {
                'description': 'AI analysis not available',
                'sub_genre': 'Unknown',
                'themes': ['Unknown'],
                'mood': 'Unknown',
                'target_audience': 'Unknown',
                'lyrical_style': 'Unknown'
            } 