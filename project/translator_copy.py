from translator_utils_copy import Operations, DictionaryKeyShortcuts, Utils

class Translator():
    def __init__(self):
        self.ops = Operations()
        self.keys = DictionaryKeyShortcuts()
        self.utils = Utils()
        self.mid_translation = []

    def translate_data_type(self, index_line, data_type, line):
        method_name = self.utils.data_types[data_type]
        
        try:        method = getattr(self.utils, method_name)
        except:     raise Exception("NO SUCH METHOD WITHIN 'Utils' CLASS")
        
        method(index_line, line)

    def mid_translate_comments(self, code_lines, word, index_line, begin_line):
        if word == "//":
            end_line = begin_line
            self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.COMMENTS, "COMMENT")})

        else:
            # Compute when the bigger comment ends
            line = code_lines[index_line]
            ending_comment = line[-2:]
            while ending_comment != "*/":
                index_line += 1
                line = code_lines[index_line]
                ending_comment = line[-2:]

            end_line = index_line
            self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.COMMENTS, "COMMENT")})

        return index_line
    
    def mid_translate_builtin_func(self, code_lines, word, index_line, begin_line):
        if word != "gate":
            end_line = begin_line
            self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.BUILTIN_FUNCTION, "BUILTIN_FUNCTION")})

        else:
            # Get when the gate building finishes
            line = code_lines[index_line]
            ending_brace = line[-1]
            while ending_brace != "}":
                index_line += 1
                line = code_lines[index_line]
                ending_brace = line[-1]

            end_line = index_line
            self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.BUILTIN_FUNCTION, "BUILTIN_FUNCTION")})

        return index_line

    def translate(self, code:str):
        code_lines = code.split("\n")
        index_line = 0
        begin_line = 0
        end_line = 0

        while index_line < len(code_lines):
            begin_line = index_line
            line = code_lines[index_line]

            word = ""
            for char in line:
                word += char
            
                # TODO:
                # Mirar como identificar cuando una variable se le asigna un valor

                try:        operation = self.utils.operation[word]
                except:     continue

                match(operation):
                    case self.ops.SPECIAL_CHAR:
                        word = ""
                        continue
                    
                    case self.ops.COMMENTS:
                        index_line = self.mid_translate_comments(code_lines, word, index_line, begin_line)
                        word = ""
                        break

                    case self.ops.DATA_TYPE:
                        # TODO:
                        # Mirar que las arrays puedan venir escritas en varias lineas debido a su contenido inicial asignado
                        end_line = begin_line
                        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.DATA_TYPE, "DATA_TYPE")})
                        word = ""
                        break
                    
                    case self.ops.BUILTIN_CONSTANT:
                        pass
                    
                    case self.ops.BUILTIN_FUNCTION:
                        index_line = self.mid_translate_builtin_func(code_lines, word, index_line, begin_line)
                        word = ""
                        break
                    
                    case self.ops.STD_GATE:
                        # TODO:
                        # Mirar caso cuando una variable se llama 'h' o tiene el nombre de una puerta
                        end_line = begin_line
                        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.STD_GATE, "STD_GATE")})
                        word = ""
                        break
                        
                    case self.ops.GATE_OPERATION:
                        end_line = begin_line
                        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.GATE_OPERATION, "GATE_OPERATION")})
                        word = ""
                        break

                    case self.ops.CLASSIC_INSTRUCTION:
                        end_line = begin_line
                        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.CLASSIC_INSTRUCTION, "CLASSIC_INSTRUCTION")})
                        word = ""
                        break                    
                
            index_line += 1

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
    # TODO:
    # Mirar que funcion es 'post'

    # code1 = '''complex[float] d = int[4](2.0) - (5 + sin(pi/2)) + (my_var * 5.5 im);'''
    
    translator = Translator()
    # translator.translate(code1)
    translator.translate(complex_code)

    # for info in translator.utils.translated_code_info.values():
    #     print(info)
    
    # print()
    # print("TRANSLATED CODE:")
    
    # for line in translator.utils.translated_code:
    #     print(line)

    for op in translator.mid_translation:
        print(op)