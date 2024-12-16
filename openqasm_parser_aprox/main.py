import pathlib

from main_translator import MainTranslator
# TODO:
# Mirar el final de los tipos de la documentacion ("Register concatenation and slicing", "Classical value bit slicing", "Array concatenation and slicing")

TEST_DIR = pathlib.Path(__file__).parent
filename = "parser_code.txt"
# filename = "parser_data_types.txt"
# filename = "parser_complex.txt"

grammar_words = {
    "program",
    "version",
    "statementOrScope",
    "statement",
    "annotation",
    "scope",
    "pragma",

    # Statement stuff
    "aliasDeclarationStatement",
    "assignmentStatement",
    "barrierStatement",
    "boxStatement",
    "breakStatement",
    "calStatement",
    "calibrationGrammarStatement",
    "classicalDeclarationStatement",
    "constDeclarationStatement",
    "continueStatement",
    "defStatement",
    "defcalStatement",
    "delayStatement",
    "endStatement",
    "expressionStatement",
    "externStatement",
    "forStatement",
    "gateCallStatement",
    "gateStatement",
    "ifStatement",
    "includeStatement",
    "ioDeclarationStatement",
    "measureArrowAssignmentStatement",
    "oldStyleDeclarationStatement",
    "quantumDeclarationStatement",
    "resetStatement",
    "returnStatement",
    "switchStatement",
    "whileStatement",
    
    # START top-level statement definitions
    # Inclusion statements

    # Control-flow stuff
    "scalarType",
    "setExpression",
    "rangeExpression",
    "expression",
    "measureExpression",
    "switchCaseItem",
    "expressionList",

    # Quantum directive statements stuff
    "gateOperandList",
    "designator",
    "gateModifier",
    "indexedIdentifier",
    "gateOperand",

    # Primite declaration statements
    "aliasExpression",
    "arrayType",
    "declarationExpression",
    "qubitType",

    # Declaration and definitions of higher-order objects
    "argumentDefinitionList",
    "returnSignature",
    "externArgumentList",
    "identifierList",

    # Non declaration assignments and calculations

    # Statements where the bulk is in the calibration language
    "defcalTarget",
    "defcalArgumentDefinitionList",
    "defcalOperandList",
    # END top-level statement definitions

    # START expression deefinitions
    "indexOperator",
    "arrayLiteral",
    # END  expression definitions

    # START type definitions
    "arrayReferenceType",
    "defcalArgumentDefinition",
    "argumentDefinition",
    "defcalOperand",
    "externArgument",
    # END type definitions


}
irrelevant_words = {
    ";",
    # ",",
    "<EOF>"
}

def remove_jump_line(code):
    result = []
    for line in code:
        result.append(line.replace("\n", ""))

    return result

# TODO:
# Junta metodos "remove_blank_spaces" y "get_relevant_info"
def remove_blank_spaces(code):
    word_to_exclude_from_starting_code = {"program", "includeStatement"}
    result = []

    for line in code:
        line = line.split(" ")
        line_result = []
        statement_found = False
        append = True

        for word in line:
            if word in word_to_exclude_from_starting_code:
                append = False
                break

            if statement_found and word != "":
                line_result.append(word)

            if not statement_found:
                line_result.append(word)

            if not statement_found and word == "statement":
                statement_found = True
        
        if append and statement_found:
            result.append(line_result)

    return result

def get_line_indent(line):
    indent = 0

    for word in line:
        if word != "":
            return indent
        indent += 1

def get_info(line):
    result = []

    for word in line:
        if word not in grammar_words and word not in irrelevant_words:
            result.append(word)

    return result

def get_relevant_info(code):
    result = []
    last_indent = -1
    parsed_indent = -1

    for line in code:
        indent = get_line_indent(line)
        info = get_info(line[indent:])

        if indent > last_indent:
            parsed_indent += 1
            last_indent = indent
        
        elif indent < last_indent:
            parsed_indent -= 1
            last_indent = indent

        result.append((parsed_indent, info))

    return result

# MAIN
if __name__ == "__main__":
    with open(TEST_DIR / filename, "r") as file:
        txt = file.read()

        code = txt.split("statementOrScope")
        translator = MainTranslator()
        
        result = remove_jump_line(code)
        result = remove_blank_spaces(result)
        result = get_relevant_info(result)

        # translated_code = translator.translate(result)

        for line in result:
            print(f"L: {line}")

        # for line in translated_code:
        #     print(f"L: {line}")