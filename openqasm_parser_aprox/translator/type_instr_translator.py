from .translator_utils import TranslatorUtils
from sympy.matrices import Matrix

class DataTypeTranslator:
    def __init__(self):
        self.translator_utils = TranslatorUtils()

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
            
            if item in self.translator_utils.data_types:
                is_casting = True
                if item == "angle": item = "float"

            if item in self.translator_utils.builtin_constants:
                item = self.translator_utils.builtin_constants[item]

            if item in self.translator_utils.builtin_functions:
                item = self.translator_utils.builtin_functions[item]

                # We assume "real" and "imag" functions are only use with variables
                if item == ".real" or item == ".imag":
                    pass
                    # TODO:
                    # Adaptar las funciones de real e imag a python
                    # De momento se traduce como -> .real(my_var)

            if item in self.translator_utils.math_operators:
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

        registered_qubits = translated_code_info[self.translator_utils.KEY_QUBITS]
        if registered_qubits:   
            last_qubit = next(reversed(registered_qubits.values()))
            start_index = last_qubit["start_index"] + last_qubit["size"]
        else:
            start_index = 0

        translated_code_info[self.translator_utils.KEY_QUBITS][var_id] = {"start_index": start_index, "size": qubit_amount}
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        registered_bits = translated_code_info[self.translator_utils.KEY_BITS]
        if registered_bits:   
            last_bit = next(reversed(registered_bits.values()))
            start_index = last_bit["start_index"] + last_bit["size"]
        else:
            start_index = 0

        translated_code_info[self.translator_utils.KEY_BITS][var_id] = {"start_index": start_index, "size": bit_amount}
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

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

        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["amount"] += 1
        translated_code_info[self.translator_utils.KEY_INSTRUCTIONS]["lines"].append(translation)
        translated_code_info[self.translator_utils.KEY_VARS_REF][var_id] = var_id

        return translation
    
