import math
from typing import Union, List


class Entity:
    def scale(self, x, y, factor):
        pass

    def move(self, x, y):
        pass

    def scale_by_reset_unit(self, factor):
        self.scale(0, 0, factor)

    def scale_by_reset_scale(self, factor):
        pass

    def scale_by_reset_factor(self, factor):
        self.scale(0, 0, factor)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError("Out Range!")

    def __repr__(self):
        return f'<{self.x},{self.y}>'

    def __add__(self, other):
        return Vector(self.x + other.x, self.y+other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y-other.y)

    def __mul__(self, factor):
        return Vector(factor * self.x, factor * self.y)

    def __rmul__(self, factor):
        return Vector(factor * self.x, factor * self.y)

    def __truediv__(self, denominator):
        return Vector(self.x / denominator, self.y / denominator)

    def __eq__(self, other):
        tol = 1e-6
        return abs(self.x - other[0]) < tol and abs(self.y - other[1]) < tol

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def unit(self):
        l = self.length()
        return Vector(self.x / l, self.y / l)

    def perpendicular(self):
        return Vector(-self.y, self.x)

    def move(self, x, y):
        self.x += x
        self.y += y
        return self

    def scale(self, x, y, factor):
        self.x = x + factor * (self.x - x)
        self.y = y + factor * (self.y - y)
        return self

    def copy(self):
        return Vector(self.x, self.y)


Point = Vector
P = Point


class Arc(Entity):
    def __init__(self, center: Point, radius: Union[float, int],
                 start_angle: Union[float, int], end_angle: Union[float, int], line_style='normal'):
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.line_style = line_style

    def move(self, x, y):
        self.center.move(x, y)

    def scale(self, x, y, factor):
        self.center.scale(x, y, factor)
        self.radius *= factor

    def draw_to(self, canvas):
        canvas.arc(self.center, self.radius,
                   self.start_angle, self.end_angle, self.line_style)

    def visit(self, visitor):
        visitor.visit_arc(self)

    def compute_bounding_box(self):
        pass


class Circle(Entity):
    def __init__(self, center, radius, line_style='normal'):
        self.center = center
        self.radius = radius
        self.line_style = line_style

    def move(self, x, y):
        self.center.move(x, y)

    def scale(self, x, y, factor):
        self.center.scale(x, y, factor)

    def draw_to(self, canvas):
        canvas.circle(self.center, self.radius, self.line_style)

    def visit(self, visitor):
        visitor.visit_circle(self)


class Ellipse(Entity):
    def __init__(self, center: Point, long_vector, ratio, start_angle=0, end_angle=360, line_style='normal'):
        super().__init__()
        self.center = center
        self.long_vector = long_vector

        assert ratio < 1
        self.ratio = ratio

        assert start_angle >= 0
        assert end_angle <= 360
        self.start_angle = start_angle
        self.end_angle = end_angle

        self.line_style = line_style

    def move(self, x, y):
        self.center.move(x, y)

    def scale(self, x, y, factor):
        self.center.scale(x, y, factor)
        self.long_vector.scale(0, 0, factor)

    def draw_to(self, canvas):
        canvas.ellipse(self.center, self.long_vector,
                       self.ratio,
                       self.start_angle, self.end_angle,
                       self.line_style)

    def visit(self, visitor):
        visitor.visit_ellipse(self)


class Line(Entity):
    def __init__(self, start: Point, end: Point, line_style='normal'):
        self.start = start
        self.end = end
        self.line_style = line_style

    def move(self, x, y):
        self.start.move(x, y)
        self.end.move(x, y)

    def scale(self, x, y, factor):
        self.start.scale(x, y, factor)
        self.end.scale(x, y, factor)

    def draw_to(self, canvas):
        canvas.line(self.start, self.end, self.line_style)

    def visit(self, visitor):
        visitor.visit_line(self)


