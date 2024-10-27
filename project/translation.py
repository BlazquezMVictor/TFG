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

class Translation():
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

        self.translated_code_info = {
            self.keys.trans_code_info.QUBITS:       {"amount": 0, "lines": []},
            self.keys.trans_code_info.BITS:         {"amount": 0, "lines": []},
            self.keys.trans_code_info.CUSTOM_GATES: {"amount": 0, "lines": []},
            self.keys.trans_code_info.INSTRUCTIONS: {"amount": 0, "lines": []},
            self.keys.trans_code_info.VARS_REF:     {}
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

    def translate_qubit(self, pending_words, extra_info):
        amount_qubits = 1
        if extra_info != "":
            amount_qubits = int(extra_info[1:-1])   # Remove square brackets

        var_id = pending_words[0][:-1]

        self.translated_code_info[self.keys.trans_code_info.QUBITS]["amount"] += amount_qubits
        self.translated_code_info[self.keys.trans_code_info.QUBITS]["lines"].append(f"QRegistry({amount_qubits}) {var_id}")
        self.translated_code_info[self.keys.trans_code_info.VARS_REF][var_id] = var_id


    def translate_data_type(self, data_type, pending_words, extra_info=""):
        method_name = self.data_types[data_type]
        try:
            method = getattr(self, method_name)
        except:
            raise Exception("NO SUCH METHOD WITHIN 'Translation' CLASS")
        
        method(pending_words, extra_info)


    def evaluate_beginning(self, beginnig:str, pending_words:list[str]):
        operation = ""
        stop_index = 0

        for char in beginnig:
            if not char.isalnum():
                break

            operation += char
            stop_index += 1

        try:
            extra_info = beginnig[stop_index:]
        except:
            extra_info = ""

        operation_type = self.line_operation[operation]

        match(operation_type):
            #  caseself.ops.SPECIAL_CHAR:
            #     pass
            
            #  caseself.ops.COMMENTS:
            #     continue
            
            case self.ops.DATA_TYPE:
                self.translate_data_type(data_type=operation, pending_words=pending_words, extra_info=extra_info)
            
            #  caseself.ops.BUILTIN_CONSTANT:
            #     pass
            
            case self.ops.BUILTIN_FUNCTION:
                pass
            
            case self.ops.STD_GATE:
                pass
            
            case self.ops.GATE_OPERATION:
                pass

            case _:
                # Check if we are modifying a variable
                if operation in self.translated_vars_ref:
                    pass

    def translate(self, code:str):
        code_lines = code.split("\n")

        for line in code_lines:
            words = line.split(" ")
            beginning = words[0]
            
            try:
                operation = self.line_operation[beginning]

            except:
                self.evaluate_beginning(beginnig=beginning, pending_words=words[1:])
                continue

            match(operation):
                case self.ops.SPECIAL_CHAR:
                    pass
                
                case self.ops.COMMENTS:
                    continue
                
                case self.ops.DATA_TYPE:
                    self.translate_data_type(data_type=beginning, pending_words=words[1:])
                
                case self.ops.BUILTIN_CONSTANT:
                    pass
                
                case self.ops.BUILTIN_FUNCTION:
                    pass
                
                case self.ops.STD_GATE:
                    pass
                
                case self.ops.GATE_OPERATION:
                    pass


if __name__ == "__main__":
    complex_code = '''
        // quantum teleportation example
        OPENQASM 3; // Version statement is optional
        include "stdgates.inc";
        qubit[3] q;
        bit c0;
        bit c1;
        bit c2;
        // optional post-rotation for state tomography
        // empty gate body => identity gate
        gate post q { }
        reset q;
        U(0.3, 0.2, 0.1) q[0];
        h q[1];
        cx q[1], q[2];
        barrier q;
        cx q[0], q[1];
        h q[0];
        c0 = measure q[0];
        c1 = measure q[1];
        if(c0==1) z q[2];
        if(c1==1) { x q[2]; }  // braces optional in this case
        post q[2];
        c2 = measure q[2];
    '''

    code1 = "qubit[3] q;"
    
    translation = Translation()
    translation.translate(code1)

    for info in translation.translated_code_info.values():
        print(info)
    
    print()
    print("TRANSLATED CODE:")
    
    for key in translation.translated_code_info.keys():
        if key != translation.keys.trans_code_info.VARS_REF:
            lines = translation.translated_code_info[key]["lines"]
            for line in lines:
                print(line)