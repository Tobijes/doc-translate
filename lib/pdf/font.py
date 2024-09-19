from typing import Any, Callable, List
from lib.pdf.models import TextBlock, Line, Span

def get_font(flags):
    italic = flags & 2**1
    serif = flags & 2**2
    bold = flags & 2**4

    if serif:
        if bold and italic:
            return "times-bolditalic"
        if bold:
            return "times-bold"
        if italic:
            return "times-italic"
        return "times-roman"
    else: 
        if bold and italic:
            return "helvetica-boldoblique"
        if bold:
            return "helvetica-bold"
        if italic:
            return "helvetica-oblique"
        return "helvetica"
    
def block_most_frequent_span_property(block: TextBlock, access_func: Callable):
    spans = block.get_spans()
    items = list(map(access_func, spans))
    most_freq = max(set(items), key=items.count) # Most frequenct
    return most_freq