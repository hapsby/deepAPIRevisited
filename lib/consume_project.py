
import os
import ast
import glob
import traceback
from pathlib import Path
from typing import Optional
from ConsumeContext import ConsumeContext
from ApiMap import ApiMap
from functions import *


def get_function_call_parts(function_call_node):
    """
    :param function_call_node: An AST node.
    :return: If the node is an expression that represents a function or method call, then this returns a list of all
            of the tokens that make up the call, e.g. if the expression is os.path.join then the return value is
            ["os", "path", "join"].  Otherwise, the return value is None.
    """
    if isinstance(function_call_node, ast.Name):
        return [function_call_node.id]
    if isinstance(function_call_node, ast.Attribute):
        prefix = get_function_call_parts(function_call_node.value)
        if prefix is None:
            return None
        return prefix + [function_call_node.attr]
    return None


def find_api_calls(node, context, local_functions=None):
    if local_functions is None:
        local_functions = {}
    function_calls = []
    if isinstance(node, ast.Call):
        function_calls = []
        for arg in node.args:
            function_calls += find_api_calls(arg, context, local_functions)
        function_call_parts = get_function_call_parts(node.func)
        if function_call_parts is not None:
            api_map = context.api_map
            if len(function_call_parts) == 1:
                if function_call_parts[0] in local_functions:
                    return local_functions[function_call_parts[0]]
                elif function_call_parts[0] in api_map.api_calls_by_function_name:
                    return api_map.api_calls_by_function_name[function_call_parts[0]]
            if function_call_parts[0] in context.external_modules:
                function_call_parts[0] = context.external_modules[function_call_parts[0]]
                function_calls += ['.'.join(function_call_parts)]
    else:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef):
                local_functions[child.name] = find_api_calls(child, context, dict(local_functions))
            else:
                function_calls += find_api_calls(child, context, local_functions)
    return function_calls


def get_first_child(node) -> Optional[ast.AST]:
    for child in ast.iter_child_nodes(node):
        return child
    return None


def get_string_constant_from_expr(node) -> Optional[str]:
    """
    If the node is an ast.Expr whose first child node is an ast.Constant, and the value of that
    ast.Constant value is a string, this returns that string.
    :param ast.AST node: An AST node.
    :return: The string in the constant, or None.
    """
    if not isinstance(node, ast.Expr):
        return None
    child = get_first_child(node)
    if isinstance(child, ast.Constant) and isinstance(child.value, str):
        return child.value
    return None


def find_description(node):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.arguments):
            continue
        else:
            name = get_string_constant_from_expr(child)
            if name is not None:
                return name
            break
    return get_description_from_name(node.name)


def import_module(module_name, real_name, new_symbol, default_new_symbol, context):
    if new_symbol is None:
        new_symbol = default_new_symbol
    if module_name[0] == ".":
        return
    filenames = [
        context.dir_path + "/" + module_name.replace(".", "/") + ".py",
        context.dir_path + "/" + module_name.replace(".", "/") + "/__init__.py"
    ]
    for filename in filenames:
        if os.path.isfile(filename):
            return
    context.external_modules[new_symbol] = real_name


def find_functions(node, context):
    api_map = context.api_map
    if isinstance(node, ast.FunctionDef):
        function_name = context.get_function_name(node.name)
        d = find_description(node)
        a = find_api_calls(node, context)
        if 30 < len(d) < 100 and 2 < len(a) < 5:
            print("Function: " + function_name)
            print("Desc: " + d)
            print("API calls: " + str(a))
        api_map.set_pair_with_stats(function_name, d, a)
    elif isinstance(node, ast.Import):
        for alias in node.names:
            import_module(alias.name, alias.name, alias.asname, alias.name, context)
    elif isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name != "*" and node.level == 0:
                import_module(node.module, node.module + "." + alias.name, alias.asname, alias.name, context)
    else:
        if isinstance(node, ast.ClassDef):
            context.class_names.append(node.name)
        for child in ast.iter_child_nodes(node):
            find_functions(child, context)
        if isinstance(node, ast.ClassDef):
            context.class_names.pop()


def get_prefix_from_filename(filename):
    parts = re.split(r"[\\/]", filename[:-3])[1:]
    return ".".join(parts) + "."


def consume_project(subdir):
    api_map = ApiMap()
    for filename in glob.glob(subdir + '/**/*.py', recursive=True):
        context = ConsumeContext(os.path.dirname(filename))
        api_map.stats.total_files += 1
        try:
            #try:
            print("Filename: " + subdir + "/" + filename)
            source = Path(filename).read_text()
            #except Exception:
                #source = Path(filename).read_text(encoding="latin_1")
            api_map.stats.total_utf8_files += 1
            tree = ast.parse(source, filename=filename, mode='exec')
            find_functions(tree, context)
            api_map.stats.total_parsed_files += 1
        except Exception as e:
            print("File " + filename + " failed: " + str(e))
            if str(e) == "unsupported operand type(s) for +: 'NoneType' and 'str'":
                t = traceback.format_exc()
                print(t)
            if str(e) == "maximum recursion depth exceeded while calling a Python object":
                t = traceback.format_exc()
                print(t)
        prefix = get_prefix_from_filename(filename)
        api_map.add_api_map(context.api_map, prefix)
    return api_map

