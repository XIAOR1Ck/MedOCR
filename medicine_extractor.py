import re
from typing import Any, Dict, List


class MedicineExtractor:
    def __init__(self):
        # Common medicine name patterns
        self.medicine_suffixes = [
            "azole",
            "cycline",
            "amine",
            "pril",
            "sartan",
            "olol",
            "pam",
            "lam",
            "caine",
            "mycin",
            "oxacin",
            "tidine",
            "amine",
            "dine",
            "pine",
            "barb",
            "vir",
            "stat",
            "mab",
            "tinib",
            "formin",
            "glitazone",
        ]

        # Strength patterns
        self.strength_patterns = [
            r"(\d+\.?\d*)\s*(MG|MCG|MG/ML|MCG/ML|%)",
            r"(\d+\.?\d*)\s*(mg|mcg|mg/ml|mcg/ml|%)",
        ]

    def extract_medicine_info(self, text: str) -> Dict[str, Any]:
        # Extract medicine name and strength from text
        text_lower = text.lower()

        return {
            "medicine_names": self._extract_medicine_names(text),
            "strengths": self._extract_strengths(text),
            "raw_text": text,
        }

    def _extract_medicine_names(self, text: str) -> List[str]:
        # Extract potential medicine names from text"""
        names = []

        # Strategy 1: Look for capitalized words that look like medicine names
        words = re.findall(r"\b[A-Z][a-z]+\b", text)
        for word in words:
            if self._looks_like_medicine_name(word):
                names.append(word)

        # Strategy 2: Look for words before strength indicators
        strength_indicators = ["mg", "mcg", "%", "ml"]
        all_words = text.lower().split()

        for i, word in enumerate(all_words):
            # Check if current word contains strength indicator
            if any(indicator in word for indicator in strength_indicators) and i > 0:
                # Previous word might be medicine name
                prev_word = all_words[i - 1]
                if len(prev_word) > 3 and prev_word[0].isupper():
                    names.append(prev_word.title())

        # Remove duplicates and return
        return list(set(names))

    def _extract_strengths(self, text: str) -> List[str]:
        # Extract strength information from text"""
        strengths = []

        for pattern in self.strength_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                strength = match.group().strip()
                # Normalize to uppercase
                strength = re.sub(
                    r"(\d+\.?\d*)\s*(mg|mcg|%)",
                    lambda m: f"{m.group(1)} {m.group(2).upper()}",
                    strength,
                    flags=re.IGNORECASE,
                )
                strengths.append(strength)

        return list(set(strengths))

    def _looks_like_medicine_name(self, word: str) -> bool:
        # Check if a word looks like a medicine name"""
        word_lower = word.lower()

        # Check length and medicine-like suffixes
        if len(word) < 4:
            return False

        # Check for common medicine suffixes
        if any(word_lower.endswith(suffix) for suffix in self.medicine_suffixes):
            return True

        # Check for common medicine patterns
        medicine_patterns = [
            r"^[A-Z][a-z]+[aeiou][a-z]*[mp]ine$",  # like amoxicillin, morphine
            r"^[A-Z][a-z]+[aeiou][a-z]*zole$",  # like pantoprazole
            r"^[A-Z][a-z]+[aeiou][a-z]*ide$",  # like lisinopril
            r"^[A-Z][a-z]+[aeiou][a-z]*mol$",  # like paracetamol
            r"^[A-Z][a-z]+[aeiou][a-z]*one$",  # like domperidone
        ]

        return any(re.match(pattern, word) for pattern in medicine_patterns)
