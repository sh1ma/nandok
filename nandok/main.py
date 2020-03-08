import ast
import random
import string
from typing import Any

import astor

alphabet = string.ascii_letters
with open("../fizzbuzz.py") as f:
    code = f.read()

constants = set()
called_functions = set()
defined_functions = set()
pure_func_dict = {}
defined_func_dict = {}
args = set()
arg_dict = {}
assigns = set()
assign_dict = {}
module_dict = {}
modules = set()

variable_dict = {}

root = ast.parse(code)


class ConstantRemover(ast.NodeTransformer):
    def visit_Name(self, node: ast.Name):
        if node.id in assign_dict:
            node.id = assign_dict[node.id]
        elif node.id in module_dict:
            node.id = module_dict[node.id]
        elif node.id in pure_func_dict:
            node.id = pure_func_dict[node.id]
        elif node.id in defined_func_dict:
            node.id = defined_func_dict[node.id]
        elif node.id in arg_dict:
            node.id = arg_dict[node.id]
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant):
        if node.value in variable_dict:
            node = ast.Name(id=variable_dict[node.value])
        return self.generic_visit(node)

    def visit_alias(self, node: ast.alias):
        if node.name in module_dict:
            node.asname = module_dict[node.name]
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name in defined_func_dict:
            node.name = defined_func_dict[node.name]
        return self.generic_visit(node)

    def visit_arg(self, node: ast.arg):
        if node.arg in arg_dict:
            node.arg = arg_dict[node.arg]
        return self.generic_visit(node)


class NameLister(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self.import_count = 0

    def visit_Constant(self, node: ast.Constant):
        constants.add(node.value)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Store):
            assigns.add(node.id)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        self.import_count += 1
        for module in node.names:
            module_name = module.asname if module.asname else module.name
            modules.add(module_name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.import_count += 1
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            called_functions.add(node.func.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        defined_functions.add(node.name)
        self.generic_visit(node)

    def visit_arg(self, node: ast.arg):
        args.add(node.arg)
        self.generic_visit(node)


lister = NameLister()
lister.visit(root)


def get_random_string(n: int) -> str:
    return "".join(random.choices(alphabet, k=n))


def insert_constant(obj: Any) -> None:
    root.body.insert(lister.import_count, obj)


pure_called_functions = called_functions - defined_functions

for value in pure_called_functions:
    new_name = get_random_string(10)
    pure_func_dict[value] = new_name

for value in assigns:
    new_name = get_random_string(10)
    assign_dict[value] = new_name

for value in constants:
    new_name = get_random_string(10)
    variable_dict[value] = new_name

for value in modules:
    new_name = get_random_string(10)
    module_dict[value] = new_name

for value in defined_functions:
    new_name = get_random_string(10)
    defined_func_dict[value] = new_name

for value in args:
    new_name = get_random_string(10)
    arg_dict[value] = new_name


ConstantRemover().visit(root)

for value, new_name in pure_func_dict.items():
    obj = ast.Assign(targets=[ast.Name(id=new_name)], value=ast.Name(id=value),)
    insert_constant(obj)


for value, new_name in variable_dict.items():
    obj = ast.Assign(targets=[ast.Name(id=new_name)], value=ast.Constant(value=value),)
    insert_constant(obj)


print(astor.to_source(root))
