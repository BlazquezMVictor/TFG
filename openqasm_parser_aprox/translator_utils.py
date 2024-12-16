class TranslatorUtils:
    def __init__(self):
        self.KEY_QUBITS = 0
        self.KEY_BITS = 1
        self.KEY_CUSTOM_GATES = 2
        self.KEY_INSTRUCTIONS = 3
        self.KEY_VARS_REF = 4

        self.special_chars = {"(", ")", "[", "]", "{", "}", "="}
        self.math_operators = {'+', '-', '*', '/'}
        self.comments = {
            "//": "#",
            "/*": "'''",
            "*/": "'''"
        }
        # TODO:
        # Dar soporte a los tipos de datos Input/Output
        self.data_types = {
            "qubit": "translate_qubit",
            "bit": "translate_bit",
            "int": "translate_int",
            "uint": "translate_int",
            "float": "translate_float",
            "angle": "translate_float",
            "complex": "translate_complex",
            "bool": "translate_bool",
            "const": "translate_const",
            # "duration": "translate_duration",
            "array": "translate_array",
            # "stretch": "translate_stretch",
            "let": "translate_let"      # not a data type but an alias -> let myreg = q[1:4]

        }
        self.builtin_constants = {
            "pi": "np.pi",
            "π": "np.pi",
            "tau": "np.pi*2",
            "τ": "np.pi*2",
            "euler": "np.e",
            "ℇ": "np.e",
            "im": "j"
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
            "rotl": "rotl",
            "rotr": "rotr",
            "sin": "np.sin",
            "sqrt": "np.sqrt",
            "tan": "np.tan",
            "real": ".real",
            "imag": ".imag"
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
        # TODO:
        # Traducir las gatee_operations
        self.gate_operations = {
            "ctrl",     # 'ctrl @' indicates that the following gate is controlled -> ctrl @ rz(pi) q1, q2; q1 is control & q2 is target
            "negctrl",  # it is as 'ctrl' but uses 0 as activation bit instead of 1
            "pow",
            "gate",       # Puede ocupar mas de una linea
            "reset",
            "measure",
            "barrier",
        }
        self.classic_instructions = {
            "&&": "and",
            "||": "or",
            "if": "if",         # Puede ocupar mas de una linea (recordar que puede tener else statement)
            "for": "for",       # Puede ocupar mas de una linea
            "while": "while",   # Puede ocupar mas de una linea
            "break": "break",
            "continue": "continue",
            "end": "",              # It terminates the program
            "switch": "match",      # Not yet implemented # Puede ocupar mas de una linea
            "case": "case",         # Not yet implemented
            "default": "case _",    # Not yet implemented
            "def": "def",           # Puede ocupar mas de una linea
            "return": "return",

        }

# TODO:
# Mirar si "rotl" y "rotr" devuelven valor o modifican directamente la array
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