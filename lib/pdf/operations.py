from typing import List

from .models import Line, Page, TextBlock, Bbox
from .filters import text_block_filter, direction_line_filter, span_superscript_filter, span_numeric_filter, span_whitespace_filter



def block_text_only(page: Page) -> Page:
    page.blocks = list(filter(text_block_filter, page.blocks))
    return page

def line_remove_unsupported_direction(page: Page) -> Page:
    for block in page.blocks:
        block.lines = list(filter(direction_line_filter, block.lines))
    return page

def span_remove_superscript(page: Page) -> Page:
    for block in page.blocks:
        for line in block.lines:
            line.spans = list(filter(span_superscript_filter, line.spans))
    return page

def span_remove_numerics(page: Page) -> Page:
    for block in page.blocks:
        for line in block.lines:
            line.spans = list(filter(span_numeric_filter, line.spans))
    return page

def remove_empty_blocks(page: Page) -> Page:
    for block in page.blocks:
        for line in block.lines:
            line.spans = list(filter(span_whitespace_filter, line.spans))
        # After spans were filtered, check for empty lines
        block.lines = list(filter(lambda line: len(line.spans) > 0, block.lines))
    # After lines were filtered, check for empty blocks
    page.blocks = list(filter(lambda block: len(block.lines) > 0, page.blocks))

    # Recompute bounding boxes
    for block in page.blocks:
        block.bbox = compute_bbox(block)

    return page

def join_texts_latin(a: str, b: str):
    a = a.rstrip()
    b = b.lstrip()
    # print("A:", a, "B:", b)
    if len(a) > 0 and a[-1] == "-":
        return a[:-1] + b
    return a + " " + b

def hydrate_block_texts(page: Page) -> Page:
    for block in page.blocks:
        block.text = ""
        for line in block.lines:
            for span in line.spans:
                block.text = join_texts_latin(block.text, span.text)
    return page


def find_regions(bool_list):
    regions = []
    start = None
    
    for i, value in enumerate(bool_list):
        if value == False:
            if start is None:
                start = i  # Start of a False region
        else:
            if start is not None:
                regions.append((start, i - 1))  # End of the False region
                start = None
    
    if start is not None:
        regions.append((start, len(bool_list) - 1))  # End of the last False region
    
    return regions

def compute_bbox(block: TextBlock) -> Bbox:
    spans = block.get_spans()
    min_x0 = min(map(lambda span: span.bbox.x0, spans))
    min_y0 = min(map(lambda span: span.bbox.y0, spans))
    max_x1 = max(map(lambda span: span.bbox.x1, spans))
    max_y1 = max(map(lambda span: span.bbox.y1, spans))
    return Bbox(min_x0, min_y0, max_x1, max_y1)

def split_blocks(page: Page) -> Page:
    resulting_blocks: List[TextBlock] = []

    for block in page.blocks:
        # If less than 3 lines, a split does not make sense
        if len(block.lines) < 3:
            resulting_blocks.append(block)
            continue
        
        # Create a list of True per line if all spans in line is whitespace else False
        splittables = list(map(lambda line: all(map(lambda span: len(span.text) == 0 or span.text.isspace(), line.spans)), block.lines))

        # If nowhere to split, reuse block
        if not any(splittables):
            resulting_blocks.append(block)
            continue
    
        # If everything is empty/splittable discard block
        if all(splittables):
            continue
        
        # Find clusters/regions of False (non-whitespace). Example
        ## List: [False, False, True, True, False, True, False]
        ## Result: [(0, 1), (4, 4), (6, 6)]
        split_regions = find_regions(splittables)

        # Using the regions, index into lines and add subblocks
        for (start, end) in split_regions:
            lines = block.lines[start:end+1]
            new_block = TextBlock(type=0, number=len(lines), bbox=Bbox(0,0,0,0), lines=lines)
            new_block.bbox = compute_bbox(new_block)
            resulting_blocks.append(new_block)

    page.blocks = resulting_blocks
    return page

# Reduction algorithm
## Remove ImageBlocks
## Remove lines with unsupported direction
## Remove spans with superscript
## Remove spans with numeric only
## Split blocks with Line/Span Line/Empty Line/Span
def reduce_page(page: Page) -> Page:
    page = block_text_only(page)
    page = line_remove_unsupported_direction(page)
    page = span_remove_superscript(page)
    page = span_remove_numerics(page)
    page = split_blocks(page)
    page = remove_empty_blocks(page)
    page = hydrate_block_texts(page)
    return page
