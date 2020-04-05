from enum import Enum


class VarTypeEnum(Enum):
    INVALID = 0
    SEQUENCE = 1
    MATRIX = 2
    VECTOR = 3
    SCALAR = 4
    INTEGER = 5
    REAL = 6


class MatrixAttrEnum(Enum):
    SYMMETRIC = 1
    DIAGONAL = 2


class LaVarType(object):
    def __init__(self, var_type, dimensions=0, desc=None, attrs=None, element_type=None, element_subscript=[]):
        super().__init__()
        self.var_type = var_type
        self.dimensions = dimensions
        self.desc = desc
        self.attrs = attrs
        self.element_type = element_type
        self.element_subscript = element_subscript


class MatrixAttrs(object):
    def __init__(self, need_exp=False, diagonal=False, sparse=False):
        super().__init__()
        self.need_exp = need_exp  # need expression
        self.diagonal = diagonal
        self.sparse = sparse


class NodeInfo(object):
    def __init__(self, la_type=None, symbol=None, content=None, pre_str=None):
        super().__init__()
        self.content = content
        self.la_type = la_type
        self.symbol = symbol
        self.pre_str = pre_str
