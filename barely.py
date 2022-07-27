import sys
import os
from collections import OrderedDict

class KeywordToken:
    def __init__(self, word):
        self.word = word

    def __str__(self) -> str:
        return "[Keyword: '" + self.word + "']"

class NameToken:
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return "[Name: '" + self.name + "']"

class OpenParenthesisToken:
    def __str__(self) -> str:
        return "[OpenParenthesis]"

class ClosedParenthesisToken:
    def __str__(self) -> str:
        return "[ClosedParenthesis]"

class OpenCurlyBracketToken:
    def __str__(self) -> str:
        return "[OpenCurlyBracket]"

class ClosedCurlyBracketToken:
    def __str__(self) -> str:
        return "[ClosedCurlyBracket]"

class SemiColonToken:
    def __str__(self) -> str:
        return "[SemiColon]"

class ColonToken:
    def __str__(self) -> str:
        return "[Colon]"

class CommaToken:
    def __str__(self) -> str:
        return "[Comma]"

class StringToken:
    def __init__(self, string):
        self.string = string

    def __str__(self) -> str:
        return "[String: '" + self.string + "']"

class NumberToken:
    def __init__(self, number):
        self.number = number

    def __str__(self) -> str:
        return "[Number: '" + str(self.number) + "']"

def is_num(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

keywords = ["function", "return", "variable"]

def tokenize_small(contents):
    tokens = []

    if contents in keywords:
        tokens.append(KeywordToken(contents))
    elif is_num(contents):
        tokens.append(NumberToken(int(contents)))
    elif contents.strip():
        tokens.append(NameToken(contents))

    return tokens

def tokenize(contents):
    tokens = []

    buffer = ""
    in_quotes = False
    for character in contents:
        if character == ' ' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            buffer = ""
        elif character == '(' and not in_quotes:
            tokens.append(NameToken(buffer))
            tokens.append(OpenParenthesisToken())
            buffer = ""
        elif character == ')' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(ClosedParenthesisToken())
            buffer = ""
        elif character == '{' and not in_quotes:
            tokens.append(OpenCurlyBracketToken())
        elif character == '}' and not in_quotes:
            tokens.append(ClosedCurlyBracketToken())
        elif character == ';' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(SemiColonToken())
            buffer = ""
        elif character == ',' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(CommaToken())
            buffer = ""
        elif character == ':' and not in_quotes:
            tokens.extend(tokenize_small(buffer))
            tokens.append(ColonToken())
            buffer = ""
        elif character == '"':
            if in_quotes:
                tokens.append(StringToken(buffer))
                buffer = ""
                in_quotes = False
            else:
                in_quotes = True
        elif character == '\t' or character == '\n':
            pass
        else:
            buffer += character


    return tokens

class FunctionNode:
    def __init__(self, name, instructions, parameters, returns, locals):
        self.name = name
        self.instructions = instructions
        self.parameters = parameters
        self.returns = returns
        self.locals = locals

class InvokeNode:
    def __init__(self, name):
        self.name = name

class RetrieveNode:
    def __init__(self, name):
        self.name = name

class AssignNode:
    def __init__(self, name):
        self.name = name

class StringNode:
    def __init__(self, string):
        self.string = string

class IntegerNode:
    def __init__(self, integer):
        self.integer = integer

class ReturnNode:
    pass

def generate_ast(tokens):
    ast = []
    
    current_function = None
    index = 0
    while index < len(tokens):
        token = tokens[index]

        if isinstance(token, KeywordToken):
            if token.word == "function":
                current_function, index = get_function_declaration(tokens, index + 1)
                ast.append(current_function)
            elif token.word == "return":
                statement, index = get_expression(tokens, index + 1)

                if current_function:
                    current_function.instructions.extend(statement)
                    current_function.instructions.append(ReturnNode())
            elif token.word == "variable":
                index2 = index
                statement, index = get_assign(tokens, index + 1)
                #print(index - index2)

                if current_function:
                    current_function.instructions.extend(statement)
        else:
            statement, index = get_expression(tokens, index)

            if current_function:
                current_function.instructions.extend(statement)

        index += 1

    for function in ast:
        for instruction in function.instructions:
            if isinstance(instruction, AssignNode):
                if not instruction.name in function.locals:
                    function.locals.append(instruction.name)

    return ast

def get_function_declaration(tokens, index):
    name = None
    searching_returns = False
    parameters = OrderedDict()
    returns = []

    name_index = 0
    parameter_name_cache = ""

    while not isinstance(tokens[index], OpenCurlyBracketToken):
        token = tokens[index]

        if isinstance(token, NameToken) and not name:
            name = token.name
        elif isinstance(token, ClosedParenthesisToken):
            searching_returns = True
        elif isinstance(token, NameToken) and searching_returns:
            returns.append(token.name)
        elif isinstance(token, NameToken):
            if name_index % 2 == 1:
                parameters[parameter_name_cache] = token.name
            else:
                parameter_name_cache = token.name
            name_index += 1

        index += 1

    # TODO: actually calculate parameters
    return FunctionNode(name, [], parameters, returns, []), index

def get_expression(tokens, index):
    statement = []

    if isinstance(tokens[index], NameToken) and isinstance(tokens[index + 1], OpenParenthesisToken):
        invoke, index = get_invoke(tokens, index + 1, tokens[index].name)
        statement.extend(invoke)
    elif isinstance(tokens[index], NameToken):
        retrieve, index = get_retrieve(index + 1, tokens[index].name)
        statement.extend(retrieve)
    elif isinstance(tokens[index], StringToken):
        statement.append(StringNode(tokens[index].string))
        index += 1
    elif isinstance(tokens[index], NumberToken):
        statement.append(IntegerNode(tokens[index].number))
        index += 1

    return statement, index

def get_invoke(tokens, index, name):
    statement = []

    index += 1
    while not isinstance(tokens[index], ClosedParenthesisToken):
        expression, index = get_expression(tokens, index)
        statement = expression + statement
        if isinstance(tokens[index], CommaToken):
            index += 1

    statement.append(InvokeNode(name))

    index += 1

    return statement, index

def get_assign(tokens, index):
    statement = []

    name = None
    expression = False

    while not isinstance(tokens[index], SemiColonToken):
        token = tokens[index]

        if expression:
            expression, index = get_expression(tokens, index)
            statement.extend(expression)

        if isinstance(token, NameToken) and not name:
            name = token.name
            index += 1
        elif isinstance(token, NameToken) and token.name == "=":
            expression = True
            index += 1

    statement.append(AssignNode(name))

    return statement, index

def get_retrieve(index, name):
    statement = []

    statement.append(RetrieveNode(name))

    return statement, index

def get_size_linux_x86_64(types):
    size = 0

    for type in types:
        if type == "*" or type == "integer":
            size += 8

    return size

def compile_linux_x86_64(ast, name):
    fasm_file = open("build/" + name + ".asm", 'w')
    contents = "format ELF64 executable\n"
    contents += "entry start\n"
    contents += "segment readable executable\n"
    contents += "start:\n"
    contents += "call main\n"
    contents += "mov rax, 60\n"
    contents += "mov rdi, 1\n"
    contents += "syscall\n"

    contents += "@print:\n"
    contents += "push rbp\n"
    contents += "mov rbp, rsp\n"
    contents += "mov rax, 1\n"
    contents += "mov rdi, 1\n"
    contents += "mov rsi, [rbp+16]\n"
    contents += "mov rdx, [rbp+24]\n"
    contents += "syscall\n"
    contents += "mov rsp, rbp\n"
    contents += "pop rbp\n"
    contents += "ret\n"

    contents += "@length:\n"
    contents += "push rbp\n"
    contents += "mov rbp, rsp\n"
    contents += "mov rax, 0\n"
    contents += "mov rdi, [rbp+16]\n"
    contents += "mov rcx, -1\n"
    contents += "repne scasb\n"
    contents += "not rcx\n"
    contents += "sub rcx, 1\n"
    contents += "mov r8, rcx\n"
    contents += "mov rsp, rbp\n"
    contents += "pop rbp\n"
    contents += "ret\n"

    contents_data = ""
    data_index = 0

    #Builtin functions
    functions = {}
    functions["@print"] = FunctionNode("@print", [], ["*", "integer"], [], [])
    functions["@length"] = FunctionNode("@length", [], ["*"], ["integer"], [])

    for function in ast:
        functions[function.name] = function

    for function in ast:
        contents += function.name + ":\n"

        contents += "push rbp\n"
        contents += "mov rbp, rsp\n"

        for instruction in function.instructions:
            if isinstance(instruction, InvokeNode):
                contents += "call " + instruction.name + "\n"
                contents += "add rsp, " + str(get_size_linux_x86_64(functions[instruction.name].parameters)) + "\n"
                for i in range(0, get_size_linux_x86_64(functions[instruction.name].returns) // 8):
                    contents += "push r" + str(8 + i) + "\n"
            elif isinstance(instruction, RetrieveNode):
                if instruction.name in function.parameters:
                    # TODO: 8 bytes only...
                    i = -1

                    for index, parameter in enumerate(function.parameters):
                        if parameter == instruction.name:
                            i = index

                    contents += "push qword [rbp+" + str(16 + 8 * i) + "]\n"
                else:
                    i = function.locals.index(instruction.name)
                    contents += "push qword [rbp-" + str(8 + 8 * i) + "]\n"
            elif isinstance(instruction, AssignNode):
                i = function.locals.index(instruction.name)
                contents += "pop qword [rbp-" + str(8 + 8 * i) + "]\n"
            elif isinstance(instruction, StringNode):
                #contents += "push " + str(len(instruction.string)) + "\n"
                contents += "push _" + str(data_index) + "\n"
                contents_data += "_" + str(data_index) + ": db \"" + instruction.string + "\", 0\n"
                data_index += 1
            elif isinstance(instruction, IntegerNode):
                contents += "push " + str(instruction.integer) + "\n"
            elif isinstance(instruction, ReturnNode):
                # TODO: only works with 8 byte sized types (technically smaller too but could be more compact)
                for i in range(0, len(functions[function.name].returns)):
                    contents += "pop r" + str(8 + i) + "\n"

                contents += "mov rsp, rbp\n"
                contents += "pop rbp\n"
                contents += "ret\n"

        contents += "mov rsp, rbp\n"
        contents += "pop rbp\n"
        contents += "ret\n"

    contents += "segment readable\n"
    contents += contents_data

    fasm_file.write(contents)
    fasm_file.close()

    os.system("fasm " + fasm_file.name + " build/" + name)

file = open(sys.argv[1])
contents = file.read()

tokens = tokenize(contents)
ast = generate_ast(tokens)

if not os.path.exists("build"):
    os.makedirs("build")

compile_linux_x86_64(ast, file.name.replace(".barely", ""))
