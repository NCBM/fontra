# fontra

![PyPI Version](https://img.shields.io/pypi/v/fontra) | ![PyPI Downloads](https://img.shields.io/pypi/dm/fontra)
| ![License](https://img.shields.io/github/license/NCBM/fontra)

Font indexing and querying support like fontconfig.

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
            --localized/[--unlocalized] | -l/[-L]
                                            Whether to show localized font names.
       fontdirs
                                            Show the font search directories.
       show NAME...
                                            Show the font information.
            [--localized]/--unlocalized | -l/[-L]
                                            Whether to lookup the localized index.
            --fuzzy/[--exact] | -f/[-F]
                                            Whether to fuzzy match.
            --verbose/-v
                                            Whether to show font path
       unlocalize NAME
                                            Convert a name into an unlocalized name.
       unpack PATH
                                            Unpack a TTC to TTF. (Requires fontra[tools] installed)
              --output OUTPUT
                                            Path to the output directory.
```

### Font indexing and querying

```python
>>> import fontra
>>> fontra.init_fontdb()  # Initialize and search fonts
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
>>> from pathlib import Path
>>> fontra.FONTDIR_CUSTOM.append(Path("~/.fonts"))
>>> fontra.update_custom_fontfiles_index()
>>> fontra.update_fontrefs_index()
>>> fontra.all_fonts()
[...]
```

#### From environment variable

```shell
PYFONTRA_CUSTOM_FONTDIRS=~/.fonts fontra 
```

## License

This project is under [MIT License](./LICENSE).
