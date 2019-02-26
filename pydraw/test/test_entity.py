from ..entity import Vector, Line


def test_vector_transform():
    v = Vector(1, 1)
    v.rotate(0, 0, 90)
    assert v == [-1, 1]
    v.mirror_x(0)
    assert v == [1, 1]


def test_line_transform():
    l = Line([0, 0], [50, 50])
    l.move(100, 0)
    assert l.start == [100, 0]
    assert l.end == [150, 50]
    l.scale(100, 0, 2)
    assert l.start == [100, 0]
    assert l.end == [200, 100]
    l.rotate(100, 0, -90)
    assert l.start == [100, 0]
    assert l.end == [200, -100]
    l.mirror_x(100)
    assert l.start == [100, 0]
    assert l.end == [0, -100]

