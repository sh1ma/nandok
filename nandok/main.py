import ast
import random
import string

import astor

alphabet = string.ascii_letters
with open("../fizzbuzz.py") as f:
    code = f.read()

constants = set()
functions = set()

func_dict = {}
assigns = set()
assign_dict = {}
module_dict = {}
modules = set()

variable_dict = {}

root = ast.parse(code)


class ConstantRemover(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id in assign_dict:
            node.id = assign_dict[node.id]
        elif node.id in module_dict:
            node.id = module_dict[node.id]
        elif node.id in func_dict:
            node.id = func_dict[node.id]
        return self.generic_visit(node)

    def visit_Constant(self, node):
        if node.value in variable_dict:
            node = ast.Name(id=variable_dict[node.value])
        return self.generic_visit(node)

    def visit_alias(self, node):
        if node.name in module_dict:
            node.asname = module_dict[node.name]
        return self.generic_visit(node)


class NameLister(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.import_count = 0

    def visit_Constant(self, node: ast.Constant):
        constants.add(node.value)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            assigns.add(node.id)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self.import_count += 1
        for module in node.names:
            module_name = module.asname if module.asname else module.name
            modules.add(module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.import_count += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            functions.add(node.func.id)
        self.generic_visit(node)


lister = NameLister()
lister.visit(root)


def get_random_string(n):
    return "".join(random.choices(alphabet, k=n))


def insert_constant(obj):
    root.body.insert(lister.import_count, obj)


for value in functions:
    new_name = get_random_string(10)
    func_dict[value] = new_name

for value in assigns:
    new_name = get_random_string(10)
    assign_dict[value] = new_name

for value in constants:
    new_name = get_random_string(10)
    variable_dict[value] = new_name

for value in modules:
    new_name = get_random_string(10)
    module_dict[value] = new_name


ConstantRemover().visit(root)

for value, new_name in func_dict.items():
    obj = ast.Assign(targets=[ast.Name(id=new_name)], value=ast.Name(id=value),)
    insert_constant(obj)


for value, new_name in variable_dict.items():
    obj = ast.Assign(targets=[ast.Name(id=new_name)], value=ast.Constant(value=value),)
    insert_constant(obj)


print(astor.to_source(root))
