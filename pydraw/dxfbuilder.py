import pyparsing
import math

class Code:
    __slots__ = ['code', 'value']

    def __init__(self, code, value):
        self.code = code
        self.value = value

    def to_string(self):
        return f'{self.code}\n{self.value}'


class Codes:
    def __init__(self, prefix: list=None, suffix: list=None):
        self.list_ = list()
        if prefix is None:
            prefix = list()
        if suffix is None:
            suffix = list()
        self.prefix = prefix
        self.suffix = suffix

    def add(self, code, value):
        self.list_.append(Code(code, value))

    def append(self, codes):
        assert isinstance(codes, Codes)
        self.list_.append(codes)

    def extend(self, codes_list):
        for codes in codes_list:
            self.append(codes)

    def to_string(self):
        return '\n'.join(c.to_string() for c in self.prefix+self.list_+self.suffix)


class DXF:
    def __init__(self):
        self._handle = 1
        self._dxf = Codes(suffix=[Code(0, 'EOF')])

        self._header = self._make_section('HEADER')
        self._classes = self._make_section('CLASSES')
        self._tables = self._make_section('TABLES')
        self._blocks = self._make_section('BLOCKS')
        self._entities = self._make_section('ENTITIES')
        self._objects = self._make_section('OBJECTS')

        self._dxf.extend([self._header,
                          self._classes,
                          self._tables,
                          self._blocks,
                          self._entities,
                          self._objects])

        self._appid_table = self._make_table('APPID')
        self._block_table = self._make_table('BLOCK_RECORD')
        self._dimstyle_table = self._make_table('DIMSTYLE', 'AcDbDimStyleTable')
        self._layer_table = self._make_table('LAYER')
        self._ltype_table = self._make_table('LTYPE')
        self._style_table = self._make_table('STYLE')
        self._ucs_table = self._make_table('UCS')
        self._view_table = self._make_table('VIEW')
        self._vport_table = self._make_table('VPORT')

        self._tables.extend([self._appid_table,
                             self._block_table,
                             self._dimstyle_table,
                             self._layer_table,
                             self._ltype_table,
                             self._style_table,
                             self._ucs_table,
                             self._view_table,
                             self._vport_table])

        self._pattern_builder = PatternBuilder('acad.pat')
        self._ltype_builder = LTypeBuilder('acad.lin')

        self._handle_dict = dict()

    def _get_hex_handle(self):
        ret = hex(self._handle).upper()[2:]
        self._handle += 1
        return ret

    def save(self, path):
        self._build()
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self._dxf.to_string())

    def _build(self):
        self._build_header()
        self._build_classes()
        self._build_tables()
        self._build_blocks()
        self._build_entities()
        self._build_objects()

    def _build_header(self):
        c = self._header
        c.add(9, '$ACADVER')
        c.add(1, 'AC1021')
        c.add(9, '$HANDSEED')
        c.add(5, '0xfffff')

    def _build_classes(self):
        c = self._classes
        c.add(0, 'CLASS')
        c.add(1, 'WIPEOUTVARIABLES')
        c.add(2, 'AcDbWipeoutVariables')
        c.add(3, r"WipeOut|Product Desc:     WipeOut Dbx Application|Company:          Autodesk, Inc.|WEB Address:      www.autodesk.com")
        c.add(90, 0)
        c.add(91, 1)
        c.add(280, 0)
        c.add(281, 0)

    def _build_tables(self):
        pass

    def _build_blocks(self):
        pass

    def _build_entities(self):
        pass

    def _build_objects(self):
        pass

    # SECTIONS
    def _make_section(self, name):
        return Codes([Code(0, 'SECTION'), Code(2, name)], [Code(0, 'ENDSEC')])

    def _make_table(self, name, subtype=None):
        prefix = [Code(0, 'TABLE'),
                  Code(2, name),
                  Code(5, self._get_hex_handle()),
                  Code(100, 'AcDbSymbolTable'),
                  Code(70, 0)]
        if subtype is not None:
            prefix.append(Code(100, subtype))
            prefix.append(Code(71, 1))
        return Codes(prefix, [Code(0, 'ENDTAB')])

    def _write_appid_item(self, name):
        c = self._appid_table
        c.add(0, 'APPID')
        c.add(5, self._get_hex_handle())
        c.add(100, 'AcDbSymbolTableRecord')
        c.add(100, 'AcDbRegAppTableRecord')
        c.add(2, name)
        c.add(70, 0)

    def _write_block_item(self, name):
        c = self._block_table
        c.add(0, 'BLOCK_RECORD')
        c.add(5, self._get_hex_handle())
        c.add(100, 'AcDbSymbolTableRecord')
        c.add(100, 'AcDbBlockTableRecord')
        c.add(2, name)
        c.add(70, 0)
        c.add(280, 1)
        c.add(281, 0)

    def _write_dimstyle_item(self, *,  name, text_style, dim_scale=1, measure_scale=1,
                             text_height=2.5, arrow_size=2.0,
                             angle_precision=1, dec_precision=0):
        c = self._dimstyle_table
        c.add(0, 'DIMSTYLE')
        c.add(105, self._get_hex_handle())
        c.add(100, 'AcDbSymbolTableRecord')
        c.add(100, 'AcDbDimStyleTableRecord')
        c.add(2, name)

        c.add(70, 0)
        c.add(41, arrow_size)  # DIMASZ,箭头尺寸
        c.add(42, 0.0)  # DIMEXO,尺寸界限延伸
        c.add(44, 2.0)  # DIMEXE,尺寸界限偏移

        c.add(73, 0)  # DIMTIH,非零时将文字水平放在内侧
        c.add(77, 1)  # DIMTAB,

        c.add(140, text_height)  # DIMTXT,标注文字高度
        c.add(147, 1.0)  # DIMCEN,中心标记/中心线的大小

        c.add(144, measure_scale)  # DIMLFAC,线性测量的比例因子
        c.add(40, dim_scale)  # DIMSCALE,全局标注比例因子
        c.add(279, 1)  # DIMTMOVE,标注文字移动规则

        c.add(280, 0)  # DIMJUST,水平标注文字位置,0-上方居中
        c.add(289, 3)  # DIMATFIT,位置放置,3-移动文字和箭头中较合适的一个
        c.add(179, angle_precision)  # DIMADEC,角度标注中显示的精度位的位数

        c.add(172, 1)  # DIMTOFL,强制在尺寸界线间绘制直线

        c.add(174, 1)  # DIMTIX,非零时将文字强制放在尺寸界线的内侧
        c.add(176, 256)  # DIMCLRD,尺寸线颜色,256随层
        c.add(177, 256)  # DIMCLRE,尺寸界限颜色,256随层
        c.add(178, 256)  # DIMCLRT,标注文字颜色,256随层

        c.add(271, dec_precision)  # DIMDEC,标注公差值的小数位数

        c.add(340, self._handle_dict[text_style])

    def _write_layer_item(self, name, ltype='CONTINUOUS', color=7):
        c = self._ltype_table
        handle = self._get_hex_handle()
        c.add(0, 'LAYER')
        c.add(5, handle)
        c.add(100, 'AcDbSymbolTableRecord')
        c.add(100, 'AcDbLayerTableRecord')
        c.add(2, name)

        c.add(70, 0)
        c.add(62, color)
        c.add(6, ltype)

        c.add(370, -3)
        c.add(390, handle + '0')
        c.add(347, handle + '1')

    def _write_ltype_item(self, name):
        c = self._ltype_table
        c.add(0, 'LTYPE')
        c.add(5, self._get_hex_handle())
        c.add(100, 'AcDbSymbolTableRecord')
        c.add(100, 'AcDbLinetypeTableRecord')
        c.add(2, name)

        c.add(70, 0)
        c.add(3, '')
        c.add(72, 65)

        if name.lower() in ['continuous', 'byblock', 'bylayer']:
            c.add(73, 0)
            c.add(40, 0.0)
        else:
            c.append(self._ltype_builder.ltype(name))

    def _write_style_item(self, name, font_name='simp1.shx',
                     big_font_name='hz.shx', width_factor=0.7, oblique_degree=0,
                     system_font_name=None, ext_data=None):
        c = self._style_table
        c.add(0, 'STYLE')
        c.add(5, self._get_hex_handle())
        c.add(100, 'AcDbSymbolTableRecord')
        c.add(100, 'AcDbTextStyleTableRecord')
        c.add(2, name)

        c.add(70, 0)
        c.add(40, 0)
        c.add(41, width_factor)
        c.add(50, oblique_degree)

        c.add(71, 0)
        c.add(3, font_name)
        c.add(4, big_font_name)

        if system_font_name:
            c.add(1001, 'ACAD')
            c.add(1000, system_font_name)
            c.add(1071, ext_data)

    def visit_block(self, name, entity_in_block, pt_base=(0, 0), layer='0'):
        c = self._blocks
        c.add(0, 'BLOCK')
        c.add(5, self._get_hex_handle())
        c.add(100, 'AcDbEntity')
        c.add(8, layer)
        c.add(100, 'AcDbBlockBegin')
        c.add(2, name)
        c.add(70, 0)
        c.add([10, 20, 30], [pt_base[0], pt_base[1], 0])
        c.add(3, name)
        for item in entity_in_block:
            c.append(item.visit(self))
        c.add(0, 'ENDBLK')
        c.add(5, self._get_hex_handle())
        c.add(100, 'AcDbEntity')
        c.add(8, '0')
        c.add(100, 'AcDbBlockEnd')


