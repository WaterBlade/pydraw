import math
import pyparsing
from collections import OrderedDict


class HandleContainer:
    def __init__(self, handle_gen):
        self.ordered_dict = OrderedDict()
        self.handle_gen = handle_gen

    def append(self, entity):
        assert isinstance(entity, TableItem)
        self.__setitem__(entity.name, entity)

    def __setitem__(self, key, entity):
        self.ordered_dict[key] = entity
        entity.set_handle(self.handle_gen.get_hex())

    def __getitem__(self, key):
        return self.ordered_dict[key]

    def __iter__(self):
        return iter(self.ordered_dict.values())


class Resource:
    def __init__(self, file_path=None):
        if file_path is not None:
            with open(file_path) as file:
                self.data_string = file.read()

        self.data = {}

    def get_data(self, data_name):
        if data_name in self.data.keys():
            return self.data[data_name]

        block = self.gen_block_parse(data_name)

        parse_result = block.searchString(self.data_string)

        data = {'name': data_name,
                'inform': parse_result[0].inform,
                'content': parse_result[0].content}

        self.data[data_name] = data
        return data

    @staticmethod
    def gen_block_parse(name):
        p = pyparsing

        start_line = p.lineStart + '*' + name + ',' + p.restOfLine('inform')

        below_one = '.' + p.OneOrMore(p.Word(p.nums))
        above_one = p.OneOrMore(p.Word(p.nums)) + p.ZeroOrMore('.') + p.ZeroOrMore(p.Word(p.nums))
        number = p.Combine(p.ZeroOrMore('-') + (below_one | above_one)).setParseAction(lambda tokens: float(tokens[0]))

        content_line = p.Group(p.lineStart + p.delimitedList(p.Word(p.alphas) | number))

        content = p.OneOrMore(content_line)('content')

        return start_line + content


class ReResource:
    def __init__(self):
        self.data = {}

    def add(self, name, inform, *content):
        self.data[name] = {'name': name,
                           'inform': inform,
                           'content': content}

    def get_data(self, name):
        return self.data[name]


class LTypeResource(ReResource):
    def __init__(self):
        super().__init__()
        self.add('CENTER',
                 'Center ____ _ ____ _ ____ _ ____ _ ____ _ ____',
                 [1.25,-.25,.25,-.25])


class PatternResource(ReResource):
    def __init__(self):
        super().__init__()
        self.add('SOLID',
                 'Solid fill',
                 [45, 0, 0, 0,.125])
        self.add('ANSI31',
                 'ANSI Iron, Brick, Stone masonry',
                 [45, 0, 0, 0, 3.175])


class GroupCode:
    def __init__(self):
        self.data = list()

    def append(self, code, value):
        if isinstance(code, list):
            assert len(code) == len(value)
            for c, v in zip(code, value):
                self.data.append(f'{c}')
                self.data.append(f'{v}')
        else:
            self.data.append(f'{code}')
            self.data.append(f'{value}')

    def extend(self, group_code):
        assert isinstance(group_code, GroupCode)
        self.data.extend(group_code.data)

    def to_string(self):
        return '\n'.join(self.data)


class Handle:
    max = 0xfffff

    def __init__(self, start=1):
        self._index = start

    def get_hex(self):
        assert self._index < self.max
        ret = hex(self._index).upper()[2:]
        self._index += 1
        return ret

    def get_dec(self):
        ret = f'{self._index}'
        self._index += 1
        return ret

    def get_max(self):
        return hex(self.max).upper()[2:]


# ------------------------------------------
# Header
# ------------------------------------------


class Variable:
    def __init__(self, name, codes, values):
        self.name = name
        self.codes = codes
        self.values = values

    def to_code(self):
        code = GroupCode()
        code.append(9, '$' + self.name)
        code.append(self.codes, self.values)

        return code


# ------------------------------------------
# Classes
# ------------------------------------------


class Class:
    def __init__(self, record_name, class_name, application_name,
                 value_90=0, value_91=0,
                 value_280=0, value_281=0):
        self.record_name = record_name
        self.class_name = class_name
        self.application_name = application_name
        self.value_90 = value_90
        self.value_91 = value_91
        self.value_280 = value_280
        self.value_281 = value_281

    def to_code(self):
        code = GroupCode()
        code.append(0, 'CLASS')
        code.append(1, self.record_name)
        code.append(2, self.class_name)
        code.append(3, self.application_name)
        code.append(90, self.value_90)
        code.append(91, self.value_91)
        code.append(280, self.value_280)
        code.append(281, self.value_281)

        return code


# ------------------------------------------
# Tables
# ------------------------------------------


class TableItem:
    def __init__(self, name):
        self.handle = None
        self.name = name

    def set_handle(self, handle):
        assert self.handle is None
        self.handle = handle


class AppID(TableItem):
    def __init__(self, name):
        super().__init__(name)

    def to_code(self):
        assert self.handle is not None
        code = GroupCode()
        code.append(0, 'APPID')
        code.append(5, self.handle)
        code.append(100, 'AcDbSymbolTableRecord')
        code.append(100, 'AcDbRegAppTableRecord')
        code.append(2, self.name)
        code.append(70, 0)

        return code


