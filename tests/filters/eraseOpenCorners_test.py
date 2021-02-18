import pytest
from fontTools.misc.loggingTools import CapturingLogHandler

from ufo2ft.filters.eraseOpenCorners import EraseOpenCornersFilter, logger


@pytest.fixture(
    params=[
        {
            "glyphs": [
                {"name": "space", "width": 500},
                {
                    "name": "hasCornerGlyph",
                    "width": 600,
                    "outline": [
                        ("moveTo", ((20, 0),)),
                        ("lineTo", ((198, 360),)),
                        ("lineTo", ((60, 353),)),
                        ("lineTo", ((179, 0),)),
                        ("closePath", ()),
                    ],
                },
                {
                    "name": "curvyCornerGlyph",
                    "width": 600,
                    "outline": [
                        ("moveTo", ((400, 0),)),
                        ("curveTo", ((400, 100), (450, 300), (300, 300))),
                        ("lineTo", ((200, 100),)),
                        ("curveTo", ((250, 100), (450, 150), (450, 50))),
                        ("closePath", ()),
                    ],
                },            ]
        }
    ]
)
def font(request, FontClass):
    font = FontClass()
    for param in request.param["glyphs"]:
        glyph = font.newGlyph(param["name"])
        glyph.width = param.get("width", 0)
        pen = glyph.getPen()
        for operator, operands in param.get("outline", []):
            getattr(pen, operator)(*operands)
    return font


class EraseOpenCornersFilterTest:
    def test_empty_glyph(self, font):
        philter = EraseOpenCornersFilter(include={"space"})
        assert not philter(font)

    def test_corner_glyph(self, font):
        philter = EraseOpenCornersFilter(include={"hasCornerGlyph"})
        assert philter(font)

        newcontour = font["hasCornerGlyph"][0]
        assert len(newcontour) == 3
        assert newcontour[1].x == pytest.approx(114.5417)
        assert newcontour[1].y == pytest.approx(191.2080)

    def test_curve_curve_glyph(self, font):
        philter = EraseOpenCornersFilter(include={"curvyCornerGlyph"})
        assert philter(font)

        newcontour = font["curvyCornerGlyph"][0]
        assert len(newcontour) == 7
        assert newcontour[0].x == pytest.approx(406.4859)
        assert newcontour[0].y == pytest.approx(104.5666)
