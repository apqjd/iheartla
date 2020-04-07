from la_parser.base_walker import *


class NumpyWalker(BaseNodeWalker):
    def __init__(self):
        super().__init__()
        self.pre_str = '''import numpy as np\n\n\n'''
        self.post_str = ''''''
        self.ret = 'ret'

    def walk_Start(self, node, **kwargs):
        pars = []
        type_checks = []
        type_declare = []
        show_doc = False
        doc = []
        for parameter in self.parameters:
            par = parameter
            if self.symtable[parameter].desc:
                show_doc = True
                doc.append('    :param :{} :{}'.format(parameter, self.symtable[parameter].desc))
            if self.symtable[parameter].var_type == VarTypeEnum.SEQUENCE:
                ele_type = self.symtable[parameter].element_type
                data_type = ele_type.element_type
                if isinstance(data_type, LaVarType):
                    if data_type.var_type == VarTypeEnum.INTEGER:
                        type_declare.append('    {} = np.asarray({}, dtype=np.integer)'.format(parameter, parameter))
                    elif data_type.var_type == VarTypeEnum.REAL:
                        type_declare.append('    {} = np.asarray({}, dtype=np.floating)'.format(parameter, parameter))
                else:
                    type_declare.append('    {} = np.asarray({})'.format(parameter, parameter))
                if ele_type.var_type == VarTypeEnum.MATRIX:
                    type_checks.append('    assert {}.shape == ({}, {}, {})'.format(parameter, self.symtable[parameter].dimensions[0], ele_type.dimensions[0], ele_type.dimensions[1]))
                elif ele_type.var_type == VarTypeEnum.VECTOR:
                    type_checks.append('    assert {}.shape == ({}, {})'.format(parameter, self.symtable[parameter].dimensions[0], ele_type.dimensions[0]))
                elif ele_type.var_type == VarTypeEnum.SCALAR:
                    type_checks.append('    assert {}.shape == ({},)'.format(parameter, self.symtable[parameter].dimensions[0]))
            elif self.symtable[parameter].var_type == VarTypeEnum.MATRIX:
                element_type = self.symtable[parameter].element_type
                if isinstance(element_type, LaVarType):
                    if element_type.var_type == VarTypeEnum.INTEGER:
                        type_declare.append('    {} = np.asarray({}, dtype=np.integer)'.format(parameter, parameter))
                    elif element_type.var_type == VarTypeEnum.REAL:
                        type_declare.append('    {} = np.asarray({}, dtype=np.floating)'.format(parameter, parameter))
                else:
                    type_checks.append('    {} = np.asarray({})'.format(parameter, parameter))
                type_checks.append('    assert {}.shape == ({}, {})'.format(parameter, self.symtable[parameter].dimensions[0], self.symtable[parameter].dimensions[1]))
            elif self.symtable[parameter].var_type == VarTypeEnum.VECTOR:
                element_type = self.symtable[parameter].element_type
                if isinstance(element_type, LaVarType):
                    if element_type.var_type == VarTypeEnum.INTEGER:
                        type_declare.append('    {} = np.asarray({}, dtype=np.integer)'.format(parameter, parameter))
                    elif element_type.var_type == VarTypeEnum.REAL:
                        type_declare.append('    {} = np.asarray({}, dtype=np.floating)'.format(parameter, parameter))
                else:
                    type_declare.append('    {} = np.asarray({})'.format(parameter, parameter))
                type_checks.append('    assert {}.shape == ({},)'.format(parameter, self.symtable[parameter].dimensions[0]))
            elif self.symtable[parameter].var_type == VarTypeEnum.SCALAR:
                type_checks.append('    assert np.ndim({}) == 0'.format(parameter))
            pars.append(par)

        content = 'def myExpression(' + ', '.join(pars) + '):\n'
        if show_doc:
            content += '    \"\"\"\n' + '\n'.join(doc) + '\n    \"\"\"\n'
        dim_content = ""
        if self.dim_dict:
            for key, value in self.dim_dict.items():
                if self.contain_subscript(value[0]):
                    main_id = self.get_main_id(value[0])
                    dim_content += "    {} = {}.shape[{}]\n".format(key, main_id, value[1]+1)
                else:
                    dim_content += "    {} = {}.shape[{}]\n".format(key, value[0], value[1])
        # merge content
        content += '\n'.join(type_declare) + '\n\n'
        content += dim_content
        content += '\n'.join(type_checks) + '\n\n'
        # statements
        stat_info = self.walk(node.stat)
        content += stat_info.content
        content += '    return ' + self.ret
        content += '\n'
        return content

    def walk_WhereConditions(self, node, **kwargs):
        pass

    def walk_Statements(self, node, **kwargs):
        index = 0
        content = ''
        for stat in node.value:
            if type(stat).__name__ == 'Statements':
                stat_info = self.walk(stat, **kwargs)
                content += stat_info.content
            else:
                ret_str = ''
                content += ''
                if index == len(node.value) - 1:
                    if type(stat).__name__ != 'Assignment':
                        self.ret = 'ret'
                        ret_str = "    " + self.ret + ' = '
                stat_info = self.walk(stat, **kwargs)
                stat_value = stat_info.content
                if isinstance(stat_info, CodeNodeInfo):
                    if stat_info.pre_list:
                        content += "".join(stat_info.pre_list)
                    content += ret_str + stat_info.content + '\n'
                else:
                    content += stat_value + '\n'
            index += 1
        return CodeNodeInfo(content)

    def walk_Summation(self, node, **kwargs):
        type_info = self.node_dict[node]
        assign_id = type_info.symbol
        if la_need_ret_vars(**kwargs):
            return self.walk(node.exp, **kwargs)
        subs = []
        for sub in node.sub:
            sub_info = self.walk(sub)
            subs.append(sub_info.content)
        kwargs[WALK_TYPE] = WalkTypeEnum.RETRIEVE_VAR
        exp_info = self.walk(node.exp, **kwargs)
        vars = exp_info.content
        kwargs[WALK_TYPE] = WalkTypeEnum.RETRIEVE_EXPRESSION
        content = []
        target_var = []
        exp_info = self.walk(node.exp)
        exp_str = exp_info.content
        for sub in subs:
            for var in vars:
                if self.contain_subscript(var):
                    var_ids = self.get_all_ids(var)
                    var_subs = var_ids[1]
                    for var_sub in var_subs:
                        if sub == var_sub:
                            target_var.append(var_ids[0])
            if self.symtable[assign_id].var_type == VarTypeEnum.MATRIX:
                content.append("    {} = np.zeros(({}, {}))\n".format(assign_id, self.symtable[assign_id].dimensions[0], self.symtable[assign_id].dimensions[1]))
            elif self.symtable[assign_id].var_type == VarTypeEnum.VECTOR:
                content.append("    {} = np.zeros({})\n".format(assign_id, self.symtable[assign_id].dimensions[0]))
            content.append("for {} in range(len({})):\n".format(sub, target_var[0]))
            for var in target_var:
                old = "{}_{}".format(var, sub)
                new = "{}[{}]".format(var, sub)
                exp_str = exp_str.replace(old, new)
            # only one sub for now
            # content += "    for {} in range(len({})):\n".format(sub, target_var)
            content.append(str("    " + assign_id + " += " + exp_str + '\n\n'))
        return CodeNodeInfo(assign_id, pre_list=["    ".join(content)])

    def walk_Determinant(self, node, **kwargs):
        if la_need_ret_vars(**kwargs):
            return self.walk(node.value, **kwargs)
        value_info = self.walk(node.value)
        value = value_info.content
        type_info = self.node_dict[node.value]
        if type_info.la_type.var_type == VarTypeEnum.VECTOR or type_info.la_type.var_type == VarTypeEnum.MATRIX or type_info.la_type.var_type == VarTypeEnum.SEQUENCE:
            if value in self.parameters:
                value_type = self.symtable[value]
                return CodeNodeInfo(str(value_type.dimensions[0]))
            elif value in self.symtable:
                return CodeNodeInfo(value + '.shape[0]')
            return CodeNodeInfo('(' + value + ').shape[0]')
        return CodeNodeInfo('np.absolute(' + value + ')')

    def walk_Matrix(self, node, **kwargs):
        content = "    "
        # lhs = kwargs[LHS]
        type_info = self.node_dict[node]
        cur_m_id = type_info.symbol
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo(set())
        elif la_need_ret_matrix(**kwargs):
            kwargs["cur_id"] = cur_m_id
            content += '{} = np.zeros(({}, {}))\n'.format(cur_m_id, self.symtable[cur_m_id].dimensions[0],
                                                         self.symtable[cur_m_id].dimensions[1])
            ret_info = self.walk(node.value, **kwargs)
            ret = ret_info.content
            for i in range(len(ret)):
                content += "    {}[{}] = [{}]\n".format(cur_m_id, i, ret[i])
            self.matrix_index += 1
            return CodeNodeInfo(content)
        self.matrix_index += 1
        return CodeNodeInfo(cur_m_id)

    def walk_MatrixRows(self, node, **kwargs):
        content = ""
        lhs = kwargs[LHS]
        cur_m_id = kwargs["cur_id"]
        rows = self.symtable[cur_m_id].dimensions[0]
        cols = self.symtable[cur_m_id].dimensions[1]
        ret = []
        if node.rs:
            rs_info = self.walk(node.rs, **kwargs)
            ret = ret + rs_info.content
        if node.r:
            r_info = self.walk(node.r, **kwargs)
            ret.append(r_info.content)
        return CodeNodeInfo(ret)

    def walk_MatrixRow(self, node, **kwargs):
        ret = []
        if node.rc:
            rc_info = self.walk(node.rc, **kwargs)
            ret.append(rc_info.content)
        if node.exp:
            exp_info = self.walk(node.exp, **kwargs)
            ret.append(exp_info.content)
        return CodeNodeInfo(', '.join(ret))

    def walk_MatrixRowCommas(self, node, **kwargs):
        ret = []
        if node.value:
            value_info = self.walk(node.value, **kwargs)
            ret.append(value_info.content)
        if node.exp:
            exp_info = self.walk(node.exp, **kwargs)
            ret.append(exp_info.content)
        return CodeNodeInfo(', '.join(ret))

    def walk_ExpInMatrix(self, node, **kwargs):
        return self.walk(node.value, **kwargs)

    def walk_Add(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        left_set = left_info.content
        right_info = self.walk(node.right, **kwargs)
        right_set = right_info.content
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo(left_set.union(right_set))
        elif la_need_ret_matrix(**kwargs):
            left_info.content += right_info.content
            return left_info
        left_info.content = left_info.content + ' + ' + right_info.content
        return left_info

    def walk_Subtract(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        left_set = left_info.content
        right_info = self.walk(node.right, **kwargs)
        right_set = right_info.content
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo(left_set.union(right_set))
        elif la_need_ret_matrix(**kwargs):
            left_info.content += right_info.content
            return left_info
        left_info.content = left_info.content + ' - ' + right_info.content
        return left_info

    def walk_Multiply(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        left_set = left_info.content
        right_info = self.walk(node.right, **kwargs)
        right_set = right_info.content
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo(left_set.union(right_set))
        elif la_need_ret_matrix(**kwargs):
            left_info.content += right_info.content
            return left_info
        l_info = self.node_dict[node.left]
        r_info = self.node_dict[node.right]
        mul = ' * '
        if l_info.la_type.var_type == VarTypeEnum.MATRIX or l_info.la_type.var_type == VarTypeEnum.VECTOR:
            if r_info.la_type.var_type == VarTypeEnum.MATRIX or r_info.la_type.var_type == VarTypeEnum.VECTOR:
                mul = ' @ '
        left_info.content = left_info.content + mul + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_Divide(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        left_set = left_info.content
        right_info = self.walk(node.right, **kwargs)
        right_set = right_info.content
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo(left_set.union(right_set))
        elif la_need_ret_matrix(**kwargs):
            left_info.content += right_info.content
            return left_info
        left_info.content = left_info.content + ' / ' + right_info.content
        return left_info

    def walk_Assignment(self, node, **kwargs):
        if la_need_ret_vars(**kwargs):
            left_info = self.walk(node.left, **kwargs)
            left_set = left_info.content
            right_info = self.walk(node.right, **kwargs)
            right_set = right_info.content
            return CodeNodeInfo(left_set.union(right_set))
        # walk matrix first
        content = ""
        matrix_exp = []
        left_info = self.walk(node.left, **kwargs)
        left_id = left_info.content
        kwargs[LHS] = left_id
        self.matrix_index = 0
        if left_id in self.m_dict:
            kwargs[WALK_TYPE] = WalkTypeEnum.RETRIEVE_MATRIX_STAT
            right_info = self.walk(node.right, **kwargs)
            content += right_info.content
            kwargs[WALK_TYPE] = WalkTypeEnum.RETRIEVE_EXPRESSION
        self.ret = self.get_main_id(left_id)
        self.matrix_index = 0
        #
        kwargs[WALK_TYPE] = WalkTypeEnum.RETRIEVE_VAR
        exp_info = self.walk(node.right, **kwargs)
        kwargs[WALK_TYPE] = WalkTypeEnum.RETRIEVE_EXPRESSION
        # self left-hand-side symbol
        content += "    ".join(matrix_exp)
        if self.symtable[left_id].var_type == VarTypeEnum.MATRIX:
            pass
            # content += '    {} = np.zeros(({},{}))\n'.format(left_id, self.symtable[left_id].dimensions[0], self.symtable[left_id].dimensions[1])
        elif self.symtable[left_id].var_type == VarTypeEnum.VECTOR:
            pass
            # content += '    {} = np.zeros(({}))\n'.format(left_id, self.symtable[left_id].dimensions[0])
        right_info = self.walk(node.right, **kwargs)
        right_value = right_info.content
        right_exp = ""
        if right_info.pre_list:
            right_exp += "".join(right_info.pre_list)
        # y_i = stat
        if self.contain_subscript(left_id):
            left_ids = self.get_all_ids(left_id)
            left_subs = left_ids[1]
            sequence = left_ids[0]  # y left_subs[0]
            # replace sequence
            for right_var in exp_info.content:
                if self.contain_subscript(right_var):
                    var_ids = self.get_all_ids(right_var)
                    right_info.content = right_info.content.replace(right_var, "{}[{}]".format(var_ids[0], var_ids[1][0]))

            right_exp += "    {}[{}] = {}".format(self.get_main_id(left_id), left_subs[0], right_info.content)
            ele_type = self.symtable[sequence].element_type
            if ele_type.var_type == VarTypeEnum.MATRIX:
                content += "    {} = np.zeros(({}, {}, {}))\n".format(sequence, self.symtable[sequence].dimensions[0], ele_type.dimensions[0], ele_type.dimensions[1])
            elif ele_type.var_type == VarTypeEnum.VECTOR:
                content += "    {} = np.zeros(({}, {}))\n".format(sequence, self.symtable[sequence].dimensions[0], ele_type.dimensions[0])
            else:
                content += "    {} = np.zeros({})\n".format(sequence, self.symtable[sequence].dimensions[0])
            content += "    for {} in range({}):\n".format(left_subs[0], self.symtable[sequence].dimensions[0])
            content += "    " + right_exp
            content += '\n'
        #
        else:
            right_exp += '    ' + self.get_main_id(left_id) + ' = ' + right_info.content
            content += right_exp
        la_remove_key(LHS, **kwargs)
        return CodeNodeInfo(content)

    def walk_IdentifierSubscript(self, node, **kwargs):
        right = []
        for value in node.right:
            value_info = self.walk(value)
            right.append(value_info.content)
        if la_need_ret_vars(**kwargs):
            left_info = self.walk(node.left)
            return CodeNodeInfo({left_info.content + '_' + ','.join(right)})
        elif la_need_ret_matrix(**kwargs):
            return CodeNodeInfo("")
        left_info = self.walk(node.left)
        content = left_info.content + '_' + ','.join(right)
        return CodeNodeInfo(content)

    def walk_IdentifierAlone(self, node, **kwargs):
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo({node.value})
        elif la_need_ret_matrix(**kwargs):
            return CodeNodeInfo("")
        return CodeNodeInfo(node.value)

    def walk_Derivative(self, node, **kwargs):
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo({})
        return CodeNodeInfo("")

    def walk_Factor(self, node, **kwargs):
        if node.id:
            return self.walk(node.id, **kwargs)
        elif node.num:
            return self.walk(node.num, **kwargs)
        elif node.sub:
            return self.walk(node.sub, **kwargs)
        elif node.m:
            return self.walk(node.m, **kwargs)
        elif node.f:
            return self.walk(node.f, **kwargs)
        elif node.op:
            return self.walk(node.op, **kwargs)

    def walk_Number(self, node, **kwargs):
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo(set())
        return self.walk(node.value, **kwargs)

    def walk_Integer(self, node, **kwargs):
        if la_need_ret_vars(**kwargs):
            return CodeNodeInfo({})
        content = ''.join(node.value)
        return CodeNodeInfo(content)

    ###################################################################
    def merge_pre_list(self, left_info, right_info):
        ret = left_info.pre_list
        if right_info.pre_list is not None:
            if ret is None:
                ret = right_info.pre_list
            else:
                ret = ret + right_info.pre_list
        return ret

