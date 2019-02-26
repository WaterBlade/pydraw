from pydraw import dxf


if __name__ == '__main__':
    d = dxf.DXF()
    m = d.model_space
    p = d.paper_space
    # arc
    arc = dxf.Arc([50, 50], 25, 0, 180)
    arc.set_layer(d.layer['0'])
    m.append(arc)
    # circle
    circle = dxf.Circle([25, 25], 10)
    circle.set_layer(d.layer['0'])
    m.append(circle)
    # ellipse
    ellipse = dxf.Ellipse([75, 75], [25, 0], 0.5)
    ellipse.set_layer(d.layer['0'])
    m.append(ellipse)
    # part ellipse 1
    ellipse_part = dxf.Ellipse([100, 100], [25, 0], 0.5, 45, 135)
    ellipse_part.set_layer(d.layer['0'])
    m.append(ellipse_part)
    # part ellipse 2
    ellipse_part = dxf.Ellipse([100, 100], [25, 0], 0.5, 135, 205)
    ellipse_part.set_layer(d.layer['0'])
    m.append(ellipse_part)
    # line
    line = dxf.Line([0, 0], [100, 100])
    line.set_layer(d.layer['0'])
    m.append(line)
    # lwpolyline
    lwpolyline = dxf.LWPolyline([[0, 0], [50, 0], [50, 50], [0, 50], [0, 0]], [0.5, 0.5, 0.5, 0.5, 0])
    lwpolyline.set_layer(d.layer['0'])
    m.append(lwpolyline)
    # text
    text = dxf.Text('hello world', [100, 100], 10)
    text.set_layer(d.layer['0'])
    text.set_style(d.style['STANDARD'])
    m.append(text)
    # mtext
    mtext = dxf.MText('hello world'*10, [50, 50], 5, 100)
    mtext.set_layer(d.layer['0'])
    mtext.set_style(d.style['STANDARD'])
    m.append(mtext)
    # arc length dimension
    arc_length_dim = dxf.ArcLengthDimension([50, 50], [0, 0], [25, 25], [50, 25])
    arc_length_dim.set_dimstyle(d.dimstyle['STANDARD'])
    arc_length_dim.set_layer(d.layer['0'])
    m.append(arc_length_dim)
    # diameter dimension
    diameter_dim = dxf.DiametricDimension([0, 0], [100, 100])
    diameter_dim.set_dimstyle(d.dimstyle['STANDARD'])
    diameter_dim.set_layer(d.layer['0'])
    m.append(diameter_dim)
    # line angular dimension
    line_angular_dimension = dxf.LineAngularDimension([50, 50], [0, 50], [80, 90], [0, 50], [100, 0])
    line_angular_dimension.set_dimstyle(d.dimstyle['STANDARD'])
    line_angular_dimension.set_layer(d.layer['0'])
    m.append(line_angular_dimension)
    # point angular dimension
    point_angular_dimension = dxf.PointAngularDimension([100, 100], [0, 0], [50, 0], [0, 50])
    point_angular_dimension.set_dimstyle(d.dimstyle['STANDARD'])
    point_angular_dimension.set_layer(d.layer['0'])
    m.append(point_angular_dimension)
    # radial dimension
    radial_dimension = dxf.RadialDimension([0, 0], [50, 20], 0)
    radial_dimension.set_dimstyle(d.dimstyle['STANDARD'])
    radial_dimension.set_layer(d.layer['0'])
    m.append(radial_dimension)
    # rotated dimension
    rotated_dimension = dxf.RotatedDimension([0, 0], [150, 0], [75, 50], 0)
    rotated_dimension.set_dimstyle(d.dimstyle['STANDARD'])
    rotated_dimension.set_layer(d.layer['0'])
    m.append(rotated_dimension)
    # hatch
    hatch = dxf.Hatch(d.pattern_resource.get_data('ANSI31'),
                      [[100, 100], [120, 100], [120, 120], [100, 120], [100, 100]])
    hatch.set_layer(d.layer['0'])
    m.append(hatch)
    # wipeout
    wipeout = dxf.Wipeout([[105, 100], [115, 100], [115, 110], [105, 100]])
    wipeout.set_layer(d.layer['0'])
    m.append(wipeout)
    # block

    # arc in paper space
    arc = dxf.Arc([50, 50], 25, 0, 180)
    arc.set_layer(d.layer['0'])
    p.append(arc)
    # viewport in paper space
    viewport = dxf.Viewport([50, 50], [100, 100], 50, 50)
    p.append(viewport)

    viewport2 = dxf.Viewport([100, 50], [100, 100], 50, 50)
    p.append(viewport2)

    d.save('demo.dxf')