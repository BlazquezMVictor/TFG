class Operations():
    def __init__(self):
        self.SPECIAL_CHAR = 0
        self.COMMENTS = 1
        self.DATA_TYPE = 2
        self.BUILTIN_CONSTANT = 3
        self.BUILTIN_FUNCTION = 4
        self.STD_GATE = 5
        self.GATE_OPERATION = 6

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

class Translator_utils():
    def __init__(self):
        self.ops = Operations()
        self.keys = DictionaryKeyShortcuts()

        self.special_chars = {'(', ')', '[', ']', '{', '}'}

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
            "pi",
            "tau",
            "euler"
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
            "barrier"
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

        self.line_operation = {
            "(": self.ops.SPECIAL_CHAR,
            ")": self.ops.SPECIAL_CHAR,
            "[": self.ops.SPECIAL_CHAR,
            "]": self.ops.SPECIAL_CHAR,
            "]": self.ops.SPECIAL_CHAR,
            "{": self.ops.SPECIAL_CHAR,
            "}": self.ops.SPECIAL_CHAR,

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
            "tau": self.ops.BUILTIN_CONSTANT,
            "euler": self.ops.BUILTIN_CONSTANT,

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