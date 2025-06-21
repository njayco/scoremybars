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
                # Try to create OpenAI client with error handling
                self.client = openai.OpenAI(api_key=api_key)
                # Test the client with a simple call
                self.client.models.list()
            except Exception as e:
                print(f"OpenAI client initialization failed: {e}")
                print("Falling back to rule-based scoring only")
                self.client = None
        
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
        """Get highlights and standout lines from the text"""
        if not self.client:
            return ["AI analysis not available - using basic highlighting"]
        
        try:
            prompt = f"""
Analyze these rap lyrics and identify 3-5 standout lines or phrases that demonstrate:
- Clever wordplay
- Strong metaphors
- Effective punchlines
- Memorable hooks

Lyrics:
{text}

Return only a JSON array of strings with the highlights.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a rap lyric analyst. Identify standout lines and return them as a JSON array."
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
            return ["AI analysis not available"]
    
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
    
    def predict_genre(self, analysis_results: List[Dict[str, Any]]) -> str:
        """Predict the most likely genre based on analysis"""
        if not analysis_results:
            return "Unknown"
        
        # Analyze overall characteristics
        total_cleverness = sum(section['scores']['cleverness'] for section in analysis_results)
        total_rhyme_density = sum(section['scores']['rhyme_density'] for section in analysis_results)
        total_wordplay = sum(section['scores']['wordplay'] for section in analysis_results)
        total_radio_score = sum(section['scores']['radio_score'] for section in analysis_results)
        
        num_sections = len(analysis_results)
        avg_cleverness = total_cleverness / num_sections
        avg_rhyme_density = total_rhyme_density / num_sections
        avg_wordplay = total_wordplay / num_sections
        avg_radio_score = total_radio_score / num_sections
        
        # Genre prediction logic
        if avg_radio_score > 75:
            return "Commercial/Pop"
        elif avg_cleverness > 80 and avg_wordplay > 80:
            return "Boom Bap/Conscious"
        elif avg_rhyme_density > 85:
            return "Trap"
        elif avg_cleverness > 70:
            return "Alternative/Experimental"
        else:
            return "Drill"
    
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
    
    def generate_song_description(self, lyrics: str, song_title: str = "", artist_name: str = "") -> Dict[str, Any]:
        """
        Generate AI-powered song description and sub-genre prediction
        
        Args:
            lyrics (str): The song lyrics
            song_title (str): Song title (optional)
            artist_name (str): Artist name (optional)
            
        Returns:
            Dict: Song description, sub-genre prediction, and themes
        """
        if not self.client:
            # Use rule-based analysis when AI is not available
            return self._rule_based_song_description(lyrics, song_title, artist_name)
        
        try:
            prompt = f"""
Analyze these rap lyrics and provide a comprehensive song description and sub-genre prediction.

Song Title: {song_title or "Untitled"}
Artist: {artist_name or "Unknown Artist"}
Lyrics:
{lyrics}

Please provide:
1. A detailed song description (2-3 sentences)
2. Sub-genre prediction (e.g., Drill, Trap, Boom Bap, Conscious, Alternative, etc.)
3. Key themes and topics
4. Mood and tone analysis
5. Target audience

Return only a JSON object like this:
{{
    "description": "A detailed description of the song's content and style",
    "sub_genre": "predicted sub-genre",
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
                        "content": "You are an expert music analyst specializing in hip-hop and rap music. Analyze lyrics to determine sub-genres, themes, and provide detailed descriptions."
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
            return self._rule_based_song_description(lyrics, song_title, artist_name)
    
    def _rule_based_song_description(self, lyrics: str, song_title: str, artist_name: str) -> Dict[str, Any]:
        """Generate song description using rule-based analysis"""
        lyrics_lower = lyrics.lower()
        words = lyrics_lower.split()
        
        # Sub-genre detection based on lyrical content
        sub_genre = self._detect_sub_genre(lyrics_lower, words)
        
        # Theme detection
        themes = self._detect_themes(lyrics_lower, words)
        
        # Mood detection
        mood = self._detect_mood(lyrics_lower, words)
        
        # Generate description
        description = self._generate_description(lyrics, song_title, artist_name, sub_genre, themes)
        
        return {
            "description": description,
            "sub_genre": sub_genre,
            "themes": themes,
            "mood": mood,
            "target_audience": self._determine_target_audience(sub_genre, themes),
            "lyrical_style": self._analyze_lyrical_style(lyrics_lower, words)
        }
    
    def _detect_sub_genre(self, lyrics: str, words: List[str]) -> str:
        """Detect sub-genre based on lyrical content"""
        # Drill indicators
        drill_indicators = ['drill', 'opps', 'opposition', 'gang', 'violence', 'shoot', 'gun', 'dead', 'kill', 'blood', 'war']
        drill_count = sum(1 for word in words if any(indicator in word for indicator in drill_indicators))
        
        # Trap indicators
        trap_indicators = ['trap', 'dope', 'drugs', 'money', 'cash', 'bands', 'racks', 'hundreds', 'thousands', 'million']
        trap_count = sum(1 for word in words if any(indicator in word for indicator in trap_indicators))
        
        # Conscious indicators
        conscious_indicators = ['conscious', 'awareness', 'social', 'justice', 'equality', 'freedom', 'rights', 'change', 'revolution']
        conscious_count = sum(1 for word in words if any(indicator in word for indicator in conscious_indicators))
        
        # Boom Bap indicators
        boom_bap_indicators = ['knowledge', 'wisdom', 'intellectual', 'philosophy', 'metaphor', 'simile', 'complex', 'sophisticated']
        boom_bap_count = sum(1 for word in words if any(indicator in word for indicator in boom_bap_indicators))
        
        # Alternative indicators
        alternative_indicators = ['alternative', 'experimental', 'unique', 'different', 'creative', 'artistic', 'abstract']
        alternative_count = sum(1 for word in words if any(indicator in word for indicator in alternative_indicators))
        
        # Determine sub-genre based on highest count
        counts = {
            'Drill': drill_count,
            'Trap': trap_count,
            'Conscious': conscious_count,
            'Boom Bap': boom_bap_count,
            'Alternative': alternative_count
        }
        
        max_genre = max(counts, key=counts.get)
        return max_genre if counts[max_genre] > 0 else 'Mainstream Hip-Hop'
    
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
    
    def _generate_description(self, lyrics: str, song_title: str, artist_name: str, sub_genre: str, themes: List[str]) -> str:
        """Generate a song description"""
        line_count = len(lyrics.split('\n'))
        word_count = len(lyrics.split())
        
        artist_text = f" by {artist_name}" if artist_name else ""
        title_text = song_title if song_title else "This track"
        
        theme_text = ", ".join(themes[:3]) if themes else "various themes"
        
        description = f"{title_text}{artist_text} is a {sub_genre.lower()} hip-hop song that explores {theme_text}. "
        
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
    
    def _determine_target_audience(self, sub_genre: str, themes: List[str]) -> str:
        """Determine target audience based on sub-genre and themes"""
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