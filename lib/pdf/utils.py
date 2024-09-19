from typing import Iterable, List
from random import uniform
import fitz

from .models import Page, TextBlock, ImageBlock
from .font import get_font, block_most_frequent_span_property

def view_doc(pages: List[Page], page_label=True, block_label=True, line_label=True, span_label=True):
    for page in pages:
        if page_label:
            print("PAGE")
        for block in page.blocks:
            if isinstance(block, TextBlock):
                if block_label:
                    print("\tBlock")
                if block.text is not None:
                    print(block.text)
                for line in block.lines:
                    if line_label:
                        print("\t\tLine")
                    for span in line.spans:
                        if span_label:
                            print("\t\t\tSpan:", repr(span.text))
                        else:
                            print(repr(span.text))
            elif isinstance(block, ImageBlock):
                print("\tImage")

def subset(input_pdf, output_pdf, page_nums):
    input_doc = fitz.open(input_pdf) 
    doc = fitz.open()

    for page_num in page_nums:

        if page_num < 0:
            continue

        if page_num >= len(input_doc):
            continue
     
        doc.insert_pdf(input_doc, from_page=page_num, to_page=page_num)

    doc.save(output_pdf)

def do_bounding_boxes(doc: fitz.Document, pages: List[Page]) -> fitz.Document:
    # Do annotation
    for i, docpage in enumerate(doc):
        page = pages[i]
        for block in page.blocks:
            block_color = (uniform(0.2, 0.8), uniform(0.2, 0.8), uniform(0.2, 0.8))
            block_line_offset = 0.05
            block_line_color = (block_color[0] + block_line_offset,block_color[1] + block_line_offset,block_color[1] + block_line_offset)
            
            docpage.add_redact_annot(quad=block.bbox, fill=block_color)

            for line in block.lines:
                for span in line.spans:
                    pass
                    docpage.add_redact_annot(
                        quad=span.bbox, 
                        text=span.text, 
                        fontname=get_font(span.flags), 
                        fontsize=span.size, 
                        text_color=fitz.sRGB_to_pdf(span.color), 
                        fill=block_line_color
                    )
        # Apply redactions
        docpage.apply_redactions()


def do_translation_redaction(doc: fitz.Document, pages: List[Page]) -> fitz.Document:
    # Do annotation
    for i, docpage in enumerate(doc):
        page = pages[i]
        for block in page.blocks:
            if block.text is None:
                continue
            docpage.add_redact_annot(
                text=block.text,
                quad=block.bbox, 
                fill=(0.9, 0.9, 0.9),
                fontname=get_font(block_most_frequent_span_property(block, lambda span: span.flags)), 
                fontsize= block_most_frequent_span_property(block, lambda span: span.size), 
                text_color=fitz.sRGB_to_pdf(block_most_frequent_span_property(block, lambda span: span.color)), 
            )

        # Apply redactions
        docpage.apply_redactions()
