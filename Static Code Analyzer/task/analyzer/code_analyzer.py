import sys
import fileinput
import re
import os
import ast
import builtins

NEW_LINE_COUNT = 0


def pep_style_001(file_name, line_number, line_content):
    if len(line_content) > 79:
        return f"{file_name}: Line {line_number}: S001 Too Long"


def pep_style_002(file_name, line_number, line_content):
    if line_content == '\n':
        return
    if (len(line_content) - len(line_content.lstrip())) % 4 != 0:
        return f"{file_name}: Line {line_number}: S002 Indentation is not a multiple of four"


def pep_style_003(file_name, line_number, line_content):
    if ';' in line_content and "'" in line_content:
        string_list = line_content.split("'")[1::2]
        for string in string_list:
            if ';' in string:
                return
    if ';' in line_content and '#' in line_content:
        if line_content.find(';') < line_content.find('#') != -1:
            return f"{file_name}: Line {line_number}: S003 Unnecessary semicolon"
    elif ';' in line_content:
        return f"{file_name}: Line {line_number}: S003 Unnecessary semicolon"


def pep_style_004(file_name, line_number, line_content):
    if re.match(r"[^#]*[^ ]( ?#)", line_content):
        return f"{file_name}: Line {line_number}: S004 Less than two spaces before inline comments"
    # if line_content[0] == "#":
    #    return f" Line {line_number}: S004 Less than two spaces before inline comments"


def pep_style_005(file_name, line_number, line_content):
    if line_content.lower().find("todo") > line_content.find('#') != -1:
        return f"{file_name}: Line {line_number}: S005 TODO found"


def pep_style_006(file_name, line_number, line_content):
    global NEW_LINE_COUNT
    if NEW_LINE_COUNT > 2 and line_content != '\n':
        NEW_LINE_COUNT = 0
        return f"{file_name}: Line {line_number}: S006 More than two blank lines used before this line"

    if line_content == '\n':
        NEW_LINE_COUNT += 1
    else:
        NEW_LINE_COUNT = 0


def pep_style_007(file_name, line_number, line_content):
    if line_content.lstrip().startswith('def  '):
        return f"{file_name}: Line {line_number}: S007 Too many spaces after 'def'"
    if line_content.lstrip().startswith('class  '):
        return f"{file_name}: Line {line_number}: S007 Too many spaces after 'class'"


def pep_style_008(file_name, line_number, line_content):
    if line_content.lstrip().startswith('class'):

        pattern = "^([A-Z][a-z]+)*$"
        class_name = line_content.split(' ')[1]
        replacements = [(':', ''), ('(', ''), (')', '')]

        for char, replacement in replacements:
            if char in class_name:
                class_name = class_name.replace(char, replacement)

        if not re.match(pattern, class_name):
            return f"{file_name}: Line {line_number}: S008 Class name '{class_name.rstrip()}' should use CamelCase"


def pep_style_009(file_name, line_number, line_content):
    if line_content.lstrip().startswith('def'):
        pattern = "^_*[a-z0-9]+(?:_[a-z0-9]+)*_*$"
        func_name = line_content.lstrip().replace('(', ' ').replace('  ', ' ').split(' ')[1]
        if not re.match(pattern, func_name):
            return f"{file_name}: Line {line_number}: S009 Function name '{func_name.rstrip()}' should be written in snake_case"


def ast_checks(file_name, file_content):

    tree = ast.parse(file_content)
    snake_pattern = "^_*[a-z0-9]+(?:_[a-z0-9]+)*_*$"
    mutable_types = ["[]", "{", ]
    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                if arg.arg not in vars(builtins) and not re.match(snake_pattern, arg.arg):
                    print(f"{file_name}: Line {arg.lineno}: S010 Argument name '{arg.arg}' should be snake_case")

        if isinstance(node, ast.Name):
            if node.id not in vars(builtins) and not re.match(snake_pattern, node.id) and node.ctx.__class__ != ast.Load:
                print(f"{file_name}: Line {node.lineno}: S011 Variable '{node.id}' in function should be snake_case")

        if isinstance(node, ast.FunctionDef):
            for arg in node.args.defaults:
                if not ast.dump(arg).startswith("Constant"):
                    print(f"{file_name}: Line {arg.lineno}: S012 Default argument value is mutable")


func_list = [pep_style_001,
             pep_style_002,
             pep_style_003,
             pep_style_004,
             pep_style_005,
             pep_style_006,
             pep_style_007,
             pep_style_008,
             pep_style_009]

file_arg = sys.argv
file_path = file_arg[1]

if file_path.endswith('.py'):
    python_files = [file_path]
elif not file_path.endswith('.py'):
    python_files = []
    with os.scandir(file_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith('.py'):
                python_files.append(os.path.relpath(entry))

for file in python_files:
    with open(file, "r") as file:
        text_data = file.readlines()
        text_file = ''.join(text_data)

    ast_checks(file.name, text_file)

    for index, row in enumerate(text_data, start=1):
        for func in func_list:
            message = func(file.name, index, row)
            if message:
                print(message)
