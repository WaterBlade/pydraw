from pydraw.drawing import PILDraw


if __name__ == '__main__':
    p = PILDraw(50, 50)
    p.arc([15, 15], 5, 0, 360)
    p.line([0, 0], [38, 38])
    p.text('hello world', [10, 10], size=5, font='arial')
    p._draw.save('hello.png', dpi=(300, 300))

