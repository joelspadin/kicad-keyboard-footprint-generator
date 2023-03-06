"""
Common utilities for generator scripts.
"""

import itertools
import shutil
from pathlib import Path
from typing import Callable, TypeVar
from KicadModTree import Footprint
from kicad_keyboard_footprints.file import FileHandler
from kicad_keyboard_footprints.model import get_model_files


T = TypeVar("T")
MaybeList = T | list[T] | None

REPO_PATH = Path(__file__).parent.parent.parent


def to_list(x: MaybeList[T]) -> list[T]:
    """
    If given a list, return it unmodified. If given a single value, return a
    list containing that value.
    """
    if isinstance(x, list):
        return x
    return [x]


def permute_options(**kwargs):
    """
    Given a dict of lists, yield all permutations of dicts with a single item
    from each list. If the input dict has a value which is not a list, it will
    be treated as a list with a single element.

    Example:
    ```
    permute_options(a=[1, 2], b=[3]) -> {a: 1, b: 3}, {a: 2, b: 3}
    ```
    """
    keys = kwargs.keys()
    lists = [to_list(x) for x in kwargs.values()]

    for options in itertools.product(*lists):
        yield dict(zip(keys, options))


def make_footprints(
    out_dir: Path | str, lib_name: str, generator: Callable[..., Footprint], **kwargs
):
    """
    Generates footprints for every permutation of the given options.

    :param out_dir: Output directory path
    :param lib_name: Library name (not including ".pretty")
    :param generator: Function to call to generate footprints
    :param kwargs: Values to permute and pass to "generator". See permute_options().
    """
    out_dir = Path(out_dir)
    lib_dir = out_dir / f"{lib_name}.pretty"
    lib_dir.mkdir(parents=True, exist_ok=True)

    for options in permute_options(**kwargs):
        mod = generator(**options)
        _copy_models(lib_dir, mod)

        file = FileHandler(mod)
        file.writeFile(lib_dir / f"{mod.name}.kicad_mod")


def _copy_models(lib_dir: Path, mod: Footprint):
    source = REPO_PATH / "3dshapes"

    for path in get_model_files(mod):
        dest = lib_dir / path
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source / path.name, dest)
