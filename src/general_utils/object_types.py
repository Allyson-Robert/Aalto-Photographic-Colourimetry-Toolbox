from dataclasses import dataclass
from typing import Optional

type Point = tuple[int, int]
type OptionalPoint = Optional[Point]

@dataclass
class CropPoints:
    top_left: Point
    bottom_right: Point