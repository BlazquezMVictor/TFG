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

        translated_code_info[self.translator_utils.KEY_QUBITS]["amount"] += qubit_amount
        translated_code_info[self.translator_utils.KEY_QUBITS]["lines"].append(translation)
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

        bit_amount = 1
        if line[0] == "[":   bit_amount = int(line[1])
        eq_symbol_index = self.get_eq_symbol_index(line)
        var_id = line[eq_symbol_index - 1]

        if eq_symbol_index == 0:
            init_value = [0 for i in range(bit_amount)]
        else:
            init_value = [int(char) for char in line[eq_symbol_index + 1] if char.isdigit()]

        translation = f"{var_id} = {init_value}"

        translated_code_info[self.translator_utils.KEY_BITS]["amount"] += bit_amount
        translated_code_info[self.translator_utils.KEY_BITS]["lines"].append(translation)
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
        UC:
        qubit[5] q;
        let my_var = q[1:4]
        '''

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