class BlockRecord(TableItem):
    def __init__(self, name):
        super().__init__(name)

    def to_code(self):
        assert self.handle is not None
        code = GroupCode()
        code.append(0, 'BLOCK_RECORD')
        code.append(5, self.handle)
        code.append(100, 'AcDbSymbolTableRecord')
        code.append(100, 'AcDbBlockTableRecord')
        code.append(2, self.name)
        code.append(70, 0)
        code.append(280, 1)
        code.append(281, 0)

        return code


class DimStyle(TableItem):
    def __init__(self, name, text_style, dim_scale=1, measure_scale=1,
                 text_height=2.5, arrow_size=2.0,
                 angle_precision=1, dec_precision=0):
        super().__init__(name)
        self.text_style = text_style
        self.dim_scale = dim_scale
        self.measure_scale = measure_scale
        self.text_height = text_height
        self.arrow_size = arrow_size
        self.angle_precision = angle_precision
        self.dec_precision = dec_precision

    def to_code(self):
        assert self.handle is not None
        code = GroupCode()
        code.append(0, 'DIMSTYLE')
        code.append(105, self.handle)
        code.append(100, 'AcDbSymbolTableRecord')
        code.append(100, 'AcDbDimStyleTableRecord')
        code.append(2, self.name)

        code.append(70, 0)
        code.append(41, self.arrow_size)  # DIMASZ,箭头尺寸
        code.append(42, 0.0)  # DIMEXO,尺寸界限延伸
        code.append(44, 2.0)  # DIMEXE,尺寸界限偏移

        code.append(73, 0)  # DIMTIH,非零时将文字水平放在内侧
        code.append(77, 1)  # DIMTAB,

        code.append(140, self.text_height)  # DIMTXT,标注文字高度
        code.append(147, 1.0)  # DIMCEN,中心标记/中心线的大小

        code.append(144, self.measure_scale)  # DIMLFAC,线性测量的比例因子
        code.append(40, self.dim_scale)  # DIMSCALE,全局标注比例因子
        code.append(279, 1)  # DIMTMOVE,标注文字移动规则

        code.append(280, 0)  # DIMJUST,水平标注文字位置,0-上方居中
        code.append(289, 3)  # DIMATFIT,位置放置,3-移动文字和箭头中较合适的一个
        code.append(179, self.angle_precision)  # DIMADEC,角度标注中显示的精度位的位数

        code.append(172, 1)  # DIMTOFL,强制在尺寸界线间绘制直线

        code.append(174, 1)  # DIMTIX,非零时将文字强制放在尺寸界线的内侧
        code.append(176, 256)  # DIMCLRD,尺寸线颜色,256随层
        code.append(177, 256)  # DIMCLRE,尺寸界限颜色,256随层
        code.append(178, 256)  # DIMCLRT,标注文字颜色,256随层

        code.append(271, self.dec_precision)  # DIMDEC,标注公差值的小数位数

        code.append(340, self.text_style.handle)

        return code


class Layer(TableItem):
    def __init__(self, name, ltype=None, color=7, no_print=False):
        super().__init__(name)
        self.ltype = ltype
        self.color = color
        self.no_print = no_print

    def to_code(self):
        assert self.handle is not None
        code = GroupCode()
        code.append(0, 'LAYER')
        code.append(5, self.handle)
        code.append(100, 'AcDbSymbolTableRecord')
        code.append(100, 'AcDbLayerTableRecord')
        code.append(2, self.name)

        code.append(70, 0)
        code.append(62, self.color)
        if self.ltype is None:
            code.append(6, 'CONTINUOUS')
        else:
            code.append(6, self.ltype.name)

        if self.no_print:
            code.append(290, 0)

        code.append(370, -3)
        code.append(390, self.handle + '0')
        code.append(347, self.handle + '1')

        return code


class LType(TableItem):
    def __init__(self, name, data=None):
        super().__init__(name)
        self.data = data

    def to_code(self):
        assert self.handle is not None
        code = GroupCode()
        code.append(0, 'LTYPE')
        code.append(5, self.handle)
        code.append(100, 'AcDbSymbolTableRecord')
        code.append(100, 'AcDbLinetypeTableRecord')
        code.append(2, self.name)

        code.append(70, 0)

        if self.name.lower() in ['continuous', 'byblock', 'bylayer']:
            code.append(3, '')
            code.append(72, 65)
            code.append(73, 0)
            code.append(40, 0.0)
        else:
            assert self.data is not None
            inform, content = self.data['inform'], self.data['content'][0]

            code.append(3, inform)
            code.append(72, 5)
            code.append(73, len(content))
            code.append(40, sum(abs(item) for item in content))
            for item in content:
                code.append([49, 74], [item, 0])

        return code


class Style(TableItem):
    def __init__(self, name, font_name='simp1.shx',
                 big_font_name='hz.shx', width_factor=0.7, oblique_degree=0,
                 system_font_name=None, ext_data=None):
        super().__init__(name)
        self.font_name = font_name
        self.big_font_name = big_font_name
        self.width_factor = width_factor
        self.oblique_degree = 0
        self.system_font_name = system_font_name
        self.ext_data = ext_data

    def to_code(self):
        assert self.handle is not None
        code = GroupCode()
        code.append(0, 'STYLE')
        code.append(5, self.handle)
        code.append(100, 'AcDbSymbolTableRecord')
        code.append(100, 'AcDbTextStyleTableRecord')
        code.append(2, self.name)

        code.append(70, 0)
        code.append(40, 0)
        code.append(41, self.width_factor)
        code.append(50, self.oblique_degree)

        code.append(71, 0)
        code.append(3, self.font_name)
        code.append(4, self.big_font_name)

        if self.system_font_name:
            code.append(1001, 'ACAD')
            code.append(1000, self.system_font_name)
            code.append(1071, self.ext_data)

        return code


