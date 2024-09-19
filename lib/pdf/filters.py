from typing import Any, Union
import re

from .models import TextBlock, ImageBlock, Line, Span
VERBOSE = False

def log_reason(reason: str, obj: Any, verbose):
    if verbose:
        print(f"Filtered ({reason})", repr(obj), flush=True)

def text_block_filter(block: Union[TextBlock, ImageBlock], verbose=VERBOSE) -> bool:
    if not isinstance(block, TextBlock):
        log_reason("non-textblock", block, verbose)
        return False
    
    return True
    
def direction_line_filter(line: Line, verbose=VERBOSE) -> bool:
    if line.wmode != 0:
        log_reason("wmode", line, verbose)
        return False
    
    if line.dir != [1.0, 0.0]:
        log_reason("direction", line, verbose)
        return False
    
    return True

def span_superscript_filter(span: Span, verbose=VERBOSE) -> bool:
    if span.flags & 2**0: 
        log_reason("superscript", span, verbose)
        return False
        
    return True

pattern_is_number = re.compile(r"^\s*\d+(?:[\,\.]\d+)*\s*$")
def span_numeric_filter(span: Span, verbose=VERBOSE) -> bool:
    if re.match(pattern_is_number, span.text):
        log_reason("numeric", span, verbose)
        return False
        
    return True

def span_whitespace_filter(span: Span, verbose=VERBOSE) -> bool:
    if len(span.text) == 0: 
        log_reason("length", span, verbose)
        return False
    
    if span.text.isspace(): 
        log_reason("whitespace", span, verbose)
        return False
        
    return True