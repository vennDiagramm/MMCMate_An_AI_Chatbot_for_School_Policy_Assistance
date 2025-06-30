from langdetect import detect, DetectorFactory
import re
import nltk
from nltk.corpus import words
from fuzzywuzzy import fuzz

# For Streamlit kasi di nya ma detect
nltk.download('words')

class InputChecker:
    def __init__(self):
        self.valid_words = set(words.words())  # Load valid words once
        DetectorFactory.seed = 0  # For consistent language detection

    # Check if the word is similar to any real word [fuzzy ratio] - So the input can be a typo
    def is_similar_to_valid_word(self, word, threshold=80):
        for valid_word in self.valid_words:
            if fuzz.ratio(word, valid_word) >= threshold: 
                return True
        return False

    # Check if the input is nonsensical
    def is_nonsensical_input(self, user_input):
        input_words = user_input.lower().split() 
        print(f"[DEBUG] Input words: {input_words}")
        if len(input_words) <= 2:
            print("[DEBUG] Passed: Too short for nonsense detection")
            return False # Skips gibberish detection for short inputs (1-2 words) - more flexibility

        # 1. Regex check: single word of lowercase letters > 7 characters (e.g., "asdkjflasj")
        if ' ' not in user_input and re.match(r'^[a-z]+$', user_input) and len(user_input) > 7:
            print(f"[DEBUG] Rejected: Found gibberish sequence in '{word}'")
            return True

        # 2. Regex check: long sequences of vowels or consonants (e.g., "aeiou" or "bcdfgh")
        for word in input_words:
            if re.search(r'(?i)([bcdfghjklmnpqrstvwxyz]{5,}|[aeiou]{5,})', word):
                print(f"[DEBUG] Rejected: Found gibberish sequence in '{word}'")
                return True

        # 3. Fuzzy dictionary check: allow up to 40% of words to be invalid (e.g., typos)
        invalid_words = 0
        for word in input_words:
            if word in self.valid_words or word in {"mmcm", "mcm"}:
                print(f"[DEBUG] Valid word: {word}")
                continue
            if not self.is_similar_to_valid_word(word):
                print(f"[DEBUG] Invalid word: {word}")
                invalid_words += 1

        invalid_ratio = invalid_words / len(input_words)
        print(f"[DEBUG] Invalid ratio: {invalid_ratio:.2f}")
        if invalid_ratio > 0.6:
            print("[DEBUG] Rejected: Too many invalid words")
            return True
        
        # 4. Language detection
        lang = detect(user_input)
        print(f"[DEBUG] Detected language: {lang}")

        # If all checks passed, input is not nonsensical
        print("[DEBUG] Passed all nonsense checks")
        return False

    # Check if math expression
    def is_mathematical_expression(self, user_input):
        # Check for a math expression like "2 + 3 * (4 - 1)"
        return re.match(r'^[\d\s\+\-\*\/\%\(\)]+$', user_input.strip()) is not None

    # Check for SQL injection attempts
    def is_sql_injection_attempt(self, user_input):
        # Normalize input
        lowered = user_input.lower()

        # Common SQL injection patterns
        sql_keywords = [
            "select", "insert", "update", "delete", "drop", "alter", "exec", "union", 
            "create", "truncate", "--", ";", "/*", "*/", "@@", "char(", "nchar(", 
            "varchar(", "cast(", "convert(", "information_schema", "xp_"
        ]

        pattern = r"|".join(re.escape(keyword) for keyword in sql_keywords)
        if re.search(pattern, lowered):
            return True

        # Generic suspicious characters
        if re.search(r"(;|'|\-\-|\bOR\b|\bAND\b).*(=|LIKE)", lowered):
            return True

        return False

    # Remove punctuation from the input text and contains keywords section
    def remove_punctuation(self, text):
        return re.sub(r'[^\w\s]', '', text)

    def contains_keywords(self, user_input, keywords):
        cleaned_input = self.remove_punctuation(user_input.lower())
        return any(keyword in cleaned_input for keyword in keywords)