# ------------------------------------------
# Blocks
# ------------------------------------------


class Block:
    index = 0

    def __init__(self, handle_gen,
                 name=None, layer=None, pt_base=(0, 0)):
        self.entity_list = list()
        self.handle_gen = handle_gen
        if name is None:
            name = f'BLOCK{self.index}'
            self.index += 1
        self.name = name
        self.layer = layer
        self.pt_base = pt_base
        self.begin_handle = self.handle_gen.get_hex()
        self.end_handle = self.handle_gen.get_hex()

        self._gen_block_record()

    def _gen_block_record(self):
        self.block_record = BlockRecord(self.name)
        self.block_record.set_handle(self.handle_gen.get_hex())
        self.record_handle = self.block_record.handle

    def append(self, entity):
        assert isinstance(entity, Entity)
        assert self.record_handle is not None
        self.entity_list.append(entity)
        entity.set_handle(self.handle_gen.get_hex())
        entity.set_owner_handle(self.record_handle)

    def to_code(self):
        assert self.begin_handle is not None
        assert self.end_handle is not None
        if self.layer is None:
            layer = '0'
        else:
            layer = self.layer.name
        code = GroupCode()
        code.append(0, 'BLOCK')
        code.append(5, self.begin_handle)
        code.append(100, 'AcDbEntity')
        code.append(8, layer)
        code.append(100, 'AcDbBlockBegin')
        code.append(2, self.name)
        code.append(70, 0)
        code.append([10, 20, 30], [self.pt_base[0], self.pt_base[1], 0])
        code.append(3, self.name)
        for entity in self.entity_list:
            code.extend(entity.to_code())
        code.append(0, 'ENDBLK')
        code.append(5, self.end_handle)
        code.append(100, 'AcDbEntity')
        code.append(8, layer)
        code.append(100, 'AcDbBlockEnd')

        return code


# ------------------------------------------
# Entities
# ------------------------------------------


class Entity:
    def __init__(self):
        self.layer = None
        self.handle = None
        self.owner_handle = None
        self.space_status = 0

    def check_before_build(self):
        assert self.layer is not None
        assert self.handle is not None
        assert self.owner_handle is not None

    def set_layer(self, layer):
        self.layer = layer

    def set_handle(self, handle):
        self.handle = handle

    def set_owner_handle(self, handle):
        self.owner_handle = handle

    def set_space_status(self, code):
        self.space_status = code


# Linear Object
# -----------------------------------------------


class Arc(Entity):
    def __init__(self, center, radius, start_angle, end_angle):
        super().__init__()
        self.center = center
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'ARC')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbCircle')
        code.append(67, self.space_status)
        code.append([10, 20, 30], [self.center[0], self.center[1], 0])
        code.append(40, self.radius)
        code.append(100, 'AcDbArc')
        code.append([50, 51], [self.start_angle, self.end_angle])

        return code


class Circle(Entity):
    def __init__(self, center, radius):
        super().__init__()
        self.center = center
        self.radius = radius

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'CIRCLE')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbCircle')
        code.append(67, self.space_status)
        code.append([10, 20, 30], [self.center[0], self.center[1], 0])
        code.append(40, self.radius)

        return code


class Ellipse(Entity):
    def __init__(self, center, long_vector, ratio, start_angle=0, end_angle=360):
        super().__init__()
        self.center = center
        self.long_vector = long_vector
        assert ratio < 1
        self.ratio = ratio

        assert start_angle >= 0
        assert end_angle <= 360
        self.start_angle = start_angle
        self.end_angle = end_angle

    def focus_radian(self, angle):
        if angle == 90:
            return 0.5 * math.pi
        elif angle == 270:
            return 1.5 * math.pi
        else:
            r = math.atan(math.tan(math.radians(angle))/self.ratio)
            if angle < 90:
                return r
            elif 90 < angle < 270:
                return math.pi + r
            elif angle > 270:
                return 2*math.pi + r

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'ELLIPSE')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbEllipse')
        code.append(67, self.space_status)
        code.append([10, 20, 30], [self.center[0], self.center[1], 0])
        code.append([11, 21, 31], [self.long_vector[0], self.long_vector[1], 0])
        code.append(40, self.ratio)

        code.append(41, self.focus_radian(self.start_angle))
        code.append(42, self.focus_radian(self.end_angle))
        # code.append([41, 42], [math.radians(self.start_angle), math.radians(self.end_angle)])
        return code


class Line(Entity):
    def __init__(self, start, end, line_scale=1):
        super().__init__()
        self.start = start
        self.end = end
        self.line_scale = line_scale

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'LINE')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(48, self.line_scale)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbLine')
        code.append(67, self.space_status)
        code.append([10, 20, 30], [self.start[0], self.start[1], 0])
        code.append([11, 21, 31], [self.end[0], self.end[1], 0])
        return code


