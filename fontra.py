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

SUPPORTED_EXT: tuple[str, ...] = (
    ".ttf", ".ttc", ".otf", ".otc", ".cff", ".woff", ".woff2",
    ".pfa", ".pfb", ".pcf", ".fnt", ".bdf", ".pfr"
)
SUPPORTED_EXT += tuple(f.upper() for f in SUPPORTED_EXT)

TT_MS_ENCODING_MAPPING = [
    "utf-16-be", "utf-16-be", "sjis", "cp936", "big5", "cp949", "johab",
    "", "", "", "utf-16-be"
]
TT_MAC_ENCODING_MAPPING = [
    "mac-roman", "sjis", "big5", "euc-kr", "mac-arabic", "hebrew",
    "mac-greek", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", ""
]  # undone as less use

FONTDIRS_SYSTEM: list[Path] = []
FONTDIRS_CUSTOM: list[Path] = []
_indexed_fontfiles_system: set[Path] = set()
_indexed_fontfiles_custom: set[Path] = set()


class FontRef(NamedTuple):
    """Data for locating font style."""
    path: Path
    bank: int


_indexed_fontrefs: dict[FontFamilyName, dict[StyleName, FontRef]] = {}
_indexed_langnames: dict[FontFamilyName, FontFamilyName] = {}


def _get_encoding(pid: int, eid: int, lid: int) -> str:
    # assert freetype.TT_PLATFORM_APPLE_UNICODE == 0
    if pid == 0:
        return "utf-16-be"
    # assert freetype.TT_PLATFORM_MACINTOSH == 1
    if pid == 1:
        if eid == 25 and lid == 33:
            return "gb18030"
        return TT_MAC_ENCODING_MAPPING[eid] or "unicode_escape"
    # assert freetype.TT_PLATFORM_MICROSOFT == 3
    if pid == 3:
        return TT_MS_ENCODING_MAPPING[eid]
    return "unicode_escape"


def _get_localized_family_name(face: freetype.Face) -> list[tuple[str, int, int, int]]:
    # assert freetype.TT_NAME_ID_FONT_FAMILY == 1
    # assert freetype.TT_NAME_ID_PREFERRED_FAMILY == 16
    _ffname = [
        (x.string, x.name_id, x.platform_id, x.encoding_id, x.language_id)
        for x in (
            face.get_sfnt_name(i) for i in range(face.sfnt_name_count)
        ) if x.name_id == 16
    ]
    if not _ffname:
        _ffname = [
            (x.string, x.name_id, x.platform_id, x.encoding_id, x.language_id)
            for x in (
                face.get_sfnt_name(i) for i in range(face.sfnt_name_count)
            ) if x.name_id == 1
        ]
    return [
        (s.decode(_get_encoding(pid, eid, lid)), pid, eid, lid)
        for s, _, pid, eid, lid in _ffname
    ]


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
        _ffname = _get_localized_family_name(face)
        _indexed_langnames.update({fn: family for fn, *_ in _ffname if fn != family})


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
    return _indexed_langnames.get(name, name)


def get_font(name: str, style: str, localized: bool = True) -> FontRef:
    """Get info for loading correct font faces.
    
    Params:
    - name: font family name.
    - style: font style.
    - localized: whether to lookup localized index.

    Return: a named tuple includes file path and collection index.
    """
    name = unlocalized_name(name) if localized else name
    if name not in _indexed_fontrefs:
        raise KeyError(f"Font {name!r} not found")
    if style not in (_fonts := _indexed_fontrefs[name]):
        raise KeyError(f"Font style {style!r} of font {name!r} not found")
    return _fonts[style]


def get_font_styles(name: str, localized: bool = True) -> list[StyleName]:
    """Get available font styles.
    
    Params:
    - name: font family name.
    - localized: whether to lookup localized index.

    Return: a list includes style names.
    """
    name = unlocalized_name(name) if localized else name
    if name not in _indexed_fontrefs:
        raise KeyError(f"Font {name!r} not found")
    return [st for st in _indexed_fontrefs[name]]


update_system_fontdirs()
update_system_fontfiles_index()
update_fontrefs_index()

if __name__ == "__main__":
    from pprint import pprint
    print("_indexed_fontrefs:")
    pprint(_indexed_fontrefs, indent=4)
    print("_indexed_langnames:")
    pprint(_indexed_langnames, indent=4)
