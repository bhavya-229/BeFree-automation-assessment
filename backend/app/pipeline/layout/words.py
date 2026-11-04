"""Unified Word stream model and geometric line clustering."""

from typing import List, Tuple
from pydantic import BaseModel, Field


class Word(BaseModel):
    """Normalized word model across native extraction and OCR."""

    page_number: int
    text: str
    x0: float = Field(..., description="Left coordinate normalized to [0, 1]")
    y0: float = Field(..., description="Top coordinate normalized to [0, 1]")
    x1: float = Field(..., description="Right coordinate normalized to [0, 1]")
    y1: float = Field(..., description="Bottom coordinate normalized to [0, 1]")
    confidence: float = Field(default=100.0, description="Confidence score [0, 100]")
    source: str = Field(default="native", description="'native' or 'ocr'")

    @property
    def x_center(self) -> float:
        return (self.x0 + self.x1) / 2.0

    @property
    def y_center(self) -> float:
        return (self.y0 + self.y1) / 2.0

    @property
    def height(self) -> float:
        return max(0.001, self.y1 - self.y0)


class TextLine(BaseModel):
    """Clustered horizontal line of words."""

    page_number: int
    words: List[Word]
    text: str
    y0: float
    y1: float
    x0: float
    x1: float

    @property
    def x_center(self) -> float:
        return (self.x0 + self.x1) / 2.0

    @property
    def y_center(self) -> float:
        return (self.y0 + self.y1) / 2.0


def cluster_words_into_lines(words: List[Word], tolerance_ratio: float = 0.5) -> List[TextLine]:
    """Cluster words into horizontal lines by y-center proximity."""
    if not words:
        return []

    # Sort words primarily by page then top-to-bottom y0
    sorted_words = sorted(words, key=lambda w: (w.page_number, w.y0, w.x0))

    lines: List[List[Word]] = []
    current_line: List[Word] = []

    for word in sorted_words:
        if not current_line:
            current_line.append(word)
            continue

        # Check if word is on same page and vertically close to current line
        first_word = current_line[0]
        if word.page_number != first_word.page_number:
            lines.append(sorted(current_line, key=lambda w: w.x0))
            current_line = [word]
            continue

        # Median height threshold
        avg_height = sum(w.height for w in current_line) / len(current_line)
        y_tolerance = avg_height * tolerance_ratio

        line_y_center = sum(w.y_center for w in current_line) / len(current_line)
        if abs(word.y_center - line_y_center) <= y_tolerance:
            current_line.append(word)
        else:
            lines.append(sorted(current_line, key=lambda w: w.x0))
            current_line = [word]

    if current_line:
        lines.append(sorted(current_line, key=lambda w: w.x0))

    result: List[TextLine] = []
    for line_words in lines:
        if not line_words:
            continue
        line_text = " ".join(w.text for w in line_words)
        result.append(
            TextLine(
                page_number=line_words[0].page_number,
                words=line_words,
                text=line_text,
                y0=min(w.y0 for w in line_words),
                y1=max(w.y1 for w in line_words),
                x0=min(w.x0 for w in line_words),
                x1=max(w.x1 for w in line_words),
            )
        )

    # Return lines sorted by page and y0
    return sorted(result, key=lambda l: (l.page_number, l.y0))