class LWPolyline(Entity):
    def __init__(self, point_list, bulge_list=None):
        super().__init__()
        self.point_list = point_list
        if bulge_list is None:
            bulge_list = [0]*len(point_list)
        assert len(bulge_list) == len(point_list)
        self.bulge_list = bulge_list

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'LWPOLYLINE')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbPolyline')
        code.append(67, self.space_status)
        code.append(90, len(self.point_list))
        for pt, bulge in zip(self.point_list, self.bulge_list):
            code.append([10, 20, 42], [pt[0], pt[1], bulge])

        return code


# Text object
# -------------------------------------------------
class _TextBase(Entity):
    def __init__(self):
        super().__init__()
        self.style = None

    def set_style(self, style):
        self.style = style


class Text(_TextBase):
    def __init__(self, text_string, insert, height,
                 h_justify=0, v_justify=0, width_factor=0.7, angle=0):
        super().__init__()
        self.text_string = text_string
        self.insert = insert
        self.height = height
        self.h_justify = h_justify
        self.v_justify = v_justify
        self.width_factor = width_factor
        self.angle = angle

        self.style = None

    def set_style(self, style):
        self.style = style

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'TEXT')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbText')
        code.append(67, self.space_status)
        code.append(1, self.text_string)
        code.append(50, self.angle)
        code.append(40, self.height)
        code.append(41, self.width_factor)
        code.append(72, self.h_justify)

        code.append([10, 20, 30], [self.insert[0], self.insert[1], 0])
        code.append([11, 21, 31], [self.insert[0], self.insert[1], 0])
        # Warning! text_style must put here, or it can't display in CAD
        # First we put upwards, and it can't display
        if self.style is None:
            code.append(7, 'STANDARD')
        else:
            code.append(7, self.style.name)
        code.append(100, 'AcDbText')
        code.append(73, self.v_justify)
        return code


class MText(_TextBase):
    def __init__(self, text_string, insert, height, width=None, attach=1):
        super().__init__()
        self.text_string = text_string
        self.insert = insert
        self.height = height
        self.width = width
        self.attach = attach

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'MTEXT')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        if self.style is None:
            code.append(7, 'STANDARD')
        else:
            code.append(7, self.style.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbMText')
        code.append(40, self.height)
        code.append(67, self.space_status)
        code.append([10, 20, 30], [self.insert[0], self.insert[1], 0])

        if self.width is not None:
            code.append(41, self.width)

        code.append(71, self.attach)

        # split word by 250
        word_count = len(self.text_string)
        if word_count < 250:
            code.append(1, self.text_string)
        else:
            text_list = [self.text_string[i:i + 250] for i in range(0, word_count, 250)]
            code.append([3]*(len(text_list)-1), self.text_string[:-1])
            code.append(1, text_list[-1])

        return code


# Dimension objects
# -------------------------------------------------


class _DimBase(Entity):
    def __init__(self):
        super().__init__()
        self.dimstyle = None

    def set_dimstyle(self, dimstyle):
        self.dimstyle = dimstyle

    def check_before_build(self):
        super().check_before_build()
        assert self.dimstyle is not None


class ArcLengthDimension(_DimBase):
    def __init__(self, center, line_insert, arc_start, arc_end):
        super().__init__()
        self.center = center
        self.line_insert = line_insert
        self.arc_start = arc_start
        self.arc_end = arc_end

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'ARC_DIMENSION')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbDimension')
        code.append(67, self.space_status)
        code.append(3, self.dimstyle.name)
        code.append([10, 20, 30], [self.line_insert[0], self.line_insert[1], 0])
        # dim type, value is magic number, according dxf spec.
        code.append(70, 37)
        code.append(100, 'AcDbArcDimension')
        code.append([15, 25, 35], [self.center[0], self.center[1], 0])
        code.append([13, 23, 33], [self.arc_start[0], self.arc_start[1], 0])
        code.append([16, 26, 36], [self.arc_start[0], self.arc_start[1], 0])
        code.append([14, 24, 34], [self.arc_end[0], self.arc_end[1], 0])
        code.append([17, 27, 37], [self.arc_end[0], self.arc_end[1], 0])

        return code


class DiametricDimension(_DimBase):
    def __init__(self, start, end, leader_length=None):
        super().__init__()
        self.start = start
        self.end = end
        self.leader_length = leader_length

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'DIMENSION')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbDimension')
        code.append(67, self.space_status)
        code.append(3, self.dimstyle.name)
        code.append([10, 20, 30], [self.end[0], self.end[1], 0])
        # dim type, value is magic number, according dxf spec.
        code.append(70, 35)
        code.append(100, 'AcDbDiametricDimension')
        if self.leader_length is not None:
            code.append(40, self.leader_length)
        code.append([15, 25, 35], [self.start[0], self.start[1], 0])

        return code


