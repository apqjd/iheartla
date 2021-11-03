from .ir_printer import *
import copy


class CodeFrame(object):
    def __init__(self, parse_type=None, desc='', include='', struct='', rand_data='', main=''):
        self.parse_type = parse_type
        self.desc = desc            # comment for iheartla file
        self.include = include      # headers
        self.struct = struct        # return structure
        self.rand_data = rand_data  # random data
        self.main = main            # main function
        self.expr = ''              # expression content in tex

    def get_code(self):
        content = ''
        if self.parse_type == ParserTypeEnum.EIGEN:
            content = self.desc + self.include + self.struct + '\n\n' + self.rand_data + '\n\n\n' + self.main
        elif self.parse_type == ParserTypeEnum.NUMPY:
            content = self.desc + self.include + self.struct + '\n\n' + self.rand_data + '\n\n\n' + self.main
        elif self.parse_type == ParserTypeEnum.MATLAB:
            content = self.struct  # struct already contains everything
        elif self.parse_type == ParserTypeEnum.LATEX:
            content = self.main
        elif self.parse_type == ParserTypeEnum.MATHJAX:
            content = self.main
        return content

    def get_mathjax_content(self):
        return self.include + self.expr + self.rand_data


class CodeModule(object):
    def __init__(self, frame=None, name='iheartla', syms=[], params=[]):
        self.frame = frame   # code frame
        self.name = name     # module name
        self.syms = syms     # imported symbols
        self.params = params # parameters


class CodeGen(IRPrinter):
    def __init__(self, parse_type=None):
        super().__init__(parse_type=parse_type)
        self.code_frame = CodeFrame(parse_type)

    def visit_code(self, node, **kwargs):
        self.module_list = node.module_list
        self.module_syms = node.module_syms
        self.content = self.pre_str + self.visit(node) + self.post_str
        return copy.deepcopy(self.code_frame)