from pathlib import Path

from typing_extensions import NamedTuple, TypeAlias

FontFamilyName: TypeAlias = str
StyleName: TypeAlias = str


class FontRef(NamedTuple):
    """Data for locating font style."""
    path: Path
    bank: int