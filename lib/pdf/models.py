from typing import Any, Dict, List, NamedTuple, Optional, Union, Literal, Union

from pydantic import BaseModel, Field

class Bbox(NamedTuple):
    x0: float
    y0: float
    x1: float
    y1: float

class Span(BaseModel):
    size: float
    flags: int
    font: str
    color: int
    ascender: float
    descender: float
    text: str
    origin: List[float]
    bbox: Bbox

class Line(BaseModel):
    spans: List[Span]
    wmode: int
    dir: List[float]
    bbox: Bbox

class ImageBlock(BaseModel):
    type: Literal[1]
    number: int
    xres: int

class TextBlock(BaseModel):
    type: Literal[0]
    number: int
    bbox: Bbox
    lines: List[Line]
    text: Optional[str] = None

    def get_spans(self):
        return [span for line in self.lines for span in line.spans]

class Page(BaseModel):
    width: float
    height: float
    blocks: List[Union[TextBlock, ImageBlock]] = Field(default_factory=list)

def model_validate(data: Dict[str, Any]) -> Page:
    return Page(blocks=data.get("blocks", []))
