# fontra

Some small work with fonts.

## Features

- Font query via display name
- Custom font directories

## Installation

Via pip:

```shell
pip install fontra
```

## Usage

- Common font query

```python-repl
>>> import fontra
>>> fontra.all_fonts()
['Noto Sans Lisu', 'Noto Serif Tamil SemiCondensed', 'Noto Serif Georgian', 'Noto Sans Armenian', ...]
>>> fontra.get_font_styles("Arial")
['Regular', 'Italic', 'Bold', 'Bold Italic', 'Black']
>>> fontra.get_font("Arial", "Italic")
FontRef(path=PosixPath('/usr/share/fonts/TTF/ariali.ttf'), bank=0)
>>> fontra.unlocalized_name("更紗ゴシック UI J")
'Sarasa UI J'
>>> fontra.get_font("更纱黑体 SC", "SemiBold Italic")
FontRef(path=PosixPath('/usr/share/fonts/sarasa-gothic/Sarasa-SemiBoldItalic.ttc'), bank=1)
```

- Custom font direciories

```python-repl
>>> fontra.FONTDIR_CUSTOM.append("./data/fonts")
>>> fontra.update_custom_fontfiles_index()
>>> fontra.update_fontrefs_index()
>>> fontra.all_fonts()
[...]
```

## License

This project is under [MIT License](./LICENSE).