class LineAngularDimension(_DimBase):
    def __init__(self, pt_line, pt_1_start, pt_1_end, pt_2_start, pt_2_end):
        super().__init__()
        self.pt_line = pt_line
        self.pt_1_start = pt_1_start
        self.pt_1_end = pt_1_end
        self.pt_2_start = pt_2_start
        self.pt_2_end = pt_2_end

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'DIMENSION')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbDimension')
        code.append(67, self.space_status)
        code.append(3, self.dimstyle.name)
        # dim type, value is magic number, according dxf spec.
        code.append(70, 34)
        code.append([10, 20, 30], [self.pt_2_start[0], self.pt_2_start[1], 0])
        code.append(100, 'AcDb2LineAngularDimension')
        code.append([13, 23, 33], [self.pt_1_end[0], self.pt_1_end[1], 0])
        code.append([14, 24, 34], [self.pt_1_start[0], self.pt_1_start[1], 0])
        code.append([15, 25, 35], [self.pt_2_end[0], self.pt_2_end[1], 0])
        code.append([16, 26, 36], [self.pt_line[0], self.pt_line[1], 0])

        return code


class PointAngularDimension(_DimBase):
    def __init__(self, pt_line, pt_center, pt_1, pt_2):
        super().__init__()
        self.pt_line = pt_line
        self.pt_center = pt_center
        self.pt_1 = pt_1
        self.pt_2 = pt_2

    def to_code(self):
        code = GroupCode()
        code.append(0, 'DIMENSION')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbDimension')
        # dim type, value is magic number, according dxf spec.
        code.append(70, 37)
        code.append(67, self.space_status)
        code.append(3, self.dimstyle.name)
        code.append([10, 20, 30], [self.pt_line[0], self.pt_line[1], 0])
        code.append(100, 'AcDb3PointAngularDimension')
        code.append([13, 23, 33], [self.pt_1[0], self.pt_1[1], 0])
        code.append([14, 24, 34], [self.pt_2[0], self.pt_2[1], 0])
        code.append([15, 25, 35], [self.pt_center[0], self.pt_center[1], 0])

        return code


class RadialDimension(_DimBase):
    def __init__(self, center, start, leader):
        super().__init__()
        self.center = center
        self.start = start
        self.leader = leader

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'DIMENSION')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbDimension')
        code.append(67, self.space_status)
        code.append(3, self.dimstyle.name)
        code.append([10, 20, 30], [self.center[0], self.center[1], 0])
        # dim type, value is magic number, according dxf spec.
        code.append(70, 36)
        code.append(100, 'AcDbRadialDimension')
        code.append(40, self.leader)
        code.append([15, 25, 35], [self.start[0], self.start[1], 0])

        return code


class RotatedDimension(_DimBase):
    def __init__(self, start, end, text_insert, rotate_angle):
        super().__init__()
        self.start = start
        self.end = end
        self.text_insert = text_insert
        self.rotate_angle = rotate_angle

    def to_code(self):
        self.check_before_build()
        code = GroupCode()
        code.append(0, 'DIMENSION')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbDimension')
        code.append(67, self.space_status)
        code.append(3, self.dimstyle.name)
        code.append([10, 20, 30], [self.text_insert[0], self.text_insert[1], 0])
        # dim type, value is magic number, according dxf spec.
        code.append(70, 32)
        code.append(100, 'AcDbAlignedDimension')
        code.append(50, self.rotate_angle)
        code.append([13, 23, 33], [self.start[0], self.start[1], 0])
        code.append([14, 24, 34], [self.end[0], self.end[1], 0])
        code.append(100, 'AcDbRotatedDimension')

        return code


# Area objects
# ------------------------------------------------


class Hatch(Entity):
    def __init__(self, pattern_data,
                 point_list, bulge_list=None,
                 rotate_angle=0, scale=1, fill_type=0):
        super().__init__()
        assert point_list[0] == point_list[-1]
        self.pattern_data = pattern_data
        self.point_list = point_list
        if bulge_list is None:
            bulge_list = [0] * len(point_list)
        assert len(bulge_list) == len(point_list)
        self.bulge_list = bulge_list
        self.rotate_angle = rotate_angle
        self.scale = scale
        self.fill_type = fill_type

    def to_code(self):
        self.check_before_build()
        name = self.pattern_data['name']
        data = self.pattern_data['content']
        angle = self.rotate_angle
        scale = self.scale

        code = GroupCode()
        code.append(0, 'HATCH')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbHatch')
        code.append([10, 20, 30], [0, 0, 0])
        code.append([210, 220, 230], [0, 0, 1])
        code.append(2, name.upper())
        code.append(70, self.fill_type)
        # code.append(67, self.space_status)

        # magic number
        code.append(71, 1)
        code.append(91, 1)
        code.append(92, 7)
        code.append(72, 1)
        code.append(73, 1)
        code.append(93, len(self.point_list))
        for pt, bulge in zip(self.point_list, self.bulge_list):
            code.append([10, 20, 42], [pt[0], pt[1], bulge])
        code.append(97, 1)
        code.append(330, self.handle)
        code.append(75, 0)
        code.append(76, 1)
        code.append(52, self.rotate_angle)
        code.append(41, self.scale)
        code.append(77, 0)

        code.append(78, len(data))

        for row in data:
            head = row[:5]
            tail = row[5:]

            head[0] = head[0] + angle

            x, y = head[1], head[2]
            radians = math.radians(angle)
            head[1] = (x * math.cos(radians) - y * math.sin(radians)) * scale
            head[2] = (y * math.cos(radians) + x * math.sin(radians)) * scale

            del_x, del_y = head[3], head[4]
            radians = math.radians(head[0])
            head[3] = (del_x * math.cos(radians) - del_y * math.sin(radians)) * scale
            head[4] = (del_y * math.cos(radians) + del_x * math.sin(radians)) * scale

            code.append([53, 43, 44, 45, 46], head)
            code.append(79, len(tail))
            for item in tail:
                code.append(40, scale*float(item))

        code.append(47, 1)
        code.append(98, 1)
        code.append([10, 20], [self.point_list[0][0], self.point_list[0][1]])

        return code


