import numpy as np


from .translator_utils import TranslatorUtils
from sympy.matrices import Matrix
from qsimov.connectors.parser import _gate_func

translator_utils = TranslatorUtils()
qsimov_name = "qj"
QCircuit_name = "qc"
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
    "cz": "CZ",
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

def get_param(line, line_index):
    param = ""

    for i in range(line_index, len(line)):
        item = line[i]
        if item == ")" or item == ",":      return param, i + 1     # +1 because of the ')' or ','
        param += item

def get_qu_bit(line, line_index):
    name = line[line_index]
    read = False
    qu_bit_index = ""

    for i in range(line_index, len(line)):
        item = line[i]
        if item  == ",":    break
        if item == "]":     return name, int(qu_bit_index), i + 2    # +2 because of the ']' and the following ','
        if read:            qu_bit_index += item
        if item == "[":     read = True

    return name, -1, line_index + 2

def get_indexes(key, name, index, translated_code_info):
    qsimov_start_index = translated_code_info[key][name]["start_index"]

    if index != -1:
        indexes = [qsimov_start_index + index]

    else:
        size_reg = translated_code_info[key][name]["size"]
        indexes = [i for i in range(qsimov_start_index, qsimov_start_index + size_reg)]

    return indexes

class DataTypeTranslator:
    def __init__(self):
        translator_utils = TranslatorUtils()

    def get_eq_symbol_index(self, line):
        try:        return line.index("=")      # Get '=' occurence index
        except:     return 0                    # Return 0 if it is not in the list

    def get_expression(self, line, is_array=False):
        is_casting = False
        expression = ""

        for item in line:
            if is_casting and item != "(":
                continue

            if is_casting and item == "(":
                is_casting = False
            
            if item in translator_utils.data_types:
                is_casting = True
                if item == "angle": item = "float"

            if item in translator_utils.builtin_constants:
                item = translator_utils.builtin_constants[item]

            if item in translator_utils.builtin_functions:
                item = translator_utils.builtin_functions[item]

                # We assume "real" and "imag" functions are only use with variables
                if item == ".real" or item == ".imag":
                    pass
                    # TODO:
                    # Adaptar las funciones de real e imag a python
                    # De momento se traduce como -> .real(my_var)

            if item in translator_utils.math_operators:
                item = " " + item + " "

            if is_array and item == "{":
                item = "["

            if is_array and item == "}":
                item = "]"

            expression += item

        return expression       

    def translate_qubit(self, line, translated_code_info):
        '''
        UCs:
        qubit[3] my_var;
        qubit my_var;
        '''

        qubit_amount = 1
        if line[0] == "[":  qubit_amount = int(line[1])
        var_id = line[self.get_eq_symbol_index(line) - 1]

        translation = f"QRegistry({qubit_amount}) {var_id}"

        registered_qubits = translated_code_info[translator_utils.KEY_QUBITS]
        if registered_qubits:   
            last_qubit = next(reversed(registered_qubits.values()))
            start_index = last_qubit["start_index"] + last_qubit["size"]
        else:
            start_index = 0

        translated_code_info[translator_utils.KEY_QUBITS][var_id] = {"start_index": start_index, "size": qubit_amount}
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

        return translation

    def translate_bit(self, line, translated_code_info):
        '''
        UCs:
        bit my_var;
        bit my_var = "1";
        bit[8] my_var;
        bit[8] my_var = "00001111";
        '''
        # TODO:
        # Mirar que cuando es solo un qubit no se genere como una lista
        bit_amount = 1
        if line[0] == "[":   bit_amount = int(line[1])
        eq_symbol_index = self.get_eq_symbol_index(line)
        var_id = line[eq_symbol_index - 1]

        if eq_symbol_index == 0:
            init_value = [0 for i in range(bit_amount)]
        else:
            init_value = [int(char) for char in line[eq_symbol_index + 1] if char.isdigit()]

        translation = f"{var_id} = {init_value}"

        registered_bits = translated_code_info[translator_utils.KEY_BITS]
        if registered_bits:   
            last_bit = next(reversed(registered_bits.values()))
            start_index = last_bit["start_index"] + last_bit["size"]
        else:
            start_index = 0

        translated_code_info[translator_utils.KEY_BITS][var_id] = {"start_index": start_index, "size": bit_amount}
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

        return translation

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
            init_value = f" = {self.get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: int{init_value}"

        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

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
            init_value = f" = {self.get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: float{init_value}"

        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

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
            init_value = f" = {self.get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: complex{init_value}"

        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

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
            init_value = f" = {self.get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: bool{init_value}"

        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

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
            init_value = f" = {self.get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}: {var_type}{init_value}"

        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

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
            init_value = f" = {self.get_expression(line[eq_symbol_index + 1:], is_array=True)}"

        translation = f"{var_id}: list{init_value}"

        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

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

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = ""

        if eq_symbol_index != 0:
            init_value = f" = {self.get_expression(line[eq_symbol_index + 1:])}"

        translation = f"{var_id}{init_value}"

        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = var_id

        return translation


