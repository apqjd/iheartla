from enum import Enum


class VarTypeEnum(Enum):
    INVALID = 0
    # LA types
    SEQUENCE = 1
    MATRIX = 2
    VECTOR = 3
    SET = 4
    SCALAR = 5
    #
    INTEGER = 6
    REAL = 7


class LaVarType(object):
    def __init__(self, var_type, desc=None, element_type=None):
        super().__init__()
        self.var_type = var_type
        self.desc = desc   # only parameters need description
        self.element_type = element_type

    def is_dim_constant(self):
        constant = False
        if self.var_type == VarTypeEnum.SEQUENCE:
            if isinstance(self.size, int):
                constant = True
        elif self.var_type == VarTypeEnum.MATRIX:
            if isinstance(self.rows, int) and isinstance(self.cols, int):
                constant = True
        elif self.var_type == VarTypeEnum.VECTOR:
            if isinstance(self.rows, int):
                constant = True
        else:
            constant = True
        return constant


class SequenceType(LaVarType):
    def __init__(self, size=0, desc=None, element_type=None):
        LaVarType.__init__(self, VarTypeEnum.SEQUENCE, desc, element_type)
        self.size = size


class MatrixType(LaVarType):
    def __init__(self, rows=0, cols=0, desc=None, element_type=None, need_exp=False, diagonal=False, sparse=False, block=False, subs=[], list_dim=None, index_var=None, value_var=None):
        LaVarType.__init__(self, VarTypeEnum.MATRIX, desc, element_type)
        self.rows = rows
        self.cols = cols
        # attributes
        self.need_exp = need_exp    # need expression
        self.diagonal = diagonal
        self.subs = subs
        # block matrix
        self.block = block
        self.list_dim = list_dim    # used by block mat
        # sparse matrix
        self.sparse = sparse
        self.index_var = index_var  # used by sparse mat
        self.value_var = value_var  # used by sparse mat


class VectorType(LaVarType):
    def __init__(self, rows=0, desc=None, element_type=None):
        LaVarType.__init__(self, VarTypeEnum.VECTOR, desc, element_type)
        self.rows = rows


class SetType(LaVarType):
    def __init__(self, size=0, desc=None, element_type=None, int_list=None):
        LaVarType.__init__(self, VarTypeEnum.SET, desc, element_type)
        self.size = size
        self.int_list = int_list     # whether the element is real number or integer


class SummationAttrs(object):
    def __init__(self, subs=None, var_list=None):
        super().__init__()
        self.subs = subs
        self.var_list = var_list


class NodeInfo(object):
    def __init__(self, la_type=None, content=None, symbols=set()):
        super().__init__()
        self.la_type = la_type
        self.content = content
        self.symbols = symbols  # symbols covered by the node


class CodeNodeInfo(object):
    def __init__(self, content=None, pre_list=[]):
        super().__init__()
        self.content = content
        self.pre_list = pre_list
