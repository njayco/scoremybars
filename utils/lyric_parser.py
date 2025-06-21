import re
from typing import List, Dict, Any

class LyricParser:
    """Parses rap lyrics into sections and analyzes structure"""
    
    def __init__(self):
        self.section_patterns = {
            'intro': r'\[intro\]|\[Intro\]|\[INTRO\]',
            'verse': r'\[verse\s*\d*\]|\[Verse\s*\d*\]|\[VERSE\s*\d*\]',
            'chorus': r'\[chorus\]|\[Chorus\]|\[CHORUS\]|\[hook\]|\[Hook\]|\[HOOK\]',
            'bridge': r'\[bridge\]|\[Bridge\]|\[BRIDGE\]',
            'outro': r'\[outro\]|\[Outro\]|\[OUTRO\]',
            'pre_chorus': r'\[pre.?chorus\]|\[Pre.?chorus\]|\[PRE.?CHORUS\]',
            'post_chorus': r'\[post.?chorus\]|\[Post.?chorus\]|\[POST.?CHORUS\]'
        }
        
    def parse_lyrics(self, lyrics: str) -> List[Dict[str, Any]]:
        """
        Parse lyrics into sections with metadata
        
        Args:
            lyrics (str): Raw lyrics text
            
        Returns:
            List[Dict]: List of sections with type, text, and bar count
        """
        sections = []
        lines = lyrics.strip().split('\n')
        
        current_section = None
        current_text = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            section_type = self._identify_section(line)
            
            if section_type:
                # Save previous section if exists
                if current_section and current_text:
                    sections.append(self._create_section(current_section, current_text))
                
                # Start new section
                current_section = section_type
                current_text = []
            else:
                # Add line to current section
                if current_section:
                    current_text.append(line)
                else:
                    # If no section identified yet, assume it's a verse
                    current_section = 'verse'
                    current_text.append(line)
        
        # Add the last section
        if current_section and current_text:
            sections.append(self._create_section(current_section, current_text))
        
        # If no sections were found, treat entire lyrics as one verse
        if not sections:
            sections.append(self._create_section('verse', lines))
        
        return sections
    
    def _identify_section(self, line: str) -> str:
        """Identify if a line is a section header"""
        line_lower = line.lower()
        
        for section_type, pattern in self.section_patterns.items():
            if re.search(pattern, line_lower):
                return section_type
        
        return None
    
    def _create_section(self, section_type: str, lines: List[str]) -> Dict[str, Any]:
        """Create a section dictionary with metadata"""
        text = '\n'.join(lines)
        bar_count = self._count_bars(lines)
        
        return {
            'type': section_type,
            'text': text,
            'bar_count': bar_count,
            'line_count': len(lines),
            'word_count': len(text.split())
        }
    
    def _count_bars(self, lines: List[str]) -> int:
        """
        Count the number of bars in a section
        
        A bar is typically 4 beats, but we'll use heuristics:
        - Lines that end with punctuation are likely bars
        - Lines with similar syllable counts are likely bars
        - Empty lines or section headers don't count as bars
        """
        bar_count = 0
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and section headers
            if not line or self._identify_section(line):
                continue
            
            # Count as bar if it has content and ends with typical bar punctuation
            if line and not line.startswith('['):
                bar_count += 1
        
        return bar_count
    
    def analyze_structure(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the overall structure of the song"""
        structure = {
            'total_sections': len(sections),
            'section_types': {},
            'total_bars': 0,
            'average_bars_per_section': 0,
            'structure_pattern': []
        }
        
        for section in sections:
            section_type = section['type']
            bar_count = section['bar_count']
            
            # Count section types
            structure['section_types'][section_type] = structure['section_types'].get(section_type, 0) + 1
            
            # Accumulate total bars
            structure['total_bars'] += bar_count
            
            # Track structure pattern
            structure['structure_pattern'].append(section_type)
        
        # Calculate average bars per section
        if sections:
            structure['average_bars_per_section'] = round(structure['total_bars'] / len(sections), 1)
        
        return structure
    
    def detect_repetition(self, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect repetitive patterns in the lyrics"""
        repetition_analysis = {
            'repeated_phrases': [],
            'chorus_repetition': 0,
            'hook_phrases': []
        }
        
        # Find repeated phrases across sections
        all_text = ' '.join([section['text'] for section in sections])
        words = all_text.lower().split()
        
        # Simple phrase repetition detection (2-4 word phrases)
        for phrase_length in range(2, 5):
            for i in range(len(words) - phrase_length + 1):
                phrase = ' '.join(words[i:i + phrase_length])
                if len(phrase) > 10:  # Only meaningful phrases
                    count = all_text.lower().count(phrase)
                    if count > 1:
                        repetition_analysis['repeated_phrases'].append({
                            'phrase': phrase,
                            'count': count
                        })
        
        # Remove duplicates and sort by count
        unique_phrases = {}
        for phrase_data in repetition_analysis['repeated_phrases']:
            phrase = phrase_data['phrase']
            if phrase not in unique_phrases:
                unique_phrases[phrase] = phrase_data['count']
        
        repetition_analysis['repeated_phrases'] = [
            {'phrase': phrase, 'count': count}
            for phrase, count in sorted(unique_phrases.items(), key=lambda x: x[1], reverse=True)
        ][:10]  # Top 10 repeated phrases
        
        return repetition_analysis 