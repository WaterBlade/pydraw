from ..dxfbuilder import Code, Codes


def test_codes_full_initiation():
    c = Codes([Code(0, 'SECTION'), Code(2, 'HEADER')], [Code(0, 'ENDSEC')])
    assert c.to_string() == '0\nSECTION\n2\nHEADER\n0\nENDSEC'


def test_codes_add():
    c = Codes()
    c.add(0, 'hello')
    assert c.to_string() == '0\nhello'


def test_codes_append():
    c = Codes()
    c1 = Codes()
    c.add(0, 'hello')
    c.append(c1)
    c1.add(1, 'world')
    assert c.to_string() == '0\nhello\n1\nworld'
