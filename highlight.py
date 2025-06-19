import re
import html
from rapidfuzz import fuzz
from phrases.phrase_categories import phrase_categories

def normalize(text):
    """
    Lowercase, normalize spaces, and convert curly quotes to straight.
    """
    text = text.lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r'\s+', ' ', text)
    return text

def highlight_phrases_by_category(text, fuzzy_threshold=80):
    """
    Highlights phrases from phrase_categories in the text using fuzzy matching.
    Returns HTML with <span> tags styled by category color.
    
    Args:
        text (str): The input transcript text.
        fuzzy_threshold (int): Fuzz ratio threshold for matching.

    Returns:
        str: HTML string with highlighted phrases.
    """
    if not text:
        return ""

    safe_text = html.escape(text)
    normalized_text = normalize(safe_text)

    # Build a list of (category, phrase, color)
    phrase_tuples = [
        (cat, phrase, data["color"])
        for cat, data in phrase_categories.items()
        for phrase in data["phrases"]
    ]

    # Sort by phrase length descending for best matching
    phrase_tuples.sort(key=lambda x: len(x[1]), reverse=True)

    highlighted = [False] * len(safe_text)
    spans = []

    tokens = normalized_text.split()
    N = len(tokens)

    for cat, phrase, color in phrase_tuples:
        phrase_norm = normalize(phrase)
        phrase_words = phrase_norm.split()
        n_words = len(phrase_words)
        # Try windows of size n_words-1, n_words, n_words+1 for fuzzier matching
        for window_size in range(max(1, n_words-1), n_words+2):
            for i in range(N - window_size + 1):
                window = ' '.join(tokens[i:i+window_size])
                score = fuzz.ratio(window, phrase_norm)
                if score >= fuzzy_threshold:
                    # Find original substring (approximate)
                    pattern = re.escape(' '.join(tokens[i:i+window_size]))
                    m = re.search(pattern, normalized_text)
                    if m:
                        start, end = m.start(), m.end()
                        # Only highlight if not already highlighted (avoid overlap)
                        if not any(highlighted[start:end]):
                            spans.append((start, end, color))
                            for j in range(start, end):
                                highlighted[j] = True

    # Sort spans and build output HTML
    spans.sort()
    result = []
    last_idx = 0
    for start, end, color in spans:
        if last_idx < start:
            result.append(safe_text[last_idx:start])
        result.append(f'<span style="background-color: {color}; font-weight: bold;">{safe_text[start:end]}</span>')
        last_idx = end
    result.append(safe_text[last_idx:])

    return ''.join(result)
