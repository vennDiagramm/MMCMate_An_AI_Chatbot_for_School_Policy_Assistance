from langdetect import detect, DetectorFactory
import re
import nltk
from nltk.corpus import words

# For Streamlit kasi di nya ma detect
nltk.download('words')

class InputChecker:
    def __init__(self):
        self.valid_words = set(words.words())  # Load valid words once
        DetectorFactory.seed = 0  # For consistent language detection

    def is_nonsensical_input(self, user_input):
        # Check for gibberish-like strings (e.g., "asdkfjlkas")
        if re.match(r'^[a-z]+$', user_input) and len(user_input) > 5:
            return True

        # Check for long sequences of vowels or consonants
        if re.search(r'(?i)([bcdfghjklmnpqrstvwxyz]{4,}|[aeiou]{4,})', user_input):
            return True

        # Check if all words are not in the dictionary
        input_words = user_input.lower().split()
        if all(word not in self.valid_words for word in input_words):
            return True

        # Check if the detected language is not English
        try:
            lang = detect(user_input)
            if lang != 'en':
                return True
        except:
            pass  # Ignore detection failures

        return False

    def is_mathematical_expression(self, user_input):
        # Check for a math expression like "2 + 3 * (4 - 1)"
        return re.match(r'^[\d\s\+\-\*\/\%\(\)]+$', user_input.strip()) is not None

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

    def remove_punctuation(self, text):
        return re.sub(r'[^\w\s]', '', text)

    def contains_keywords(self, user_input, keywords):
        cleaned_input = self.remove_punctuation(user_input.lower())
        user_words = set(cleaned_input.split())
        return bool(user_words.intersection(keywords))