class ResourceBuilder:
    def __init__(self, file_path=None):
        if file_path is not None:
            with open(file_path) as file:
                self.data_string = file.read()

        self.data_dict = {}

    def get_data(self, data_name):
        if data_name in self.data_dict.keys():
            return self.data_dict[data_name]

        block = self.block_parse(data_name)

        parse_result = block.searchString(self.data_string)

        data = {'inform': parse_result[0].inform,
                'content': parse_result[0].content}

        self.data_dict[data_name] = data
        return data

    def block_parse(self, name):
        p = pyparsing

        start_line = p.lineStart + '*' + name + ',' + p.restOfLine('inform')

        below_one = '.' + p.OneOrMore(p.Word(p.nums))
        above_one = p.OneOrMore(p.Word(p.nums)) + p.ZeroOrMore('.') + p.ZeroOrMore(p.Word(p.nums))
        number = p.Combine(p.ZeroOrMore('-') + (below_one | above_one)).setParseAction(lambda tokens: float(tokens[0]))

        content_line = p.Group(p.lineStart + p.delimitedList(p.Word(p.alphas) | number))

        content = p.OneOrMore(content_line)('content')

        return start_line + content


class PatternBuilder(ResourceBuilder):
    def pattern(self, pattern_name, angle=0, scale=1):
        data = self.get_data(pattern_name)['content']

        code = Codes()

        code.add(78, len(data))

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
            head[3] = (del_x * math.cos(radians) - del_y * math.sin(radians))*scale
            head[4] = (del_y * math.cos(radians) + del_x * math.sin(radians))*scale

            code.add([53, 43, 44, 45, 46], head)
            code.add(79, len(tail))
            code.add([49], [scale*float(item) for item in tail])

        return code


class LTypeBuilder(ResourceBuilder):
    def ltype(self, ltype_name):
        data = self.get_data(ltype_name)
        inform, content = data['inform'], data['content'][0]

        code = Codes()
        code.add(3, inform)
        code.add(72, 5)
        code.add(73, len(content) - 1)
        code.add(40, sum(abs(item) for item in content[1:]))
        for item in content[1:]:
            code.add([49, 74], [item, 0])

        return code
