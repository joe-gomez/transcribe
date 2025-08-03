# highlight.py
import re

def highlight_greenwashing_strategies(
    text, sensitivity=2, detect_collective=True, 
    detect_individual=True, detect_metaphors=True, 
    detect_buzzwords=True
):
    """
    Highlight greenwashing strategies in text based on thematic analysis patterns.
    Returns (highlighted_text, statistics_dict)
    """
    # Collect patterns and classes
    pattern_classes = []

    if detect_collective:
        for pat in get_collective_patterns(sensitivity):
            pattern_classes.append((pat, 'collective-we'))
    if detect_individual:
        for pat in get_individual_patterns(sensitivity):
            pattern_classes.append((pat, 'individualising'))
    if detect_metaphors:
        for pat in get_metaphor_patterns(sensitivity):
            pattern_classes.append((pat, 'moral-metaphors'))
    if detect_buzzwords:
        for pat in get_buzzword_patterns(sensitivity):
            pattern_classes.append((pat, 'green-buzzwords'))

    # Find all non-overlapping matches
    matches = []
    for pat, css_class in pattern_classes:
        for m in re.finditer(pat, text, re.IGNORECASE):
            matches.append({'start': m.start(), 'end': m.end(), 'css': css_class, 'text': m.group(), 'pattern': pat})

    # Remove overlaps: keep earliest match, longest span
    matches.sort(key=lambda x: (x['start'], -x['end']))
    non_overlapping = []
    last_end = 0
    for m in matches:
        if m['start'] >= last_end:
            non_overlapping.append(m)
            last_end = m['end']

    # Build stats
    stats = {'collective': 0, 'individual': 0, 'metaphors': 0, 'buzzwords': 0}
    for m in non_overlapping:
        if m['css'] == 'collective-we':
            stats['collective'] += 1
        elif m['css'] == 'individualising':
            stats['individual'] += 1
        elif m['css'] == 'moral-metaphors':
            stats['metaphors'] += 1
        elif m['css'] == 'green-buzzwords':
            stats['buzzwords'] += 1

    # Rebuild text from matches (process from end to start)
    highlighted = text
    offset = 0
    for m in sorted(non_overlapping, key=lambda x: x['start']):
        start = m['start'] + offset
        end = m['end'] + offset
        tag = f'<span class="{m["css"]}">{highlighted[start:end]}</span>'
        highlighted = highlighted[:start] + tag + highlighted[end:]
        offset += len(tag) - (end - start)

    return highlighted, stats

def get_collective_patterns(sensitivity):
    """Get collective 'we' patterns based on sensitivity level."""
    base_patterns = [
        r'\bwe\s+are\b', r'\bwe\s+need\b', r'\bwe\s+must\b', r'\bwe\s+should\b',
        r'\bwe\s+can\b', r'\bwe\s+have\b', r'\blet\'s\b', r'\bour\s+\w+\b',
        r'\btogether\s+we\b', r'\ball\s+of\s+us\b'
    ]
    
    moderate_patterns = [
        r'\bwe\'re\b', r'\bwe\'ll\b', r'\bwe\'ve\b', r'\bus\s+to\b',
        r'\bour\s+responsibility\b', r'\bour\s+duty\b', r'\bour\s+mission\b',
        r'\bcollectively\b', r'\bas\s+a\s+society\b'
    ]
    
    broad_patterns = [
        r'\beveryone\s+needs\b', r'\bhumanity\s+must\b', r'\bpeople\s+should\b',
        r'\bthe\s+world\s+needs\b', r'\bwe\s+all\s+know\b',
        r'\btogether\b', r'\bunited\b', r'\bcommunity\b'
    ]
    
    if sensitivity == 1:
        return base_patterns
    elif sensitivity == 2:
        return base_patterns + moderate_patterns
    else:
        return base_patterns + moderate_patterns + broad_patterns