class Wipeout(Entity):
    def __init__(self, point_list):
        super().__init__()
        assert point_list[0] == point_list[-1]
        self.point_list = point_list

    def _process_points(self):
        points = self.point_list
        left, bottom = points[0][0], points[0][1]
        right, top = left, bottom

        for pt in points:
            x, y = pt[0], pt[1]
            left = min(left, x)
            right = max(right, x)
            bottom = min(bottom, y)
            top = max(top, y)

        insert_point = [left, bottom, 0]
        height, width = top - bottom, right - left
        u_vector = [width, 0, 0]
        v_vector = [0, height, 0]

        x0, y0 = (left + right) / 2.0, (bottom + top) / 2.0
        rel_points = []
        for point in points:
            x = (point[0] - x0) / width
            y = - (point[1] - y0) / height
            rel_points.append([x, y])

        # rel_points.extend(rel_points[:2])

        return insert_point, u_vector, v_vector, rel_points

    def to_code(self):
        self.check_before_build()
        insert_point, u_vector, v_vector, rel_points = self._process_points()

        code = GroupCode()
        code.append(0, 'WIPEOUT')
        code.append(5, self.handle)
        code.append(8, self.layer.name)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbEntity')
        code.append(67, self.space_status)
        code.append(100, 'AcDbWipeout')

        code.append(90, 0)
        code.append([10, 20, 30], insert_point)
        code.append([11, 21, 31], u_vector)
        code.append([12, 22, 32], v_vector)
        code.append([13, 23], [1, 1])
        code.append(340, 0)
        code.append(70, 7)
        code.append([280, 281, 282, 283], [1, 50, 50, 0])
        code.append(360, 0)
        code.append(71, 2)
        code.append(91, len(rel_points))
        for point in rel_points:
            code.append([14, 24], point)
        # code.append([14, 24], rel_points)

        return code


# Block insert
# -------------------------------------------------


class Insert(Entity):
    def __init__(self, pt_insert, block_name,
                 scale_x=1, scale_y=1, rotate_angle=0):
        super().__init__()
        self.pt_insert = pt_insert
        self.block_name = block_name
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.rotate_angle = rotate_angle

    def gen_code(self):
        code = GroupCode()
        code.append(0, 'INSERT')
        code.append(5, self.handle)
        code.append(330, self.owner_handle)
        code.append(67, self.space_status)
        code.append(100, 'AcDbEntity')
        code.append(100, 'AcDbBlockReference')
        code.append([10, 20, 30], [self.pt_insert[0], self.pt_insert[1], 0])
        code.append(2, self.block_name)
        code.append([41, 42, 43], [self.scale_x, self.scale_y, 1])
        code.append(50, self.rotate_angle)

        return code
    

# No drawing object
# -------------------------------------------------


class Viewport(Entity):
    def __init__(self, pt_model_center,
                 pt_doc_center,
                 doc_width, doc_height,
                 port_id=1,
                 scale=1,
                 angle=0):
        super().__init__()
        self.pt_model_center = pt_model_center
        self.pt_doc_center = pt_doc_center
        self.doc_width = doc_width
        self.doc_height = doc_height
        self.port_id = port_id
        self.scale = scale
        self.angle = angle

    def set_port_id(self, port_id):
        self.port_id = port_id

    def to_code(self):
        code = GroupCode()
        code.append(0, 'VIEWPORT')
        code.append(5, self.handle)
        code.append(100, 'AcDbEntity')
        code.append(8, 'Defpoints')
        code.append(330, self.owner_handle)
        code.append(67, self.space_status)
        code.append(100, 'AcDbViewport')
        code.append(67, 1)
        code.append([40, 41], [self.doc_width, self.doc_height])
        code.append(68, 2)
        code.append(69, self.port_id)
        code.append([10, 20, 30], [self.pt_model_center[0], self.pt_model_center[1], 0])
        if self.angle == 0:
            code.append([12, 22], [self.pt_doc_center[0], self.pt_doc_center[1]])
        else:
            code.append([12, 22], [0, 0])
            code.append([17, 27, 37], [self.pt_doc_center[0], self.pt_doc_center[1], 0])
        code.append(45, self.doc_height * self.scale)
        code.append(51, self.angle)

        code.append(71, 1)
        code.append(90, 16384)
        code.append([110, 120, 130], [0, 0, 0])
        code.append([111, 121, 131], [1, 0, 0])
        code.append([112, 122, 132], [0, 1, 0])

        return code


# ------------------------------------------
# Objects
# ------------------------------------------


class ObjectItem:
    def __init__(self):
        self.handle = None
        self.owner_handle = None

    def set_handle(self, handle):
        self.handle = handle

    def set_owner_handle(self, handle):
        self.owner_handle = handle


