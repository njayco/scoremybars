import re
import pronouncing
from typing import List, Dict, Any, Tuple

class RhymeEngine:
    """Analyzes rhyme patterns and density in rap lyrics"""
    
    def __init__(self):
        self.vowels = 'aeiouAEIOU'
        self.consonants = 'bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
        
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
            'slant_rhymes': self._find_slant_rhymes(lines)
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
                        'words': [word1, word2],
                        'syllables': self._count_syllables(word1)
                    })
        
        return multi_syllabic_rhymes
    
    def _find_slant_rhymes(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Find slant rhymes (near rhymes)"""
        slant_rhymes = []
        
        for line_idx, line in enumerate(lines):
            words = line.lower().split()
            words = [word.strip('.,!?;:()[]{}') for word in words]
            
            for i in range(len(words)):
                for j in range(i + 1, len(words)):
                    if self._is_slant_rhyme(words[i], words[j]):
                        slant_rhymes.append({
                            'line_index': line_idx,
                            'words': [words[i], words[j]],
                            'similarity': self._calculate_similarity(words[i], words[j])
                        })
        
        return slant_rhymes
    
    def _words_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words rhyme"""
        if word1 == word2:
            return False
        
        # Get pronunciations
        pronunciations1 = pronouncing.phones_for_word(word1)
        pronunciations2 = pronouncing.phones_for_word(word2)
        
        if not pronunciations1 or not pronunciations2:
            return False
        
        # Check if any pronunciations rhyme by comparing ending sounds
        for pron1 in pronunciations1:
            for pron2 in pronunciations2:
                if self._pronunciations_rhyme(pron1, pron2):
                    return True
        
        return False
    
    def _pronunciations_rhyme(self, pron1: str, pron2: str) -> bool:
        """Check if two pronunciations rhyme by comparing ending sounds"""
        # Split pronunciations into phonemes
        phonemes1 = pron1.split()
        phonemes2 = pron2.split()
        
        if len(phonemes1) < 2 or len(phonemes2) < 2:
            return False
        
        # Check if they end with the same vowel sound and consonant
        # Look for the last stressed vowel and everything after it
        stressed_vowel1 = None
        stressed_vowel2 = None
        
        # Find last stressed vowel in pronunciation 1
        for i, phoneme in enumerate(phonemes1):
            if '1' in phoneme:  # Stressed vowel
                stressed_vowel1 = i
                break
        
        # Find last stressed vowel in pronunciation 2
        for i, phoneme in enumerate(phonemes2):
            if '1' in phoneme:  # Stressed vowel
                stressed_vowel2 = i
                break
        
        # If no stressed vowels found, use the last vowel
        if stressed_vowel1 is None:
            for i, phoneme in enumerate(phonemes1):
                if any(vowel in phoneme for vowel in ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']):
                    stressed_vowel1 = i
        
        if stressed_vowel2 is None:
            for i, phoneme in enumerate(phonemes2):
                if any(vowel in phoneme for vowel in ['AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW']):
                    stressed_vowel2 = i
        
        if stressed_vowel1 is None or stressed_vowel2 is None:
            return False
        
        # Get the ending sounds (from stressed vowel to end)
        ending1 = phonemes1[stressed_vowel1:]
        ending2 = phonemes2[stressed_vowel2:]
        
        # Check if endings match
        return ending1 == ending2
    
    def _get_rhyme_key(self, word: str) -> str:
        """Get a rhyme key for grouping rhyming words"""
        pronunciations = pronouncing.phones_for_word(word)
        if not pronunciations:
            return word
        
        # Use the first pronunciation
        return pronunciations[0]
    
    def _is_multi_syllabic_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words form a multi-syllabic rhyme"""
        if not self._words_rhyme(word1, word2):
            return False
        
        syllables1 = self._count_syllables(word1)
        syllables2 = self._count_syllables(word2)
        
        return syllables1 >= 2 and syllables2 >= 2
    
    def _is_slant_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words form a slant rhyme"""
        if word1 == word2 or self._words_rhyme(word1, word2):
            return False
        
        # Check for similar ending sounds
        similarity = self._calculate_similarity(word1, word2)
        return similarity > 0.7
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        pronunciations = pronouncing.phones_for_word(word)
        if not pronunciations:
            return 1
        
        return pronouncing.syllable_count(pronunciations[0])
    
    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate similarity between two words"""
        # Simple similarity based on ending sounds
        if len(word1) < 3 or len(word2) < 3:
            return 0.0
        
        # Check ending similarity
        min_len = min(len(word1), len(word2))
        common_ending = 0
        
        for i in range(1, min_len + 1):
            if word1[-i:] == word2[-i:]:
                common_ending = i
            else:
                break
        
        return common_ending / max(len(word1), len(word2)) 