import numpy as np


from .translator_utils import TranslatorUtils
from sympy.matrices import Matrix
from qsimov.connectors.parser import _gate_func

translator_utils = TranslatorUtils()
stdgates_open_to_qsimov = {
    "p": "P",
    "x": "X",
    "y": "Y",
    "z": "Z",
    "h": "H",
    "s": "S",
    "sdg": "S-1",
    "t": "T",
    "tdg": "T-1",
    "sx": "SqrtX",
    "rx": "RX",
    "ry": "RY",
    "rz": "RZ",
    "swap": "SWAP",
    "cx": "X",
    "cy": "Y",
    "cz": "z",
    "cp": "P",
    "crx": "RX",
    "cry": "RY",
    "crz": "RZ",
    "ch": "H",
    "ccx": "X",
    "cswap": "SWAP",
    "cu": "U",
    "U": "U"
}
stdgates_with_params = {
    "p": 1,
    "rx": 1,
    "ry": 1,
    "rz": 1,
    "cp": 1,
    "crx": 1,
    "cry": 1,
    "crz": 1,
    "cu": 4,
    "U": 3
}
custom_gate_qargs = {}

# TODO:
# traducir el acceso a arrays bien, my_array[0, 2:3] -> my_array[0][2:3]
def get_expression(line, is_array=False):
        is_casting = False
        expression = ""
        jumps = 0

        for i, item in enumerate(line):

            if jumps > 0:
                jumps -= 1
                continue

            if is_casting and item != "(":
                continue

            if is_casting and item == "(":
                is_casting = False
            
            if item in translator_utils.data_types:
                is_casting = True
                if item == "angle": item = "float"

            elif item in translator_utils.builtin_constants:
                item = translator_utils.builtin_constants[item]

            elif item in translator_utils.builtin_functions:
                item = translator_utils.builtin_functions[item]

                if item == ".real" or item == ".imag":
                    close_bracket_i = line[i:].index(")")
                    expr = get_expression(line[i+2:close_bracket_i])    # We add +2 to point to the first relevant intem from '('

                    if len(expr.split(" ")) > 1:    item = f"({expr}){item}"
                    else:                           item = f"{expr}{item}"

                    jumps = close_bracket_i - i

                elif item == "len":
                    close_bracket_i = line[i:].index(")")
                    expr = get_expression(line[i+2:close_bracket_i])

                    var_id = line[i + 2]
                    next_to_var_id = line[i + 3]
                    dimension = 0
                    level = "[0]"
                    levels = ""
                    
                    if next_to_var_id == ",":
                        dimension = int(line[i + 4])

                    elif next_to_var_id == "[":
                        dimension_1 = int(line[i + 4]) + 1       # We add +1 at the end to point to the correct dimension in python
                        dimension_2 = int(line[close_bracket_i - 1])
                        dimension = dimension_1 + dimension_2

                    for d in range(dimension):
                        levels += level

                    item = f"len({var_id}{levels})"

                    jumps = close_bracket_i - i


            elif item in translator_utils.math_logic_operators:
                item = translator_utils.math_logic_operators[item]
                item = " " + item + " "

            if is_array and item == "{":
                item = "["

            if is_array and item == "}":
                item = "]"

            expression += item

        return expression

def get_param(line, line_index, is_custom_gate=False):
    param = ""

    for i in range(line_index, len(line)):
        item = line[i]
        if item == ")" or item == ",":
            if is_custom_gate:
                return get_expression([param]), i + 1                 # +1 because of the ')' or ','
            else:
                return "{" + get_expression([param]) + "}", i + 1     # +1 because of the ')' or ','
        param += item

def get_qu_bit(line, line_index):
        name = line[line_index]

        if TranslatorUtils.is_custom_gate:      return name, -1, line_index + 2

        read = False
        qu_bit_index = ""

        for i in range(line_index, len(line)):
            item = line[i]
            if item  == ",":                    break
            if item == "]":
                if qu_bit_index.isdigit():      return name, int(qu_bit_index), i + 2    # +2 because of the ']' and the following ','
                else:                           return name, qu_bit_index, i + 2    # +2 because of the ']' and the following ','
            if read:                            qu_bit_index += item
            if item == "[":                     read = True

        return name, -1, line_index + 2

def get_indexes(key, name, index, translated_code_info):
    global custom_gate_qargs

    # Normal case
    if not TranslatorUtils.is_custom_gate and not TranslatorUtils.is_custom_def:
        qsimov_start_index = translated_code_info[key][name]["start_index"]

        if index != -1:
            indexes = [qsimov_start_index + index]

        else:
            size_reg = translated_code_info[key][name]["size"]
            indexes = [i for i in range(qsimov_start_index, qsimov_start_index + size_reg)]

        return indexes
    
    # Translating a custom gate
    elif not TranslatorUtils.is_custom_def:
        return [custom_gate_qargs[name]]        # Return as list to keep format from normal flow
    
    # Translating a custom def
    else:
        if index != -1:
            return f"{name}[{index}]"
        else:
            return name

