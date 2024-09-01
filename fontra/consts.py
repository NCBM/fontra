SUPPORTED_EXT: tuple[str, ...] = (
    ".ttf", ".ttc", ".otf", ".otc", ".cff", ".woff", ".woff2",
    ".pfa", ".pfb", ".pcf", ".fnt", ".bdf", ".pfr"
)
SUPPORTED_EXT += tuple(f.upper() for f in SUPPORTED_EXT)  # pyright: ignore[reportConstantRedefinition]

TT_MS_ENCODING_MAPPING = [
    "utf-16-be", "utf-16-be", "sjis", "cp936", "big5", "cp949", "johab",
    "", "", "", "utf-16-be"
]
TT_MAC_ENCODING_MAPPING = [
    "mac-roman", "sjis", "big5", "euc-kr", "mac-arabic", "hebrew",
    "mac-greek", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
    "", "", "", "", "", "", "", "", "", "", ""
]  # undone as less use