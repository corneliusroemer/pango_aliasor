from pango_aliasor.aliasor import Aliasor

def test_pango_designation_init():
    aliasor = Aliasor()

def test_uncompression():
    aliasor = Aliasor()
    assert aliasor.uncompress('BA.1') == 'B.1.1.529.1'
    assert aliasor.uncompress('AY.4') == 'B.1.617.2.4'
    assert aliasor.uncompress('AY.4.3.2') == 'B.1.617.2.4.3.2'
    assert aliasor.uncompress('B.1') == 'B.1'

def test_compression():
    aliasor = Aliasor()
    assert aliasor.compress('B.1.1.529.1') == 'BA.1'
    assert aliasor.compress('B.1.617.2.4') == 'AY.4'
    assert aliasor.compress('B.1.617.2.4.3.1') == 'AY.4.3.1'
    assert aliasor.compress('B.1.617.2') == 'B.1.617.2'
    assert aliasor.compress('B.1') == 'B.1'

def test_except_recombinants():
    aliasor = Aliasor()
    assert aliasor.uncompress('XA.1') == 'XA.1'
    assert aliasor.compress('XA.1') == 'XA.1'

def test_double_alias_compression():
    aliasor = Aliasor()
    assert aliasor.compress('B.1.1.529.5.3.1.1') == 'BE.1'

def test_double_alias_uncompression():
    aliasor = Aliasor()
    assert aliasor.uncompress('BE.1') == 'B.1.1.529.5.3.1.1'