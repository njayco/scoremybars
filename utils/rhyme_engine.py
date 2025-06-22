import re
from typing import List, Dict, Any, Tuple

class RhymeEngine:
    """Analyzes rhyme patterns and density in rap lyrics"""
    
    def __init__(self):
        self.vowels = 'aeiouAEIOU'
        self.consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        
        # Common rhyme patterns for simple detection
        self.rhyme_patterns = {
            'ing': ['ing', 'in', 'im'],
            'er': ['er', 'ir', 'ur'],
            'ed': ['ed', 'd', 't'],
            's': ['s', 'z', 'es'],
            'ly': ['ly', 'lee', 'li'],
            'tion': ['tion', 'sion', 'cion'],
            'able': ['able', 'ible'],
            'ous': ['ous', 'us'],
            'al': ['al', 'el', 'il', 'ol', 'ul'],
            'ate': ['ate', 'it', 'et'],
            'ize': ['ize', 'ise', 'yze'],
            'ment': ['ment', 'mint'],
            'ness': ['ness', 'nis'],
            'ful': ['ful', 'full'],
            'less': ['less', 'les'],
            'ing': ['ing', 'in', 'im'],
            'ed': ['ed', 'd', 't'],
            's': ['s', 'z', 'es'],
            'ly': ['ly', 'lee', 'li'],
            'tion': ['tion', 'sion', 'cion'],
            'able': ['able', 'ible'],
            'ous': ['ous', 'us'],
            'al': ['al', 'el', 'il', 'ol', 'ul'],
            'ate': ['ate', 'it', 'et'],
            'ize': ['ize', 'ise', 'yze'],
            'ment': ['ment', 'mint'],
            'ness': ['ness', 'nis'],
            'ful': ['ful', 'full'],
            'less': ['less', 'les']
        }
        
    def analyze_rhymes(self, text: str) -> Dict[str, Any]:
        """
        Analyze rhyme patterns in the given text
        
        Args:
            text (str): Lyrics text to analyze
            
        Returns:
            Dict: Rhyme analysis results
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        analysis = {
            'end_rhymes': self._analyze_end_rhymes(lines),
            'internal_rhymes': self._analyze_internal_rhymes(lines),
            'rhyme_density': self._calculate_rhyme_density(lines),
            'rhyme_scheme': self._detect_rhyme_scheme(lines),
            'multi_syllabic_rhymes': self._find_multi_syllabic_rhymes(lines),
            'slant_rhymes': self._find_slant_rhymes(lines),
            'pattern': self._detect_rhyme_scheme(lines)  # Add pattern for compatibility
        }
        
        return analysis
    
    def _analyze_end_rhymes(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze end rhymes in the lines"""
        end_rhymes = {
            'rhyme_groups': [],
            'rhyme_pairs': [],
            'rhyme_density': 0
        }
        
        # Get last words of each line
        last_words = []
        for line in lines:
            words = line.split()
            if words:
                last_words.append(words[-1].lower().strip('.,!?;:()[]{}'))
        
        # Find rhyming pairs
        rhyme_pairs = []
        for i in range(len(last_words)):
            for j in range(i + 1, len(last_words)):
                if self._words_rhyme(last_words[i], last_words[j]):
                    rhyme_pairs.append((i, j, last_words[i], last_words[j]))
        
        end_rhymes['rhyme_pairs'] = rhyme_pairs
        
        # Group rhymes
        rhyme_groups = {}
        for pair in rhyme_pairs:
            word1, word2 = pair[2], pair[3]
            rhyme_key = self._get_rhyme_key(word1)
            
            if rhyme_key not in rhyme_groups:
                rhyme_groups[rhyme_key] = []
            
            if word1 not in rhyme_groups[rhyme_key]:
                rhyme_groups[rhyme_key].append(word1)
            if word2 not in rhyme_groups[rhyme_key]:
                rhyme_groups[rhyme_key].append(word2)
        
        end_rhymes['rhyme_groups'] = [
            {'rhyme_key': key, 'words': words}
            for key, words in rhyme_groups.items()
        ]
        
        # Calculate rhyme density
        if len(lines) > 1:
            end_rhymes['rhyme_density'] = len(rhyme_pairs) / (len(lines) * (len(lines) - 1) / 2)
        
        return end_rhymes
    
    def _analyze_internal_rhymes(self, lines: List[str]) -> Dict[str, Any]:
        """Analyze internal rhymes within lines"""
        internal_rhymes = {
            'internal_rhyme_pairs': [],
            'internal_rhyme_density': 0
        }
        
        total_internal_rhymes = 0
        
        for line_idx, line in enumerate(lines):
            words = line.lower().split()
            words = [word.strip('.,!?;:()[]{}') for word in words]
            
            # Find internal rhymes within the line
            line_internal_rhymes = []
            for i in range(len(words)):
                for j in range(i + 1, len(words)):
                    if self._words_rhyme(words[i], words[j]):
                        line_internal_rhymes.append((i, j, words[i], words[j]))
            
            if line_internal_rhymes:
                internal_rhymes['internal_rhyme_pairs'].append({
                    'line_index': line_idx,
                    'line': line,
                    'rhymes': line_internal_rhymes
                })
                total_internal_rhymes += len(line_internal_rhymes)
        
        # Calculate internal rhyme density
        total_words = sum(len(line.split()) for line in lines)
        if total_words > 1:
            internal_rhymes['internal_rhyme_density'] = total_internal_rhymes / total_words
        
        return internal_rhymes
    
    def _calculate_rhyme_density(self, lines: List[str]) -> float:
        """Calculate overall rhyme density"""
        if not lines:
            return 0.0
        
        total_rhymes = 0
        total_possible_rhymes = 0
        
        # Count end rhymes
        last_words = []
        for line in lines:
            words = line.split()
            if words:
                last_words.append(words[-1].lower().strip('.,!?;:()[]{}'))
        
        for i in range(len(last_words)):
            for j in range(i + 1, len(last_words)):
                total_possible_rhymes += 1
                if self._words_rhyme(last_words[i], last_words[j]):
                    total_rhymes += 1
        
        # Count internal rhymes
        for line in lines:
            words = line.lower().split()
            words = [word.strip('.,!?;:()[]{}') for word in words]
            
            for i in range(len(words)):
                for j in range(i + 1, len(words)):
                    total_possible_rhymes += 1
                    if self._words_rhyme(words[i], words[j]):
                        total_rhymes += 1
        
        if total_possible_rhymes == 0:
            return 0.0
        
        return total_rhymes / total_possible_rhymes
    
    def _detect_rhyme_scheme(self, lines: List[str]) -> str:
        """Detect the rhyme scheme pattern"""
        if len(lines) < 2:
            return "A"
        
        last_words = []
        for line in lines:
            words = line.split()
            if words:
                last_words.append(words[-1].lower().strip('.,!?;:()[]{}'))
        
        rhyme_scheme = []
        rhyme_map = {}
        current_letter = 'A'
        
        for i, word in enumerate(last_words):
            # Check if this word rhymes with any previous word
            found_rhyme = False
            for j, prev_word in enumerate(last_words[:i]):
                if self._words_rhyme(word, prev_word):
                    rhyme_scheme.append(rhyme_scheme[j])
                    found_rhyme = True
                    break
            
            if not found_rhyme:
                rhyme_scheme.append(current_letter)
                current_letter = chr(ord(current_letter) + 1)
        
        return ''.join(rhyme_scheme)
    
    def _find_multi_syllabic_rhymes(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Find multi-syllabic rhymes"""
        multi_syllabic_rhymes = []
        
        for line_idx, line in enumerate(lines):
            words = line.lower().split()
            words = [word.strip('.,!?;:()[]{}') for word in words]
            
            # Look for multi-syllabic rhymes (2+ syllables)
            for i in range(len(words) - 1):
                word1 = words[i]
                word2 = words[i + 1]
                
                if self._is_multi_syllabic_rhyme(word1, word2):
                    multi_syllabic_rhymes.append({
                        'line_index': line_idx,
                        'line': line,
                        'word1': word1,
                        'word2': word2,
                        'position': (i, i + 1)
                    })
        
        return multi_syllabic_rhymes
    
    def _find_slant_rhymes(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Find slant rhymes (near rhymes)"""
        slant_rhymes = []
        
        for line_idx, line in enumerate(lines):
            words = line.lower().split()
            words = [word.strip('.,!?;:()[]{}') for word in words]
            
            for i in range(len(words) - 1):
                word1 = words[i]
                word2 = words[i + 1]
                
                if self._is_slant_rhyme(word1, word2):
                    slant_rhymes.append({
                        'line_index': line_idx,
                        'line': line,
                        'word1': word1,
                        'word2': word2,
                        'position': (i, i + 1),
                        'similarity': self._calculate_similarity(word1, word2)
                    })
        
        return slant_rhymes
    
    def _words_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words rhyme using custom algorithm"""
        if word1 == word2:
            return False
        
        # Clean words
        word1 = word1.lower().strip('.,!?;:()[]{}')
        word2 = word2.lower().strip('.,!?;:()[]{}')
        
        # Check for exact ending match
        if word1.endswith(word2) or word2.endswith(word1):
            return True
        
        # Check for common rhyme patterns
        for pattern, variations in self.rhyme_patterns.items():
            if word1.endswith(pattern) and word2.endswith(pattern):
                return True
            for variation in variations:
                if word1.endswith(variation) and word2.endswith(variation):
                    return True
        
        # Check for vowel-consonant ending patterns
        if len(word1) >= 3 and len(word2) >= 3:
            # Get last 3 characters
            end1 = word1[-3:]
            end2 = word2[-3:]
            
            # Check if they have similar vowel-consonant patterns
            if self._similar_ending_pattern(end1, end2):
                return True
        
        # Check for similar endings (last 2-4 characters)
        for length in [2, 3, 4]:
            if len(word1) >= length and len(word2) >= length:
                if word1[-length:] == word2[-length:]:
                    return True
        
        return False
    
    def _similar_ending_pattern(self, end1: str, end2: str) -> bool:
        """Check if two word endings have similar vowel-consonant patterns"""
        if len(end1) != len(end2):
            return False
        
        # Convert to vowel/consonant pattern
        pattern1 = ''.join(['V' if c in self.vowels else 'C' for c in end1])
        pattern2 = ''.join(['V' if c in self.vowels else 'C' for c in end2])
        
        return pattern1 == pattern2
    
    def _get_rhyme_key(self, word: str) -> str:
        """Get a rhyme key for grouping similar rhymes"""
        word = word.lower().strip('.,!?;:()[]{}')
        
        # Use last 3 characters as rhyme key
        if len(word) >= 3:
            return word[-3:]
        return word
    
    def _is_multi_syllabic_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words form a multi-syllabic rhyme"""
        if not self._words_rhyme(word1, word2):
            return False
        
        # Check if both words have multiple syllables
        syllables1 = self._count_syllables(word1)
        syllables2 = self._count_syllables(word2)
        
        return syllables1 >= 2 and syllables2 >= 2
    
    def _is_slant_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words form a slant rhyme (near rhyme)"""
        if self._words_rhyme(word1, word2):
            return False
        
        # Calculate similarity
        similarity = self._calculate_similarity(word1, word2)
        return similarity >= 0.7  # 70% similarity threshold
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word using vowel groups"""
        word = word.lower()
        vowels = 'aeiou'
        
        # Count vowel groups
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_char_was_vowel:
                syllable_count += 1
            prev_char_was_vowel = is_vowel
        
        # Handle silent 'e' at the end
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words"""
        if word1 == word2:
            return 1.0
        
        # Use simple character-based similarity
        shorter = min(len(word1), len(word2))
        longer = max(len(word1), len(word2))
        
        if longer == 0:
            return 1.0
        
        # Count matching characters
        matches = 0
        for i in range(shorter):
            if word1[i] == word2[i]:
                matches += 1
        
        return matches / longer 