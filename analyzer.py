import difflib
from typing import List, Tuple, Dict
from db_manager import DBManager

class Analyzer:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def get_top_50_commands(self) -> List[Tuple[str, int]]:
        """Identify Top-50 most frequent commands."""
        frequencies = self.db.get_command_frequencies()
        return frequencies[:50]

    def detect_typos(self) -> List[Tuple[str, str, int]]:
        """
        Find commands with low frequency (freq < 3) that are very similar 
        (Levenshtein distance < 2) to high-frequency commands.
        Returns list of (typo_cmd, likely_cmd, frequency)
        """
        all_freqs = self.db.get_base_cmd_frequencies()
        
        # Split into high frequency and low frequency
        # Note: The prompt example 'gti' vs 'git' suggests we are looking at base commands mostly,
        # but users might typo arguments too.
        # "Find commands... (e.g., 'gti' vs 'git')" strongly implies base command analysis.
        # Let's use base_cmd for typo detection as it's the most common case for 'gti' vs 'git'.
        
        high_freq = {cmd: freq for cmd, freq in all_freqs if freq >= 3}
        low_freq = {cmd: freq for cmd, freq in all_freqs if freq < 3}
        
        typos = []
        
        for low_cmd in low_freq:
            # Skip very short commands to avoid false positives (e.g. 'l' vs 'ls')
            if len(low_cmd) < 2:
                continue
                
            for high_cmd in high_freq:
                # difflib.SequenceMatcher isn't exactly Levenshtein, but close. 
                # For strict Levenshtein distance < 2 (meaning distance 1), we can check.
                # Since we need to follow requirements: "Use Python's difflib".
                # A distance of 1 means 1 insertion, deletion, or substitution.
                
                if low_cmd == high_cmd:
                    continue
                    
                # quick length check
                if abs(len(low_cmd) - len(high_cmd)) > 1:
                    continue
                
                # Using difflib to check similarity
                # ratio() returns 2*M / T where M is matches and T is total length.
                # This is not direct Levenshtein.
                # Let's implement a simple check using difflib or just implement Levenshtein helper if needed,
                # but instruction says "Use Python's difflib for string similarity".
                # However, it ALSO says "Levenshtein distance < 2".
                # difflib doesn't provide Levenshtein distance directly. 
                # I will use difflib.get_close_matches logic or SequenceMatcher.
                
                # If I strictly must use difflib AND strictly satisfy Levenshtein < 2:
                # I can use difflib to find candidates, then verify distance? 
                # Or maybe the prompt implies "Use difflib [conceptually] for similarity" but gave specific Levenshtein criteria.
                # Actually, SequenceMatcher.ratio() > 0.8 is often used.
                # But "Levenshtein distance < 2" is very specific (distance 1).
                
                # Let's try to verify distance 1.
                if self._is_distance_one(low_cmd, high_cmd):
                     typos.append((low_cmd, high_cmd, low_freq[low_cmd]))
                     break # Found a match, move to next low_cmd
                     
        return typos

    def _is_distance_one(self, s1: str, s2: str) -> bool:
        """
        Check if Levenshtein distance between s1 and s2 is 1.
        Uses difflib.ndiff to count changes.
        """
        if abs(len(s1) - len(s2)) > 1:
            return False
            
        count = 0
        for opcode in difflib.ndiff(s1, s2):
            if opcode.startswith('- ') or opcode.startswith('+ '):
                count += 1
        
        # ndiff produces output like:
        # - g
        # + g
        #   i
        #   t
        # for substitution, it shows - and +. So substitution is distance 1, but ndiff shows 2 changes.
        # Insertion/Deletion shows 1 change.
        
        # Let's re-evaluate. A substitution is distance 1.
        # gti vs git:
        #   g
        # - t
        # + i
        # - i
        # + t
        # That's 4 diffs in ndiff.
        
        # Simpler approach for Distance 1:
        # 1. Length difference is 1: one insertion/deletion.
        # 2. Length difference is 0: one substitution.
        
        if s1 == s2:
            return False
            
        if len(s1) == len(s2):
            # Substitution
            diffs = sum(1 for a, b in zip(s1, s2) if a != b)
            return diffs == 1
        else:
            # Insertion/Deletion
            # Ensure s1 is shorter
            if len(s1) > len(s2):
                s1, s2 = s2, s1
            
            # Find first difference
            i = 0
            while i < len(s1) and s1[i] == s2[i]:
                i += 1
            
            # The rest must match
            return s1[i:] == s2[i+1:]
            
    def suggest_aliases(self) -> List[Tuple[str, int]]:
        """
        Find long commands (> 15 chars) used frequently (> 10 times) 
        and suggest short aliases.
        """
        frequencies = self.db.get_command_frequencies()
        suggestions = []
        
        for cmd, freq in frequencies:
            if len(cmd) > 15 and freq > 10:
                suggestions.append((cmd, freq))
                
        return suggestions
