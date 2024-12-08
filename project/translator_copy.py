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

    def mid_translate_comments(self, code_lines, word, index_line, begin_line, append):
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

        info = {"lines": (begin_line, end_line), "operation": (self.ops.COMMENTS, "COMMENT"), "word": word, "inner_ops": []}

        if append:  self.mid_translation.append(info)

        return index_line, info
    
    def mid_translate_data_type(self, code_lines, word, index_line, begin_line, append):
        if word != "array":
            inner_ops = []
            end_line = begin_line

        else:
            index_line, inner_ops = self.get_ending_brace_line(code_lines, index_line)
            end_line = index_line
            
        # TODO:
        # El inner operations seguramente no funcione con las arrays porque empiezan con '{'
        info = {"lines": (begin_line, end_line), "operation": (self.ops.DATA_TYPE, "DATA_TYPE"), "word": word, "inner_ops": inner_ops}

        if append:  self.mid_translation.append(info)

        return index_line, info
    
    def mid_translate_std_gate(self, code_lines, word, index_line, begin_line, append):
        end_line = begin_line
        info = {"lines": (begin_line, end_line), "operation": (self.ops.STD_GATE, "STD_GATE"), "word": word, "inner_ops": []}

        if append:  self.mid_translation.append(info)

        return index_line, info
    
    def mid_translate_gate_operation(self, code_lines, word, index_line, begin_line, append):
        if word != "gate":
            inner_ops = []
            end_line = begin_line

        else:
            index_line, inner_ops = self.get_ending_brace_line(code_lines, index_line)
            end_line = index_line

        info = {"lines": (begin_line, end_line), "operation": (self.ops.GATE_OPERATION, "GATE_OPERATION"), "word": word, "inner_ops": inner_ops}
        
        if append:  self.mid_translation.append(info)

        return index_line, info
    
    def mid_translate_classic_instc(self, code_lines, word, index_line, begin_line, append):
        if word not in {"if", "for", "while", "switch", "def"}:
            inner_ops = []
            end_line = begin_line

        else:
            index_line, inner_ops = self.get_ending_brace_line(code_lines, index_line)
            end_line = index_line

        info = {"lines": (begin_line, end_line), "operation": (self.ops.CLASSIC_INSTRUCTION, "CLASSIC_INSTRUCTION"), "word": word, "inner_ops": inner_ops}
        
        if append:  self.mid_translation.append(info)

        return index_line, info

    def get_ending_brace_line(self, code_lines, index_line):
        line = code_lines[index_line]
        brace_count = line.count("{")
        brace_count -= line.count("}")
        inner_operations = []

        while brace_count > 0:
            index_line += 1
            line = code_lines[index_line]

            info = self.mid_translate(line, False)
            inner_operations.append(info)

            brace_count += line.count("{")
            brace_count -= line.count("}")

        return index_line, inner_operations


    def mid_translate(self, code, append):
        code_lines = code.split("\n")
        index_line = 0
        begin_line = 0
        end_line = 0
        info = {}

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
                        index_line, info = self.mid_translate_comments(code_lines, word, index_line, begin_line, append)

                    case self.ops.DATA_TYPE:
                        index_line, info = self.mid_translate_data_type(code_lines, word, index_line, begin_line, append)
                    
                    case self.ops.BUILTIN_CONSTANT:
                        pass
                    
                    case self.ops.BUILTIN_FUNCTION:
                        pass
                    
                    case self.ops.STD_GATE:
                        index_line, info = self.mid_translate_std_gate(code_lines, word, index_line, begin_line, append)
                        
                    case self.ops.GATE_OPERATION:
                        index_line, info = self.mid_translate_gate_operation(code_lines, word, index_line, begin_line, append)

                    case self.ops.CLASSIC_INSTRUCTION:
                        index_line, info = self.mid_translate_classic_instc(code_lines, word, index_line, begin_line, append)

            else:
                # Chek it we are reading a comment of type "//text" or "/*text..."
                if word[:2] in self.utils.comments:
                    index_line = self.mid_translate_comments(code_lines, word[:2], index_line, begin_line)
        
                # Check if we are modifiying a variable
                elif self.is_var_identifier(word):
                    end_line = begin_line
                    self.mid_translation.append({"lines": (begin_line, end_line), "operation": (self.ops.USER_DEFINED, "USER_DEFINED"), "word": word})
                
            index_line += 1

        return info

    def last_translate(self):
        for op in self.mid_translation:
            self.utils.translate(op)

    def translate(self, code:str):
        self.mid_translate(code, True)
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
        * Prepare a parameterized number of Bell pairs
        * and teleport a qubit using them.
        */
        include "stdgates.inc";

        const int[32] n_pairs = 10;  // number of teleportations to do

        def bellprep(qubit[2] q) {
        reset q;
        h q[0];
        cx q[0], q[1];
        }

        def xprepare(qubit q) {
        reset q;
        h q;
        }

        qubit input_qubit;
        bit output_qubit;
        qubit[2*n_pairs] q;

        xprepare(input_qubit);
        rz(pi / 4) input_qubit;

        let io = input_qubit;
        for uint i in [0: n_pairs - 1] {
        let bp = q[{2*i, 2*i + 1}];
        bit[2] pf;
        bellprep bp;
        cx io, bp[0];
        h io;
        pf[0] = measure io;
        pf[1] = measure bp[0];
        if (pf[0]==1) z bp[1];
        if (pf[1]==1) x bp[1];
        let io = bp[1];
        }

        h io;
        output_qubit = measure io;  // should get zero
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