from difflib import get_close_matches
from typing import Optional

from .fontdb import indexed_classical_fontrefs as _indexed_classical_fontrefs
from .fontdb import indexed_fontrefs as _indexed_fontrefs


def match_font_name(font_name: str, *, cutoff: float = 0.6, classical: bool = False) -> Optional[str]:
    """Get the best match by the given font name.
    
    Params:
    - font_name: font name to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.
    - classical: whether to lookup classical index (where family names may contain styles).

    Return: a font family name if matched, otherwise None.
    """
    match = get_close_matches(
        font_name,
        _indexed_classical_fontrefs if classical else _indexed_fontrefs,
        1,
        cutoff
    )
    return match[0] if match else None


def match_font_names(font_name: str, *, cutoff: float = 0.6, classical: bool = False) -> list[str]:
    """Get the matchs by the given font name, sorted by possibilities.
    
    Params:
    - font_name: font name to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.
    - classical: whether to lookup classical index (where family names may contain styles).

    Return: a list of font family names, sorted by possibilities.
    """
    match = get_close_matches(
        font_name,
        _indexed_classical_fontrefs if classical else _indexed_fontrefs,
        len(_indexed_fontrefs.keys()),
        cutoff
    )
    return match


def match_font_style(font_name: str, font_style: str, *, cutoff: float = 0.6, classical: bool = False) -> Optional[str]:
    """Get the best match by the given font style.
    
    Params:
    - font_name: font family name.
    - font_style: font style to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.
    - classical: whether to lookup classical index (where family names may contain styles).

    Return: a font style if matched, otherwise None.
    """
    if font_name not in _indexed_fontrefs:
        raise KeyError(
            f"Font {font_name!r} not found. Please use `match_font_name({font_name!r})` first."
        )
    match = get_close_matches(
        font_style,
        _indexed_classical_fontrefs[font_name] if classical else _indexed_fontrefs[font_name],
        1,
        cutoff
    )
    return match[0] if match else None


def match_font_styles(font_name: str, font_style: str, *, cutoff: float = 0.6, classical: bool = False) -> list[str]:
    """Get the matchs by the given font style, sorted by possibilities.
    
    Params:
    - font_name: font family name.
    - font_style: font style to match.
    - cutoff: least match possibilities, will be passed into `difflib.get_close_matches(...)`.
    - classical: whether to lookup classical index (where family names may contain styles).

    Return: a list of font styles, sorted by possibilities.
    """
    if font_name not in _indexed_fontrefs:
        raise KeyError(
            f"Font {font_name!r} not found. Please use `match_font_name({font_name!r})` first."
        )
    styles = _indexed_classical_fontrefs[font_name] if classical else _indexed_fontrefs[font_name]
    match = get_close_matches(font_style, styles, len(styles), cutoff)
    return match