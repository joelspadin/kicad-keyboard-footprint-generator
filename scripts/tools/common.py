import itertools
import shutil
from pathlib import Path
from typing import Callable, TypeVar
from KicadModTree import Footprint, KicadFileHandler
from KicadKeyboardFootprints.model import get_model_files, update_model_path


T = TypeVar("T")
MaybeList = T | list[T] | None


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
        yield {key: value for key, value in zip(keys, options)}


def make_footprints(
    out_dir: Path | str, lib_name: str, generator: Callable[..., Footprint], **kwargs
):
    out_dir = Path(out_dir)
    lib_dir = out_dir / f"{lib_name}.pretty"
    lib_dir.mkdir(parents=True, exist_ok=True)

    for options in permute_options(**kwargs):
        mod = generator(**options)
        update_model_path(mod, lib_name)
        _copy_models(out_dir, mod)

        file = KicadFileHandler(mod)
        file.writeFile(lib_dir / f"{mod.name}.kicad_mod")


def _copy_models(out_dir: Path, mod: Footprint):
    source = Path(__file__).parent.parent.parent / "3dshapes"

    for path in get_model_files(mod):
        dest = out_dir / path
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(source / path.name, dest)