def get_individual_patterns(sensitivity):
    """Get individualising language patterns."""
    base_patterns = [
        r'\byou\s+should\b', r'\byou\s+must\b', r'\byou\s+can\b',
        r'\byour\s+responsibility\b', r'\bdo\s+your\s+part\b',
        r'\bit\'s\s+up\s+to\s+you\b', r'\bpersonal\s+responsibility\b'
    ]
    
    moderate_patterns = [
        r'\byour\s+choice\b', r'\byour\s+actions\b', r'\beach\s+person\b',
        r'\bindividual\s+choice\b', r'\bpersonal\s+duty\b',
        r'\bmake\s+a\s+difference\b', r'\bstart\s+with\s+yourself\b'
    ]
    
    broad_patterns = [
        r'\byou\s+have\s+the\s+power\b', r'\bevery\s+little\s+bit\s+helps\b',
        r'\bsmall\s+changes\b', r'\bpersonal\s+impact\b',
        r'\bconsumer\s+choice\b', r'\blifestyle\s+changes\b'
    ]
    
    if sensitivity == 1:
        return base_patterns
    elif sensitivity == 2:
        return base_patterns + moderate_patterns
    else:
        return base_patterns + moderate_patterns + broad_patterns

def get_metaphor_patterns(sensitivity):
    """Get moral metaphor patterns."""
    base_patterns = [
        r'\bjourney\b', r'\bmission\b', r'\bbattle\b', r'\bfight\b',
        r'\bwar\s+against\b', r'\bcrusade\b', r'\bquest\b'
    ]
    
    moderate_patterns = [
        r'\bimpending\s+doom\b', r'\bno\s+planet\s+b\b', r'\bcrisis\b',
        r'\bemergency\b', r'\bbig\s+dreams\b', r'\bhope\s+for\b',
        r'\bsave\s+the\b', r'\brescue\b', r'\bpath\s+forward\b'
    ]
    
    broad_patterns = [
        r'\bchallenge\b', r'\bstruggle\b', r'\bvision\b', r'\bdream\b',
        r'\bhope\b', r'\bfuture\s+generations\b', r'\blegacy\b',
        r'\bthreat\b', r'\bdanger\b', r'\bsurvival\b'
    ]
    
    if sensitivity == 1:
        return base_patterns
    elif sensitivity == 2:
        return base_patterns + moderate_patterns
    else:
        return base_patterns + moderate_patterns + broad_patterns

def get_buzzword_patterns(sensitivity):
    """Get green buzzword patterns."""
    base_patterns = [
        r'\bplanet\b', r'\bnature\b', r'\brecycle\b', r'\bsustainable\b',
        r'\beco-friendly\b', r'\bgreen\b', r'\benvironment\b'
    ]
    
    moderate_patterns = [
        r'\bresponsible\b', r'\brenewable\b', r'\bclean\b', r'\bnatural\b',
        r'\borganic\b', r'\bcarbon\s+footprint\b', r'\bclimate\b',
        r'\bhealthier\s+planet\b', r'\bearth\b', r'\bmother\s+nature\b'
    ]
    
    broad_patterns = [
        r'\bconservation\b', r'\bpreservation\b', r'\bbiodiversity\b',
        r'\becosystem\b', r'\bwildlife\b', r'\bpollution\b',
        r'\bemissions\b', r'\bcarbon\s+neutral\b', r'\bzero\s+waste\b',
        r'\bplant-based\b', r'\beco\b', r'\bgreen\s+energy\b'
    ]
    
    if sensitivity == 1:
        return base_patterns
    elif sensitivity == 2:
        return base_patterns + moderate_patterns
    else:
        return base_patterns + moderate_patterns + broad_patterns

def apply_highlighting(text, patterns, css_class):
    """Apply highlighting to text based on patterns."""
    count = 0
    highlighted_text = text
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        count += len(matches)
        
        highlighted_text = re.sub(
            pattern, 
            rf'<span class="{css_class}">\g<0></span>', 
            highlighted_text, 
            flags=re.IGNORECASE
        )
    
    return highlighted_text, count

# Legacy function for backward compatibility
def highlight_individualising_language(text, phrases):
    """Legacy function - kept for backward compatibility."""
    pattern = r'(' + '|'.join(re.escape(p) for p in phrases) + r')'
    highlighted = re.sub(pattern, r'<span class="highlight">\1</span>', text, flags=re.IGNORECASE)
    return highlighted
