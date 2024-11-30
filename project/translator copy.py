from translator_utils import Operations, DictionaryKeyShortcuts, Utils

class Translator():
    def __init__(self):
        self.ops = Operations()
        self.keys = DictionaryKeyShortcuts()
        self.utils = Utils()

    def translate_data_type(self, index_line, data_type, line):
        method_name = self.utils.data_types[data_type]
        
        try:        method = getattr(self.utils, method_name)
        except:     raise Exception("NO SUCH METHOD WITHIN 'Utils' CLASS")
        
        method(index_line, line)

    def translate(self, code:str):
        code_lines = code.split("\n")
        index_line = -1

        for line in code_lines:
            index_line += 1
            index_char = 0

            word = ""
            for char in line:
                if char in self.utils.special_chars:
                    new_line = line[index_char:]
                    break

                word += char
                index_char += 1
            
            try:        operation = self.utils.operation[word]
            except:     raise Exception("Unknown operation " + word)

            match(operation):
                case self.ops.SPECIAL_CHAR:
                    pass
                
                case self.ops.COMMENTS:
                    continue
                
                case self.ops.DATA_TYPE:
                    self.translate_data_type(index_line=index_line, data_type=word, line=new_line)
                
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

    code1 = '''complex[float] d = int[4](2.0) - (5 + sin(pi/2)) + (my_var * 5.5 im);'''
    
    translator = Translator()
    translator.translate(code1)

    for info in translator.utils.translated_code_info.values():
        print(info)
    
    print()
    print("TRANSLATED CODE:")
    
    for line in translator.utils.translated_code:
        print(line)