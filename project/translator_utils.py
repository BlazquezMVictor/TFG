import numpy as np

class Operations():
    def __init__(self):
        self.SPECIAL_CHAR = 0
        self.MATH_OPERATOR = 1
        self.COMMENTS = 2
        self.DATA_TYPE = 3
        self.BUILTIN_CONSTANT = 4
        self.BUILTIN_FUNCTION = 5
        self.STD_GATE = 6
        self.GATE_OPERATION = 7

class TranslatedCodeInfo():
    def __init__(self):
        self.QUBITS = 0
        self.BITS = 1
        self.CUSTOM_GATES = 2
        self.INSTRUCTIONS = 3
        self.VARS_REF = 4

class DictionaryKeyShortcuts():
    def __init__(self):
        self.trans_code_info = TranslatedCodeInfo()

class Utils():
    def __init__(self):
        self.ops = Operations()
        self.keys = DictionaryKeyShortcuts()

        self.special_chars = {"(", ")", "[", "]", "{", "}", "=", " "}
        self.math_operators = {'+', '-', '*', '/'}
        self.comments = {
            "//": "#",
            "/*": "'''",
            "*/": "'''"
        }
        self.data_types = {
            "qubit": "translate_qubit",
            "bit": "translate_bit",
            "int": "translate_int",
            "uint": "translate_int",
            "float": "translate_float",
            "angle": "translate_angle",
            "complex": "translate_complex",
            "bool": "translate_bool",
            "const": "translate_const",
            "duration": "translate_duration",
            "array": "translate_array",
            "stretch": "translate_stretch",
            "let": "translate_let"      # not a data type but an alias -> let myreg = q[1:4]

        }
        self.builtin_constants = {
            "pi": np.pi,
            "π": np.pi,
            "tau": np.pi*2,
            "τ": np.pi*2,
            "euler": np.e,
            "ℇ": np.e,
            "im": 1j
        }
        self.builtin_functions = {
            "arcos",
            "arsin",
            "arctan",
            "ceiling",
            "cos",
            "exp",
            "floor",
            "log",
            "mod",
            "popcount",
            "pow",
            "rotl",
            "rotr",
            "sin",
            "sqrt",
            "tan",
            "gate",
            "reset",
            "measure",
            "barrier",
            "real",
            "imag"
        }
        self.std_gates = {
            "p",
            "x",
            "y",
            "z",
            "h",
            "s",
            "sdg",
            "t",
            "tdg",
            "sx",
            "rx",
            "ry",
            "rz",
            "cx",
            "cy",
            "cz",
            "cp",
            "crx",
            "cry",
            "crz",
            "ch",
            "swap",
            "ccx",
            "cswap",
            "cu",
            "U",
            "gphase",
        }
        self.gate_operations = {
            "ctrl",     # 'ctrl @' indicates that the following gate is controlled -> ctrl @ rz(pi) q1, q2; q1 is control & q2 is target
            "negctrl",  # it is as 'ctrl' but uses 0 as activation bit instead of 1
            "pow"
        }
        self.operation = {
            "(": self.ops.SPECIAL_CHAR,
            ")": self.ops.SPECIAL_CHAR,
            "[": self.ops.SPECIAL_CHAR,
            "]": self.ops.SPECIAL_CHAR,
            "]": self.ops.SPECIAL_CHAR,
            "{": self.ops.SPECIAL_CHAR,
            "}": self.ops.SPECIAL_CHAR,
            "=": self.ops.SPECIAL_CHAR,
            " ": self.ops.SPECIAL_CHAR,

            "//": self.ops.COMMENTS,
            "/*": self.ops.COMMENTS,
            "*/": self.ops.COMMENTS,

            "qubit": self.ops.DATA_TYPE,
            "bit": self.ops.DATA_TYPE,
            "int": self.ops.DATA_TYPE,
            "uint": self.ops.DATA_TYPE,
            "float": self.ops.DATA_TYPE,
            "angle": self.ops.DATA_TYPE,
            "complex": self.ops.DATA_TYPE,
            "bool": self.ops.DATA_TYPE,
            "const": self.ops.DATA_TYPE,
            "duration": self.ops.DATA_TYPE,
            "array": self.ops.DATA_TYPE,
            "stretch": self.ops.DATA_TYPE,
            "let": self.ops.DATA_TYPE,

            "pi": self.ops.BUILTIN_CONSTANT,
            "π": self.ops.BUILTIN_CONSTANT,
            "tau": self.ops.BUILTIN_CONSTANT,
            "τ": self.ops.BUILTIN_CONSTANT,
            "euler": self.ops.BUILTIN_CONSTANT,
            "ℇ": self.ops.BUILTIN_CONSTANT,
            "im": self.ops.BUILTIN_CONSTANT,

            "arcos": self.ops.BUILTIN_FUNCTION,
            "arsin": self.ops.BUILTIN_FUNCTION,
            "arctan": self.ops.BUILTIN_FUNCTION,
            "ceiling": self.ops.BUILTIN_FUNCTION,
            "cos": self.ops.BUILTIN_FUNCTION,
            "exp": self.ops.BUILTIN_FUNCTION,
            "floor": self.ops.BUILTIN_FUNCTION,
            "log": self.ops.BUILTIN_FUNCTION,
            "mod": self.ops.BUILTIN_FUNCTION,
            "popcount": self.ops.BUILTIN_FUNCTION,
            "pow": self.ops.BUILTIN_FUNCTION,
            "rotl": self.ops.BUILTIN_FUNCTION,
            "rotr": self.ops.BUILTIN_FUNCTION,
            "sin": self.ops.BUILTIN_FUNCTION,
            "sqrt": self.ops.BUILTIN_FUNCTION,
            "tan": self.ops.BUILTIN_FUNCTION,
            "gate": self.ops.BUILTIN_FUNCTION,
            "reset": self.ops.BUILTIN_FUNCTION,
            "measure": self.ops.BUILTIN_FUNCTION,
            "barrier": self.ops.BUILTIN_FUNCTION,
            "real": self.ops.BUILTIN_FUNCTION,
            "imag": self.ops.BUILTIN_FUNCTION,

            "p": self.ops.STD_GATE,
            "x": self.ops.STD_GATE,
            "y": self.ops.STD_GATE,
            "z": self.ops.STD_GATE,
            "h": self.ops.STD_GATE,
            "s": self.ops.STD_GATE,
            "sdg": self.ops.STD_GATE,
            "t": self.ops.STD_GATE,
            "tdg": self.ops.STD_GATE,
            "sx": self.ops.STD_GATE,
            "rx": self.ops.STD_GATE,
            "ry": self.ops.STD_GATE,
            "rz": self.ops.STD_GATE,
            "cx": self.ops.STD_GATE,
            "cy": self.ops.STD_GATE,
            "cz": self.ops.STD_GATE,
            "cp": self.ops.STD_GATE,
            "crx": self.ops.STD_GATE,
            "cry": self.ops.STD_GATE,
            "crz": self.ops.STD_GATE,
            "ch": self.ops.STD_GATE,
            "swap": self.ops.STD_GATE,
            "ccx": self.ops.STD_GATE,
            "cswap": self.ops.STD_GATE,
            "cu": self.ops.STD_GATE,
            "U": self.ops.STD_GATE,
            "gphase": self.ops.STD_GATE,

            "ctrl": self.ops.GATE_OPERATION,
            "negctrl": self.ops.GATE_OPERATION,
            "pow": self.ops.GATE_OPERATION
        }
        self.translated_code_info = {
            self.keys.trans_code_info.QUBITS:       {"amount": 0, "lines": []},
            self.keys.trans_code_info.BITS:         {"amount": 0, "lines": []},
            self.keys.trans_code_info.CUSTOM_GATES: {"amount": 0, "lines": []},
            self.keys.trans_code_info.INSTRUCTIONS: {"amount": 0, "lines": []},
            self.keys.trans_code_info.VARS_REF:     {}
        }
        self.translated_code = []

    def translate_internal_expr(self, expression):
        internal_expr = ""
        index_char = 0
        start_reading = False

        for char in expression:
            if char == ")":
                index_char += 1
                return self.translate_expression(internal_expr), index_char
            
            if start_reading:
                internal_expr += char

            if char == "(":
                start_reading = True
            
            index_char += 1

    def translate_expression_word(self, index_char, expression, word):
        new_expression = expression[index_char:]
                
        try:    operation = self.operation[word]
        except: operation = "Unknown"

        match(operation):                    
            # Casting
            case self.ops.DATA_TYPE:
                result, index_char_addition = self.translate_internal_expr(new_expression)
                result = f"{word}({result})"

            case self.ops.BUILTIN_CONSTANT:
                index_char_addition = 0
                result = self.builtin_constants[word]
            
            case self.ops.BUILTIN_FUNCTION:
                result , index_char_addition = self.translate_internal_expr(new_expression)
                result = f"{self.builtin_functions[word]}({result})"

            case "Unknown":
                # Number
                if word.isdigit():
                    result = word
                    index_char_addition = 0

                # Variable
                else:
                    # Array access
                    if new_expression[0] == "[":
                        variable_access = ""
                        index_char = 0

                        for char in new_expression:
                            index_char += 1
                            variable_access += char

                            if char == "]":
                                break

                        result = word + variable_access
                        index_char_addition = index_char

                    # Not array
                    else:
                        result = word
                        index_char_addition = 0

        return result, index_char_addition

    def translate_expression(self, expression):
        '''
        Process:
        - Check data type (casting)
        - Check builtin function
        - Check builtin constant
        - Check variable
        - Check number
        '''
        
        '''
        UCs:
        complex[float] d = int(2.0) + sin(pi/2) + (my_var * 5.5 im);
        complex[float] d = int[4](2.0) + sin(pi/2) + (my_var * 5.5 im);
        '''
        
        word = ""
        translation = ""

        for index_char in range(len(expression)):
            char = expression[index_char]

            if char == ";":
                continue

            if char == " " or char in self.math_operators:
                if word == "":
                    translation += char

                else:
                    result, index_char_addition = self.translate_expression_word(index_char, expression, word)

                    translation += result + char
                    index_char += index_char_addition
                    word = ""

            elif char in self.special_chars:
                result, index_char_addition = self.translate_expression_word(index_char, expression, word)

                translation += result
                index_char += index_char_addition
                word = ""
                
            else:
                word += char

        if word != "":
            result, _ = self.translate_expression_word(index_char, expression, word)
            translation += result

        return translation
        
    # TODO
    # Probar que self.translate_expression funciona
            

    # DATA TYPES TRANSLATIONS
    def translate_qubit(self, index_line, line):
        '''
        UCs:
        qubit[3] my_var;
        qubit my_var;
        '''
        line_splitted = line.split(" ")

        # Get qubit amount
        amount_qubits = 1
        if line_splitted[0] != "":
            amount_qubits = int(line_splitted[0][1:-1]) # Remove square brackets

        # Get var ID
        var_id = line_splitted[1][:-1]

        # Translate the line
        translated_line = f"QRegistry({amount_qubits}) {var_id}"

        # Update translation info
        self.translated_code_info[self.keys.trans_code_info.QUBITS]["amount"] += amount_qubits
        self.translated_code_info[self.keys.trans_code_info.QUBITS]["lines"].append(translated_line)
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id
        self.translated_code.append(translated_line)

    def translate_bit(self, index_line, line):
        '''
        UCs:
        bit my_var;
        bit my_var = "1";
        bit[8] my_var;
        bit[8] my_var = "00001111";
        '''

        line_splitted = line.split(" ")

        # Get bit amount
        amount_bits = 1
        if line_splitted[0] != "":
            amount_bits = int(line_splitted[0][1:-1]) # Remove square brackets

        # No value assignation
        if len(line_splitted) == 2:
            var_id = line_splitted[1][:-1]
            value = [0 for i in range(amount_bits)]

        # Value assignation
        else:
            var_id = line_splitted[1]
            value = [int(char) for char in line_splitted[-1][1:-2]]

        # Translate the line
        translated_line = f"{var_id} = {value}"

        # Update translation info
        self.translated_code_info[self.keys.trans_code_info.BITS]["amount"] += amount_bits
        self.translated_code_info[self.keys.trans_code_info.BITS]["lines"].append(translated_line)
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id
        self.translated_code.append(translated_line)

    def translate_int(self, index_line, line):
        '''
        UCs:
        uint/int[16] my_var = 10;
        uint/int[16] my_var;
        uint/int my_var = 10;
        uint/int my_var;
        '''

        line_splitted = line.split(" ")

        if line_splitted[0] != "":
            amount_int_bits = int(line_splitted[0][1:-1])   # Remove square brackets

        # No value assignation
        if len(line_splitted) == 2:
            var_id = line_splitted[1][:-1]
            value = ""

        # Value assignation
        else:
            var_id = line_splitted[1]
            value = f" = {line_splitted[-1][:-1]}"

        # Translate the line
        translated_line = f"{var_id}: int{value}"

        # Update translation info
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["amount"] += 1
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["lines"].append(translated_line)
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id
        self.translated_code.append(translated_line)

    def translate_float(self, index_line, operation, line):
        '''
        UCs:
        float[16] my_var = π;
        float[16] my_var;
        float my_var = 2.3;
        float my_var;
        '''

        if line != "":
            amount_float_bits = int(line[1:-1])   # Remove square brackets

         # Check in which UC we are
        amount_operation = len(operation)
        # No value assignation
        if amount_operation == 1:
            var_id = operation[0][:-1]
            value = ""

        # Value assignation
        elif amount_operation > 1:
            var_id = operation[0]
            value = operation[2][:-1]
            if value in self.builtin_constants:     value = f" = {self.builtin_constants[value]}"
            else:                                   value = f" = {value}"

        # Translate the line
        translated_line = f"{var_id}: int{value}"

        # Update translation info
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["amount"] += 1
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["lines"].append(translated_line)
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id
        self.translated_code.append(translated_line)

    def translate_angle(self, index_line, operation, line):
        pass

    def translate_complex(self, index_line, operation, line):
        pass

    def translate_bool(self, index_line, operation, line):
        pass

    def translate_const(self, index_line, operation, line):
        pass

    def translate_duration(self, index_line, operation, line):
        pass

    def translate_array(self, index_line, operation, line):
        pass

    def translate_strech(self, index_line, operation, line):
        pass

    def translate_let(self, index_line, operation, line):
        pass