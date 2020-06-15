from tatsu.model import NodeWalker
from tatsu.objectmodel import Node
from tatsu.symtables import *
from la_parser.la_types import *
from la_parser.type_walker import *
from la_tools.la_visualizer import LaVisualizer
from la_tools.la_logger import *


class ParserTypeEnum(Enum):
    LATEX = 1
    NUMPY = 2
    EIGEN = 3
    MATLAB = 4
    JULIA = 5
    PYTORCH = 6
    ARMADILLO = 7
    TENSORFLOW = 8


class BaseNodeWalker(NodeWalker):
    def __init__(self, parse_type):
        super().__init__()
        self.pre_str = ''
        self.post_str = ''
        self.symtable = {}
        self.def_dict = {}
        self.parameters = set()
        self.subscripts = {}
        self.node_dict = {}
        self.dim_dict = {}
        self.sub_name_dict = {}
        self.ids_dict = {}    # identifiers with subscripts
        self.ret_symbol = None
        self.stat_list = None
        self.visualizer = LaVisualizer()
        self.parse_type = parse_type
        self.logger = LaLogger.getInstance().get_logger(LoggerTypeEnum.DEFAULT)

    def print_symbols(self):
        self.logger.info("symtable:")
        for (k, v) in self.symtable.items():
            dims = ""
            if v.var_type == VarTypeEnum.MATRIX:
                dims = ", rows:{}, cols:{}".format(v.rows, v.cols)
            elif v.var_type == VarTypeEnum.VECTOR:
                dims = ", rows:{}".format(v.rows)
            elif v.var_type == VarTypeEnum.SEQUENCE or v.var_type == VarTypeEnum.SET:
                dims = ", size:{}".format(v.size)
            self.logger.info(k + ':' + str(v.var_type) + dims)
        self.logger.info("parameters:\n" + str(self.parameters))
        self.logger.info("subscripts:\n" + str(self.subscripts))
        self.logger.info("dim_dict:\n" + str(self.dim_dict))
        self.logger.info("sub_name_dict:\n" + str(self.sub_name_dict) + '\n')
        # print("node_dict:\n" + str(self.node_dict) + '\n')

    def walk_model(self, node):
        # self.visualizer.visualize(node)
        type_walker = TypeWalker()
        type_walker.walk(node)
        self.symtable = type_walker.symtable
        for key in self.symtable.keys():
            self.def_dict[key] = False
        self.parameters = type_walker.parameters
        self.subscripts = type_walker.subscripts
        self.node_dict = type_walker.node_dict
        self.dim_dict = type_walker.dim_dict
        self.ids_dict = type_walker.ids_dict
        self.sub_name_dict = type_walker.sub_name_dict
        self.ret_symbol = type_walker.ret_symbol
        self.stat_list = type_walker.stat_list
        self.print_symbols()
        content = self.pre_str + self.walk(node) + self.post_str
        return content

    def walk_Node(self, node):
        print('Reached Node: ', node)

    def walk_str(self, s):
        return s

    def walk_object(self, o):
        raise Exception('Unexpected type %s walked: %s', type(o).__name__, o)
    ###################################################################
    def is_keyword(self, name):
        return False

    def trim_content(self, content):
        # convert special string in identifiers
        res = content
        ids_list = list(self.symtable.keys())
        for ids in self.ids_dict.keys():
            all_ids = self.get_all_ids(ids)
            ids_list += all_ids[1]
        names_dict = []
        for special in ids_list:
            if '`' not in special:
                continue
            new_str = ''.join(e for e in special if e.isalnum() or e is '_')
            if new_str is '' or new_str[0].isnumeric():
                new_str = '_' + new_str
            if new_str is not special:
                while new_str in names_dict or new_str in self.symtable.keys() or self.is_keyword(new_str):
                    new_str = '_' + new_str
                names_dict.append(new_str)
                res = res.replace(special, new_str)
        return res

    def contain_subscript(self, identifier):
        if identifier in self.ids_dict:
            return self.ids_dict[identifier].contain_subscript()
        return False

    def get_all_ids(self, identifier):
        if identifier in self.ids_dict:
            return self.ids_dict[identifier].get_all_ids()
        res = identifier.split('_')
        subs = []
        for index in range(len(res[1])):
            subs.append(res[1][index])
        return [res[0], subs]

    def get_main_id(self, identifier):
        if identifier in self.ids_dict:
            return self.ids_dict[identifier].get_main_id()
        if self.contain_subscript(identifier):
            ret = self.get_all_ids(identifier)
            return ret[0]
        return identifier