class DataTypeTranslator:
    def __init__(self):
        pass

    def get_eq_symbol_index(self, line):
        try:        return line.index("=")      # Get '=' occurence index
        except:     return 0                    # Return 0 if it is not in the list

    def translate_qubit(self, line, translated_code_info):
        '''
        UCs:
        qubit[3] my_var;
        qubit my_var;
        '''

        qubit_amount = 1
        if line[0] == "[":  qubit_amount = int(line[1])
        var_id = line[self.get_eq_symbol_index(line) - 1]

        # translation = f"QRegistry({qubit_amount}) {var_id}"

        registered_qubits = translated_code_info[translator_utils.KEY_QUBITS]
        if registered_qubits:   
            last_qubit = next(reversed(registered_qubits.values()))
            start_index = last_qubit["start_index"] + last_qubit["size"]
        else:
            start_index = 0

        translated_code_info[translator_utils.KEY_QUBITS][var_id] = {"start_index": start_index, "size": qubit_amount}
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "qubit"}

        return ""

    def translate_bit(self, line, translated_code_info):
        '''
        UCs:
        bit my_var;
        bit my_var = "1";
        bit[8] my_var;
        bit[8] my_var = "00001111";
        '''

        bit_amount = 1
        if line[0] == "[":   bit_amount = int(line[1])
        var_id = line[self.get_eq_symbol_index(line) - 1]

        # if eq_symbol_index == 0:
        #     if bit_amount > 1:      init_value = [0 for i in range(bit_amount)]
        #     else:                   init_value = 0
        # else:
        #     if bit_amount > 1:      init_value = [int(char) for char in line[eq_symbol_index + 1] if char.isdigit()]
        #     else:                   init_value = line[eq_symbol_index + 1][1]       # We get the number without the '"', that is why we add '[1]' at the end

        # translation = f"{var_id} = {init_value}"

        registered_bits = translated_code_info[translator_utils.KEY_BITS]
        if registered_bits:   
            last_bit = next(reversed(registered_bits.values()))
            start_index = last_bit["start_index"] + last_bit["size"]
        else:
            start_index = 0

        translated_code_info[translator_utils.KEY_BITS][var_id] = {"start_index": start_index, "size": bit_amount}
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "bit"}

        return ""

    def translate_int(self, line, translated_code_info):
        '''
        UCs:
        uint/int[16] my_var = 10;
        uint/int[16] my_var;
        uint/int my_var = 10;
        uint/int my_var;
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = ""

        if eq_symbol_index != 0:
            init_value = f" = {get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: int{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "int"}

        return translation

    def translate_float(self, line, translated_code_info):
        '''
        UCs:
        float[16] my_var = π;
        float[16] my_var;
        float my_var = 2.3;
        float my_var;

        angle[16] my_var = π;
        angle[16] my_var;
        angle my_var = π;
        angle my_var;
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = ""

        if eq_symbol_index != 0:
            init_value = f" = {get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: float{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "float"}

        return translation

    def translate_complex(self, line, translated_code_info):
        '''
        UCs:
        complex[float[16]] my_var = π;
        complex[float[16]] my_var;
        complex[float] my_var = 2.3;
        complex[float] my_var;
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = ""

        if eq_symbol_index != 0:
            init_value = f" = {get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: complex{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "complex"}

        return translation

    def translate_bool(self, line, translated_code_info):
        '''
        UCs:
        bool my_var = true;
        bool my_var = false;
        bool my_var;
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = ""

        if eq_symbol_index != 0:
            init_value = f" = {get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: bool{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "bool"}

        return translation

    def translate_const(self, line, translated_code_info):
        '''
        UCs:
        const uint my_var = 32;
        const float[32] my_var = 2.5
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_type = line[0]
        var_id = line[eq_symbol_index - 1].upper()
        init_value = ""

        if eq_symbol_index != 0:
            init_value = f" = {get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: {var_type}{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": var_type}

        return translation

    def translate_array(self, line, translated_code_info):
        '''
        UCs:
        array[int[32], 5] my_var;
        array[int[32], 5] my_var = {0, 1, 2, 3, 4};
        array[float[32], 3, 2] my_var = {{1.1, 1.2}, {2.1, 2.2}, {3.1, 3.2}};


        DECLARATION:
        array[data_type, dim_size1, (dim_size2), ..., (dim_size7)]
        - data_type: bit, int, uint, float, complex, angle, bool, duration

        NOTES:
        - Se deben declarar en el scope global, no vale cualquier otro sitio
        - Pueden usar indices negativos como en python para su acceso
        - El tamaño maximo es de 7 dimensiones
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = f" = []"

        if eq_symbol_index != 0:
            init_value = f" = {get_expression(line[eq_symbol_index + 1:], is_array=True)}"

        translation = f"{var_id}: list{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "array"}

        return translation

    def translate_let(self, line, translated_code_info):
        '''
        UCs:
        qubit[5] q;
        let my_var = q[1:4]
        let my_var = q[{0,3,5}]     # It returns the first, fourth and sixth elements
        '''
        # TODO:
        # Implementar solucion para el ultimo UC
        # TODO:
        # Que se pueda accerder al let como a cualquier otra variable

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = ""

        if eq_symbol_index != 0:
            init_value = f" = {get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "let"}

        return translation


