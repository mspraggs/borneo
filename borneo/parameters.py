from __future__  import absolute_import

import inspect
from itertools import product
import operator
from lxml import etree
from lxml.etree import _Comment
import xml.dom.minidom as minidom


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


def combine_parameters(parameters1, parameters2):
    """Combine the two supplied parameter lists using a product iteration"""
    out = []
    for params1, params2 in product(parameters1, parameters2):
        params_out = params1.copy()
        params_out.update(params2)
        out.append(params_out)
    return out


def filter_for_func(func, parameters):
    """Filters out the supplied parameter dictionary so that it only contains
    the keys corresponding to func's arguments"""
    try:
        argspec = inspect.getargspec(func)
    except TypeError:
        argspec = inspect.getargspec(func.__call__)
    if argspec.keywords:
        return parameters
    else:
        return dict([(key, value) for key, value in parameters.items()
                     if key in argspec.args])


def parse_etree(etree, path):
    """Parses the supplied ElementTree, looking in the specified path for
    <parameters> tags from which to load dictionaries of parameters"""

    ret = []
    for parameters in etree.iterfind(path):
        params_dict = {}
        if parameters.tag != "parameters":
            continue
        for param_elem in parameters:
            if type(param_elem) is _Comment:
                continue
            text = param_elem.text.strip()
            try:
                params_dict[param_elem.tag] = eval(text)
            except NameError:
                params_dict[param_elem.tag] = text
        ret.append(params_dict)
    return ret


def generate_etree(parameters, root_name):
    """Generate an xml Element using the specified list of parameters"""

    root = etree.Element(root_name)

    for params in parameters:
        node = etree.SubElement(root, 'parameters')
        for key, value in params.items():
            try:
                parameter = etree.SubElement(node, key)
            except TypeError:
                pass
            else:
                parameter.text = str(value)

    return root


def parse_xml(filename, path):
    """Load and parse the supplied xml file to generate a parameter list"""

    tree = etree.parse(filename)
    tree.xinclude()
    root = tree.getroot()
    return parse_etree(root, path)


def write_xml(filename, tree):
    """Write the supplied element/element tree to a file"""

    with open(filename, "w") as f:
        f.write(etree.tostring(tree, pretty_print=True))


def filter_xml(input_filename, input_root, output_filename, output_root,
               *args, **kwargs):
    """Load the parameters from supplied xml file and root (path to element),
    filter them according to args and kwargs, then write them to
    output_filename, in the element specified by output_root"""

    params = parse_xml(input_filename, input_root)
    filtered_params = Query(*args, **kwargs).evaluate(params)
    write_xml(output_filename, generate_etree(filtered_params, output_root))


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
