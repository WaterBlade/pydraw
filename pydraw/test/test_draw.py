from ..drawing import PILDraw
from pytest_mock import mocker
from PIL import ImageColor, ImageFont


def test_draw_arc(mocker):
    arc = mocker.patch('PIL.ImageDraw.ImageDraw.arc')
    p = PILDraw(50.8, 50.8)
    p.arc([25.4, 25.4], 25.4, 0, 360)
    arc.assert_called_with((0, 0, 600, 600), 0, 360,
                           fill=ImageColor.getrgb('black'),
                           width=4)


def test_draw_line(mocker):
    line = mocker.patch('PIL.ImageDraw.ImageDraw.line')
    p = PILDraw(25.4, 25.4)
    p.line([0, 0], [12.7, 12.7])
    line.assert_called_with((0, 300, 150, 150),
                            fill=ImageColor.getrgb('black'),
                            width=4)


def test_draw_text(mocker):
    text = mocker.patch('PIL.ImageDraw.ImageDraw.text', fill=ImageColor.getrgb('black'))
    p = PILDraw(25.4, 25.4)
    p.text('hello world', [12.7, 12.7])
    fnt = p._get_font('simhei', 10)
    text.assert_called_with((150, 150), 'hello world', font=fnt, fill=ImageColor.getrgb('black'))