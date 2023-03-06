"""
Workaround for
https://gitlab.com/kicad/libraries/kicad-footprint-generator/-/issues/659
"""

from KicadModTree import KicadFileHandler
from KicadModTree.util.kicad_util import formatTimestamp, SexprSerializer


class FileHandler(KicadFileHandler):
    """
    Workaround for
    https://gitlab.com/kicad/libraries/kicad-footprint-generator/-/issues/659
    """

    def serialize(self, **kwargs):
        """
        Get a valid string representation of the footprint in the .kicad_mod format
        """

        sexpr = [
            "module",
            self.kicad_mod.name,
            ["layer", "F.Cu"],
            ["tedit", formatTimestamp(kwargs.get("timestamp"))],
            SexprSerializer.NEW_LINE,
        ]

        if self.kicad_mod.description:
            sexpr.append(["descr", self.kicad_mod.description])
            sexpr.append(SexprSerializer.NEW_LINE)

        if self.kicad_mod.tags:
            sexpr.append(["tags", self.kicad_mod.tags])
            sexpr.append(SexprSerializer.NEW_LINE)

        if self.kicad_mod.attribute:
            attributes = (
                [self.kicad_mod.attribute]
                if isinstance(self.kicad_mod.attribute, str)
                else self.kicad_mod.attribute
            )

            sexpr.append(["attr", *attributes])
            sexpr.append(SexprSerializer.NEW_LINE)

        if self.kicad_mod.maskMargin:
            sexpr.append(["solder_mask_margin", self.kicad_mod.maskMargin])
            sexpr.append(SexprSerializer.NEW_LINE)

        if self.kicad_mod.pasteMargin:
            sexpr.append(["solder_paste_margin", self.kicad_mod.pasteMargin])
            sexpr.append(SexprSerializer.NEW_LINE)

        if self.kicad_mod.pasteMarginRatio:
            sexpr.append(["solder_paste_ratio", self.kicad_mod.pasteMarginRatio])
            sexpr.append(SexprSerializer.NEW_LINE)

        sexpr.extend(self._serializeTree())

        return str(SexprSerializer(sexpr))
