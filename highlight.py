# highlight.py
import re

def highlight_greenwashing_strategies(text, sensitivity=2, detect_collective=True, 
                                    detect_individual=True, detect_metaphors=True, 
                                    detect_buzzwords=True):
    """
    Highlight greenwashing strategies in text based on thematic analysis patterns.
    
    Args:
        text: Input text to analyze
        sensitivity: 1=strict, 2=moderate, 3=broad
        detect_*: Boolean flags for each strategy type
    
    Returns:
        tuple: (highlighted_text, statistics_dict)
    """
    
    # Define patterns based on sensitivity level
    patterns = {
        'collective': get_collective_patterns(sensitivity),
        'individual': get_individual_patterns(sensitivity),
        'metaphors': get_metaphor_patterns(sensitivity),
        'buzzwords': get_buzzword_patterns(sensitivity)
    }
    
    # Initialize statistics
    stats = {
        'collective': 0,
        'individual': 0,
        'metaphors': 0,
        'buzzwords': 0
    }
    
    highlighted_text = text
    
    # Apply highlighting for each strategy if enabled
    if detect_collective:
        highlighted_text, stats['collective'] = apply_highlighting(
            highlighted_text, patterns['collective'], 'collective-we'
        )
    
    if detect_individual:
        highlighted_text, stats['individual'] = apply_highlighting(
            highlighted_text, patterns['individual'], 'individualising'
        )
    
    if detect_metaphors:
        highlighted_text, stats['metaphors'] = apply_highlighting(
            highlighted_text, patterns['metaphors'], 'moral-metaphors'
        )
    
    if detect_buzzwords:
        highlighted_text, stats['buzzwords'] = apply_highlighting(
            highlighted_text, patterns['buzzwords'], 'green-buzzwords'
        )
    
    return highlighted_text, stats

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