# TODO:
# mirar que tambien se acepte qubit[2:4] etc
class STDGateTranslator:
    def __init__(self):
        self.S_matrix = Matrix([[1, 0], [0, 1j]])
        self.T_matrix = Matrix([[1, 0], [0, 0.70710678 + 0.70710678j]])
        self.is_S_implemented = False
        self.is_T_implemented = False
        self.S_gate_name = "S"
        self.T_gate_name = "T"
        self.S_gate_aliases = ["s", "sqrtZ", "SqrtZ"]
        self.T_gate_aliases = ["t", "sqrtS", "SqrtS"]

    def get_S_matrix(self):
        return self.S_matrix
    
    def get_T_matrix(self):
        return self.T_matrix

    # TODO:
    # En el github de openqasm parece que el qubit es de control y lo que se hace es un cambio de fase global
    # -> gate p(λ) a { ctrl @ gphase(λ) a; }
    def translate_p(self, line, translated_code_info):
        '''
        UC:
        p(pi) my_qubit;
        '''

        angle, line_index = get_param(line, 1)     # Start at index 1 to avoid reading first '('
        qubit_name, qubit_index, line_index = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["p"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_x(self, line, translated_code_info):
        '''
        UC:
        x my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["x"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_y(self, line, translated_code_info):
        '''
        UC:
        y my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["y"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_z(self, line, translated_code_info):
        '''
        UC:
        z my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["z"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_h(self, line, translated_code_info):
        '''
        UC:
        h my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["h"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_s(self, line, translated_code_info):
        '''
        UC:
        s my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.S_gate_name}\""

        if self.is_S_implemented:
            return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_S_implemented = True
            
            translation =   f"{TranslatorUtils.qsimov_name}.add_gate({t_gate}, {self.get_S_matrix}, 0, 0, aliases={self.S_gate_aliases})"
            translation += "\n"
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

            return translation
            
    def translate_sdg(self, line, translated_code_info):
        '''
        UC:
        sdg my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.S_gate_name}-1\""

        if self.is_S_implemented:
            return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_S_implemented = True

            translation =   f"{TranslatorUtils.qsimov_name}.add_gate(f\"{self.S_gate_name}\", {self.get_S_matrix}, 0, 0, aliases={self.S_gate_aliases})"
            translation += "\n"
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

            return translation

    def translate_t(self, line, translated_code_info):
        '''
        UC:
        t my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.T_gate_name}\""

        if self.is_T_implemented:
            return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_T_implemented = True

            translation =   f"{TranslatorUtils.qsimov_name}.add_gate({t_gate}, {self.get_T_matrix}, 0, 0, aliases={self.T_gate_aliases})"
            translation += "\n"
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

            return translation

    def translate_tdg(self, line, translated_code_info):
        '''
        UC:
        tdg my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.T_gate_name}-1\""

        if self.is_T_implemented:
            return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_T_implemented = True

            translation =   f"{TranslatorUtils.qsimov_name}.add_gate(f\"{self.T_gate_name}\", {self.get_T_matrix}, 0, 0, aliases={self.T_gate_aliases})"
            translation += "\n"
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

            return translation

    def translate_sx(self, line, translated_code_info):
        '''
        UC:
        sx my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line,0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["sx"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_rx(self, line, translated_code_info):
        '''
        UC:
        rx my_qubit;
        '''

        angle, line_index = get_param(line, 1)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["rx"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_ry(self, line, translated_code_info):
        '''
        UC:
        ry my_qubit;
        '''

        angle, line_index = get_param(line, 1)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["ry"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_rz(self, line, translated_code_info):
        '''
        UC:
        rz my_qubit;
        '''

        angle, line_index = get_param(line, 1)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["rz"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_cx(self, line, translated_code_info):
        '''
        UC:
        cx my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["cx"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_cy(self, line, translated_code_info):
        '''
        UC:
        cy my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["cy"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_cz(self, line, translated_code_info):
        '''
        UC:
        cz my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["cz"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_cp(self, line, translated_code_info):
        '''
        UC:
        cp(pi) my_qubit[0], my_qubit[1];
        '''

        angle, line_index = get_param(line, 1)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["cp"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_crx(self, line, translated_code_info):
        '''
        UC:
        crx my_qubit[0], my_qubit[1];
        '''

        angle, line_index = get_param(line, 1)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["crx"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_cry(self, line, translated_code_info):
        '''
        UC:
        cry my_qubit[0], my_qubit[1];
        '''

        angle, line_index = get_param(line, 1)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["cry"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_crz(self, line, translated_code_info):
        '''
        UC:
        crz my_qubit[0], my_qubit[1];
        '''

        angle, line_index = get_param(line, 1)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["crz"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_ch(self, line, translated_code_info):
        '''
        UC:
        ch my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["ch"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_swap(self, line, translated_code_info):
        '''
        UC:
        swap my_qubit[0], my_qubit[1];
        '''

        qubit_name_1, qubit_index_1, line_index = get_qu_bit(line, 0)
        qubit_name_2, qubit_index_2, _ = get_qu_bit(line, line_index)

        qsimov_qubit_index_1 = translated_code_info[translator_utils.KEY_QUBITS][qubit_name_1]["start_index"] + qubit_index_1
        qsimov_qubit_index_2 = translated_code_info[translator_utils.KEY_QUBITS][qubit_name_2]["start_index"] + qubit_index_2

        qsimov_gate = stdgates_open_to_qsimov["swap"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{qsimov_qubit_index_1},{qsimov_qubit_index_2}])"

    def translate_ccx(self, line, translated_code_info):
        '''
        UC:
        ccx my_qubit[0], my_qubit[1], my_qubit[2];
        '''

        control_qubit_name_1, control_qubit_index_1, line_index = get_qu_bit(line, 0)
        control_qubit_name_2, control_qubit_index_2, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls_1 = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name_1, control_qubit_index_1, translated_code_info)
        controls_2 = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name_2, control_qubit_index_2, translated_code_info)
        controls = controls_1 + controls_2
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["ccx"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

    def translate_cswap(self, line, translated_code_info):
        '''
        UC:
        cswap my_qubit[0], my_qubit[1], my_qubit[2];
        '''

        control_qubit_name, control_qubit_index_1, line_index = get_qu_bit(line, 0)
        target_qubit_name_1, target_qubit_index_1, line_index = get_qu_bit(line, line_index)
        target_qubit_name_2, target_qubit_index_2, _ = get_qu_bit(line, line_index)

        qsimov_control_qubit_index = translated_code_info[translator_utils.KEY_QUBITS][control_qubit_name]["start_index"] + control_qubit_index_1
        qsimov_target_qubit_index_1 = translated_code_info[translator_utils.KEY_QUBITS][target_qubit_name_1]["start_index"] + target_qubit_index_1
        qsimov_target_qubit_index_2 = translated_code_info[translator_utils.KEY_QUBITS][target_qubit_name_2]["start_index"] + target_qubit_index_2

        qsimov_gate = stdgates_open_to_qsimov["cswap"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{qsimov_target_qubit_index_1}, {qsimov_target_qubit_index_2}], controls=[{qsimov_control_qubit_index}])"

    def translate_cu(self, line, translated_code_info):
        '''
        UC:
        cu(0,0,pi, pi) my_qubit[0], my_qubit[1];
        '''

        u_angle_1, line_index = get_param(line, 1)
        u_angle_2, line_index = get_param(line, line_index)
        u_angle_3, line_index = get_param(line, line_index)
        p_angle, line_index = get_param(line, line_index)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate_p = stdgates_open_to_qsimov["p"]
        qsimov_gate_u = stdgates_open_to_qsimov["U"]
        t_gate_p = f"f\"{qsimov_gate_p}({p_angle} - {u_angle_1}/2)\""
        t_gate_u = f"f\"{qsimov_gate_u}({u_angle_1}, {u_angle_2}, {u_angle_3})\""

        translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate_p}, targets={controls})"
        translation += "\n"
        translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate_u}, targets={targets}, controls={controls})"

        return translation

    def translate_u(self, line, translated_code_info):
        '''
        UC:
        U(0, 0, pi) my_qubit[0];
        '''
        angle_1, line_index = get_param(line, 1)
        angle_2, line_index = get_param(line, line_index)
        angle_3, line_index = get_param(line, line_index)
        qubit_name, qubit_index, line_index = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["U"]
        t_gate = f"f\"{qsimov_gate}({angle_1}, {angle_2}, {angle_3})\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_gphase(self, line, translated_code_info):
        # TODO:
        # Esto parece que es una builtin function
        pass

class GateOperationTranslator:
    def __init__(self):
        pass

    def get_mod_param(self, line, line_index):
        param = ""
        read = False

        for i in range(line_index, len(line)):
            item = line[i]
            if item == "@":     break
            if item == ")":     return int(param), i + 2     # +1 because of the ')' and the '@'
            if read:            param += item
            if item == "(":     read = True

        return 1, line_index + 2

    def pow_gate(self, exp, gate):
        gate_matrix = _gate_func[stdgates_open_to_qsimov[gate]]
        return gate_matrix.pow(int(exp))
    
    def invert_gate(self, matrix):
        # Verify that the input is square
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Input matrix must be square.")

        # Compute the inverse
        try:
            inverse = matrix.inv()
        except:
            raise ValueError("Matrix is singular and cannot be inverted.")

        return inverse
    
    def get_modifiers(self, line):
        mod_anti_controls = []
        mod_inv_pow = []

        line_index = 0
        mod = line[0]
        while mod in translator_utils.gate_operations:
            param, line_index = self.get_mod_param(line, line_index)

            if mod == "ctrl" or mod == "negctrl":
                mod_anti_controls.append((mod, param))

            else:
                mod_inv_pow.append((mod, param))

            mod = line[line_index]

        # Remember the gate to apply
        gate = mod
        line_index += 1

        return mod_anti_controls, mod_inv_pow, gate, line_index
    
    def get_gate_params(self, gate, line, line_index, translated_code_info, is_custom_gate=False):
        gate_params = ""
        params_amount = 0
        is_first_param = True

        if gate in stdgates_with_params:
            params_amount = stdgates_with_params[gate]

        elif gate in translated_code_info[translator_utils.KEY_CUSTOM_GATES]:
            params_amount = translated_code_info[translator_utils.KEY_CUSTOM_GATES][gate]

        if params_amount > 0:
            line_index += 1
            for i in range(params_amount):
                param, line_index = get_param(line,line_index, is_custom_gate)
                
                if is_first_param:
                    is_first_param = False
                    gate_params += param
                
                else:
                    gate_params += f", {param}"

        return f"({gate_params})", line_index
    
    def get_mod_qu_bits(self, line, line_index, translated_code_info):
        mod_qu_bits = []

        while line_index < len(line):
            qubit_name, qubit_index, line_index = get_qu_bit(line, line_index)

            if TranslatorUtils.is_custom_def:
                if translated_code_info[translator_utils.KEY_SUBROUTINE_PARAMS][qubit_name]["type"] == "qubit":     key = translator_utils.KEY_QUBITS
                elif translated_code_info[translator_utils.KEY_SUBROUTINE_PARAMS][qubit_name]["type"] == "bit":     key = translator_utils.KEY_BITS

            elif TranslatorUtils.is_custom_gate:                                                                    key = translator_utils.KEY_QUBITS
            elif qubit_name in translated_code_info[translator_utils.KEY_QUBITS]:                                   key = translator_utils.KEY_QUBITS
            elif qubit_name in translated_code_info[translator_utils.KEY_CUSTOM_GATES]:                             key = translator_utils.KEY_QUBITS
            else:                                                                                                   key = translator_utils.KEY_BITS

            qubits = get_indexes(key, qubit_name, qubit_index, translated_code_info)

            if TranslatorUtils.is_custom_def:       mod_qu_bits.append(([qubits], key))
            else:                                   mod_qu_bits.append((qubits, key))

        return mod_qu_bits, line_index
    
    def get_q_c_controls_anticontrols(self, mod_anti_controls, mod_qu_bits, q_controls, c_controls, q_anticontrols, c_anticontrols):
        i = 0
        for mod, param in mod_anti_controls:
            param += i
            if mod == "ctrl":
                for qu_bit in mod_qu_bits[i:param]:
                    if qu_bit[1] == translator_utils.KEY_QUBITS:
                        q_controls += qu_bit[0]
                    else:
                        c_controls += qu_bit[0]

            if mod == "negctrl":
                for qu_bit in mod_qu_bits[i:param]:
                    if qu_bit[1] == translator_utils.KEY_QUBITS:
                        q_anticontrols += qu_bit[0]
                    else:
                        c_anticontrols += qu_bit[0]

            i = param
    
    def rewrite_anti_controls(self, q_controls, q_anticontrols, c_controls, c_anticontrols, targets):
        # q_controls
        is_first_item = True
        list_rewritten = ""
        for item in q_controls:
            if is_first_item:
                is_first_item = False
                list_rewritten += item
            else:
                list_rewritten += f", {item}"
        if list_rewritten:      rewritten_q_controls = f"{list_rewritten}"
        else:                   rewritten_q_controls = ""

        # q_anticontrols
        is_first_item = True
        list_rewritten = ""
        for item in q_anticontrols:
            if is_first_item:
                is_first_item = False
                list_rewritten += item
            else:
                list_rewritten += f", {item}"
        if list_rewritten:      rewritten_q_anticontrols = f"{list_rewritten}"
        else:                   rewritten_q_anticontrols = ""

        # c_controls
        is_first_item = True
        list_rewritten = ""
        for item in c_controls:
            if is_first_item:
                is_first_item = False
                list_rewritten += item
            else:
                list_rewritten += f", {item}"
        if list_rewritten:      rewritten_c_controls = f"{list_rewritten}"
        else:                   rewritten_c_controls = ""

        # c_anticontrols
        is_first_item = True
        list_rewritten = ""
        for item in c_anticontrols:
            if is_first_item:
                is_first_item = False
                list_rewritten += item
            else:
                list_rewritten += f", {item}"
        if list_rewritten:      rewritten_c_anticontrols = f"{list_rewritten}"
        else:                   rewritten_c_anticontrols = ""

        # targets
        is_first_item = True
        list_rewritten = ""
        for item in targets:
            if is_first_item:
                is_first_item = False
                list_rewritten += item
            else:
                list_rewritten += f", {item}"
        if list_rewritten:      rewritten_targets = f"{list_rewritten}"
        else:                   rewritten_targets = ""

        return rewritten_q_controls, rewritten_q_anticontrols, rewritten_c_controls, rewritten_c_anticontrols, rewritten_targets
        
    # TODO:
    # permitir el uso de puertas propias del usuario (gate my_gate ...)
    def translate_mod(self, line, translated_code_info):
        '''
        UCs:
        
        ctrl @ negctrl @ inv @ pow(2) @ x controls[0], controls[1], target;
        ctrl(2) @ negctrl(2) @ inv @ pow(2) @ x controls[0], controls[1], controls[2], controls[3], target;
        ctrl @ negctrl @ ctrl @ inv @ pow(2) @ x controls[0], controls[1], controls[2], target;
        '''

        mod_inv_pow = []
        mod_anti_controls = []
        mod_qu_bits = []
        q_controls = []
        q_anticontrols = []
        c_controls = []
        c_anticontrols = []

        # Get in order the modifiers and put them in its corresponding list
        mod_anti_controls, mod_inv_pow, gate, line_index = self.get_modifiers(line)

        # Get the gate's parameters, if it has
        gate_params, line_index = self.get_gate_params(gate, line, line_index, translated_code_info)

        # Get in order the qubits/bits used as controls or anticontrols
        mod_qu_bits, line_index = self.get_mod_qu_bits(line, line_index, translated_code_info)

        # Differentiate between q/c controls/anticontrols according to the order of the modifiers
        self.get_q_c_controls_anticontrols(mod_anti_controls, mod_qu_bits, q_controls, c_controls, q_anticontrols, c_anticontrols)

        # Compute translation components
        if gate in stdgates_open_to_qsimov:
            if len(gate_params) > 2:
                t_gate = f"f\"{stdgates_open_to_qsimov[gate]}{gate_params}\""
            
            else:
                t_gate = f"f\"{stdgates_open_to_qsimov[gate]}\""

        elif gate in translated_code_info[translator_utils.KEY_CUSTOM_GATES]:
            if len(gate_params) > 2:
                t_gate = f"f{gate}{gate_params}"
        
            else:
                t_gate = f"f{gate}()"

        # Get the target qubits
        qubits = []
        for qubit in mod_qu_bits:
            qubits += qubit[0]

        targets = set(qubits) - set(q_controls)
        targets -= set(q_anticontrols)
        targets -= set(c_controls)
        targets -= set(c_anticontrols)
        targets = list(targets)

        if TranslatorUtils.is_custom_def:
            q_controls, q_anticontrols, c_controls, c_anticontrols, targets = self.rewrite_anti_controls(q_controls, q_anticontrols, c_controls, c_anticontrols, targets)

        t_targets = f"targets={targets}"
        t_controls = f", controls={q_controls}"                         if q_controls       else ""
        t_anticontrols = f", anticontrols={q_anticontrols}"             if q_anticontrols   else ""
        t_c_controls = f", c_controls={c_controls}"                     if c_controls       else ""
        t_c_anticontrols = f", c_anticontrols={c_anticontrols}"         if c_anticontrols   else ""

        # Build the translation
        translation =  f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, {t_targets}{t_controls}{t_anticontrols}{t_c_controls}{t_c_anticontrols})"

        # TODO:
        # terminar con los modificadores 'inv' y 'pow'

        return translation

    def translate_gate(self, line, translated_code_info):
        '''
        UC:

        gate crz(pi) c, t {
            ctrl @ rz(pi) c, t;
        }
        crz(pi) controls[0], target;
        '''
        global custom_gate_qargs

        TranslatorUtils.is_custom_gate = True
        TranslatorUtils.QCircuit_name = translator_utils.QGate_name

        first_param = True
        params = ""
        params_counter = 0
        custom_gate_qargs = {}
        qargs_counter = 0

        gate_name = line[0]
        line_index = 1

        # Get the gate parameters
        if line[1] == "(":
            line_index = 2
            while line[line_index-1] != ")":
                param, line_index = get_param(line, line_index, True)
                if first_param:     
                    first_param = False
                    params += param
                else:
                    params += f", {param}"
                params_counter += 1

        # Get the rest of the arguments
        line_length = len(line)
        while line_index < line_length:
            qarg = line[line_index]

            if qarg == "," or qarg == "{":
                line_index += 1
                continue

            custom_gate_qargs[qarg] = qargs_counter
            qargs_counter += 1
            line_index += 1

        translation = f"def {gate_name}({params}):"
        translation += "\n"
        translation += f"\tcustom_gate = {TranslatorUtils.qsimov_name}.QGate({qargs_counter}, 0, \"{gate_name}\")"

        translated_code_info[translator_utils.KEY_CUSTOM_GATES][gate_name] = params_counter

        return translation

    def translate_custom_gate(self, line, translated_code_info):
        gate = line[0]
        gate_params, line_index = self.get_gate_params(gate, line, 1, translated_code_info, True)   # starting line_index = 1 to avoid reading '(' as the function also adds 1 to the variable
        qubits, line_index = self.get_mod_qu_bits(line, line_index, translated_code_info)
        # As the previus methods returns a list of tuples formed by qubit and key, we need to get just the qubits in this case
        t_qubits = []
        for qubit in qubits:
            t_qubits += qubit[0]
        
        t_gate = f"{gate}{gate_params}"     if gate_params      else    f"{gate}()"

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={t_qubits})"

    def translate_reset(self, line, translated_code_info):
        '''
        UC:

        reset target;
        reset targets[0];
        reset targets;
        '''

    def translate_measure(self, line, translated_code_info):
        '''
        UC:
        
        measurement = measure target;
        measurements[2] = measure targets[0];
        measurements = measure targets;
        '''
        bits_name, bits_index, line_index = get_qu_bit(line, 0)
        qubits_name, qubits_index, _ = get_qu_bit(line, line_index + 1)     # +1 to line_index to avoid "measure" keyword

        bits = get_indexes(translator_utils.KEY_BITS, bits_name, bits_index, translated_code_info)
        qubits = get_indexes(translator_utils.KEY_QUBITS, qubits_name,  qubits_index, translated_code_info)

        return f"{TranslatorUtils.QCircuit_name}.add_operation(\"MEASURE\", targets={qubits}, outputs={bits})"

    def translate_barrier(self, line, translated_code_info):
        '''
        UCs:

        barrier target;
        barrier controls[0];
        barrier controls;
        '''
        # reg_name, reg_index, _ = get_qu_bit(line, 0)

        # if reg_name in translated_code_info[translator_utils.KEY_QUBITS]:   key = translator_utils.KEY_QUBITS
        # else:                                                               key = translator_utils.KEY_BITS

        # targets = get_indexes(key, reg_name, reg_index, translated_code_info)

        return f"{TranslatorUtils.QCircuit_name}.add_operation(\"BARRIER\")"
    
class ClassicInstTranslator:
    def __init__(self):
        self.is_rotl_defined = False
        self.is_rotr_defined = False
        self.returning_types = {
            "bit": "int",
            "int": "int",
            "float": "float",
            "complex": "complex",
            "bool": "bool",
            "array": "list"
        }

    def rotl(self):
        func = '''
def rotl(array, distance):
    for i in range(distance):
        first = array.pop(0)
        array.append(first)
        '''
        return func
    
    def rotr(self):
        func = '''
def rotr(array, distance):
    for i in range(distance):
        first = array.pop(0)
        array.insert(0, first)
        '''
        return func

    def get_def_params(self, line):
        var_ids = []
        types = []

        is_searching = True
        while is_searching:
            try:
                comma_index = line.index(",")

                if line[comma_index + 1] in translator_utils.data_types:
                    type = line[0]
                    var_id = line[comma_index - 1]
                    line = line[comma_index + 1:]

                    var_ids.append(var_id)
                    types.append(type)

                elif line[comma_index + 1] == "readonly" or line[comma_index + 1] == "mutable":
                    type = "array"
                    var_id = line[comma_index - 1]
                    line = line[comma_index + 1:]

                    var_ids.append(var_id)
                    types.append(type)

                else:
                    line.pop(comma_index)

            except ValueError:
                # Add last parameter as in this case there are no more key ','
                if line[0] in translator_utils.data_types:
                    type = line[0]
                    var_id = line[-1]

                    var_ids.append(var_id)
                    types.append(type)

                elif line[0] == "readonly" or line[0] == "mutable":
                    type = "array"
                    var_id = line[-1]

                    var_ids.append(var_id)
                    types.append(type)
                
                is_searching = False
        
        return var_ids, types

    def translate_var_operation(self, line, translated_code_info):
        return get_expression(line)
    
    def translate_rotl(self, line, translated_code_info):
        translation = ""

        if not self.is_rotl_defined:
            self.is_rotl_defined = True

            translation = self.rotl()
            translation += "\n"

        translation += "rotl" + get_expression(line)
        return translation

    def translate_rotr(self, line, translated_code_info):
        translation = ""

        if not self.is_rotr_defined:
            self.is_rotr_defined = True

            translation = self.rotr()
            translation += "\n"

        translation += "rotr" + get_expression(line)
        return translation
    
    def translate_if_else(self, line, translated_code_info):
        return get_expression(line) + ":"

    def translate_for(self, line, translated_code_info):
        item = line[0]
        i = 0
        is_range = False
        
        # Forget about the data type
        i = line.index("in")
        var_id = line[i-1]

        # Check if the range is a normal range to adecuate it to python
        # OPENQASM -> [init, step, end]
        # PYTHON   -> [init, end, step]
        if line[i+1] == "[":
            is_range = True
            i += 2
            params = []
            param = ""
            item = line[i]

            while (item != "]"):
                if item == ":":
                    params.append(param)
                    param = ""

                else:
                    param += item
                
                i += 1
                item = line[i]
            # Append last param
            params.append(param)

        if is_range:
            if len(params) == 2:        range = f"range({params[0]}, {params[1]} + 1)"
            else:                       range = f"range({params[0]}, {params[2]} + {params[1]}, {params[1]})"

        else:
            range = get_expression(line[i+1:])       # Here i points to keyword 'in'

        translation = f"for {var_id} in {range}:"

        return translation

    def translate_while(self, line, translated_code_info):
        return get_expression(line) + ":"

    def translate_def(self, line, translated_code_info):
        TranslatorUtils.is_custom_def = True

        open_bracket_index = line.index("(")
        close_bracket_index = line.index(")")

        def_name = line[open_bracket_index-1]
        if line[close_bracket_index + 1] == "{":    t_return_type = ""
        else:                                       t_return_type = f" -> {self.returning_types[line[-2]]}"

        var_ids, types = self.get_def_params(line[open_bracket_index+1:close_bracket_index])        # +1 to init range to avoid sending '('

        amount_params = len(var_ids)
        var_ids_str = ""
        is_first_param = True

        for i in range(amount_params):
            translated_code_info[translator_utils.KEY_SUBROUTINE_PARAMS][var_ids[i]] = {"id":var_ids[i], "type": types[i]}
            
            if is_first_param:
                is_first_param = False
                var_ids_str += var_ids[i]
            
            else:
                var_ids_str += f", {var_ids[i]}"

        if amount_params == 1:      t_params = f"({var_ids[0]})"
        elif amount_params > 1:     t_params = f"({var_ids_str})"
        else:                       t_params = "()"

        translated_code_info[translator_utils.KEY_SUBROUTINES][def_name] = {"amount_params": amount_params, "returning_type": t_return_type.split(" ")[-1]}

        translation = f"def {def_name}{t_params}{t_return_type}:"

        return translation

    def translate_break(self, line, translated_code_info):
        return "break"
    
    def translate_continue(self, line, translated_code_info):
        return "continue"
    
    def translate_return(self, line, translated_code_info):
        return f"return {get_expression(line[1:])}"

    def translate_end(self, line, translated_code_info):
        return f"{TranslatorUtils.QCircuit_name}.add_operation(\"END\")"

    # TODO:
    # En la llamada a la funcion habria que pasar la lista de las ids de los registros correspondientes
    def translate_custom_def(self, line, translated_code_info):
        return get_expression(line)
