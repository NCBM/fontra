import freetype
from freetype.ft_enums import (
    TT_NAME_ID_FONT_FAMILY,
    TT_NAME_ID_PREFERRED_FAMILY,
    TT_PLATFORM_APPLE_UNICODE,
    TT_PLATFORM_MACINTOSH,
    TT_PLATFORM_MICROSOFT,
)

from .consts import TT_MAC_ENCODING_MAPPING, TT_MS_ENCODING_MAPPING


def _get_encoding(pid: int, eid: int, lid: int) -> str:
    if pid == TT_PLATFORM_APPLE_UNICODE:
        return "utf-16-be"
    if pid == TT_PLATFORM_MACINTOSH:
        if eid == 25 and lid == 33:
            return "gb18030"
        return TT_MAC_ENCODING_MAPPING[eid] or "unicode_escape"
    if pid == TT_PLATFORM_MICROSOFT:
        return TT_MS_ENCODING_MAPPING[eid]
    return "unicode_escape"


def get_localized_family_name(face: freetype.Face) -> list[tuple[str, int, int, int]]:
    _ffname = [
        (x.string, x.name_id, x.platform_id, x.encoding_id, x.language_id)
        for x in (
            face.get_sfnt_name(i) for i in range(face.sfnt_name_count)
        ) if x.name_id == TT_NAME_ID_PREFERRED_FAMILY
    ]
    if not _ffname:
        _ffname = [
            (x.string, x.name_id, x.platform_id, x.encoding_id, x.language_id)
            for x in (
                face.get_sfnt_name(i) for i in range(face.sfnt_name_count)
            ) if x.name_id == TT_NAME_ID_FONT_FAMILY
        ]
    return [
        (s.decode(_get_encoding(pid, eid, lid)), pid, eid, lid)
        for s, _, pid, eid, lid in _ffname
    ]