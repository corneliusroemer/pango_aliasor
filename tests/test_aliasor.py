from __future__ import unicode_literals

import os
from distutils import dir_util

from pango_aliasor.aliasor import Aliasor
from pytest import fixture


@fixture
def datadir(tmpdir, request):
    '''
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    '''
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir,str(tmpdir))

    return tmpdir

def test_pango_designation_init():
    aliasor = Aliasor()

def test_uncompression():
    aliasor = Aliasor()
    assert aliasor.uncompress('BA.1') == 'B.1.1.529.1'
    assert aliasor.uncompress('AY.4') == 'B.1.617.2.4'
    assert aliasor.uncompress('AY.4.3.2') == 'B.1.617.2.4.3.2'
    assert aliasor.uncompress('B.1') == 'B.1'
    assert aliasor.uncompress('B') == 'B'
    assert aliasor.uncompress('') == ''

def test_compression():
    aliasor = Aliasor()
    assert aliasor.compress('B.1.1.529.1') == 'BA.1'
    assert aliasor.compress('B.1.617.2.4') == 'AY.4'
    assert aliasor.compress('B.1.617.2.4.3.1') == 'AY.4.3.1'
    assert aliasor.compress('B.1.617.2') == 'B.1.617.2'
    assert aliasor.compress('B.1') == 'B.1'
    assert aliasor.compress('B') == 'B'
    assert aliasor.compress('') == ''

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

def test_read_from_file(datadir):
    aliasor = Aliasor(datadir.join('alias_key.json'))
    assert aliasor.compress('B.1.1.529.1') == 'BA.1'

def test_partial_alias_up_to():
    aliasor = Aliasor()
    assert aliasor.partial_compress('B.1.1.529.1.2', up_to = 0) == 'B.1.1.529.1.2'
    assert aliasor.partial_compress('B.1.1.529.2.75.1.2', up_to = 1) == 'BA.2.75.1.2'
    assert aliasor.partial_compress('B.1.1.529.2.75.1.2', up_to = 2) == 'BL.2'

def test_partial_alias_accepted():
    aliasor = Aliasor()
    assert aliasor.partial_compress('B.1.1.529.1.2', accepted_aliases={"BA","AZ"}) == "BA.1.2"
    assert aliasor.partial_compress('B.1.617.2.3', accepted_aliases={"BA","AZ"}) == "B.1.617.2.3"
    assert aliasor.partial_compress('B.1.1.529.2.75.1.2', accepted_aliases={"BA"}) == 'BA.2.75.1.2'

def test_partial_alias_combination():
    aliasor = Aliasor()
    assert aliasor.partial_compress('B.1.1.529.1.2',up_to=1, accepted_aliases={"BA","AZ"}) == "BA.1.2"
    assert aliasor.partial_compress('B.1.617.2.3',up_to=1, accepted_aliases={"BA","AZ"}) == "AY.3"
    assert aliasor.partial_compress('B.1.1.529.2.75.1.2',up_to=3, accepted_aliases={"BA"}) == 'BL.2'
    assert aliasor.partial_compress('B.1.1.529.2.75.1.2',up_to=4, accepted_aliases={"BA"}) == 'BL.2'
    assert aliasor.partial_compress('B.1.1.529.2.75.1.2',up_to=1, accepted_aliases={"BA"}) == 'BA.2.75.1.2'

def test_collapse():
    aliasor = Aliasor()
    assert aliasor.collapse('B.1.1.529.3.1', potential_parents=['BA.3']) == 'BA.3'
    assert aliasor.collapse('B.1.1.529.3.1', potential_parents=['BA.3', 'BA.3.1']) == 'BA.3.1'
    assert aliasor.collapse('B.1.1.529.3.1', potential_parents=['B.1.1', 'BZ.1', 'AY.4']) == 'B.1.1'
    assert aliasor.collapse('B.1.1.529.3.1', potential_parents=['A']) == 'B.1.1.529.3.1'
    assert aliasor.collapse('XA.1', potential_parents=['B.1.1', 'BZ.1', 'AY.4']) == 'XA.1'