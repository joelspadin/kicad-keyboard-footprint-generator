"""
3D model utilities
"""

from pathlib import Path
from KicadModTree import Footprint, Model


def get_model_files(mod: Footprint) -> list[Path]:
    """
    Return the paths for all 3D models in a footprint.
    """
    for child in mod.getNormalChilds():
        if isinstance(child, Model):
            yield Path(child.filename)