class Dictionary(ObjectItem):
    def __init__(self, handle_gen, name):
        super().__init__()
        self.handle_gen = handle_gen
        self.name = name
        self.dict_list = list()

    def append(self, item):
        assert isinstance(item, ObjectItem)
        self.dict_list.append(item)
        item.set_handle(self.handle_gen.get_hex())
        item.set_owner_handle(self.handle)

    def to_code(self):
        assert self.handle is not None
        assert self.owner_handle is not None
        code = GroupCode()
        code.append(0, 'DICTIONARY')
        code.append(5, self.handle)
        code.append(330, self.owner_handle)
        code.append(100, 'AcDbDictionary')
        for item in self.dict_list:
            code.append(3, item.name)
            code.append(350, item.handle)

        return code


class Layout(ObjectItem):
    def __init__(self, name, pt_lb, pt_rt):
        super().__init__()
        self.space_handle = None
        self.name = name
        self.pt_lb = pt_lb
        self.pt_rt = pt_rt

    def set_space_handle(self, handle):
        self.space_handle = handle

    def to_code(self):
        assert self.space_handle is not None
        code = GroupCode()

        code.append(0, 'LAYOUT')
        code.append(5, self.handle)
        code.append(330, self.owner_handle)
        # plot settings
        code.append(100, 'AcDbPlotSettings')
        code.append(1, '')
        code.append(2, 'none_device')

        width = self.pt_rt[0] - self.pt_lb[0]
        height = self.pt_rt[1] - self.pt_lb[1]
        code.append(4, 'ISO_A2_({:.2f}_x_{:.2f}_MM)'.format(width, height))

        code.append(6, '')
        code.append([40, 41, 42, 43], [5, 5, 5, 5])
        code.append([44, 45], [height, width])
        code.append([46, 47], [0, 0])
        code.append([142, 143], [1, 1])
        code.append(70, 1)
        code.append(72, 1)
        code.append(73, 1)
        code.append(74, 5)
        code.append(75, 16)
        code.append(77, 2)
        code.append([148, 149], [0, 0])

        # -------------
        code.append(100, 'AcDbLayout')
        code.append(1, self.name)
        code.append([10, 20], [self.pt_lb[0], self.pt_lb[1]])
        code.append([11, 21], [self.pt_rt[0], self.pt_rt[1]])
        code.append([14, 24, 34], [self.pt_lb[0] - 100, self.pt_lb[1] - 100, 0])
        code.append([15, 25, 35], [self.pt_rt[0] + 100, self.pt_rt[1] + 100, 0])
        code.append(330, self.space_handle)

        return code


# ------------------------------------------
# Space Interface
# ------------------------------------------


class Space:
    def __init__(self, handle_gen):
        self.entity_list = list()
        self.handle_gen = handle_gen
        self.block = None
        self.block_record = None
        self.record_handle = None

    def init_space_block(self, name):
        self.block = Block(self.handle_gen, name)
        self.block_record = self.block.block_record
        self.record_handle = self.block_record.handle

    def append(self, entity):
        self.entity_list.append(entity)
        entity.set_handle(self.handle_gen.get_hex())
        entity.set_owner_handle(self.record_handle)


class ModelSpace(Space):
    def __init__(self, handle_gen):
        super().__init__(handle_gen)
        self.name = '*MODEL_SPACE'
        self.init_space_block(self.name)

    def append(self, entity):
        assert not isinstance(entity, Viewport)
        super().append(entity)


class PaperSpace(Space):
    index = 0

    def __init__(self, handle_gen, width=594, height=420):
        super().__init__(handle_gen)
        self.viewport_id_gen = Handle(1)
        if self.index == 0:
            self.name = '*PAPER_SPACE'
        else:
            self.name = f'*PAPER_SPACE{self.index}'
        self.index += 1
        self.init_space_block(self.name)
        self.layout = Layout(f'Layout{self.index}', (0, 0), (width, height))
        self.layout.set_space_handle(self.record_handle)
        self.append(Viewport((0, 0), (0, height/2),
                             width, height))

    def append(self, entity):
        super().append(entity)
        entity.set_space_status(1)
        if isinstance(entity, Viewport):
            entity.set_port_id(self.viewport_id_gen.get_dec())


