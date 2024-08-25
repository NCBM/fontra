# fontra

![PyPI Version](https://img.shields.io/pypi/v/fontra) | ![PyPI Downloads](https://img.shields.io/pypi/dm/fontra)
| ![License](https://img.shields.io/github/license/NCBM/fontra)

Some small work with fonts.

## Features

- Font indexing and querying via display name
- Specifying custom font directories
- CLI for listing fonts

## Installation

Via pip:

```shell
pip install fontra
```

> For some advanced tools:
>
> ```shell
> pip install fontra[tools]
> ```
>
> which currently enables you to:
>
> - Extract a .ttc file to .ttf files

## Usage

### Command-line interface

```shell
fontra --help
       --version
       list
                                            List available fonts.
            --tree/[--table] | -t/[-T]
                                            Whether to display a tree or a table.
            --sort/[--no-sort] | -s/[-S]
                                            Whether to output with sorted font names.
            --with-localized-names/[--without-localized-names] | -l/[-L]
                                            Whether to show localized font names.
       path
                                            Show the font directories.
       show
                                            Show the font information.
            [--localized]/--no-localized NAME...  # will fix name in next version
                                            Whether to lookup the localized index.
       unlocalized NAME  # will fix name in next version
                                            Convert a name into an unlocalized name.
```

### Font indexing and querying

```python
>>> import fontra
>>> fontra.all_fonts()
['Noto Sans Lisu', 'Noto Serif Tamil SemiCondensed', 'Noto Serif Georgian', 'Noto Sans Armenian', ...]
>>> fontra.get_font_styles("Arial")
['Regular', 'Italic', 'Bold', 'Bold Italic', 'Black']
>>> fontra.get_font("Arial", "Italic")
FontRef(path=PosixPath('/usr/share/fonts/TTF/ariali.ttf'), bank=0)
>>> fontra.has_font_family("Helvetica")
False
>>> fontra.has_font_style("Comic Sans MS", "Light")
False
>>> fontra.get_unlocalized_name("更紗ゴシック UI J")
'Sarasa UI J'
>>> fontra.get_localized_names("LXGW WenKai TC")
['霞鶩文楷 TC', '霞鹜文楷 TC']
>>> fontra.get_font("更纱黑体 SC", "SemiBold Italic")
FontRef(path=PosixPath('/usr/share/fonts/sarasa-gothic/Sarasa-SemiBoldItalic.ttc'), bank=1)
```

### Custom font directories

```python
>>> fontra.FONTDIR_CUSTOM.append("./data/fonts")
>>> fontra.update_custom_fontfiles_index()
>>> fontra.update_fontrefs_index()
>>> fontra.all_fonts()
[...]
```

## License

This project is under [MIT License](./LICENSE).
