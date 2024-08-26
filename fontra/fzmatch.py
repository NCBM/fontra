from difflib import get_close_matches
from typing import Optional

from .fontdb import indexed_fontrefs as _indexed_fontrefs


def match_font_name(font_name: str, *, cutoff: float = 0.6) -> Optional[str]:
    """Get the best match by the given font name.
    
    Params:
    - font_name: font name to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.

    Return: a font family name if matched, otherwise None.
    """
    match = get_close_matches(font_name, _indexed_fontrefs.keys(), 1, cutoff)
    return match[0] if match else None


def match_font_names(font_name: str, *, cutoff: float = 0.6) -> list[str]:
    """Get the matchs by the given font name, sorted by possibilities.
    
    Params:
    - font_name: font name to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.

    Return: a list of font family names, sorted by possibilities.
    """
    match = get_close_matches(
        font_name, _indexed_fontrefs.keys(), len(_indexed_fontrefs.keys()), cutoff
    )
    return match


def match_font_style(font_name: str, font_style: str, *, cutoff: float = 0.6) -> Optional[str]:
    """Get the best match by the given font style.
    
    Params:
    - font_name: font family name.
    - font_style: font style to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.

    Return: a font style if matched, otherwise None.
    """
    if font_name not in _indexed_fontrefs:
        raise KeyError(
            f"Font {font_name!r} not found. Please use `match_font_name({font_name!r})` first."
        )
    match = get_close_matches(
        font_style, _indexed_fontrefs[font_name].keys(), 1, cutoff
    )
    return match[0] if match else None


def match_font_styles(font_name: str, font_style: str, *, cutoff: float = 0.6) -> list[str]:
    """Get the matchs by the given font style, sorted by possibilities.
    
    Params:
    - font_name: font family name.
    - font_style: font style to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.

    Return: a list of font styles, sorted by possibilities.
    """
    if font_name not in _indexed_fontrefs:
        raise KeyError(
            f"Font {font_name!r} not found. Please use `match_font_name({font_name!r})` first."
        )
    match = get_close_matches(
        font_style, _indexed_fontrefs[font_name].keys(),
        len(_indexed_fontrefs[font_name].keys()), cutoff
    )
    return match