# TODO:
# mirar que tambien se acepte qubit[2:4] etc
# TODO:
# cambiar el nombre de las puertas y usar el diccionario 'stdgates_open_to_qsimov'
class STDGateTranslator:
    def __init__(self):
        self.qsimov_name = "qj"
        self.QCircuit_name = "qc"
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

        return f"{self.QCircuit_name}.add_operation(\"P({angle})\", targets={targets})"

    def translate_x(self, line, translated_code_info):
        '''
        UC:
        x my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"X\", targets={targets})"

    def translate_y(self, line, translated_code_info):
        '''
        UC:
        y my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Y\", targets={targets})"

    def translate_z(self, line, translated_code_info):
        '''
        UC:
        z my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Z\", targets={targets})"

    def translate_h(self, line, translated_code_info):
        '''
        UC:
        h my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"H\", targets={targets})"

    def translate_s(self, line, translated_code_info):
        '''
        UC:
        s my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        if self.is_S_implemented:
            return f"{self.QCircuit_name}.add_operation(\"{self.S_gate_name}\", targets={targets})"
        
        else:
            self.is_S_implemented = True
            
            translation =   f"{self.qsimov_name}.add_gate(\"{self.S_gate_name}\", {self.get_S_matrix}, 0, 0, aliases={self.S_gate_aliases})"
            translation += "\n"
            translation += f"{self.QCircuit_name}.add_operation(\"{self.S_gate_name}\", targets={targets})"

            return translation
            
    def translate_sdg(self, line, translated_code_info):
        '''
        UC:
        sdg my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        if self.is_S_implemented:
            return f"{self.QCircuit_name}.add_operation(\"{self.S_gate_name}-1\", targets={targets})"
        
        else:
            self.is_S_implemented = True

            translation =   f"{self.qsimov_name}.add_gate(\"{self.S_gate_name}\", {self.get_S_matrix}, 0, 0, aliases={self.S_gate_aliases})"
            translation += "\n"
            translation += f"{self.QCircuit_name}.add_operation(\"{self.S_gate_name}-1\", targets={targets})"

            return translation

    def translate_t(self, line, translated_code_info):
        '''
        UC:
        t my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        if self.is_T_implemented:
            return f"{self.QCircuit_name}.add_operation(\"{self.T_gate_name}\", targets={targets})"
        
        else:
            self.is_T_implemented = True

            translation =   f"{self.qsimov_name}.add_gate(\"{self.T_gate_name}\", {self.get_T_matrix}, 0, 0, aliases={self.T_gate_aliases})"
            translation += "\n"
            translation += f"{self.QCircuit_name}.add_operation(\"{self.T_gate_name}\", targets={targets})"

            return translation

    def translate_tdg(self, line, translated_code_info):
        '''
        UC:
        tdg my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        if self.is_T_implemented:
            return f"{self.QCircuit_name}.add_operation(\"{self.T_gate_name}-1\", targets={targets})"
        
        else:
            self.is_T_implemented = True

            translation =   f"{self.qsimov_name}.add_gate(\"{self.T_gate_name}\", {self.get_T_matrix}, 0, 0, aliases={self.T_gate_aliases})"
            translation += "\n"
            translation += f"{self.QCircuit_name}.add_operation(\"{self.T_gate_name}-1\", targets={targets})"

            return translation

    def translate_sx(self, line, translated_code_info):
        '''
        UC:
        sx my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line,0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"sqrtX\", targets={targets})"

    def translate_rx(self, line, translated_code_info):
        '''
        UC:
        rx my_qubit;
        '''

        angle, line_index = get_param(line, 1)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RX({angle})\", targets={targets})"

    def translate_ry(self, line, translated_code_info):
        '''
        UC:
        ry my_qubit;
        '''

        angle, line_index = get_param(line, 1)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RY({angle})\", targets={targets})"

    def translate_rz(self, line, translated_code_info):
        '''
        UC:
        rz my_qubit;
        '''

        angle, line_index = get_param(line, 1)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RZ({angle})\", targets={targets})"

    def translate_cx(self, line, translated_code_info):
        '''
        UC:
        cx my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"X\", targets={targets}, controls={controls})"

    def translate_cy(self, line, translated_code_info):
        '''
        UC:
        cy my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Y\", targets={targets}, controls={controls})"

    def translate_cz(self, line, translated_code_info):
        '''
        UC:
        cz my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Z\", targets={targets}, controls={controls})"

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

        return f"{self.QCircuit_name}.add_operation(\"P({angle})\", targets={targets}, controls={controls})"

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

        return f"{self.QCircuit_name}.add_operation(\"RX({angle})\", targets={targets}, controls={controls})"

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

        return f"{self.QCircuit_name}.add_operation(\"RY({angle})\", targets={targets}, controls={controls})"

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

        return f"{self.QCircuit_name}.add_operation(\"RZ({angle})\", targets={targets}, controls={controls})"

    def translate_ch(self, line, translated_code_info):
        '''
        UC:
        ch my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, 0)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"H\", targets={targets}, controls={controls})"

    def translate_swap(self, line, translated_code_info):
        '''
        UC:
        swap my_qubit[0], my_qubit[1];
        '''

        qubit_name_1, qubit_index_1, line_index = get_qu_bit(line, 0)
        qubit_name_2, qubit_index_2, _ = get_qu_bit(line, line_index)

        qsimov_qubit_index_1 = translated_code_info[translator_utils.KEY_QUBITS][qubit_name_1]["start_index"] + qubit_index_1
        qsimov_qubit_index_2 = translated_code_info[translator_utils.KEY_QUBITS][qubit_name_2]["start_index"] + qubit_index_2

        return f"{self.QCircuit_name}.add_operation(\"SWAP\", targets=[{qsimov_qubit_index_1},{qsimov_qubit_index_2}])"

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

        return f"{self.QCircuit_name}.add_operation(\"X\", targets={targets}, controls={controls})"

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

        return f"{self.QCircuit_name}.add_operation(\"SWAP\", targets=[{qsimov_target_qubit_index_1}, {qsimov_target_qubit_index_2}], controls=[{qsimov_control_qubit_index}])"

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

        translation = f"{self.QCircuit_name}.add_operation(\"P({p_angle} - {u_angle_1}/2)\", targets={controls})"
        translation += "\n"
        translation += f"{self.QCircuit_name}.add_operation(\"U({u_angle_1}, {u_angle_2}, {u_angle_3})\", targets={targets}, controls={controls})"

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

        return f"{self.QCircuit_name}.add_operation(\"U({angle_1}, {angle_2}, {angle_3})\", targets={targets})"

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
            inverse = np.linalg.inv(matrix)
        except np.linalg.LinAlgError:
            raise ValueError("Matrix is singular and cannot be inverted.")

        return inverse
    
    def get_modifiers(self, line, mod_anti_controls, mod_inv_pow):
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

        return gate, line_index
    
    def get_gate_params(self, gate, line, line_index):
        gate_params = []

        if gate in stdgates_with_params:
            line_index += 1
            for i in range(stdgates_with_params[gate]):
                param, line_index = get_param(line,line_index)
                gate_params.append(param)

        return tuple(gate_params), line_index
    
    def get_mod_qu_bits(self, line, line_index, mod_qu_bits, translated_code_info):
        while line_index < len(line):
            qubit_name, qubit_index, line_index = get_qu_bit(line, line_index)

            if qubit_name in translated_code_info[translator_utils.KEY_QUBITS]:     key = translator_utils.KEY_QUBITS
            else:                                                                   key = translator_utils.KEY_BITS

            qubits = get_indexes(key, qubit_name, qubit_index, translated_code_info)

            mod_qu_bits.append((qubits, key))

        return line_index
    
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
        gate, line_index = self.get_modifiers(line, mod_anti_controls, mod_inv_pow)

        # Get the gate's parameters, if it has
        gate_params, line_index = self.get_gate_params(gate, line, line_index)

        # Get in order the qubits/bits used as controls or anticontrols
        line_index = self.get_mod_qu_bits(line, line_index, mod_qu_bits, translated_code_info)

        # Differentiate between q/c controls/anticontrols according to the order of the modifiers
        self.get_q_c_controls_anticontrols(mod_anti_controls, mod_qu_bits, q_controls, c_controls, q_anticontrols, c_anticontrols)

        # Compute translation components
        t_gate = f"\"{stdgates_open_to_qsimov[gate]}{gate_params}\""    if gate_params      else f"\"{stdgates_open_to_qsimov[gate]}\""
        t_controls = f", controls={q_controls}"                         if q_controls       else ""
        t_anticontrols = f", anticontrols={q_anticontrols}"             if q_anticontrols   else ""
        t_c_controls = f", c_controls={c_controls}"                     if c_controls       else ""
        t_c_anticontrols = f", c_anticontrols={c_anticontrols}"         if c_anticontrols   else ""

        # Build the translation
        translation =  f"{QCircuit_name}.add_operation({t_gate}, targets={mod_qu_bits[-1][0]}{t_controls}"
        translation += f"{t_anticontrols}{t_c_controls}{t_c_anticontrols})"

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

        return f"{QCircuit_name}.add_operation(\"MEASURE\", targets={qubits}, outputs={bits})"

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

        return f"{QCircuit_name}.add_operation(\"BARRIER\")"