"""
3D model utilities
"""

from pathlib import Path
from KicadModTree import Footprint, Model

LIB_PATH_PLACEHOLDER = "{LIBNAME}"
PROJECT_PATH_VAR = "${KIPRJMOD}"


def update_model_path(mod: Footprint, libname: str):
    """
    Replace LIB_PATH_PLACEHOLDER with the library path in all 3D models
    in a footprint.
    """
    for model in _get_models(mod):
        model.filename = str(model.filename).replace(
            LIB_PATH_PLACEHOLDER, f"{PROJECT_PATH_VAR}/{libname}.pretty"
        )


def get_model_files(mod: Footprint) -> list[Path]:
    """
    Return the paths relative to the project directory for all 3D models
    in a footprint.
    """
    for model in _get_models(mod):
        yield Path(model.filename).relative_to(PROJECT_PATH_VAR)


def _get_models(mod: Footprint):
    for child in mod.getNormalChilds():
        if isinstance(child, Model):
            yield child