class LWPolyline(Entity):
    def __init__(self, point_list: List[Point], bulge_list=None, line_style='normal'):
        super().__init__()
        self.point_list = point_list
        if bulge_list is None:
            bulge_list = [0]*len(point_list)
        assert len(bulge_list) == len(point_list)
        self.bulge_list = bulge_list
        self.line_style = line_style

    def move(self, x, y):
        for point in self.point_list:
            point.move(x, y)

    def scale(self, x, y, factor):
        for point in self.point_list:
            point.scale(x, y, factor)

    def draw_to(self, canvas):
        canvas.lwpolyline(self.point_list, self.bulge_list, self.line_style)

    def visit(self, visitor):
        visitor.visit_lwpolyline(self)


class Text(Entity):
    def __init__(self, text_string, insert, height,
                 h_justify=0, v_justify=0, width_factor=0.7, angle=0, font='normal'):
        super().__init__()
        self.text_string = text_string
        self.insert = insert
        self.height = height
        self.h_justify = h_justify
        self.v_justify = v_justify
        self.width_factor = width_factor
        self.angle = angle

        self.font = font

    def move(self, x, y):
        self.insert.move(x, y)

    def scale(self, x, y, factor):
        self.insert.scale(x, y, factor)
        self.height *= factor

    def draw_to(self, canvas):
        canvas.text(self.text_string, self.insert,
                    self.height,
                    self.h_justify, self.v_justify,
                    self.width_factor, self.angle,
                    self.font)

    def visit(self, visitor):
        visitor.visit_text(self)


class MText(Entity):
    def __init__(self, text_string, insert, height, width=None, attach=1, font='normal'):
        self.text_string = text_string
        self.insert = insert
        self.height = height
        self.width = width
        self.attach = attach
        self.font = font

    def move(self, x, y):
        self.insert.move(x, y)

    def scale(self, x, y, factor):
        self.insert.scale(x, y, factor)
        self.height *= factor

    def draw_to(self, canvas):
        canvas.mtext(self.text_string, self.insert,
                     self.height, self.width,
                     self.attach, self.font)

    def visit(self, visitor):
        visitor.visit_mtext(self)


class Context:
    def __init__(self, unit='mm', scale=1, factor=1):
        self.unit = unit
        self.scale = scale
        self.factor = factor
        self.insert_point = Point(0, 0)
        self.entity_list = list()

    def reset_unit(self, unit):
        if self.unit != unit:
            if self.unit == 'mm':
                self.scale_by_reset_unit(1000)
            elif self.unit == 'm':
                self.scale_by_reset_unit(0.001)
            else:
                raise RuntimeError(f'Unknown unit: {unit}')
            self.unit = unit

    def reset_scale(self, scale):
        for entity in self.entity_list:
            entity.scale_by_reset_scale(scale / self.scale)
        self.scale = scale

    def reset_factor(self, factor):
        for entity in self.entity_list:
            entity.scale_by_reset_factor(factor / self.factor)
        self.factor = factor

    def append(self, entity):
        assert isinstance(entity, Entity) or isinstance(entity, Context)
        self.entity_list.append(entity)

    def move(self, x, y):
        self.insert_point.move(x, y)

    def scale_by_reset_unit(self, factor):
        self.insert_point.scale(0, 0, factor)
        for entity in self.entity_list:
            entity.scale_by_reset_unit(factor)

    def scale_by_reset_scale(self, factor):
        for entity in self.entity_list:
            entity.scale_by_reset_scale(factor)

    def scale_by_reset_factor(self, factor):
        self.insert_point.scale(0, 0, factor)
        for entity in self.entity_list:
            entity.scale_by_reset_factor(factor)

    def draw_to(self, canvas):
        x, y = self.insert_point
        for entity in self.entity_list:
            entity.move(x, y)
            entity.draw_to(canvas)

    def visit(self, visitor):
        visitor.visit_context(self)

    def __iter__(self):
        return iter(self.entity_list)


class Symbol(Context):
    def scale_by_reset_scale(self, factor):
        for entity in self.entity_list:
            entity.scale(0, 0, factor)

    def scale_by_reset_factor(self, factor):
        self.insert_point.scale(0, 0, factor)


class Figure:
    pass


