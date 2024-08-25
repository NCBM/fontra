"""Fontra CLI application."""

from importlib.metadata import version
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from rich.console import Console
from rich.progress import Progress
from rich.table import Table, box
from rich.tree import Tree
from typer import Argument, Option

from fontra import (
    FontFamilyName,
    all_fonts,
    get_font_styles,
    get_fontdirs,
    get_localized_names,
    get_unlocalized_name,
)

app = typer.Typer(no_args_is_help=True)
console = Console()


def check_fonttools_installed() -> bool:
    try:
        import fontTools  # noqa: F401  # pyright: ignore[reportUnusedImport, reportMissingImports]
        return True
    except ModuleNotFoundError:
        return False


try:
    __version__ = version("fontra")
except Exception:
    __version__ = None


def version_callback(value: bool) -> None:
    """Show the version and exit"""
    if value:
        console.print(f"Fontra, version: {__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: Annotated[  # noqa: F811
        Optional[bool], 
        Option("--version", "-v", callback=version_callback, is_eager=True, help="Show the version and exit")
    ] = None
) -> None:
    """Hello Fontra"""


@app.command(help="List available fonts.")
def list(
    tree: Annotated[
        Optional[bool],
        Option("--tree/--table", "-t/-T", help="Display a tree of fonts")
    ] = False,
    sort: Annotated[
        Optional[bool],
        Option("--sort/--no-sort", "-s/-S", help="Output with sorted font names")
    ] = False,
    locnames: Annotated[
        Optional[bool],
        Option(
            "--with-localized-names/--without-localized-names", "-l/-L",
            help="Output with localized font names"
        )
    ] = False
) -> None:
    fonts = all_fonts()
    if sort:
        fonts.sort()
    if tree:
        fonts_tree = Tree("Fonts")
        for font in fonts:
            if locnames and (_names := get_localized_names(font)):
                _label = (
                    f"[blue]{font}[/] ([yellow]"
                    + "[/], [yellow]".join(_names) + "[/])"
                )
            else:
                _label = f"[blue]{font}[/]"
            _tree = fonts_tree.add(_label)
            for style in get_font_styles(font):
                _tree.add(style)
    else:
        fonts_table = Table("Name", "Style", box=box.DOUBLE_EDGE, show_lines=True)
        for font in fonts:
            if locnames and (_names := get_localized_names(font)):
                _fns = (
                    f"[blue]{font}[/]\n[yellow]"
                    + "[/]\n[yellow]".join(_names) + "[/]"
                )
            else:
                _fns = f"[blue]{font}[/]"
            fonts_table.add_row(_fns, " | ".join(get_font_styles(font)))
    console.print(f"{len(fonts)} font(s) found.")
    console.print(fonts_tree if tree else fonts_table)  # pyright: ignore[reportPossiblyUnboundVariable]


@app.command(help="Show the font directories.")
def path() -> None:
    for dir in get_fontdirs():
        console.print(f"- {dir!s}")


@app.command(help="Show the font information.")
def show(
    name: Annotated[List[FontFamilyName], Argument(help="Font family name.")], 
    localized: Annotated[bool, Option(help="Whether to lookup localized index.")] = True
) -> None:
    try:
        font_name = " ".join(name)
        styles = get_font_styles(font_name, localized)
        console.print(f"The font family '{font_name}' contains {len(styles)} styles:")
        for style in styles:
            console.print(f"- {style}")
    except KeyError as e:
        console.print(f"Error: {e}", style="bold red")


@app.command(help="Convert a name into an unlocalized name.")
def unlocalized(name: Annotated[FontFamilyName, Argument(help="Font family name.")]) -> None:
    console.print(f"Unlocalized name: {get_unlocalized_name(name)}")


@app.command(help="Convert TTC to TTF", rich_help_panel="Utils", hidden=not check_fonttools_installed())
def unpack(
    path: Annotated[Path, Argument(help="Path to the font file.")],
    output: Annotated[Optional[Path], Option(help="Path to the output directory.")] = None,
) -> None:
    try:
        from fontTools.ttLib.ttCollection import (  # noqa: F401  # pyright: ignore[reportMissingImports]
            TTCollection,
        )
    except ModuleNotFoundError:
        console.print(
            "Error: Please install fontTools first to use fontra cli utils.",
            "Install with pip: `pip install fontra\\[tools]`",
            style="bold red"
        )
        raise typer.Exit()

    if not path.suffix == ".ttc":
        console.print(f"Error: The file {path} is not a font collection.", style="bold red")
        raise typer.Exit()

    if not path.exists() or not path.is_file():
        console.print(f"Error: The file {path} does not exist.", style="bold red")
        raise typer.Exit()

    if output is None:
        output_dir = path.parent / f"{path.stem}_fonts"
    else:
        output_dir = output
    
    output_dir.mkdir(parents=True, exist_ok=True)

    ttc = TTCollection(str(path))
    total_fonts = len(ttc)

    with Progress() as progress:
        task = progress.add_task("Extracting fonts...", total=total_fonts)
        for i, font in enumerate(iterable=ttc):
            output_filename = output_dir / f"{path.stem}#{i}.ttf"
            font.save(str(output_filename))
            progress.update(task, advance=1)
        
        progress.update(task, completed=total_fonts)
        progress.console.print(f"[bold cyan]{total_fonts} fonts have been successfully extracted![/]")


@app.command(help="Report an issue", rich_help_panel="Others")
def report() -> None:
    console.print("🌈 [bold magenta]Redirecting to Github Issue...[/bold magenta] 🌈")
    typer.launch("https://github.com/NCBM/fontra/issues", wait=True)


if __name__ == "__main__":
    app()