class STDGateTranslator:
    def __init__(self):
        self.translator_utils = TranslatorUtils()
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

    def get_angle(self, line, line_index):
        angle = ""

        for i in range(line_index, len(line)):
            item = line[i]
            if item == ")" or item == ",":      return angle, i + 1     # +1 because of the ')' or ','
            angle += item

    def get_qubit(self, line, line_index):
        name = line[line_index]
        read = False
        qubit_index = ""

        for i in range(line_index, len(line)):
            item = line[i]
            if item == "]":     return name, int(qubit_index), i + 2    # +2 because of the ']' and the following ','
            if read:            qubit_index += item
            if item == "[":     read = True

        return name, -1, i
    
    def get_indexes(self, qubit_name, qubit_index, translated_code_info):
        qsimov_start_qb_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"]

        if qubit_index != -1:
            indexes = [qsimov_start_qb_index + qubit_index]

        else:
            size_qb_reg = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["size"]
            indexes = [i for i in range(qsimov_start_qb_index, qsimov_start_qb_index + size_qb_reg)]

        return indexes

    # TODO:
    # En el github de openqasm parece que el qubit es de control y lo que se hace es un cambio de fase global
    # -> gate p(λ) a { ctrl @ gphase(λ) a; }
    def translate_p(self, line, translated_code_info):
        '''
        UC:
        p(pi) my_qubit;
        '''

        angle, line_index = self.get_angle(line, 1)     # Start at index 1 to avoid reading first '('
        qubit_name, qubit_index, line_index = self.get_qubit(line, line_index)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"P({angle})\", targets={targets})"

    def translate_x(self, line, translated_code_info):
        '''
        UC:
        x my_qubit;
        '''

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"X\", targets={targets})"

    def translate_y(self, line, translated_code_info):
        '''
        UC:
        y my_qubit;
        '''

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Y\", targets={targets})"

    def translate_z(self, line, translated_code_info):
        '''
        UC:
        z my_qubit;
        '''

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Z\", targets={targets})"

    def translate_h(self, line, translated_code_info):
        '''
        UC:
        h my_qubit;
        '''

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"H\", targets={targets})"

    def translate_s(self, line, translated_code_info):
        '''
        UC:
        s my_qubit;
        '''

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

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

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

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

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

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

        qubit_name, qubit_index, _ = self.get_qubit(line, 0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

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

        qubit_name, qubit_index, _ = self.get_qubit(line,0)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"sqrtX\", targets={targets})"

    def translate_rx(self, line, translated_code_info):
        '''
        UC:
        rx my_qubit;
        '''

        angle, line_index = self.get_angle(line, 1)
        qubit_name, qubit_index, _ = self.get_qubit(line, line_index)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RX({angle})\", targets={targets})"

    def translate_ry(self, line, translated_code_info):
        '''
        UC:
        ry my_qubit;
        '''

        angle, line_index = self.get_angle(line, 1)
        qubit_name, qubit_index, _ = self.get_qubit(line, line_index)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RY({angle})\", targets={targets})"

    def translate_rz(self, line, translated_code_info):
        '''
        UC:
        rz my_qubit;
        '''

        angle, line_index = self.get_angle(line, 1)
        qubit_name, qubit_index, _ = self.get_qubit(line, line_index)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RZ({angle})\", targets={targets})"

    def translate_cx(self, line, translated_code_info):
        '''
        UC:
        cx my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, 0)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"X\", targets={targets}, controls={controls})"

    def translate_cy(self, line, translated_code_info):
        '''
        UC:
        cy my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, 0)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Y\", targets={targets}, controls={controls})"

    def translate_cz(self, line, translated_code_info):
        '''
        UC:
        cz my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, 0)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"Z\", targets={targets}, controls={controls})"

    def translate_cp(self, line, translated_code_info):
        '''
        UC:
        cp(pi) my_qubit[0], my_qubit[1];
        '''

        angle, line_index = self.get_angle(line, 1)
        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, line_index)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"P({angle})\", targets={targets}, controls={controls})"

    def translate_crx(self, line, translated_code_info):
        '''
        UC:
        crx my_qubit[0], my_qubit[1];
        '''

        angle, line_index = self.get_angle(line, 1)
        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, line_index)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RX({angle})\", targets={targets}, controls={controls})"

    def translate_cry(self, line, translated_code_info):
        '''
        UC:
        cry my_qubit[0], my_qubit[1];
        '''

        angle, line_index = self.get_angle(line, 1)
        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, line_index)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RY({angle})\", targets={targets}, controls={controls})"

    def translate_crz(self, line, translated_code_info):
        '''
        UC:
        crz my_qubit[0], my_qubit[1];
        '''

        angle, line_index = self.get_angle(line, 1)
        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, line_index)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"RZ({angle})\", targets={targets}, controls={controls})"

    def translate_ch(self, line, translated_code_info):
        '''
        UC:
        ch my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, 0)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"H\", targets={targets}, controls={controls})"

    def translate_swap(self, line, translated_code_info):
        '''
        UC:
        swap my_qubit[0], my_qubit[1];
        '''

        qubit_name_1, qubit_index_1, line_index = self.get_qubit(line, 0)
        qubit_name_2, qubit_index_2, _ = self.get_qubit(line, line_index)

        qsimov_qubit_index_1 = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name_1]["start_index"] + qubit_index_1
        qsimov_qubit_index_2 = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name_2]["start_index"] + qubit_index_2

        return f"{self.QCircuit_name}.add_operation(\"SWAP\", targets=[{qsimov_qubit_index_1},{qsimov_qubit_index_2}])"

    def translate_ccx(self, line, translated_code_info):
        '''
        UC:
        ccx my_qubit[0], my_qubit[1], my_qubit[2];
        '''

        control_qubit_name_1, control_qubit_index_1, line_index = self.get_qubit(line, 0)
        control_qubit_name_2, control_qubit_index_2, line_index = self.get_qubit(line, line_index)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls_1 = self.get_indexes(control_qubit_name_1, control_qubit_index_1, translated_code_info)
        controls_2 = self.get_indexes(control_qubit_name_2, control_qubit_index_2, translated_code_info)
        controls = controls_1 + controls_2
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"X\", targets={targets}, controls={controls})"

    def translate_cswap(self, line, translated_code_info):
        '''
        UC:
        cswap my_qubit[0], my_qubit[1], my_qubit[2];
        '''

        control_qubit_name, control_qubit_index_1, line_index = self.get_qubit(line, 0)
        target_qubit_name_1, target_qubit_index_1, line_index = self.get_qubit(line, line_index)
        target_qubit_name_2, target_qubit_index_2, _ = self.get_qubit(line, line_index)

        qsimov_control_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][control_qubit_name]["start_index"] + control_qubit_index_1
        qsimov_target_qubit_index_1 = translated_code_info[self.translator_utils.KEY_QUBITS][target_qubit_name_1]["start_index"] + target_qubit_index_1
        qsimov_target_qubit_index_2 = translated_code_info[self.translator_utils.KEY_QUBITS][target_qubit_name_2]["start_index"] + target_qubit_index_2

        return f"{self.QCircuit_name}.add_operation(\"SWAP\", targets=[{qsimov_target_qubit_index_1}, {qsimov_target_qubit_index_2}], controls=[{qsimov_control_qubit_index}])"

    def translate_cu(self, line, translated_code_info):
        '''
        UC:
        cu(0,0,pi, pi) my_qubit[0], my_qubit[1];
        '''

        u_angle_1, line_index = self.get_angle(line, 1)
        u_angle_2, line_index = self.get_angle(line, line_index)
        u_angle_3, line_index = self.get_angle(line, line_index)
        p_angle, line_index = self.get_angle(line, line_index)
        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line, line_index)
        target_qubit_name, target_qubit_index, _ = self.get_qubit(line, line_index)

        controls = self.get_indexes(control_qubit_name, control_qubit_index, translated_code_info)
        targets = self.get_indexes(target_qubit_name, target_qubit_index, translated_code_info)

        translation = f"{self.QCircuit_name}.add_operation(\"P({p_angle} - {u_angle_1}/2)\", targets={controls})"
        translation += "\n"
        translation += f"{self.QCircuit_name}.add_operation(\"U({u_angle_1}, {u_angle_2}, {u_angle_3})\", targets={targets}, controls={controls})"

        return translation

    def translate_u(self, line, translated_code_info):
        '''
        UC:
        U(0, 0, pi) my_qubit[0];
        '''
        angle_1, line_index = self.get_angle(line, 1)
        angle_2, line_index = self.get_angle(line, line_index)
        angle_3, line_index = self.get_angle(line, line_index)
        qubit_name, qubit_index, line_index = self.get_qubit(line, line_index)

        targets = self.get_indexes(qubit_name, qubit_index, translated_code_info)

        return f"{self.QCircuit_name}.add_operation(\"U({angle_1}, {angle_2}, {angle_3})\", targets={targets})"

    def translate_gphase(self, line, translated_code_info):
        # TODO:
        # Esto parece que es una builtin function
        pass