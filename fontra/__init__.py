"""
Font indexing and querying support like fontconfig.
"""

import os
from pathlib import Path

from .fontdb import FONTDIRS_CUSTOM as FONTDIRS_CUSTOM
from .fontdb import FONTDIRS_SYSTEM as FONTDIRS_SYSTEM
from .fontdb import all_fonts as all_fonts
from .fontdb import get_fontdirs as get_fontdirs
from .fontdb import get_localized_names as get_localized_names
from .fontdb import get_unlocalized_name as get_unlocalized_name
from .fontdb import indexed_classical_fontrefs as _indexed_classical_fontrefs
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

# init_by_environ: bool = False


def init_fontdb(*custom_dirs: Path, accept_envvars: bool = True):
    update_system_fontdirs()
    update_system_fontfiles_index()
    if custom_dirs:
        FONTDIRS_CUSTOM.extend(custom_dirs)
    if accept_envvars:
        FONTDIRS_CUSTOM.extend(
            Path(x).expanduser().resolve() for x in
            os.environ.get("PYFONTRA_CUSTOM_FONTDIRS", "").split(os.pathsep) if x
        )
    update_custom_fontfiles_index()
    update_fontrefs_index()


def get_font(name: FontFamilyName, style: str, localized: bool = True, fuzzy: bool = False, classical: bool = False) -> FontRef:
    """Get info for loading correct font faces.
    
    Params:
    - name: font family name.
    - style: font style.
    - localized: whether to lookup localized index.
    - fuzzy: whether to fuzzy match.
    - classical: whether to lookup classical index (where family names contain styles).

    Return: a named tuple includes file path and collection index.
    """
    index = _indexed_classical_fontrefs if classical else _indexed_fontrefs
    name = get_unlocalized_name(name) if localized and not classical else name
    if name not in index:
        match = match_font_name(name, classical=classical)
        if fuzzy and match:
            name = match
        else:
            raise KeyError(
                f"Font {name!r} not found."
                + (f" Did you mean {match!r} ?" if match else "")
            )
    if style not in (_fonts := index[name]):
        match = match_font_style(name, style, classical=classical)
        if fuzzy and match:
            style = match
        else:
            raise KeyError(
                f"Font style {style!r} of font {name!r} not found."
                + (f" Did you mean {match!r} ?" if match else "")
            )
    return _fonts[style]


def get_font_styles(name: FontFamilyName, localized: bool = True, fuzzy: bool = False, classical: bool = False) -> list[StyleName]:
    """Get available font styles.
    
    Params:
    - name: font family name.
    - localized: whether to lookup localized index.
    - fuzzy: whether to fuzzy match.
    - classical: whether to lookup classical index (where family names contain styles).

    Return: a list includes style names.
    """
    index = _indexed_classical_fontrefs if classical else _indexed_fontrefs
    name = get_unlocalized_name(name) if localized and not classical else name
    if name not in index:
        match = match_font_name(name, classical=classical)
        if fuzzy and match:
            return [st for st in index[match]]
        raise KeyError(
            f"Font {name!r} not found."
            + (f" Did you mean {match!r} ?" if match else "")
        )
    return [st for st in index[name]]


def has_font_family(name: FontFamilyName, localized: bool = True, classical: bool = False) -> bool:
    """Check whether the specified font family name exists.
    
    Params:
    - name: font family name.
    - localized: whether to lookup localized index.
    - classical: whether to lookup classical index (where family names contain styles).

    Return: whether the specified font family name exists.
    """
    if classical:
        return name in _indexed_classical_fontrefs
    name = get_unlocalized_name(name) if localized else name
    return name in _indexed_fontrefs


def has_font_style(name: FontFamilyName, style: str, localized: bool = True, classical: bool = False) -> bool:
    """Check whether the specified font style exists.
    
    Params:
    - name: font family name.
    - style: font style.
    - localized: whether to lookup localized index.
    - classical: whether to lookup classical index (where family names contain styles).

    Return: whether the specified font style exists.
    """
    if classical:
        return name in _indexed_classical_fontrefs
    name = get_unlocalized_name(name) if localized else name
    return name in _indexed_fontrefs and style in _indexed_fontrefs[name]


# if os.environ.get("PYFONTRA_INIT_FONTDB", "0") == "1":
#     init_fontdb()
#     init_by_environ = True