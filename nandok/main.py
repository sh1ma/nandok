import ast
import random
import string

import astor

alphabet = string.ascii_letters
with open("tests/test_helloworld.py") as f:
    code = f.read()

constants = set()
functions = set()

func_dict = {}
before_assign_dict = {}

variable_dict = {}

root = ast.parse(code)


class ConstantRemover(ast.NodeTransformer):
    def visit_Assign(self, node):
        if (
            isinstance(node.value, ast.Name) and node.value.id in before_assign_dict
        ) or (
            isinstance(node.value, ast.Constant) and node.value.value in variable_dict
        ):
            for target in node.targets:
                target.id = variable_dict[node.value.value]
            node = None
        return node

    def visit_Call(self, node):
        # 引数の処理
        for arg in node.args.copy():
            if isinstance(arg, ast.Name) and arg.id in before_assign_dict:
                # 変数定義してあった場合
                arg.id = variable_dict[before_assign_dict[arg.id]]
            elif isinstance(arg, ast.Constant):
                # 定数だった場合
                new_node = ast.Name(id=variable_dict[arg.value])
                node.args.insert(node.args.index(arg), new_node)
                node.args.remove(arg)
        # 関数名変更
        node.func.id = func_dict[node.func.id]
        return node

    def visit_Constant(self, node):
        if node.value not in variable_dict:
            return node
        new_node = ast.Name(id=variable_dict[node.value])
        return new_node


class NameLister(ast.NodeVisitor):
    def visit_Constant(self, node: ast.Constant):
        constants.add(node.value)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if not isinstance(node.value, ast.Constant) or not isinstance(
                node.value.value, (int, str, bool)
            ):
                continue
            before_assign_dict[target.id] = node.value.value
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        functions.add(node.func.id)
        self.generic_visit(node)


def get_random_string(n):
    return "".join(random.choices(alphabet, k=n))


def insert_constant(obj):
    root.body.insert(0, obj)


NameLister().visit(root)

for value in functions:
    new_name = get_random_string(5)
    func_dict[value] = new_name

for value in before_assign_dict.values():
    new_name = get_random_string(5)
    variable_dict[value] = new_name

for value in constants:
    new_name = get_random_string(5)
    variable_dict[value] = new_name


ConstantRemover().visit(root)

for value, new_name in func_dict.items():
    obj = ast.Assign(targets=[ast.Name(id=new_name)], value=ast.Name(id=value),)
    insert_constant(obj)


for value, new_name in variable_dict.items():
    obj = ast.Assign(targets=[ast.Name(id=new_name)], value=ast.Constant(value=value),)
    insert_constant(obj)


print(astor.to_source(root))
