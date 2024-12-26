from .translator_utils import TranslatorUtils

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
        self.qc_name = "qc"

    def get_angle(self, line):
        read = False
        angle = ""

        for i in range(len(line)):
            item = line[i]
            if item == ")":     return angle, i + 1
            if read:            angle += item
            if item == "(":     read = True

    def get_qubit(self, line):
        name = line[0]
        read = False
        qubit_index = ""

        for i in range(len(line)):
            item = line[i]
            if item == "]":     return name, qubit_index, i
            if read:            qubit_index += item
            if item == "[":     read = True

    def translate_p(self, line, translated_code_info):
        '''
        UC:
        p(pi) my_qubit;
        '''

        angle, line_index = self.get_angle(line)
        qubit_name, qubit_index, line_index = self.get_qubit(line[line_index:])

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"P({angle})\", targets={qsimov_qubit_index})"


    def translate_x(self, line, translated_code_info):
        '''
        UC:
        x my_qubit;
        '''

        qubit_name, qubit_index, line_index = self.get_qubit(line)

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"X\", targets={qsimov_qubit_index})"

    def translate_y(self, line, translated_code_info):
        '''
        UC:
        y my_qubit;
        '''

        qubit_name, qubit_index, line_index = self.get_qubit(line)

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"Y\", targets={qsimov_qubit_index})"

    def translate_z(self, line, translated_code_info):
        '''
        UC:
        z my_qubit;
        '''

        qubit_name, qubit_index, line_index = self.get_qubit(line)

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"Z\", targets={qsimov_qubit_index})"

    def translate_h(self, line, translated_code_info):
        '''
        UC:
        h my_qubit;
        '''

        qubit_name, qubit_index, line_index = self.get_qubit(line)

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"H\", targets={qsimov_qubit_index})"

    def translate_s(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_sdg(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_t(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_tdg(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_sx(self, line, translated_code_info):
        '''
        UC:
        sx my_qubit;
        '''

        qubit_name, qubit_index, line_index = self.get_qubit(line)

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"sqrtX\", targets={qsimov_qubit_index})"

    def translate_rx(self, line, translated_code_info):
        '''
        UC:
        rx my_qubit;
        '''

        angle, line_index = self.get_angle(line)
        qubit_name, qubit_index, line_index = self.get_qubit(line[line_index:])

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"RX({angle})\", targets={qsimov_qubit_index})"

    def translate_ry(self, line, translated_code_info):
        '''
        UC:
        ry my_qubit;
        '''

        angle, line_index = self.get_angle(line)
        qubit_name, qubit_index, line_index = self.get_qubit(line[line_index:])

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"RY({angle})\", targets={qsimov_qubit_index})"

    def translate_rz(self, line, translated_code_info):
        '''
        UC:
        rz my_qubit;
        '''

        angle, line_index = self.get_angle(line)
        qubit_name, qubit_index, line_index = self.get_qubit(line[line_index:])

        qsimov_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][qubit_name]["start_index"] + qubit_index

        return f"{self.qc_name}.add_operation(\"RZ({angle})\", targets={qsimov_qubit_index})"

    def translate_cx(self, line, translated_code_info):
        '''
        UC:
        cx my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line)
        target_qubit_name, target_qubit_index, line_index = self.get_qubit(line[line_index:])

        qsimov_control_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][control_qubit_name]["start_index"] + control_qubit_index
        qsimov_target_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][target_qubit_name]["start_index"] + target_qubit_index

        return f"{self.qc_name}.add_operation(\"X\", targets={qsimov_target_qubit_index}, controls={qsimov_control_qubit_index})"

    def translate_cy(self, line, translated_code_info):
        '''
        UC:
        cy my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line)
        target_qubit_name, target_qubit_index, line_index = self.get_qubit(line[line_index:])

        qsimov_control_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][control_qubit_name]["start_index"] + control_qubit_index
        qsimov_target_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][target_qubit_name]["start_index"] + target_qubit_index

        return f"{self.qc_name}.add_operation(\"Y\", targets={qsimov_target_qubit_index}, controls={qsimov_control_qubit_index})"

    def translate_cz(self, line, translated_code_info):
        '''
        UC:
        cz my_qubit[0], my_qubit[1];
        '''

        control_qubit_name, control_qubit_index, line_index = self.get_qubit(line)
        target_qubit_name, target_qubit_index, line_index = self.get_qubit(line[line_index:])

        qsimov_control_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][control_qubit_name]["start_index"] + control_qubit_index
        qsimov_target_qubit_index = translated_code_info[self.translator_utils.KEY_QUBITS][target_qubit_name]["start_index"] + target_qubit_index

        return f"{self.qc_name}.add_operation(\"Z\", targets={qsimov_target_qubit_index}, controls={qsimov_control_qubit_index})"

    def translate_cp(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_crx(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_cry(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_crz(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_ch(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_swap(self, line, translated_code_info):
        # SWAP
        pass

    def translate_ccx(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_cswap(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_cu(self, line, translated_code_info):
        # Not in qsimov
        pass

    def translate_u(self, line, translated_code_info):
        # U
        pass

    def translate_gphase(self, line, translated_code_info):
        # TODO:
        # Esto parece que es una builtin function
        pass