class DXF:
    def __init__(self):
        self.handle_gen = Handle()
        self.ltype_resource = LTypeResource()
        self.pattern_resource = PatternResource()

        # header
        self.variable_list = list()
        # classes
        self.class_list = list()
        # tables
        self.appid = AppID('ACAD')
        self.appid.set_handle(self.handle_gen.get_hex())
        self.block_record_list = list()
        self.dimstyle = HandleContainer(self.handle_gen)
        self.layer = HandleContainer(self.handle_gen)
        self.ltype = HandleContainer(self.handle_gen)
        self.style = HandleContainer(self.handle_gen)
        # blocks
        self.block_list = list()
        # entities
        self.model_space = ModelSpace(self.handle_gen)
        self.paper_space = PaperSpace(self.handle_gen)
        # objects
        self.object_list = list()
        # init
        self.init_header()
        self.init_classes()
        self.init_tables()
        self.init_blocks()
        self.init_objects()

    def init_header(self):
        var = self.variable_list
        var.append(Variable('ACADVER', 1, 'AC1021'))
        var.append(Variable('HANDSEED', 5, self.handle_gen.get_max()))

    def init_classes(self):
        cls = self.class_list
        cls.append(Class('WIPEOUTVARIABLES', 'AcDbWipeoutVariables',
                         r"WipeOut|Product Desc:     WipeOut Dbx Application|Company:          Autodesk, Inc.|WEB Address:      www.autodesk.com",
                         0, 1, 0, 0))

    def init_tables(self):
        self.block_record_list.append(self.model_space.block_record)
        self.block_record_list.append(self.paper_space.block_record)

        self.ltype.append(LType('CONTINUOUS'))
        self.ltype.append(LType('ByBlock'))
        self.ltype.append(LType('ByLayer'))
        self.style.append(Style('STANDARD'))
        self.dimstyle.append(DimStyle('STANDARD', self.style['STANDARD']))
        self.layer.append(Layer('0'))
        self.layer.append(Layer('Defpoints', no_print=True))

    def init_blocks(self):
        self.block_list.append(self.model_space.block)
        self.block_list.append(self.paper_space.block)

    def init_objects(self):
        root_dict = Dictionary(self.handle_gen, 'root')
        group_dict = Dictionary(self.handle_gen, 'ACAD_GROUP')
        layout_dict = Dictionary(self.handle_gen, 'ACAD_LAYOUT')
        layout = self.paper_space.layout

        root_dict.set_handle(self.get_handle())
        root_dict.set_owner_handle(0)
        root_dict.append(group_dict)
        root_dict.append(layout_dict)
        layout_dict.append(layout)

        self.object_list.append(root_dict)
        self.object_list.append(group_dict)
        self.object_list.append(layout_dict)
        self.object_list.append(layout)

    def build(self):
        code = GroupCode()
        code.extend(self.build_header())
        code.extend(self.build_classes())
        code.extend(self.build_tables())
        code.extend(self.build_blocks())
        code.extend(self.build_entities())
        code.extend(self.build_objects())
        code.append(0, 'EOF')
        return code

    def build_header(self):
        code = GroupCode()
        code.append(0, 'SECTION')
        code.append(2, 'HEADER')
        for var in self.variable_list:
            code.extend(var.to_code())
        code.append(0, 'ENDSEC')
        return code

    def build_classes(self):
        code = GroupCode()
        code.append(0, 'SECTION')
        code.append(2, 'CLASSES')
        for cls in self.class_list:
            code.extend(cls.to_code())
        code.append(0, 'ENDSEC')
        return code

    def build_tables(self):
        code = GroupCode()
        code.append(0, 'SECTION')
        code.append(2, 'TABLES')
        code.extend(self.build_appid_table())
        code.extend(self.build_block_table())
        code.extend(self.build_dimstyle_table())
        code.extend(self.build_layer_table())
        code.extend(self.build_ltype_table())
        code.extend(self.build_style_table())
        code.extend(self.build_ucs_table())
        code.extend(self.build_view_table())
        code.extend(self.build_vport_table())
        code.append(0, 'ENDSEC')
        return code

    def build_blocks(self):
        code = GroupCode()
        code.append(0, 'SECTION')
        code.append(2, 'BLOCKS')
        for block in self.block_list:
            code.extend(block.to_code())
        code.append(0, 'ENDSEC')
        return code

    def build_entities(self):
        code = GroupCode()
        code.append(0, 'SECTION')
        code.append(2, 'ENTITIES')
        for entity in self.model_space.entity_list:
            code.extend(entity.to_code())
        for entity in self.paper_space.entity_list:
            code.extend(entity.to_code())
        code.append(0, 'ENDSEC')
        return code

    def build_objects(self):
        code = GroupCode()
        code.append(0, 'SECTION')
        code.append(2, 'OBJECTS')
        for obj in self.object_list:
            code.extend(obj.to_code())
        code.append(0, 'ENDSEC')
        return code

    def build_appid_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'APPID')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        code.extend(self.appid.to_code())

        code.append(0, 'ENDTAB')

        return code

    def build_block_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'BLOCK_RECORD')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        for block in self.block_record_list:
            code.extend(block.to_code())

        code.append(0, 'ENDTAB')

        return code

    def build_dimstyle_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'DIMSTYLE')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)
        code.append(100, 'AcDbDimStyleTable')
        code.append(71, 1)

        for dim in self.dimstyle:
            code.extend(dim.to_code())

        code.append(0, 'ENDTAB')
        return code

    def build_layer_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'LAYER')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        for layer in self.layer:
            code.extend(layer.to_code())

        code.append(0, 'ENDTAB')
        return code

    def build_ltype_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'LTYPE')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        for ltype in self.ltype:
            code.extend(ltype.to_code())

        code.append(0, 'ENDTAB')
        return code

    def build_style_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'STYLE')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        for style in self.style:
            code.extend(style.to_code())

        code.append(0, 'ENDTAB')
        return code

    def build_ucs_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'UCS')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        code.append(0, 'ENDTAB')

        return code

    def build_view_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'VIEW')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        code.append(0, 'ENDTAB')

        return code

    def build_vport_table(self):
        code = GroupCode()
        code.append(0, 'TABLE')
        code.append(2, 'VPORT')
        code.append(5, self.get_handle())
        code.append(100, 'AcDbSymbolTable')
        code.append(70, 0)

        code.append(0, 'ENDTAB')

        return code

    def get_handle(self):
        return self.handle_gen.get_hex()

    def save(self, path):
        code = self.build()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code.to_string())
