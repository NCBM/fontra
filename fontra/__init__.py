"""
some small work with fonts.
"""

import os
from pathlib import Path

from .fontdb import FONTDIRS_CUSTOM as FONTDIRS_CUSTOM
from .fontdb import FONTDIRS_SYSTEM as FONTDIRS_SYSTEM
from .fontdb import all_fonts as all_fonts
from .fontdb import get_fontdirs as get_fontdirs
from .fontdb import get_localized_names as get_localized_names
from .fontdb import get_unlocalized_name as get_unlocalized_name
from .fontdb import indexed_fontrefs as _indexed_fontrefs
from .fontdb import update_custom_fontfiles_index as update_custom_fontfiles_index
from .fontdb import update_fontrefs_index as update_fontrefs_index
from .fontdb import update_system_fontdirs as update_system_fontdirs
from .fontdb import update_system_fontfiles_index as update_system_fontfiles_index
from .fzmatch import match_font_name as match_font_name
from .fzmatch import match_font_names as match_font_names
from .fzmatch import match_font_style as match_font_style
from .fzmatch import match_font_styles as match_font_styles
from .typing import FontFamilyName, StyleName
from .typing import FontRef as FontRef


def init_fontdb(*custom_dirs: Path):
    update_system_fontdirs()
    update_system_fontfiles_index()
    if custom_dirs:
        FONTDIRS_CUSTOM.extend(custom_dirs)
        update_custom_fontfiles_index()
    update_fontrefs_index()


def get_font(name: FontFamilyName, style: str, localized: bool = True, fuzzy: bool = False) -> FontRef:
    """Get info for loading correct font faces.
    
    Params:
    - name: font family name.
    - style: font style.
    - localized: whether to lookup localized index.
    - fuzzy: whether to fuzzy match.

    Return: a named tuple includes file path and collection index.
    """
    name = get_unlocalized_name(name) if localized else name
    if name not in _indexed_fontrefs:
        match = match_font_name(name)
        if fuzzy and match:
            name = match
        else:
            raise KeyError(
                f"Font {name!r} not found."
                + (f" Did you mean {match!r} ?" if match else "")
            )
    if style not in (_fonts := _indexed_fontrefs[name]):
        match = match_font_style(name, style)
        if fuzzy and match:
            style = match
        else:
            raise KeyError(
                f"Font style {style!r} of font {name!r} not found."
                + (f" Did you mean {match!r} ?" if match else "")
            )
    return _fonts[style]


def get_font_styles(name: FontFamilyName, localized: bool = True, fuzzy: bool = False) -> list[StyleName]:
    """Get available font styles.
    
    Params:
    - name: font family name.
    - localized: whether to lookup localized index.
    - fuzzy: whether to fuzzy match.

    Return: a list includes style names.
    """
    name = get_unlocalized_name(name) if localized else name
    if name not in _indexed_fontrefs:
        match = match_font_name(name)
        if fuzzy and match:
            return [st for st in _indexed_fontrefs[match]]
        raise KeyError(
            f"Font {name!r} not found."
            + (f" Did you mean {match!r} ?" if match else "")
        )
    return [st for st in _indexed_fontrefs[name]]


def has_font_family(name: FontFamilyName, localized: bool = True) -> bool:
    name = get_unlocalized_name(name) if localized else name
    return name in _indexed_fontrefs


def has_font_style(name: FontFamilyName, style: str, localized: bool = True) -> bool:
    name = get_unlocalized_name(name) if localized else name
    return name in _indexed_fontrefs and style in _indexed_fontrefs[name]


if os.environ.get("PYFONTRA_INIT_FONTDB", "0") == "1":
    init_fontdb(
        *(
            Path(x) for x in
            os.environ.get("PYFONTRA_CUSTOM_FONTDIRS", "").split(os.pathsep) if x
        )
    )