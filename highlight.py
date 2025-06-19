import re
import html
from rapidfuzz import fuzz
from phrases.phrase_categories import phrase_categories  # Import the external phrase categories

def normalize(text):
    """Lowercase, normalize spaces, convert curly quotes to straight."""
    text = text.lower()
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r'\s+', ' ', text)
    return text

def highlight_phrases_by_category(text, fuzzy_threshold=80):
    """
    Highlights phrases from phrase_categories in the text using fuzzy matching.
    Returns HTML with <span> tags styled by category color.
    """
    safe_text = html.escape(text)
    normalized_text = normalize(safe_text)

    phrase_tuples = []
    for cat, data in phrase_categories.items():
        color = data["color"]
        for phrase in data["phrases"]:
            phrase_tuples.append((cat, phrase, color))

    # Sort by phrase length descending for better matching
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
                        if not any(highlighted[start:end]):
                            spans.append((start, end, color))
                            for j in range(start, end):
                                highlighted[j] = True

    # Sort spans and build output
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
