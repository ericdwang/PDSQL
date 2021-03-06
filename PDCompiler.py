import copy


# Does not have not -- must be desugared down.
unary_map = {
    '_sum': 'SUM',
    '_avg': 'AVG',
    '_count': 'COUNT',
    '_first': 'FIRST',
    '_last': 'LAST',
    '_max': 'MAX',
    '_min': 'MIN',
    '_abs': 'ABS',
    '_ceil': 'CEIL',
    '_floor': 'FLOOR',
    '_round': 'ROUND',
    '_not': 'NOT'
}

binary_middle_map = {
    '_add': '+',
    '_sub': '-',
    '_mul': '*',
    '_div': '/',
    '_concat': '+',
    '_or': 'OR',
    '_and': 'AND',
    '_eq': '=',
    '_ne': '<>',
    '_lt': '<',
    '_gt': '>',
    '_le': '<=',
    '_ge': '>=',
    '_in': 'IN',
    '_between': 'BETWEEN',
    '_like': 'LIKE',
}

binary_function_map = {
    '_mod': 'MOD'
}

binary_set_map = {
    '_union': 'UNION',
    '_intersect': 'INTERSECT',
    '_except': 'EXCEPT',
}

_uniquegen_counter = 0


# Structure taken from Berkeley's Fall 2014 CS164 projects
def compile_to_sql(ast):
    # Import here to avoid circular imports
    from PDColumn import PDColumn
    from PDTable import PDTable

    def uniquegen():
        global _uniquegen_counter
        _uniquegen_counter += 1
        return '#reg-' + str(_uniquegen_counter)

    def apply_children(node, func):
        if isinstance(node, PDColumn):
            func(node)
            for child in node._children:
                apply_children(child, func)

        elif isinstance(node, PDTable):
            func(node)
            ops = node._operation_ordering
            for op in ops:
                if op[0] == '_select':
                    for col in op[1]:
                        apply_children(col['column'], func)
                else:
                    apply_children(op[1], func)

        elif hasattr(node, '__iter__'):
            for child in node:
                apply_children(child, func)

    def rewrite_select(node):
        if isinstance(node, PDTable):
            ops = node._operation_ordering
            if len([i[1] for i in ops if i[0] == '_select']) == 0:
                node._operation_ordering.append(
                    ('_select', [{'column': PDColumn(name='*')}]))


    def rewrite_exists(node):
        """
        Rewrite EXISTS to IN when the following conditions are met:
            * There is at least one restrictive equality condition on
              the subquery. E.g., where(subtable.col = 123)
            * There is an equality correlation between the queries.

        This currently only rewrites the base node, and does not attempt
        to convert multiple exists in the same query.
        """
        if isinstance(node, PDTable):
            parent_name = node._name
            ops = node._operation_ordering
            exist_list = []
            exist_child = None
            exist_index = None

            for idx, op in enumerate(ops):
                if op[0] == '_where_exists':
                    exist_list.append((idx, op[1]))

            for p_idx, child in exist_list:
                selective = False
                correlation_pair = None
                ops = child._operation_ordering
                for idx, op in enumerate(ops):
                    if op[0] == '_where':
                        col = op[1]
                        # Equality clauses
                        if isinstance(col, PDColumn) and col._binary_op == '_eq':
                            # Check for selectivity
                            selective = (len([i for i in col._children if \
                                    isinstance(i, PDColumn) and \
                                    i.table._name == child._name]) > 0) and \
                                    (len([i for i in col._children if not \
                                    (isinstance(i, PDTable)\
                                    or isinstance(i, PDColumn))]) > 0)

                            # Check for correlation
                            c1 = col._children[0]
                            c2 = col._children[1]
                            if isinstance(c1, PDColumn) and isinstance(c2, PDColumn):
                                name1 = c1.table._name
                                name2 = c2.table._name
                                if name1 == parent_name and name2 == child._name:
                                    correlation_pair = (idx, c1, c2)
                                elif name1 == child._name and name2 == parent_name:
                                    correlation_pair = (idx, c2, c1)

                # Here, we know if a rewrite for this child is necessary
                # if it is selective and a correlation_pair exists.
                if selective and correlation_pair:
                    # Remove old where clause for correlation
                    child._operation_ordering.pop(correlation_pair[0])

                    # Select the correlation.
                    child._operation_ordering = \
                        [i for i in child._operation_ordering if i[0] != '_select']
                    child._operation_ordering.append(("_select",\
                         [{'column':correlation_pair[2]}]))

                    exist_child = child
                    exist_index = p_idx
                    # Currently only supports rewriting one.
                    break

            if exist_index and exist_child:
                node._operation_ordering.pop(exist_index)
                in_col = correlation_pair[1].in_(exist_child)
                node._operation_ordering.append(('_where', in_col))

        return node

    def strip_parens(strings):
        if strings[0] == '(' and strings[-1] == ')':
            return strings[1:-1]
        return strings

    def get_table_name(node):
        if node._alias:
            return ['{} {}'.format(node._name, node._alias)]
        return [node._name]

    def get_binary_op_strings(node):
        children = [compilenode(child) for child in node._children]

        # Switch on all binary ops

        if node._binary_op in binary_middle_map:
            strings = ['('] + children[0] + \
                [binary_middle_map[node._binary_op]] + \
                children[1] + [')']

        elif node._binary_op in binary_function_map:
            strings = [binary_function_map[node._binary_op] + '('] + \
                children[0] + [','] + children[1] + [')']

        elif node._binary_op in binary_set_map:
            strings = strip_parens(children[0]) + \
                [binary_set_map[node._binary_op]] + \
                strip_parens(children[1])

        else:
            raise Exception(
                "AST column contains unrecognized binary op: "
                + node._binary_op)
        return strings

    def compilenode(node):
        node = copy.deepcopy(node)
        apply_children(node, rewrite_select)
        strings = []

        if isinstance(node, PDColumn):

            if len(node._children) > 0:
                strings = get_binary_op_strings(node)

            # In the case where no children, fill strings with basic
            # information about the column.
            else:
                if (hasattr(node.table, '_name')
                        and not isinstance(node.table._name, PDTable)
                        and not node._count):
                    if node.table._alias:
                        strings = [node.table._alias + '.' + node.name]
                    else:
                        strings = [node.table._name + '.' + node.name]
                else:
                    strings = [node.name]

            # At this point, we have either a base column or some composition
            # of columns in 'strings'. Now we apply unary operators.

            for op in node.ops:
                if op in unary_map:
                    strings = [unary_map[op] + '('] + strings + [')']
                else:
                    raise Exception(
                        "AST column contains unrecognized unary op: "
                        + op)

            if node.null is True:
                strings.append('IS NULL')
            elif node.null is False:
                strings.append('IS NOT NULL')

        elif isinstance(node, PDTable):

            if len(node._children) > 0:
                return get_binary_op_strings(node)

            ops = node._operation_ordering

            # SELECT
            select_list = ['SELECT']
            if node._distinct:
                select_list.append('DISTINCT')

            for col_list in [i[1] for i in ops if i[0] == '_select']:
                for col in col_list:
                    s = []
                    if 'name' in col:
                        s += ['AS \"' + col['name'] + '\"']
                    s = compilenode(col['column']) + s
                    select_list += s + [',']
            select_list.pop()

            # FROM + JOIN
            joins = [i[1] for i in ops if i[0] == '_join']

            from_list = ['FROM']

            if not joins:
                if not isinstance(node._name, PDTable):
                    from_list += get_table_name(node)
                else:
                    from_list += ['('] + compilenode(node._name) + [')']
            else:
                from_list += ['('] + get_table_name(node)
                for join in joins:
                    table = join['table']
                    # No operations on the table, so just use the name
                    if len(table._operation_ordering) == 0:
                        from_list += ['INNER JOIN'] + get_table_name(table)
                    else:
                        from_list += ['INNER JOIN'] + compilenode(table)
                    if join['cond']:
                        from_list += ['ON'] + compilenode(join['cond'])
                from_list += [')']

            # WHERE and WHERE EXISTS
            where_list = ['WHERE']
            for col in [i[1] for i in ops if i[0] == '_where_exists']:
                where_list += ['EXISTS'] + ['('] + compilenode(col) + [')'] + ['AND']
            for col in [i[1] for i in ops if i[0] == '_where']:
                where_list += ['('] + compilenode(col) + [')'] + ['AND']
            where_list.pop()

            # GROUP BY
            group_list = ['GROUP BY']
            group = [i[1] for i in ops if i[0] == '_group']
            for col in group:
                group_list += compilenode(col) + [',']
            group_list.pop()

            # HAVING
            having_list = ['HAVING']
            having = [i[1] for i in ops if i[0] == '_having']
            # Must have a GROUP BY clause for HAVING
            if having and not group:
                raise Exception('Must have a GROUP BY clause if using HAVING')
            for col in having:
                having_list += ['('] + compilenode(col) + [')'] + ['AND']
            having_list.pop()

            # ORDER
            order_list = ['ORDER BY']
            for col in [i[1] for i in ops if i[0] == '_order']:
                order_list += compilenode(col) + [',']
            order_list.pop()
            if len(order_list) > 0:
                if node._reverse_val:
                    order_list += ['DESC']
                else:
                    order_list += ['ASC']

            limit_list = []
            if node._limit is not None:
                limit_list += ['LIMIT', str(node._limit)]

            strings = ['('] + select_list + from_list + where_list + group_list + \
                having_list + order_list + limit_list + [')']

        elif isinstance(node, tuple):
            new_elements = []
            for item in node:
                if isinstance(item, basestring):
                    new_elements += ['"' + item + '"']
                else:
                    new_elements += [str(item)]
            new_elements = ','.join(new_elements)
            strings = ['(' + new_elements + ')']

        elif isinstance(node, basestring):
            strings = ['"' + node + '"']

        else:
            strings = [str(node)]

        return strings

    ast = copy.deepcopy(ast)
    ast = rewrite_exists(ast)
    strings = strip_parens(compilenode(ast))
    return ' '.join(strings) + ';'
