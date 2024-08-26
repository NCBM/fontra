import freetype

from .consts import TT_MAC_ENCODING_MAPPING, TT_MS_ENCODING_MAPPING


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


def get_localized_family_name(face: freetype.Face) -> list[tuple[str, int, int, int]]:
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