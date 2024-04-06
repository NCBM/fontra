"""
some small work with fonts.
"""

import os
import sys
from pathlib import Path
from typing import cast

import freetype
from typing_extensions import NamedTuple, TypeAlias

FontFamilyName: TypeAlias = str
StyleName: TypeAlias = str

FONTDIRS_SYSTEM: list[Path] = []
FONTDIRS_CUSTOM: list[Path] = []
SUPPORTED_EXT: tuple[str, ...] = (
    ".ttf", ".ttc", ".otf", ".otc", ".cff", ".woff", ".woff2",
    ".pfa", ".pfb", ".pcf", ".fnt", ".bdf", ".pfr"
)
SUPPORTED_EXT += tuple(f.upper() for f in SUPPORTED_EXT)
_indexed_fontfiles_system: set[Path] = set()
_indexed_fontfiles_custom: set[Path] = set()


class FontRef(NamedTuple):
    """Data for locating font style."""
    path: Path
    bank: int


_indexed_fontrefs: dict[FontFamilyName, dict[StyleName, FontRef]] = {}
_indexed_langnames: dict[FontFamilyName, FontFamilyName] = {}


def sfnt_decode(data: bytes, platform_id: int, language_id: int = -1) -> str:
    """Decode SFNT content data."""
    if platform_id != 1:
        return data.decode("utf-16-be")
    if language_id == 11:
        return data.decode("sjis")
    if language_id == 19:
        return data.decode("big5")
    if language_id == 23:
        return data.decode("euc-kr")
    if language_id == 33:
        return data.decode("gb18030")
    return data.decode()


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
            # thank you xdg
            # (some weird platforms does not have `/usr/share`)
            xdgdata = "/usr/share" if os.path.exists("/usr/share") else ""
        FONTDIRS_SYSTEM.extend(
            Path(datadir) / "fonts"
            for datadir in xdgdata.split(":") if datadir
        )
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
    family = cast(bytes, face.family_name).decode()
    style = cast(bytes, face.style_name).decode()
    _indexed_fontrefs.setdefault(family, {})
    _indexed_fontrefs[family][style] = FontRef(fn, face.face_index)
    if face.is_sfnt:
        _sfnt_dat = [face.get_sfnt_name(i) for i in range(face.sfnt_name_count)]
        _ffname = [
            sfnt_decode(x.string, x.platform_id, x.language_id)
            for x in _sfnt_dat if x.name_id == 16
        ]  # use short family name first
        if not _ffname:  # short family name not exist, use standard name
            _ffname = [
                sfnt_decode(x.string, x.platform_id, x.language_id)
                for x in _sfnt_dat if x.name_id == 1
            ]
        _indexed_langnames.update({fn: family for fn in _ffname})
    else:
        _indexed_langnames.update({family: family})


def update_fontrefs_index():
    """Update font references index."""
    _indexed_fontrefs.clear()
    _indexed_langnames.clear()
    for fn in (*_indexed_fontfiles_system, *_indexed_fontfiles_custom):
        face = freetype.Face(str(fn))
        _update_fontref_index(fn, face)
        for i in range(1, face.num_faces):
            face = freetype.Face(str(fn), i)
            _update_fontref_index(fn, face)


def all_fonts() -> list[FontFamilyName]:
    """Get available fonts, without localized name.

    Return: a list includes font family names.
    
    The name list is not guaranteed to be sorted.
    """
    return list(_indexed_fontrefs)


def unlocalized_name(name: FontFamilyName) -> FontFamilyName:
    """Try convert a name into an unlocalized name."""
    if name in _indexed_langnames:
        return _indexed_langnames[name]
    return name


def get_font(name: str, style: str, localized: bool = True) -> FontRef:
    """Get info for loading correct font faces.
    
    Params:
    - name: font family name.
    - style: font style.
    - localized: whether to lookup localized index.

    Return: a named tuple includes file path and collection index.
    """
    if localized:
        return _indexed_fontrefs[unlocalized_name(name)][style]
    return _indexed_fontrefs[name][style]


def get_font_styles(name: str, localized: bool = True) -> list[StyleName]:
    """Get available font styles.
    
    Params:
    - name: font family name.
    - localized: whether to lookup localized index.

    Return: a list includes style names.
    """
    if localized:
        return list(_indexed_fontrefs[unlocalized_name(name)].keys())
    return list(_indexed_fontrefs[name].keys())


update_system_fontdirs()
update_system_fontfiles_index()
update_fontrefs_index()

if __name__ == "__main__":
    from pprint import pprint
    print("_indexed_fontrefs:")
    pprint(_indexed_fontrefs, indent=4)
    print("_indexed_langnames:")
    pprint(_indexed_langnames, indent=4)
