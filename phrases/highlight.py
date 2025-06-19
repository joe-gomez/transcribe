import re
import html
from rapidfuzz import fuzz
from phrases.phrase_categories import phrase_categories  # Import the external phrase categories

def get_flexible_pattern(phrase):
    # Allow for flexible whitespace, no end boundary
    escaped = re.escape(phrase)
    flexible = re.sub(r'\\ ', r'\\s+', escaped)
    return r'(?<!\w)' + flexible

def highlight_phrases_by_category(text, fuzzy_threshold=80):
    safe_text = html.escape(text)
    phrase_tuples = []
    for cat, data in phrase_categories.items():
        color = data["color"]
        for phrase in data["phrases"]:
            phrase_tuples.append((cat, phrase, color))

    # Sort by phrase length descending for better matching
    phrase_tuples.sort(key=lambda x: len(x[1]), reverse=True)
    highlighted = [False] * len(safe_text)
    spans = []

    # --- REGEX (exact/near-exact) MATCHING ---
    for cat, phrase, color in phrase_tuples:
        pattern = get_flexible_pattern(phrase)
        for match in re.finditer(pattern, safe_text, flags=re.IGNORECASE):
            start, end = match.start(), match.end()
            if not any(highlighted[start:end]):
                spans.append((start, end, color))
                for i in range(start, end):
                    highlighted[i] = True

    # --- FUZZY matching (optional, for inexact cases) ---
    # You can add a fuzzy window or additional logic here if desired.

    # Assemble highlighted text
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
