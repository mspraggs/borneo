from __future__  import absolute_import

from itertools import product
import operator
from xml.etree import ElementTree as ET


def _aprx(x, y, rtol, atol):
    """Simple approximate operator"""
    return abs(x - y) <= rtol * abs(y) + atol


def add_sweep(base, **kwargs):
    """Generate a list of dictionaries containing all possible combinations of
    the supplied parameters, using the provided list as a base. Parameters
    should be specified using keywords with either single values or iterables.
    """

    output = []
    for params in base:
        for items in product(*kwargs.values()):
            params_to_add = params.copy()
            params_to_add.update(zip(kwargs.keys(), items))
            output.append(params_to_add)
    return output


def add_spokes(base, **kwargs):
    """Generate a list of dictionaries all based on the supplied base
    dictionaries. Each of the entries in the supplied list of dictionaries are
    varied in turn using the supplied keyword arguments, which themselves should
    be iterables"""

    output = []
    for params in base:
        output.append(params)
        for key, values in kwargs.items():
            for value in values:
                params_copy = params.copy()
                params_copy[key] = value
                output.append(params_copy)
    return output


def parse_etree(etree, path):
    """Parses the supplied ElementTree, looking in the specified path for
    <parameters> tags from which to load dictionaries of parameters"""

    # Handle broken findall on ElementTree if ET.VERSION == 1.3.x
    if path.startswith('/') and ET.VERSION.split('.')[:2] == ['1', '3']:
        path = '.' + path

    ret = []
    for parameters in etree.iterfind(path):
        params_dict = {}
        for param_elem in parameters:
            try:
                params_dict[param_elem.tag] = eval(param_elem.text)
            except NameError:
                params_dict[param_elem.tag] = param_elem.text
        ret.append(params_dict)
    return ret


def generate_etree(parameters, root_name):
    """Generate an xml Element using the specified list of parameters"""

    root = ET.Element(root_name)

    for params in parameters:
        node = ET.SubElement(root, 'parameters')
        for key, value in params.items():
            parameter = ET.SubElement(node, key)
            parameter.text = str(value)

    return root


def parse_xml(filename, path):
    """Load and parse the supplied xml file to generate a parameter list"""

    tree = ET.parse(filename)
    root = tree.getroot()
    return parse_etree(root, path)


class Query(object):
    """Parameter filtering class using tree/node structure"""

    comparison_map = {'gt': operator.gt,
                      'gte': operator.ge,
                      'lt': operator.lt,
                      'lte': operator.le,
                      'aprx': lambda x, y: _aprx(x, y, 1e-5, 1e-8)}

    def __init__(self, *args, **kwargs):
        """Query Constructor"""
        self.children = []
        for arg in args:
            if not isinstance(arg, type(arg)):
                raise TypeError("Invalid argument {} to with type {} passed "
                                "to {} constructor".format(arg, type(arg),
                                                           self.__class__
                                                           .__name__))
            self.children.append(arg)

        for key, value in kwargs.items():
            key_split = key.split('__')
            child = type(self)()
            op = (
                self.comparison_map[key_split[-1]]
                if len(key_split) > 1 else operator.eq
            )
            child._set_filter(op, key_split[0], value)
            self.children.append(child)

        self.connector = operator.and_
        self.filter_func = None
        self.negate = False

    def _set_filter(self, func, parameter_name, parameter_value):
        """Specify a filter function that returns True or False for a given
        parameter value"""
        self.filter_func = lambda d: func(d[parameter_name], parameter_value)

    def _recurse(self, parameters):
        """Recursively call _recurse on children to build up a list of True
        and False statements"""

        if self.filter_func:
            results = map(self.filter_func, parameters)
        else:
            if self.children:
                results = [child._recurse(parameters)
                           for child in self.children]
                results = [reduce(self.connector, result)
                           for result in zip(*results)]
            else:
                results = [True] * len(parameters)
        return [not result if self.negate else result for result in results]

    def evaluate(self, parameters):
        """Evaluate which parameters we're keeping and which we're discarding,
        returning the list of parameter combinations that we do want to keep"""

        results = self._recurse(parameters)
        return [params for keep, params in zip(results, parameters) if keep]

    def __and__(self, other):
        """And operator"""
        out = type(self)(self, other)
        out.connector = operator.and_
        return out

    def __or__(self, other):
        """Or operator"""
        out = type(self)(self, other)
        out.connector = operator.or_
        return out

    def __invert__(self):
        """Not operator"""
        ret = type(self)(*self.children)
        ret.negate = not self.negate
        return ret
