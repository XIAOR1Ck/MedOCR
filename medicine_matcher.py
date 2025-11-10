import pandas as pd
from fuzzywuzzy import process, fuzz
from typing import List, Dict, Any, Tuple
import re

class MedicineMatcher:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess the medicine database"""
        self.df['search_text'] = self.df['RXSTRING'].str.lower()
        self.df['extracted_strength'] = self.df['RXSTRING'].apply(self._extract_strength_from_description)
    
    def _extract_strength_from_description(self, description: str) -> str:
        """Extract strength information from medicine description"""
        patterns = [
            r'(\d+\.?\d*)\s*(MG|MCG|MG/ML|MCG/ML|%)',
            r'(\d+\.?\d*)\s*(mg|mcg|mg/ml|mcg/ml|%)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            if matches:
                return ' '.join(matches[0]).upper()
        return ''
    
    def find_matches(self, extracted_info: Dict[str, Any], top_n: int = 5) -> List[Tuple[Dict, float]]:
        """Find matching medicines based on extracted medicine names and strengths"""
        matches = []
        
        medicine_names = extracted_info['medicine_names']
        strengths = extracted_info['strengths']
        
        # Strategy 1: Direct name matching
        if medicine_names:
            name_matches = self._match_by_names(medicine_names, strengths)
            matches.extend(name_matches)
        
        # Strategy 2: Fuzzy matching with entire OCR text
        fuzzy_matches = self._match_by_fuzzy(extracted_info['raw_text'])
        matches.extend(fuzzy_matches)
        
        # Remove duplicates and sort by score
        unique_matches = self._deduplicate_matches(matches)
        unique_matches.sort(key=lambda x: x[1], reverse=True)
        
        return unique_matches[:top_n]
    
    def _match_by_names(self, medicine_names: List[str], strengths: List[str]) -> List[Tuple[Dict, float]]:
        """Match using extracted medicine names"""
        matches = []
        
        for name in medicine_names:
            # Find entries containing this medicine name
            name_matches = self.df[self.df['search_text'].str.contains(name.lower(), na=False)]
            
            for _, row in name_matches.iterrows():
                score = self._calculate_name_match_score(row, name, strengths)
                matches.append((row.to_dict(), score))
        
        return matches
    
    def _match_by_fuzzy(self, ocr_text: str) -> List[Tuple[Dict, float]]:
        """Match using fuzzy string similarity with OCR text"""
        matches = []
        
        # Use first 100 characters for fuzzy matching
        search_text = ocr_text[:100].lower()
        
        if len(search_text) > 10:
            fuzzy_results = process.extract(
                search_text, 
                self.df['search_text'].tolist(), 
                scorer=fuzz.partial_ratio, 
                limit=10
            )
            
            for matched_text, score in fuzzy_results:
                if score > 50:  # Reasonable threshold
                    row = self.df[self.df['search_text'] == matched_text].iloc[0]
                    matches.append((row.to_dict(), score))
        
        return matches
    
    def _calculate_name_match_score(self, row: Dict, medicine_name: str, strengths: List[str]) -> float:
        """Calculate match score based on name and strength"""
        score = 0
        description = row['search_text']
        
        # Name matching (most important)
        if medicine_name.lower() in description:
            score += 60
            
            # Bonus if name appears at the beginning
            if description.startswith(medicine_name.lower()):
                score += 20
        
        # Strength matching
        row_strength = row['extracted_strength']
        for strength in strengths:
            if strength and strength in row_strength:
                score += 30
                break
        
        return min(score, 100)
    
    def _deduplicate_matches(self, matches: List[Tuple[Dict, float]]) -> List[Tuple[Dict, float]]:
        """Remove duplicate matches based on SETID"""
        seen_setids = set()
        unique_matches = []
        
        for match, score in matches:
            setid = match['SETID']
            if setid not in seen_setids:
                seen_setids.add(setid)
                unique_matches.append((match, score))
        
        return unique_matches
