from __future__ import absolute_import
from __future__ import unicode_literals

import xml.etree.ElementTree as ET

import pytest

from borneo.parameters import (Query, generate_etree, add_sweep, add_spokes,
                               parse_etree)


@pytest.fixture
def xml_params():

    root = ET.Element('root')

    for a, b in [(x, y) for x in range(10) for y in range(10)]:
        parameter_set = ET.SubElement(root, "parameters")
        elem_a = ET.SubElement(parameter_set, "a")
        elem_a.text = str(a)
        elem_b = ET.SubElement(parameter_set, 'b')
        elem_b.text = str(b)

    return root


@pytest.fixture
def random_parameters():
    return [{'a': a, 'b': b, 'c': c}
            for a in range(10) for b in range(10, 30) for c in ['foo', 'bar']]


def test_add_sweep():
    """Test the global sweep parameter set generation function"""
    parameters = add_sweep([{}], a=range(5), b=range(10), c=["tree", "car"])
    assert len(parameters) == 100
    for params in [dict(a=a, b=b, c=c) for a in range(5) for b in range(10)
                   for c in ["tree", "car"]]:
        assert params in parameters


def test_add_spokes():
    """Test the hub and spokes parameter set generation function"""
    parameters = add_spokes([{'a': 1, 'b': 2, 'c': 'foo'}],
                            a=range(2, 10), b=range(3, 5),
                            c=['tree', 'bush'])
    assert len(parameters) == 13
    assert {'a': 1, 'b': 2, 'c': 'foo'} in parameters
    for a in range(2, 10):
        assert {'a': a, 'b': 2, 'c': 'foo'} in parameters
    for b in range(3, 5):
        assert {'a': 1, 'b': b, 'c': 'foo'} in parameters
    for c in ['tree', 'bush']:
        assert {'a': 1, 'b': 2, 'c': c} in parameters


def test_parse_etree(xml_params):
    """Test xml parsing of parameters"""

    parameters = parse_etree(xml_params, '/')
    expected_params = [{'a': a, 'b': b}
                       for a in range(5) for b in range(10)]

    for params, expect_params in zip(parameters, expected_params):
        assert params == expect_params


def test_generate_etree(xml_params):
    """Test xml generation of parameter lists"""

    params = [{'a': a, 'b': b} for a in range(10) for b in range(10)]
    etree = generate_etree(params, 'root')
    assert len(etree.getchildren()) == len(xml_params.getchildren())
    assert ET.tostring(etree) == ET.tostring(xml_params)


class TestQuery(object):

    def test_init(self):
        """Test the constructor"""
        q = Query(a=1, b=3)
        assert len(q.children) == 2
        assert hasattr(q, 'connector')
        assert q.negate is False
        assert q.filter_func is None
        for child in q.children:
            assert isinstance(child, Query)

    def test_set_filter(self):
        """Test the _set_filter function"""
        q = Query()
        q._set_filter(lambda x, y: x > y, 'foo', 2)
        assert q.filter_func({'foo': 4})
        assert not q.filter_func({'foo': 2})

    def test_evaluate(self, random_parameters):
        """Test the evaluation of the query on a parameter set"""

        q = Query()
        results = q.evaluate(random_parameters)
        assert results == random_parameters

        q = Query(a=1, b=10)
        results = q.evaluate(random_parameters)
        assert len(results) == 2
        for result in results:
            assert result['a'] == 1
            assert result['b'] == 10

        q = Query(a=1, b__gte=20)
        results = q.evaluate(random_parameters)
        assert len(results) == 20
        for result in results:
            assert result['a'] == 1
            assert result['b'] >= 10

        q = Query(a=1) | Query(b__gte=20)
        results = q.evaluate(random_parameters)
        assert len(results) == 220
        for result in results:
            assert result['a'] == 1 or result['b'] >= 20

        q2 = q & Query(c='foo')
        results = q2.evaluate(random_parameters)
        assert len(results) == 110
        for result in results:
            assert (
                (result['a'] == 1 or result['b'] >= 20) and result['c'] == 'foo'
            )

        q = ~Query(a=1)
        results = q.evaluate(random_parameters)
        assert len(results) == 360
        for result in results:
            assert not result['a'] == 1