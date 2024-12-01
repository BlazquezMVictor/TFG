import re


from translator_utils_copy import Operations, DictionaryKeyShortcuts, Utils

class Translator():
    def __init__(self):
        self.ops = Operations()
        self.keys = DictionaryKeyShortcuts()
        self.utils = Utils()
        self.mid_translation = []
        self.identifier_RE = r"^[a-zA-Z_][a-zA-Z0-9_]*$"

    def is_var_identifier(self, identifier):
        return bool(re.match(self.identifier_RE, identifier))

    def mid_translate_comments(self, code_lines, word, index_line, begin_line):
        if word != "/*":
            end_line = begin_line

        else:
            # Compute when the bigger comment ends
            line = code_lines[index_line]
            ending_comment = line[-2:]
            while ending_comment != "*/":
                index_line += 1
                line = code_lines[index_line]
                ending_comment = line[-2:]

            end_line = index_line
            
        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.COMMENTS, "COMMENT"), "word": word})

        return index_line
    
    def mid_translate_data_type(self, code_lines, word, index_line, begin_line):
        if word != "array":
            end_line = begin_line

        else:
            index_line = self.get_ending_brace_line(code_lines, index_line)
            end_line = index_line
            
        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.DATA_TYPE, "DATA_TYPE"), "word": word})

        return index_line
    
    def mid_translate_gate_operation(self, code_lines, word, index_line, begin_line):
        if word != "gate":
            end_line = begin_line

        else:
            index_line = self.get_ending_brace_line(code_lines, index_line)
            end_line = index_line

        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.GATE_OPERATION, "GATE_OPERATION"), "word": word})

        return index_line
    
    def mid_translate_classic_instc(self, code_lines, word, index_line, begin_line):
        if word not in {"if", "for", "while", "switch", "def"}:
            end_line = begin_line

        else:
            index_line = self.get_ending_brace_line(code_lines, index_line)
            end_line = index_line

        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.CLASSIC_INSTRUCTION, "CLASSIC_INSTRUCTION"), "word": word})

        return index_line

    def get_ending_brace_line(self, code_lines, index_line):
        line = code_lines[index_line]
        brace_count = line.count("{")
        brace_count -= line.count("}")

        while brace_count > 0:
            index_line += 1
            line = code_lines[index_line]

            brace_count += line.count("{")
            brace_count -= line.count("}")

        return index_line


    def mid_translate(self, code):
        code_lines = code.split("\n")
        index_line = 0
        begin_line = 0
        end_line = 0

        while index_line < len(code_lines):
            begin_line = index_line
            line = code_lines[index_line]

            word = ""
            char_found = False
            for char in line:
                if char != " ": char_found = True

                if (char == " " or char in self.utils.special_chars) and char_found:
                    break

                word += char
            word = word.lstrip()

            if word in self.utils.operation:
                match(self.utils.operation[word]):
                    case self.ops.SPECIAL_CHAR:
                        pass

                    case self.ops.COMMENTS:
                        index_line = self.mid_translate_comments(code_lines, word, index_line, begin_line)

                    case self.ops.DATA_TYPE:
                        index_line = self.mid_translate_data_type(code_lines, word, index_line, begin_line)
                    
                    case self.ops.BUILTIN_CONSTANT:
                        pass
                    
                    case self.ops.BUILTIN_FUNCTION:
                        pass
                    
                    case self.ops.STD_GATE:
                        end_line = begin_line
                        self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.STD_GATE, "STD_GATE"), "word": word})
                        
                    case self.ops.GATE_OPERATION:
                        index_line = self.mid_translate_gate_operation(code_lines, word, index_line, begin_line)

                    case self.ops.CLASSIC_INSTRUCTION:
                        index_line = self.mid_translate_classic_instc(code_lines, word, index_line, begin_line)

            else:
                # Chek it we are reading a comment of type "//text" or "/*text..."
                if word[:2] in self.utils.comments:
                    index_line = self.mid_translate_comments(code_lines, word[:2], index_line, begin_line)
        
                # Check if we are modifiying a variable
                elif self.is_var_identifier(word):
                    end_line = begin_line
                    self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.USER_DEFINED, "USER_DEFINED"), "word": word})
                
            index_line += 1

    def last_translate(self):
        for op in self.mid_translation:
            self.utils.translate(op)

    def translate(self, code:str):
        self.mid_translate(code)
        # self.last_translate()

if __name__ == "__main__":
    # openqasm_code = '''
    #     // quantum teleportation example
    #     OPENQASM 3; // Version statement is optional
    #     include "stdgates.inc";
    #     qubit[3] q;
    #     bit c0;
    #     bit c1;
    #     bit c2;
    #     // optional post-rotation for state tomography
    #     // empty gate body => identity gate
    #     gate post q { }
    #     reset q;
    #     U(0.3, 0.2, 0.1) q[0];
    #     h q[1];
    #     cx q[1], q[2];
    #     barrier q;
    #     cx q[0], q[1];
    #     h q[0];
    #     c0 = measure q[0];
    #     c1 = measure q[1];
    #     if(c0==1) z q[2];
    #     if(c1==1) { x q[2]; }  // braces optional in this case
    #     post q[2];
    #     c2 = measure q[2];
    # '''
    complex_code = '''
        /*
        * Repeat-until-success circuit for Rz(theta),
        * cos(theta-pi)=3/5, from Nielsen and Chuang, Chapter 4.
        */
        OPENQASM 3;
        include "stdgates.inc";

        /*
        * Applies identity if out is 01, 10, or 11 and a Z-rotation by
        * theta + pi where cos(theta)=3/5 if out is 00.
        * The 00 outcome occurs with probability 5/8.
        */
        def segment qubit[2] anc, qubit psi -> bit[2] {
        bit[2] b;
        reset anc;
        h anc;
        ccx anc[0], anc[1], psi;
        s psi;
        ccx anc[0], anc[1], psi;
        z psi;
        h anc;
        measure anc -> b;
        return b;
        }

        qubit input;
        qubit[2] ancilla;
        bit[2] flags = "11";
        bit output;

        reset input;
        h input;

        // braces are optional in this case
        while(int(flags) != 0) {
        flags = segment ancilla, input;
        }
        rz(pi - arccos(3 / 5)) input;
        h input;
        output = measure input;  // should get zero
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