import numpy as np
from sympy.matrices import Matrix

class TranslatorUtils:
    # Shared variables used when translating a custom gate
    is_custom_gate = False
    is_custom_def = False
    qsimov_name = "qj"
    QCircuit_name = "qc"

    def __init__(self):
        self.qsimov_name = "qj"
        self.QCircuit_name = "qc"
        self.QGate_name = "custom_gate"

        self.AMOUNT_QUBITS = 0
        self.AMOUNT_BITS = 1
        self.KEY_QUBITS = 2
        self.KEY_BITS = 3
        self.KEY_CUSTOM_GATES = 4
        self.KEY_SUBROUTINES = 5
        self.KEY_SUBROUTINE_PARAMS = 6
        self.KEY_VARS_REF = 7
        self.KEY_NEW_MATRICES = 8
        self.KEY_BIT_INITS = 9

        self.special_chars = {"(", ")", "[", "]", "{", "}", "="}
        self.math_logic_operators = {
            '+': "+",
            '-': '-',
            '*': '*',
            '/': '/',
            '%': '%',
            '**': '**',
            '+=': '+=',
            '-=': '-=',
            '*=': '*=',
            '/=': '/=',
            '%=': '%=',
            '**=': '**=',
            
            '>': '>',
            '<': '<',
            '>=': '>=',
            '<=': '<=',
            '==': '==',
            '!=': '!=',
            '=': '=',

            "++": "++",

            '^': '^',
            '<<': '<<',
            '>>': '>>',
            '|': '|',
            '&': '&',
            '~': '-',
            '&&': 'and',
            '||': 'or',
            '&=': '&=',
            '|=': '|=',
            '^=': "^=",
            '<<=': '<<=',
            '>>=': '>>=',

            'true': 'True',
            'false': 'False'
        }
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
            "angle": "translate_float",
            "complex": "translate_complex",
            "bool": "translate_bool",
            "const": "translate_const",
            "array": "translate_array",
            "let": "translate_let",      # not a data type but an alias -> let myreg = q[1:4]
            "duration": "translate_duration",
            "stretch": "translate_stretch",
            "input": "translate_input",
            "output": "translate_output"

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
            "sin": "np.sin",
            "sqrt": "np.sqrt",
            "tan": "np.tan",
            "real": ".real",
            "imag": ".imag",
            "sizeof": "len"
        }
        self.std_gates = {
            "p": "translate_p",
            "x": "translate_x",
            "y": "translate_y",
            "z": "translate_z",
            "h": "translate_h",
            "s": "translate_s",
            "sdg": "translate_sdg",
            "t": "translate_t",
            "tdg": "translate_tdg",
            "sx": "translate_sx",
            "rx": "translate_rx",
            "ry": "translate_ry",
            "rz": "translate_rz",
            "cx": "translate_cx",
            "cy": "translate_cy",
            "cz": "translate_cz",
            "cp": "translate_cp",
            "crx": "translate_crx",
            "cry": "translate_cry",
            "crz": "translate_crz",
            "ch": "translate_ch",
            "swap": "translate_swap",
            "ccx": "translate_ccx",
            "cswap": "translate_cswap",
            "cu": "translate_cu",
            "U": "translate_u",
            "gphase": "translate_gphase",
        }
        self.gate_operations = {
            "ctrl": "translate_mod",     # 'ctrl @' indicates that the following gate is controlled -> ctrl @ rz(pi) q1, q2; q1 is control & q2 is target
            "negctrl": "translate_mod",  # it is as 'ctrl' but uses 0 as activation bit instead of 1
            "inv": "translate_mod",
            "pow": "translate_mod",
            "reset": "translate_reset",
            "barrier": "translate_barrier",
        }
        self.classic_instructions = {
            "rotl": "translate_rotl",
            "rotr": "translate_rotr",
            "if": "translate_if_else",
            "else": "translate_if_else",
            "for": "translate_for",
            "while": "translate_while",
            "break": "translate_break",
            "continue": "translate_continue",
            "return": "translate_return",
            "end": "translate_end",              # It terminates the program
            # "switch": "match",      # Not yet implemented in openqasm
            # "case": "case",         # Not yet implemented in openqasm
            # "default": "case _",    # Not yet implemented in openqasm

        }
    
    def matrix_square_roots(matrix):
        # Verify that the input is square
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Input matrix must be square.")

        # Perform eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eig(matrix)

        # Compute principal square root of eigenvalues
        sqrt_eigenvalues = np.diag(np.emath.sqrt(eigenvalues))

        # Reconstruct the principal square root
        principal_sqrt = eigenvectors @ sqrt_eigenvalues @ np.linalg.inv(eigenvectors)

        return Matrix(principal_sqrt)