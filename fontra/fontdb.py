import os
import sys
import traceback
import warnings
from itertools import chain
from pathlib import Path

import freetype
import freetype.ft_errors

from .consts import SUPPORTED_EXT
from .locutil import get_font_names, get_localized_family_name, get_preferred_names
from .typing import FontFamilyName, FontRef, StyleName

FONTDIRS_SYSTEM: list[Path] = []
FONTDIRS_CUSTOM: list[Path] = []
_indexed_fontfiles_system: set[Path] = set()
_indexed_fontfiles_custom: set[Path] = set()

indexed_fontrefs: dict[FontFamilyName, dict[StyleName, FontRef]] = {}
indexed_classical_fontrefs: dict[FontFamilyName, dict[StyleName, FontRef]] = {}
indexed_langnames: dict[FontFamilyName, FontFamilyName] = {}


def update_system_fontdirs() -> None:
    """Update system font directories (in `FONTDIRS_SYSTEM`)."""
    FONTDIRS_SYSTEM.clear()
    if sys.platform == "win32":
        if localappdata := os.getenv("LOCALAPPDATA"):
            # include user-site font directory
            if (
                _localfontdir := Path(localappdata) / "Microsoft" / "Windows" / "Fonts"
            ).is_dir():
                FONTDIRS_SYSTEM.append(_localfontdir)
        if windir := os.getenv("WINDIR"):
            # include system-site font directory
            FONTDIRS_SYSTEM.append(Path(windir) / "fonts")
    elif sys.platform in ("linux", "linux2"):
        if not (xdgdata := os.getenv("XDG_DATA_DIRS")):
            # some weird platforms does not have `/usr/share`
            xdgdata = "/usr/share" if os.path.exists("/usr/share") else ""
        # thank you xdg
        FONTDIRS_SYSTEM.extend(
            Path(datadir) / "fonts"
            for datadir in xdgdata.split(":") if datadir
        )
        if (userfonts := Path("~/.fonts").expanduser()).is_dir():
            FONTDIRS_SYSTEM.append(userfonts)
        if android_root := os.getenv("ANDROID_ROOT"):
            # try include Android system font directory
            if (android_fonts := Path(android_root) / "fonts").is_dir():
                FONTDIRS_SYSTEM.append(android_fonts)
    elif sys.platform == "darwin":
        FONTDIRS_SYSTEM.extend(
            (
                Path("~/Library/Fonts").expanduser(),
                Path("/Library/Fonts"), Path("/System/Library/Fonts")
            )
        )


def get_fontdirs() -> list[Path]:
    """Get all font directories."""
    return FONTDIRS_CUSTOM + FONTDIRS_SYSTEM


def update_system_fontfiles_index() -> None:
    """Update system font files index."""
    _indexed_fontfiles_system.clear()
    for directory in FONTDIRS_SYSTEM:
        for r, _, fs in os.walk(directory):
            _indexed_fontfiles_system.update(
                {Path(r) / fn for fn in fs if fn.endswith(SUPPORTED_EXT)}
            )


def update_custom_fontfiles_index() -> None:
    """Update font files index."""
    _indexed_fontfiles_custom.clear()
    for directory in FONTDIRS_CUSTOM:
        for r, _, fs in os.walk(directory):
            _indexed_fontfiles_custom.update(
                {Path(r) / fn for fn in fs if fn.endswith(SUPPORTED_EXT)}
            )


def _update_fontref_index(fn: Path, face: freetype.Face) -> None:
    family = face.family_name.decode()
    style = face.style_name.decode()
    indexed_fontrefs.setdefault(family, {})[style] = FontRef(fn, face.face_index)
    if face.is_sfnt:
        for name, style_ in chain(get_font_names(face), get_preferred_names(face)):
            indexed_classical_fontrefs.setdefault(name, {})[style_] = indexed_fontrefs[family][style]
        _ffname = get_localized_family_name(face)
        indexed_langnames.update({fn: family for fn, *_ in _ffname if fn != family})


def _ft_open_face(fn: Path, index: int = 0) -> freetype.Face:
    if os.name == "nt":
        return freetype.Face(open(fn, "rb"), index)
    return freetype.Face(str(fn), index)


def update_fontrefs_index() -> None:
    """Update font references index."""
    indexed_fontrefs.clear()
    indexed_classical_fontrefs.clear()
    indexed_langnames.clear()
    for fn in (*_indexed_fontfiles_system, *_indexed_fontfiles_custom):
        try:
            face = _ft_open_face(fn)
        except freetype.ft_errors.FT_Exception:
            warnings.warn(
                f"Some error occurred when loading font {str(fn)!r}, skipped.\n"
            )
            traceback.print_exc()
            continue
        _update_fontref_index(fn, face)
        for i in range(1, face.num_faces):
            face = _ft_open_face(fn, i)
            _update_fontref_index(fn, face)


def all_fonts(*, classical: bool = False) -> list[FontFamilyName]:
    """Get available fonts, without localized name.

    Return: a list includes font family names.
    
    The name list is not guaranteed to be sorted.
    """
    if classical:
        return list(indexed_classical_fontrefs)
    return list(indexed_fontrefs)


def get_unlocalized_name(name: FontFamilyName) -> FontFamilyName:
    """Try convert a name into an unlocalized name."""
    return indexed_langnames.get(name, name)


def get_localized_names(name: FontFamilyName) -> list[FontFamilyName]:
    return [k for k, v in indexed_langnames.items() if v == name]