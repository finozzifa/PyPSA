

## Copyright 2015 Tom Brown (FIAS), Jonas Hoersch (FIAS)

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Python for Power Systems Analysis (PyPSA)

Grid calculation library.
"""


# make the code as Python 3 compatible as possible
from __future__ import print_function, division
from __future__ import absolute_import
from six import iteritems



__version__ = "0.1"
__author__ = "Tom Brown (FIAS), Jonas Hoersch (FIAS)"
__copyright__ = "Copyright 2015 Tom Brown (FIAS), Jonas Hoersch (FIAS), GNU GPL 3"





#weak references are necessary to make sure the key-value pair are
#destroyed if the key object goes out of scope
from weakref import WeakKeyDictionary

from collections import OrderedDict

from distutils.version import StrictVersion

import networkx as nx
assert StrictVersion(nx.__version__) >= '1.10', "NetworkX needs to be at least version 1.10"

import pandas as pd

import inspect

class OrderedGraph(nx.MultiGraph):
    node_dict_factory = OrderedDict
    adjlist_dict_factory = OrderedDict



#Some descriptors to control variables - idea is to do type checking
#and in future facilitate interface with Database / GUI

class Float(object):
    """A descriptor to manage floats."""

    typ = float

    #the name is set by Network.__init__
    name = None

    def __init__(self,default=0.0):
        self.default = default

    def __get__(self,obj,cls):
        return getattr(obj.network,obj.__class__.list_name)[self.name][obj.name]

    def __set__(self,obj,val):
        try:
            getattr(obj.network,obj.__class__.list_name).loc[obj.name,self.name] = self.typ(val)
        except:
            print("could not convert",val,"to a float")


class Integer(object):
    """A descriptor to manage integers."""

    typ = int

    #the name is set by Network.__init__
    name = None

    def __init__(self,default=0):
        self.default = default

    def __get__(self,obj,cls):
        return getattr(obj.network,obj.__class__.list_name)[self.name][obj.name]

    def __set__(self,obj,val):
        try:
            getattr(obj.network,obj.__class__.list_name).loc[obj.name,self.name] = self.typ(val)
        except:
            print("could not convert",val,"to an integer")



class Boolean(object):
    """A descriptor to manage booleans."""

    typ = bool

    #the name is set by Network.__init__
    name = None

    def __init__(self,default=True):
        self.default = default

    def __get__(self,obj,cls):
        return getattr(obj.network,obj.__class__.list_name)[self.name][obj.name]

    def __set__(self,obj,val):
        try:
            getattr(obj.network,obj.__class__.list_name).loc[obj.name,self.name] = self.typ(val)
        except:
            print("could not convert",val,"to a boolean")



class String(object):
    """A descriptor to manage strings."""

    typ = str

    #the name is set by Network.__init__
    name = None

    def __init__(self,default="",restricted=None):
        self.default = default
        self.restricted = restricted

    def __get__(self,obj,cls):
        return getattr(obj.network,obj.__class__.list_name)[self.name][obj.name]

    def __set__(self,obj,val):
        try:
            getattr(obj.network,obj.__class__.list_name).loc[obj.name,self.name] = self.typ(val)
        except:
            print("could not convert",val,"to a string")
            return

        if self.restricted is not None and self.typ(val) not in self.restricted:
            print(val,"not in list of acceptable entries:",self.restricted)




class GraphDesc(object):

    typ = OrderedGraph

    #the name is set by Network.__init__
    name = None

    def __init__(self):
        self.values = WeakKeyDictionary()

    def __get__(self,obj,cls):
        try:
            return self.values[obj]
        except KeyError:
            graph = self.typ()
            self.values[obj] = graph
            return graph

    def __set__(self,obj,val):
        if not isinstance(val, self.typ):
            raise AttributeError("val must be an OrderedGraph")
        else:
            self.values[obj] = val

class Series(object):
    """A descriptor to manage series."""

    typ = pd.Series

    #the name is set by Network.__init__
    name = None

    def __init__(self, dtype=float, default=0.0):
        self.dtype = dtype
        self.default = default
        self.values = WeakKeyDictionary()

    def __get__(self, obj, cls):
        return getattr(getattr(obj.network,obj.__class__.list_name),self.name)[obj.name]

    def __set__(self,obj,val):
        df = getattr(getattr(obj.network,obj.__class__.list_name),self.name)
        #following should work for ints, floats, numpy ints/floats, series and numpy arrays of right size
        try:
            df[obj.name] = self.typ(data=val, index=obj.network.snapshots, dtype=self.dtype)
        except AttributeError:
            print("count not assign",val,"to series")




def get_descriptors(cls,allowed_descriptors=[]):
    d = OrderedDict()

    mro = list(inspect.getmro(cls))

    #make sure get closest descriptor in inheritance tree
    mro.reverse()

    for kls in mro:
        for k,v in iteritems(vars(kls)):
            if type(v) in allowed_descriptors:
                d[k] = v
    return d


simple_descriptors = [Integer, Float, String, Boolean]


def get_simple_descriptors(cls):
    return get_descriptors(cls,simple_descriptors)

def get_series_descriptors(cls):
    return get_descriptors(cls,[Series])