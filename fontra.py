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
_indexed_fontfiles: set[Path] = set()


class FontRef(NamedTuple):
    """Data for locating font style."""
    path: Path
    bank: int


_indexed_fontrefs: dict[FontFamilyName, dict[StyleName, FontRef]] = {}
_indexed_langnames: dict[FontFamilyName, FontFamilyName] = {}


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


def update_fontfiles_index() -> None:
    """Update font files index."""
    for directory in FONTDIRS_SYSTEM:
        for r, _, fs in os.walk(directory):
            _indexed_fontfiles.update(
                {Path(r) / fn for fn in fs if fn.endswith(SUPPORTED_EXT)}
            )
    for directory in FONTDIRS_CUSTOM:
        for r, _, fs in os.walk(directory):
            _indexed_fontfiles.update(
                {Path(r) / fn for fn in fs if fn.endswith(SUPPORTED_EXT)}
            )


def _update_fontref_index(fn: Path, face: freetype.Face) -> None:
    family = cast(bytes, face.family_name).decode()
    style = cast(bytes, face.style_name).decode()
    _indexed_fontrefs.setdefault(family, {})
    _indexed_fontrefs[family][style] = FontRef(fn, face.face_index)
    _indexed_langnames.update(
        {
            (
                sfo.string.decode("utf-16-be" if sfo.platform_id != 1 else "gbk")
                # here actually I should use platform encoding dictionaries instead
                #  of single `gbk`, but it'll take some time.
            ): family
            for sfo in (
                face.get_sfnt_name(i) for i in range(face.sfnt_name_count)
            ) if sfo.name_id in (1, 16)
        }
    )


def update_fontrefs_index():
    """Update font references index."""
    for fn in _indexed_fontfiles:
        face = freetype.Face(str(fn))
        _update_fontref_index(fn, face)
        for i in range(1, face.num_faces):
            face = freetype.Face(str(fn), i)
            _update_fontref_index(fn, face)


def get_font(name: str, style: str, lookup_langindex: bool = True) -> FontRef:
    """Get info for loading correct font faces."""
    if lookup_langindex:
        return _indexed_fontrefs[_indexed_langnames[name]][style]
    return _indexed_fontrefs[name][style]


update_system_fontdirs()
update_fontfiles_index()
update_fontrefs_index()

if __name__ == "__main__":
    from pprint import pprint
    print("_indexed_fontrefs:")
    pprint(_indexed_fontrefs, indent=4)
    print("_indexed_langnames:")
    pprint(_indexed_langnames, indent=4)
