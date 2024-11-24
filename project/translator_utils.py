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
            "pi": "np.pi",
            "π": "np.pi",
            "tau": "np.pi*2",
            "τ": "np.pi*2",
            "euler": "np.e",
            "ℇ": "np.e",
            "im": "1j"
        }
        self.builtin_functions = {
            "arcos": "np.arccos",
            "arsin": "np.arcsin",
            "arctan": "np.arctan",
            "ceiling": "np.ceil",
            "cos": "np.cos",
            "exp": "np.exp",
            "floor": "np.floor",
            "log": "np.log",
            "mod": "np.mod",
            "popcount": "np.count_nonzero",
            "pow": "np.power",
            "rotl": "translator.utils.rotl",
            "rotr": "translator.utils.rotr",
            "sin": "np.sin",
            "sqrt": "np.sqrt",
            "tan": "np.tan",
            # TODO
            # Translate this functions
            # "gate",
            # "reset",
            # "measure",
            # "barrier",
            # "real",
            # "imag"
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

    def rotl(self, array, distance):
        for i in range(distance):
            first = array.pop(0)
            array.append(first)

        return array
    
    def rotr(self, array, distance):
        for i in range(distance):
            first = array.pop()
            array.insert(0, first)

        return array

    def translate_word(self, word):
                
        try:    operation = self.operation[word]
        except: operation = "Unknown"

        match(operation):                    
            # Casting
            case self.ops.DATA_TYPE:
                result = word

            case self.ops.BUILTIN_CONSTANT:
                result = self.builtin_constants[word]
            
            case self.ops.BUILTIN_FUNCTION:
                result = self.builtin_functions[word]

            case "Unknown":
                result = word

        return result

    def translate_expression(self, expression):       
        '''
        UCs:
        complex[float] d = int(2.0) + sin(pi/2) + (my_var * 5.5 im);
        complex[float] d = int[4](2.0) + sin(pi/2) + (my_var * 5.5 im);
        '''
        
        word = ""
        translation = ""
        index_char = 0
        char = expression[0]

        while index_char < len(expression):
            char = expression[index_char]

            if char == " " or char in self.math_operators or char in self.special_chars:
                # There is nothing to translate -> "int(2.0) aleready read and translated, next char is " " and next one "+" "
                if word == "":
                    translation += char

                # There is something to translate:
                # -> pi in "pi/2", we read pi and next char is "/" so we have to translate pi before continuing
                # -> my_var in "(my_var * ..."
                # -> int in "int(2.0) ..."
                else:
                    result = self.translate_word(word)

                    # Add the translation plus the current read char
                    translation += result + char
                    # Reset word to read another expression
                    word = ""
                
            else:
                word += char

            index_char += 1

        return translation            

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

        # if line_splitted[0] != "":
        #     amount_int_bits = int(line_splitted[0][1:-1])   # Remove square brackets

        # No value assignation
        if len(line_splitted) == 2:
            var_id = line_splitted[1][:-1]
            value = ""

        # Value assignation
        else:
            var_id = line_splitted[1]
            pending_line = " ".join(line_splitted[3:])[:-1]
            value = f" = {self.translate_expression(pending_line)}"

        # Translate the line
        translated_line = f"{var_id}: int{value}"

        # Update translation info
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["amount"] += 1
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["lines"].append(translated_line)
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id
        self.translated_code.append(translated_line)

    def translate_float(self, index_line, line):
        '''
        UCs:
        float[16] my_var = π;
        float[16] my_var;
        float my_var = 2.3;
        float my_var;
        '''

        line_splitted = line.split(" ")

        # if line != "":
        #     amount_float_bits = int(line[1:-1])   # Remove square brackets

        # No value assignation
        if len(line_splitted) == 2:
            var_id = line_splitted[1][:-1]
            value = ""

        # Value assignation
        else:
            var_id = line_splitted[1]
            pending_line = " ".join(line_splitted[3:])[:-1]
            value = f" = {self.translate_expression(pending_line)}"

        # Translate the line
        translated_line = f"{var_id}: float{value}"

        # Update translation info
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["amount"] += 1
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["lines"].append(translated_line)
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id
        self.translated_code.append(translated_line)

    def translate_angle(self, index_line, line):
        pass

    def translate_complex(self, index_line, line):
        '''
        UCs:
        complex[float[16]] my_var = π;
        complex[float[16]] my_var;
        complex[float] my_var = 2.3;
        complex[float] my_var;
        '''

        line_splitted = line.split(" ")

        # Here it is different
        # if line != "":
        #     amount_float_bits = int(line[1:-1])   # Remove square brackets

        # No value assignation
        if len(line_splitted) == 2:
            var_id = line_splitted[1][:-1]
            value = ""

        # Value assignation
        else:
            var_id = line_splitted[1]
            pending_line = " ".join(line_splitted[3:])[:-1]
            value = f" = {self.translate_expression(pending_line)}"

        # Translate the line
        translated_line = f"{var_id}: complex{value}"

        # Update translation info
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["amount"] += 1
        self.translated_code_info[self.keys.trans_code_info.INSTRUCTIONS]["lines"].append(translated_line)
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id
        self.translated_code.append(translated_line)

    def translate_bool(self, index_line, line):
        pass

    def translate_const(self, index_line, line):
        pass

    def translate_duration(self, index_line, line):
        pass

    def translate_array(self, index_line, line):
        pass

    def translate_strech(self, index_line, line):
        pass

    def translate_let(self, index_line, line):
        pass