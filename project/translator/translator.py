from .type_instr_translator import *
from .translator_utils import TranslatorUtils
from openqasm_grammar import openqasm_reference_parser as parser

class Translator:
    def __init__(self, shots=1):
        self.init_type_instr_translators()
        self.init_data_structures()
        self.shots = shots

    def init_type_instr_translators(self):
        self.translator_utils = TranslatorUtils()
        self.data_type_translator = DataTypeTranslator()
        self.std_gate_translator = STDGateTranslator()
        self.gate_op_translator = GateOperationTranslator()
        self.classic_inst_translator = ClassicInstTranslator()

    def init_data_structures(self):
        self.translated_code_info = {
            self.translator_utils.AMOUNT_QUBITS:           0,
            self.translator_utils.AMOUNT_BITS:             0,
            self.translator_utils.KEY_QUBITS:               {},
            self.translator_utils.KEY_BITS:                 {},
            self.translator_utils.KEY_CUSTOM_GATES:         {},
            self.translator_utils.KEY_SUBROUTINES:          {},
            self.translator_utils.KEY_SUBROUTINE_PARAMS:    {},
            self.translator_utils.KEY_VARS_REF:             {},
            self.translator_utils.KEY_NEW_MATRICES:         {},
            self.translator_utils.KEY_BIT_INITS:            []
        }
        self.translated_code = []

        self.grammar_words = {
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
        self.irrelevant_items = {
            ";",
            "<EOF>"
        }

    def compute_indent(self, amount_tabs):
        tab = "\t"
        indent = ""
        for i in range(amount_tabs):
            indent += tab

        return indent
    
    def add_first_code_lines(self):
        qsimov_name = TranslatorUtils.qsimov_name
        QCircuit_name = TranslatorUtils.QCircuit_name
        amount_qubits = self.translated_code_info[self.translator_utils.AMOUNT_QUBITS]
        amount_bits = self.translated_code_info[self.translator_utils.AMOUNT_BITS]

        if amount_qubits == 0:  amount_qubits = 1

        lines = f"import qsimov as {qsimov_name}\n"
        lines += f"import numpy as np\n"
        lines += f"from sympy.matrices import Matrix\n"
        lines += f"from sympy import I\n"
        lines += f"\n{QCircuit_name} = {qsimov_name}.QCircuit({amount_qubits}, {amount_bits}, \"my_qsimov_circuit\")"

        return [lines]

    def get_translation(self, clean_code):
        custom_gate_init_indent = -1
        custom_def_init_indent = -1
        gate_translation = ""

        for i, line in enumerate(clean_code):
            # Get the keyword of the instruction to know which kind of translation we have to do
            keyword = line[1][0]

            # Check if we have finished translating a custom gate
            if line[0] == custom_gate_init_indent:
                last_line = f"return {self.translator_utils.QGate_name}"
                gate_translation += self.compute_indent(custom_gate_init_indent + 1) + last_line + "\n"

                TranslatorUtils.is_custom_gate = False
                TranslatorUtils.QCircuit_name = self.translator_utils.QCircuit_name
                custom_gate_init_indent = -1

                self.translated_code.append(gate_translation)
                gate_translation = ""

            if line[0] == custom_def_init_indent:
                TranslatorUtils.is_custom_def = False
                custom_def_init_indent = -1
                self.translated_code.append("") # Add a blank line after the custom def

            # Check measurement
            if "measure" in line[1]:
                translation = self.gate_op_translator.translate_measure(i, line[1], self.translated_code_info)

            # Check custom gate definition
            elif keyword == "gate":
                custom_gate_init_indent = line[0]
                translation = self.gate_op_translator.translate_gate(i, line[1][1:], self.translated_code_info)

            # Check custom def definition
            elif keyword == "def":
                custom_def_init_indent = line[0]
                translation = self.classic_inst_translator.translate_def(i, line[1], self.translated_code_info)

            # Check data type
            elif keyword in self.translator_utils.data_types:
                method = self.translator_utils.data_types[keyword]

                if method == "translate_bit":
                    if line[0] != 0:    is_global = False
                    else:               is_global = True
                    translation = self.data_type_translator.translate_bit(i, line[1][1:], is_global, self.translated_code_info)
                
                else:
                    translation = getattr(self.data_type_translator, method)(i, line[1][1:], self.translated_code_info)

            # Check std gate
            elif keyword in self.translator_utils.std_gates:
                method = self.translator_utils.std_gates[keyword]
                translation = getattr(self.std_gate_translator, method)(i, line[1][1:], self.translated_code_info)

            # Check if we are applying a custom gate
            elif keyword in self.translated_code_info[self.translator_utils.KEY_CUSTOM_GATES]:
                translation = self.gate_op_translator.translate_custom_gate(i, line[1], self.translated_code_info)

            # Check gate operation
            elif keyword in self.translator_utils.gate_operations:
                method = self.translator_utils.gate_operations[keyword]
                translation = getattr(self.gate_op_translator, method)(i, line[1], self.translated_code_info)  # This time we maintain the keyword

            # Check variable operation
            elif keyword in self.translated_code_info[self.translator_utils.KEY_VARS_REF]:
                translation = self.classic_inst_translator.translate_var_operation(i, line[1], self.translator_utils.KEY_VARS_REF, self.translated_code_info)
            elif keyword in self.translated_code_info[self.translator_utils.KEY_SUBROUTINE_PARAMS]:
                translation = self.classic_inst_translator.translate_var_operation(i, line[1], self.translator_utils.KEY_SUBROUTINE_PARAMS, self.translated_code_info)
                
            # Check if we are calling a custom function
            elif keyword in self.translated_code_info[self.translator_utils.KEY_SUBROUTINES]:
                translation = self.classic_inst_translator.translate_custom_def(i, line[1], self.translated_code_info)

            # Check classic instruction
            elif keyword in self.translator_utils.classic_instructions:
                method = self.translator_utils.classic_instructions[keyword]
                translation = getattr(self.classic_inst_translator, method)(i, line[1], self.translated_code_info)

            # Check if we are translating a custom gate
            if not TranslatorUtils.is_custom_gate and translation:
                indent = self.compute_indent(line[0])
                translation = indent + translation

                self.translated_code.append(translation)
            elif TranslatorUtils.is_custom_gate:
                # Add the translation to the custom gate
                gate_translation += self.compute_indent(line[0]) + translation + "\n"

        translation = self.add_first_code_lines()
        translation += self.translated_code_info[self.translator_utils.KEY_BIT_INITS]
        translation += ["\n"]
        translation += self.translated_code_info[self.translator_utils.KEY_NEW_MATRICES].values()
        translation += [""]
        translation += self.translated_code

        str_translation = ""
        for line in translation:
            str_translation += line
            str_translation += "\n"

        str_translation += f"\nexecutor = {TranslatorUtils.qsimov_name}.Drewom()\n"
        str_translation += f"result = executor.execute({TranslatorUtils.QCircuit_name}, shots={self.shots})\n"
        # str_translation += f"print(result)"

        return str_translation
    
    def parse_code(self, code):
        return  parser.pretty_tree(program=code)

    def remove_jump_line(self, code):
        result = []
        for line in code:
            result.append(line.replace("\n", ""))

        return result

    # TODO:
    # Junta metodos "remove_blank_spaces" y "get_relevant_info"
    def remove_blank_spaces(self, code):
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

    def get_line_indent(self, line):
        indent = 0

        for word in line:
            if word != "":
                return indent
            indent += 1

    def get_info(self, line):
        result = []

        for word in line:
            if word not in self.grammar_words and word not in self.irrelevant_items:
                result.append(word)

        return result

    def get_relevant_info(self, code):
        result = []
        last_indent = 0
        plus_1_indent_keywords = {"if", "for", "while", "def", "gate"}

        for line in code:
            blank_indent = self.get_line_indent(line)
            info = self.get_info(line[blank_indent:])

            result.append((last_indent, info))

            if info[0] in plus_1_indent_keywords:
                last_indent += 1

            if info[0] != "for" and info[0] != "array":
                item = info[-1]
                i = -1
                while (item == "}"):
                    last_indent -= 1
                    i -= 1
                    item = info[i]
            

        return result

    def remove_scope_brackets(self, code):
        code_length = len(code)
        i = 0

        while i < code_length:
            _, line = code[i]

            if line[0] != "array" and line[0] != "for":
                if line[0] == "else":
                    i += 1
                    continue

                if line[-1] == "else":
                    code.insert(i+1, (code[i+1][0]-1, ["else"]))
                    code_length += 1
                    line.pop(-1)

                item = line[-1]
                while (item == "}"):
                    line.pop(-1)
                    item = line[-1]

            i += 1

    def clean_code(self, code):
        result = code.split("statementOrScope")
        result = self.remove_jump_line(result)
        result = self.remove_blank_spaces(result)
        result = self.get_relevant_info(result)
        self.remove_scope_brackets(result)

        return result
    
    def translate(self, code):
        # self.init_type_instr_translators()
        self.init_data_structures()

        result = self.parse_code(code)
        result = self.clean_code(result)
        result = self.get_translation(result)

        return result