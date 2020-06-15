from la_parser.base_walker import *
import keyword


class NumpyWalker(BaseNodeWalker):
    def __init__(self):
        super().__init__(ParserTypeEnum.LATEX)
        self.pre_str = '''import numpy as np\nimport scipy\nfrom scipy import sparse\n\n\n'''
        self.post_str = ''''''

    def walk_Start(self, node, **kwargs):
        type_checks = []
        type_declare = []
        doc = []
        show_doc = False
        func_name = "myExpression"
        rand_func_name = "generateRandomData"
        test_content = ["def " + rand_func_name + "():"]
        rand_int_max = 10
        main_content = ["if __name__ == '__main__':",
                        "    {} = {}()".format(', '.join(self.parameters), rand_func_name)]
        dim_content = ""
        if self.dim_dict:
            for key, value in self.dim_dict.items():
                test_content.append("    {} = np.random.randint({})".format(key, rand_int_max))
                if self.contain_subscript(value[0]):
                    main_id = self.get_main_id(value[0])
                    dim_content += "    {} = {}.shape[{}]\n".format(key, main_id, value[1]+1)
                else:
                    dim_content += "    {} = {}.shape[{}]\n".format(key, value[0], value[1])
        for parameter in self.parameters:
            if self.symtable[parameter].desc:
                show_doc = True
                doc.append('    :param :{} :{}'.format(parameter, self.symtable[parameter].desc))
            if self.symtable[parameter].var_type == VarTypeEnum.SEQUENCE:
                ele_type = self.symtable[parameter].element_type
                data_type = ele_type.element_type
                size_str = ""
                if ele_type.var_type == VarTypeEnum.MATRIX:
                    type_checks.append('    assert {}.shape == ({}, {}, {})'.format(parameter, self.symtable[parameter].size, ele_type.rows, ele_type.cols))
                    size_str = '{}, {}, {}'.format(self.symtable[parameter].size, ele_type.rows, ele_type.cols)
                elif ele_type.var_type == VarTypeEnum.VECTOR:
                    type_checks.append('    assert {}.shape == ({}, {})'.format(parameter, self.symtable[parameter].size, ele_type.rows))
                    size_str = '{}, {}'.format(self.symtable[parameter].size, ele_type.rows)
                elif ele_type.var_type == VarTypeEnum.SCALAR:
                    type_checks.append('    assert {}.shape == ({},)'.format(parameter, self.symtable[parameter].size))
                    size_str = '{}'.format(self.symtable[parameter].size)
                if isinstance(data_type, LaVarType):
                    if data_type.var_type == VarTypeEnum.INTEGER:
                        type_declare.append('    {} = np.asarray({}, dtype=np.integer)'.format(parameter, parameter))
                        test_content.append('    {} = np.random.randint({}, size=({}))'.format(parameter, rand_int_max, size_str))
                    elif data_type.var_type == VarTypeEnum.REAL:
                        type_declare.append('    {} = np.asarray({}, dtype=np.floating)'.format(parameter, parameter))
                        test_content.append('    {} = np.random.randn({})'.format(parameter, size_str))
                else:
                    type_declare.append('    {} = np.asarray({})'.format(parameter, parameter))
                    test_content.append('    {} = np.random.randn({})'.format(parameter, size_str))
            elif self.symtable[parameter].var_type == VarTypeEnum.MATRIX:
                element_type = self.symtable[parameter].element_type
                if isinstance(element_type, LaVarType):
                    if element_type.var_type == VarTypeEnum.INTEGER:
                        type_declare.append('    {} = np.asarray({}, dtype=np.integer)'.format(parameter, parameter))
                        test_content.append('    {} = np.random.randint({}, size=({}, {}))'.format(parameter, rand_int_max, self.symtable[parameter].rows, self.symtable[parameter].cols))
                    elif element_type.var_type == VarTypeEnum.REAL:
                        type_declare.append('    {} = np.asarray({}, dtype=np.floating)'.format(parameter, parameter))
                        test_content.append('    {} = np.random.randn({}, {})'.format(parameter, self.symtable[parameter].rows, self.symtable[parameter].cols))
                else:
                    type_checks.append('    {} = np.asarray({})'.format(parameter, parameter))
                    test_content.append('    {} = np.random.randn({}, {})'.format(parameter, self.symtable[parameter].rows, self.symtable[parameter].cols))
                type_checks.append('    assert {}.shape == ({}, {})'.format(parameter, self.symtable[parameter].rows, self.symtable[parameter].cols))
            elif self.symtable[parameter].var_type == VarTypeEnum.VECTOR:
                element_type = self.symtable[parameter].element_type
                if isinstance(element_type, LaVarType):
                    if element_type.var_type == VarTypeEnum.INTEGER:
                        type_declare.append('    {} = np.asarray({}, dtype=np.integer)'.format(parameter, parameter))
                        test_content.append('    {} = np.random.randint({}, size=({}))'.format(parameter, rand_int_max, self.symtable[parameter].rows))
                    elif element_type.var_type == VarTypeEnum.REAL:
                        type_declare.append('    {} = np.asarray({}, dtype=np.floating)'.format(parameter, parameter))
                        test_content.append('    {} = np.random.randn({})'.format(parameter, self.symtable[parameter].rows))
                else:
                    type_declare.append('    {} = np.asarray({})'.format(parameter, parameter))
                    test_content.append('    {} = np.random.randn({})'.format(parameter, self.symtable[parameter].rows))
                type_checks.append('    assert {}.shape == ({},)'.format(parameter, self.symtable[parameter].rows))
            elif self.symtable[parameter].var_type == VarTypeEnum.SCALAR:
                type_checks.append('    assert np.ndim({}) == 0'.format(parameter))
                test_content.append('    {} = np.random.randn()'.format(parameter))
            elif self.symtable[parameter].var_type == VarTypeEnum.SET:
                type_checks.append('    assert isinstance({}, list) and len({}) > 0'.format(parameter, parameter))
                type_checks.append('    assert len({}[0]) == {}'.format(parameter, self.symtable[parameter].size))
                test_content.append('    {} = []'.format(parameter))
                test_content.append('    {}_0 = np.random.randint(1, {})'.format(parameter, rand_int_max))
                test_content.append('    for i in range({}_0):'.format(parameter))
                gen_list = []
                for i in range(self.symtable[parameter].size):
                    if self.symtable[parameter].int_list[i]:
                        gen_list.append('np.random.randint({})'.format(rand_int_max))
                    else:
                        gen_list.append('np.random.randn()')
                test_content.append('        {}.append(('.format(parameter) + ', '.join(gen_list) + '))')

            main_content.append('    print("{}:", {})'.format(parameter, parameter))
        content = 'def ' + func_name + '(' + ', '.join(self.parameters) + '):\n'
        if show_doc:
            content += '    \"\"\"\n' + '\n'.join(doc) + '\n    \"\"\"\n'
        # merge content
        content += '\n'.join(type_declare) + '\n\n'
        content += dim_content
        content += '\n'.join(type_checks) + '\n\n'
        # statements
        stats_content = ""
        for index in range(len(self.stat_list)):
            ret_str = ''
            if index == len(self.stat_list) - 1:
                if type(self.stat_list[index]).__name__ != 'Assignment':
                    kwargs[LHS] = self.ret_symbol
                    ret_str = "    " + self.ret_symbol + ' = '
            else:
                if type(self.stat_list[index]).__name__ != 'Assignment':
                    # meaningless
                    continue
            stat_info = self.walk(self.stat_list[index], **kwargs)
            if stat_info.pre_list:
                stats_content += "".join(stat_info.pre_list)
            stats_content += ret_str + stat_info.content + '\n'
        #
        content += stats_content
        content += '    return ' + self.ret_symbol
        content += '\n'
        # convert special string in identifiers
        content = self.trim_content(content)
        # test
        test_content.append('    return {}'.format(', '.join(self.parameters)))
        main_content.append("    func_value = {}({})".format(func_name, ', '.join(self.parameters)))
        main_content.append('    print("func_value: ", func_value)')
        content += '\n\n' + '\n'.join(test_content) + '\n\n\n' + '\n'.join(main_content)
        return content

    def walk_WhereConditions(self, node, **kwargs):
        pass

    def walk_Statements(self, node, **kwargs):
        index = 0
        content = ''
        if node.stats:
            stat_info = self.walk(node.stats, **kwargs)
            content += stat_info.content
        else:
            ret_str = ''
            content += ''
            if type(node.stat).__name__ != 'Assignment':
                ret_str = "    " + self.ret_symbol + ' = '
            stat_info = self.walk(node.stat, **kwargs)
            stat_value = stat_info.content
            if isinstance(stat_info, CodeNodeInfo):
                if stat_info.pre_list:
                    content += "".join(stat_info.pre_list)
                content += ret_str + stat_info.content + '\n'
            else:
                content += stat_value + '\n'
        return CodeNodeInfo(content)

    def walk_Expression(self, node, **kwargs):
        exp_info = self.walk(node.value, **kwargs)
        if node.sign:
            exp_info.content = '-' + exp_info.content
        return exp_info

    def walk_Summation(self, node, **kwargs):
        type_info = self.node_dict[node]
        assign_id = type_info.symbol
        cond_content = ""
        if node.cond:
            if LHS in kwargs:
                lhs = kwargs[LHS]
                if self.contain_subscript(lhs):
                    lhs_ids = self.get_all_ids(lhs)
                    assert lhs_ids[1][0] == lhs_ids[1][1], "multiple subscripts for sum"
                    sub = type_info.content
                    cond_info = self.walk(node.cond, **kwargs)
                    cond_content = cond_info.content
        else:
            sub_info = self.walk(node.sub)
            sub = sub_info.content
        vars = type_info.symbols
        kwargs[WALK_TYPE] = WalkTypeEnum.RETRIEVE_EXPRESSION
        content = []
        target_var = []
        exp_info = self.walk(node.exp)
        exp_str = exp_info.content
        for var in vars:
            if self.contain_subscript(var):
                var_ids = self.get_all_ids(var)
                var_subs = var_ids[1]
                for var_sub in var_subs:
                    if sub == var_sub:
                        target_var.append(var_ids[0])
        if self.symtable[assign_id].var_type == VarTypeEnum.MATRIX:
            content.append("{} = np.zeros(({}, {}))\n".format(assign_id, self.symtable[assign_id].rows, self.symtable[assign_id].cols))
        elif self.symtable[assign_id].var_type == VarTypeEnum.VECTOR:
            content.append("{} = np.zeros({})\n".format(assign_id, self.symtable[assign_id].rows))
        elif self.symtable[assign_id].var_type == VarTypeEnum.SEQUENCE:
            ele_type = self.symtable[assign_id].element_type
            content.append("{} = np.zeros(({}, {}, {}))\n".format(assign_id, self.symtable[assign_id].size, ele_type.rows, ele_type.cols))
        else:
            content.append("{} = 0\n".format(assign_id))
        content.append("for {} in range(len({})):\n".format(sub, target_var[0]))
        if node.cond:
            for right_var in type_info.symbols:
                if self.contain_subscript(right_var):
                    var_ids = self.get_all_ids(right_var)
                    exp_str = exp_str.replace(right_var, "{}[{}][{}]".format(var_ids[0], var_ids[1][0], var_ids[1][1]))
                    if exp_info.pre_list:
                        for index in range(len(exp_info.pre_list)):
                            exp_info.pre_list[index] = exp_info.pre_list[index].replace(old, new)
        else:
            for var in target_var:
                old = "{}_{}".format(var, sub)
                new = "{}[{}]".format(var, sub)
                exp_str = exp_str.replace(old, new)
                if exp_info.pre_list:
                    for index in range(len(exp_info.pre_list)):
                        exp_info.pre_list[index] = exp_info.pre_list[index].replace(old, new)
        if exp_info.pre_list:   # catch pre_list
            list_content = "".join(exp_info.pre_list)
            # content += exp_info.pre_list
            list_content = list_content.split('\n')
            for index in range(len(list_content)):
                if index != len(list_content)-1:
                    content.append(list_content[index] + '\n')
        # only one sub for now
        if node.cond:
            content.append("    " + cond_content)
            content.append(str("        " + assign_id + " += " + exp_str + '\n'))
        else:
            content.append(str("    " + assign_id + " += " + exp_str + '\n'))
        content[0] = "    " + content[0]
        return CodeNodeInfo(assign_id, pre_list=["    ".join(content)])

    def walk_Determinant(self, node, **kwargs):
        value_info = self.walk(node.value)
        value = value_info.content
        type_info = self.node_dict[node.value]
        if type_info.la_type.var_type == VarTypeEnum.VECTOR or type_info.la_type.var_type == VarTypeEnum.MATRIX or type_info.la_type.var_type == VarTypeEnum.SEQUENCE:
            if value in self.parameters:
                value_type = self.symtable[value]
                if type_info.la_type.var_type == VarTypeEnum.SEQUENCE:
                    dim = value_type.size
                else:
                    dim = value_type.rows
                return CodeNodeInfo(str(dim))
            elif value in self.symtable:
                return CodeNodeInfo(value + '.shape[0]')
            return CodeNodeInfo('(' + value + ').shape[0]')
        return CodeNodeInfo('np.absolute(' + value + ')')

    def walk_Transpose(self, node, **kwargs):
        f_info = self.walk(node.f, **kwargs)
        f_info.content = "{}.T".format(f_info.content)
        return f_info

    def walk_Power(self, node, **kwargs):
        base_info = self.walk(node.base, **kwargs)
        if node.t:
            base_info.content = "{}.T".format(base_info.content)
        elif node.r:
            base_info.content = "np.linalg.inv({})".format(base_info.content)
        else:
            power_info = self.walk(node.power, **kwargs)
            base_info.content = base_info.content + '^' + power_info.content
        return base_info

    def walk_Solver(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = "np.linalg.solve({}, {})".format(left_info.content, right_info.content)
        return left_info

    def walk_SparseMatrix(self, node, **kwargs):
        op_type = kwargs[ASSIGN_TYPE]
        lhs = kwargs[LHS]
        type_info = self.node_dict[node]
        cur_m_id = type_info.symbol
        pre_list = []
        index_var = type_info.la_type.index_var
        value_var = type_info.la_type.value_var
        pre_list.append("    {} = []\n".format(index_var))
        pre_list.append("    {} = []\n".format(value_var))
        if_info = self.walk(node.ifs, **kwargs)
        pre_list += if_info.content
        # assignment
        if op_type == '=':
            pre_list.append("    {} = scipy.sparse.coo_matrix(({}, np.asarray({}).T), shape=({}, {}))\n".format(cur_m_id, value_var, index_var, self.symtable[cur_m_id].rows,
                                                          self.symtable[cur_m_id].cols))
        elif op_type == '+=':
            # left_ids = self.get_all_ids(lhs)
            # left_subs = left_ids[1]
            pre_list.append(
                "    {} = scipy.sparse.coo_matrix(({}+{}.data.tolist(), np.hstack((np.asarray({}).T, np.asarray(({}.row, {}.col))))), shape=({}, {}))\n".format(cur_m_id, value_var, self.get_main_id(lhs),
                                                                                                    index_var, self.get_main_id(lhs), self.get_main_id(lhs),
                                                                                                    self.symtable[
                                                                                                        cur_m_id].rows,
                                                                                                    self.symtable[
                                                                                                        cur_m_id].cols))

        return CodeNodeInfo(cur_m_id, pre_list)

    def walk_SparseIfs(self, node, **kwargs):
        ret = []
        pre_list = []
        if node.ifs:
            ifs_info = self.walk(node.ifs, **kwargs)
            ret += ifs_info.content
            pre_list += ifs_info.pre_list
        if node.value:
            value_info = self.walk(node.value, **kwargs)
            ret += value_info.content
            pre_list += value_info.pre_list
        return CodeNodeInfo(ret, pre_list)

    def walk_SparseIf(self, node, **kwargs):
        sparse_node = node.parent
        while type(sparse_node).__name__ != 'SparseMatrix':
            sparse_node = sparse_node.parent
        type_info = self.node_dict[sparse_node]
        id0_info = self.walk(node.id0, **kwargs)
        id0 = id0_info.content
        id1_info = self.walk(node.id1, **kwargs)
        id1 = id1_info.content
        id2_info = self.walk(node.id2, **kwargs)
        id2 = id2_info.content
        stat_info = self.walk(node.stat, **kwargs)
        content = []
        content.append('    for {}, {} in {}:\n'.format(id0, id1, id2))
        content.append('        {}.append(({}, {}))\n'.format(type_info.la_type.index_var, id0, id1))
        stat_content = stat_info.content
        # replace '_ij' with '(i,j)'
        stat_content = stat_content.replace('_{}{}'.format(id0, id1), '[{}][{}]'.format(id0, id1))
        content.append('        {}.append({})\n'.format(type_info.la_type.value_var, stat_content))
        return CodeNodeInfo(content)

    def walk_SparseOther(self, node, **kwargs):
        content = ''
        return CodeNodeInfo('    '.join(content))

    def walk_Matrix(self, node, **kwargs):
        content = "    "
        # lhs = kwargs[LHS]
        type_info = self.node_dict[node]
        cur_m_id = type_info.symbol
        kwargs["cur_id"] = cur_m_id
        ret_info = self.walk(node.value, **kwargs)
        ret = ret_info.content
        if type_info.la_type.block:
            all_rows = []
            m_content = ""
            for i in range(len(ret)):
                if type_info.la_type.list_dim:
                    for j in range(len(ret[i])):
                        if (i, j) in type_info.la_type.list_dim:
                            dims = type_info.la_type.list_dim[(i, j)]
                            if ret[i][j] == '0':
                                func_name = 'np.zeros'
                            elif ret[i][j] == '1':
                                func_name = 'np.ones'
                            elif 'I' in ret[i][j] and 'I' not in self.symtable:
                                # todo: assert in type checker
                                assert dims[0] == dims[1], "I must be square matrix"
                                ret[i][j] = ret[i][j].replace('I', 'np.identity({})'.format(dims[0]))
                                continue
                            else:
                                func_name = ret[i][j] + ' * np.ones'
                            if dims[1] == 1:
                                # vector
                                ret[i][j] = '{}({})'.format(func_name, dims[0])
                            else:
                                ret[i][j] = '{}(({}, {}))'.format(func_name, dims[0], dims[1])
                all_rows.append('[' + ', '.join(ret[i]) + ']')
            m_content += 'np.block([{}])'.format(', '.join(all_rows))
            if len(ret) > 1 and len(ret[0]) > 1:
                content += '{} = {}\n'.format(cur_m_id, m_content)
            elif len(ret) == 1:
                # single row
                content += '{} = np.hstack(({}))\n'.format(cur_m_id, ', '.join(ret[0]))
            else:
                # single col
                for i in range(len(ret)):
                    ret[i] = ''.join(ret[i])
                content += '{} = np.vstack(({}))\n'.format(cur_m_id, ', '.join(ret))
        else:
            # dense
            content += '{} = np.zeros(({}, {}))\n'.format(cur_m_id, self.symtable[cur_m_id].rows,
                                                          self.symtable[cur_m_id].cols)
            for i in range(len(ret)):
                content += "    {}[{}] = [{}]\n".format(cur_m_id, i, ', '.join(ret[i]))
        #####################
        pre_list = [content]
        if ret_info.pre_list:
            pre_list = ret_info.pre_list + pre_list
        return CodeNodeInfo(cur_m_id, pre_list)

    def walk_MatrixRows(self, node, **kwargs):
        ret = []
        pre_list = []
        if node.rs:
            rs_info = self.walk(node.rs, **kwargs)
            ret = ret + rs_info.content
            pre_list += rs_info.pre_list
        if node.r:
            r_info = self.walk(node.r, **kwargs)
            ret.append(r_info.content)
            pre_list += r_info.pre_list
        return CodeNodeInfo(ret, pre_list)

    def walk_MatrixRow(self, node, **kwargs):
        ret = []
        pre_list = []
        if node.rc:
            rc_info = self.walk(node.rc, **kwargs)
            ret += rc_info.content
            pre_list += rc_info.pre_list
        if node.exp:
            exp_info = self.walk(node.exp, **kwargs)
            ret.append(exp_info.content)
            pre_list += exp_info.pre_list
        return CodeNodeInfo(ret, pre_list)

    def walk_MatrixRowCommas(self, node, **kwargs):
        ret = []
        pre_list = []
        if node.value:
            value_info = self.walk(node.value, **kwargs)
            ret += value_info.content
            pre_list += value_info.pre_list
        if node.exp:
            exp_info = self.walk(node.exp, **kwargs)
            ret.append(exp_info.content)
            pre_list += exp_info.pre_list
        return CodeNodeInfo(ret, pre_list)

    def walk_ExpInMatrix(self, node, **kwargs):
        exp_info = self.walk(node.value, **kwargs)
        if node.sign:
            exp_info.content = '-' + exp_info.content
        return exp_info

    def walk_NumMatrix(self, node, **kwargs):
        type_info = self.node_dict[node]
        post_s = ''
        if node.id:
            func_name = "np.identity"
        else:
            if node.left == '0':
                func_name = "np.zeros"
            elif node.left == '1':
                func_name = "np.ones"
            else:
                func_name = "({} * np.ones".format(left_info.content)
                post_s = ')'
        id1_info = self.walk(node.id1, **kwargs)
        if node.id2:
            id2_info = self.walk(node.id2, **kwargs)
            content = "{}(({}, {}))".format(func_name, id1_info.content, id2_info.content)
        else:
            content = "{}({})".format(func_name, id1_info.content)
        node_info = CodeNodeInfo(content+post_s)
        return node_info

    def walk_Add(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' + ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_Subtract(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' - ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_AddSub(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' +- ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_Multiply(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
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
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' / ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_Subexpression(self, node, **kwargs):
        value_info = self.walk(node.value, **kwargs)
        value_info.content = '(' + value_info.content + ')'
        return value_info

    def walk_Assignment(self, node, **kwargs):
        type_info = self.node_dict[node]
        # walk matrix first
        content = ""
        left_info = self.walk(node.left, **kwargs)
        left_id = left_info.content
        kwargs[LHS] = left_id
        kwargs[ASSIGN_TYPE] = node.op
        # self left-hand-side symbol
        right_info = self.walk(node.right, **kwargs)
        right_exp = ""
        if right_info.pre_list:
            content += "".join(right_info.pre_list)
        # y_i = stat
        if self.contain_subscript(left_id):
            left_ids = self.get_all_ids(left_id)
            left_subs = left_ids[1]
            if len(left_subs) == 2: # matrix only
                sequence = left_ids[0]  # y left_subs[0]
                sub_strs = left_subs[0] + left_subs[1]
                if self.symtable[sequence].var_type == VarTypeEnum.MATRIX and self.symtable[sequence].sparse:
                    # sparse mat assign
                    right_exp += '    ' + sequence + ' = ' + right_info.content
                    content += right_exp
                elif left_subs[0] == left_subs[1]:
                    # L_ii
                    content = ""
                    content += "    for {} in range({}):\n".format(left_subs[0], self.symtable[sequence].rows)
                    if right_info.pre_list:
                        for list in right_info.pre_list:
                            lines = list.split('\n')
                            content += "    " + "\n    ".join(lines)
                    content += "    {}[{}][{}] = {}".format(sequence, left_subs[0], left_subs[0], right_info.content)
                else:
                    for right_var in type_info.symbols:
                        if sub_strs in right_var:
                            var_ids = self.get_all_ids(right_var)
                            right_info.content = right_info.content.replace(right_var, "{}[{}][{}]".format(var_ids[0], var_ids[1][0], var_ids[1][1]))
                    right_exp += "    {}[{}][{}] = {}".format(self.get_main_id(left_id), left_subs[0], left_subs[1], right_info.content)
                    if self.symtable[sequence].var_type == VarTypeEnum.MATRIX:
                        if node.op == '=':
                            # declare
                            content += "    {} = np.zeros(({}, {}))\n".format(sequence,
                                                                              self.symtable[sequence].rows,
                                                                              self.symtable[sequence].cols)
                    content += "    for {} in range({}):\n".format(left_subs[0], self.symtable[sequence].rows)
                    content += "        for {} in range({}):\n".format(left_subs[1], self.symtable[sequence].cols)
                    content += "        " + right_exp
                    # content += '\n'
            elif len(left_subs) == 1: # sequence only
                sequence = left_ids[0]  # y left_subs[0]
                # replace sequence
                for right_var in type_info.symbols:
                    if self.contain_subscript(right_var):
                        var_ids = self.get_all_ids(right_var)
                        right_info.content = right_info.content.replace(right_var, "{}[{}]".format(var_ids[0], var_ids[1][0]))

                right_exp += "    {}[{}] = {}".format(self.get_main_id(left_id), left_subs[0], right_info.content)
                ele_type = self.symtable[sequence].element_type
                if ele_type.var_type == VarTypeEnum.MATRIX:
                    content += "    {} = np.zeros(({}, {}, {}))\n".format(sequence, self.symtable[sequence].size, ele_type.rows, ele_type.cols)
                elif ele_type.var_type == VarTypeEnum.VECTOR:
                    content += "    {} = np.zeros(({}, {}))\n".format(sequence, self.symtable[sequence].size, ele_type.rows)
                else:
                    content += "    {} = np.zeros({})\n".format(sequence, self.symtable[sequence].size)
                content += "    for {} in range({}):\n".format(left_subs[0], self.symtable[sequence].size)
                content += "    " + right_exp
                # content += '\n'
        #
        else:
            op = ' = '
            if node.op == '+=':
                op = ' += '
            right_exp += '    ' + self.get_main_id(left_id) + op + right_info.content
            content += right_exp
        content += '\n'
        la_remove_key(LHS, **kwargs)
        return CodeNodeInfo(content)

    def walk_IfCondition(self, node, **kwargs):
        ret_info = self.walk(node.cond)
        ret_info.content = "if " + ret_info.content + ":\n"
        return ret_info

    def walk_NeCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' != ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_EqCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' == ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_InCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' in ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_NotInCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + 'not in' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_GreaterCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' > ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_GreaterEqualCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' >= ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_LessCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' < ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_LessEqualCondition(self, node, **kwargs):
        left_info = self.walk(node.left, **kwargs)
        right_info = self.walk(node.right, **kwargs)
        left_info.content = left_info.content + ' <= ' + right_info.content
        left_info.pre_list = self.merge_pre_list(left_info, right_info)
        return left_info

    def walk_IdentifierSubscript(self, node, **kwargs):
        right = []
        for value in node.right:
            value_info = self.walk(value)
            right.append(value_info.content)
        left_info = self.walk(node.left)
        content = left_info.content + '_' + ''.join(right)
        return CodeNodeInfo(content)

    def walk_IdentifierAlone(self, node, **kwargs):
        if node.value:
            value = node.value
        else:
            value = '`' + node.id + '`'
        return CodeNodeInfo(value)

    def walk_Derivative(self, node, **kwargs):
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
        elif node.nm:
            return self.walk(node.nm, **kwargs)
        elif node.op:
            return self.walk(node.op, **kwargs)
        elif node.s:
            return self.walk(node.s, **kwargs)

    def walk_Number(self, node, **kwargs):
        return self.walk(node.value, **kwargs)

    def walk_Integer(self, node, **kwargs):
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

    def is_keyword(self, name):
        return keyword.iskeyword(name)

