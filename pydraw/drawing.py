from PIL import Image, ImageDraw, ImageColor, ImageFont


class PILDraw:
    def __init__(self, width, height):
        self._dpi = 300
        self._line_width = 4
        # size in mm
        self._width = self._mm_to_pixel(width)
        self._height = self._mm_to_pixel(height)
        self._draw = Image.new('RGB', (self._width, self._height), ImageColor.getrgb('white'))
        self._canvas = ImageDraw.Draw(self._draw)
        self._font = {}

    def _get_font(self, font, size):
        size = self._mm_to_pixel(size)
        font = font + '.ttf'
        if font not in self._font:
            self._font[font] = {}
            self._font[font][size] = ImageFont.truetype(font, size)
        elif size not in self._font[font]:
            self._font[font][size] = ImageFont.truetype(font, size)

        return self._font[font][size]

    def _mm_to_pixel(self, mm):
        return round(self._dpi * mm / 25.4)

    def arc(self, center, radius, start_degree, end_degree):
        x, y = center
        x = self._mm_to_pixel(x)
        y = self._mm_to_pixel(y)
        radius = self._mm_to_pixel(radius)
        self._canvas.arc((x-radius, self._height - y - radius,
                          x+radius, self._height - y + radius),
                         start_degree, end_degree,
                         fill=ImageColor.getrgb('black'),
                         width=self._line_width)

    def line(self, start_pt, end_pt):
        x1, y1 = start_pt
        x2, y2 = end_pt
        x1 = self._mm_to_pixel(x1)
        y1 = self._mm_to_pixel(y1)
        x2 = self._mm_to_pixel(x2)
        y2 = self._mm_to_pixel(y2)
        self._canvas.line((x1, self._height - y1, x2, self._height - y2),
                          fill=ImageColor.getrgb('black'),
                          width=self._line_width)

    def text(self, string, insert_pt, size=10, font='simhei'):
        x, y = insert_pt
        x = self._mm_to_pixel(x)
        y = self._mm_to_pixel(y)
        self._canvas.text((x, y), string, font=self._get_font(font, size),
                          fill=ImageColor.getrgb('black'))
