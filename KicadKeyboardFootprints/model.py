from pathlib import Path
from KicadModTree import Footprint, Model

MODEL_PATH_PLACEHOLDER = "{LIBNAME}"
PROJECT_PATH_VAR = "${KIPRJMOD}"


def update_model_path(mod: Footprint, libname: str):
    for model in _get_models(mod):
        model.filename = str(model.filename).replace(
            MODEL_PATH_PLACEHOLDER, f"{PROJECT_PATH_VAR}/{libname}"
        )


def get_model_files(mod: Footprint) -> list[Path]:
    for model in _get_models(mod):
        yield Path(model.filename).relative_to(PROJECT_PATH_VAR)


def _get_models(mod: Footprint):
    for child in mod.getNormalChilds():
        if isinstance(child, Model):
            yield child
