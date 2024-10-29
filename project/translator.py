class Translator():
    def __init__(self):
        
        self.translated_code_info = {
            self.keys.trans_code_info.QUBITS:       {"amount": 0, "lines": []},
            self.keys.trans_code_info.BITS:         {"amount": 0, "lines": []},
            self.keys.trans_code_info.CUSTOM_GATES: {"amount": 0, "lines": []},
            self.keys.trans_code_info.INSTRUCTIONS: {"amount": 0, "lines": []},
            self.keys.trans_code_info.VARS_REF:     {}
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
            raise Exception("NO SUCH METHOD WITHIN 'translator' CLASS")
        
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
    
    translator = Translator()
    translator.translate(code1)

    for info in translator.translated_code_info.values():
        print(info)
    
    print()
    print("TRANSLATED CODE:")
    
    for key in translator.translated_code_info.keys():
        if key != translator.keys.trans_code_info.VARS_REF:
            lines = translator.translated_code_info[key]["lines"]
            for line in lines:
                print(line)