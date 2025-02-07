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
# Si el tamaño de un registro viene dado por una variable, debo saber el contenido de la misma
# Esto implica que debo ir actualizando el valor de las variables conforme opero con ellas
# El problema de esto es si no puedo conocer el valor de la variable
    # bit c;
    # c = measure q;
    # qubit[5 + c] q2;
    # No se le da soporte a este caso
# Otro problema es que si es una expresion numerica pero compleja (5 + int(3.5) * var_1), tengo que ejecutarla y conseguir el valor

def get_close_bracket_index(line, start_index):
    bracket_level = 0

    for i in range(start_index, len(line)):
        if line[i] == "(":
            bracket_level += 1
        elif line[i] == ")":
            bracket_level -= 1

        if bracket_level == 0:
            return i
        
    return start_index

def get_expression(line_number, line, translated_code_info, is_array=False):
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
                close_bracket_i = get_close_bracket_index(line, i + 1)                      # We add +1 to point to the first '('
                expr = get_expression(line_number, line[i+2:close_bracket_i], translated_code_info)      # We add +2 to point to the first relevant intem from '('

                if len(expr.split(" ")) > 1:    item = f"({expr}){item}"
                else:                           item = f"{expr}{item}"

                jumps = close_bracket_i - i

            elif item == "len":
                close_bracket_i = get_close_bracket_index(line, i + 1)                      # We add +1 to point to the first '('
                expr = get_expression(line_number, line[i+2:close_bracket_i], translated_code_info)

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

        elif item in translated_code_info[translator_utils.KEY_SUBROUTINES]:
            close_bracket_i = get_close_bracket_index(line, i + 1)                              # We add +1 to point to the first '('
            item = ClassicInstTranslator().translate_custom_def(line_number, line[i:close_bracket_i + 1], translated_code_info)  # We add +1 to include close bracket

            jumps = close_bracket_i - i

        elif item in translated_code_info[translator_utils.KEY_BITS]:
            error = f"There is no support yet to 'bit' variable access during execution of circuit\n"
            error += f"\t(({line_number}, {i}): {line})"
            raise NotImplementedError(error)
        
        elif item in translated_code_info[translator_utils.KEY_SUBROUTINE_PARAMS] and translated_code_info[translator_utils.KEY_SUBROUTINE_PARAMS][item]["type"] == "bit":
            error = f"There is no support yet to 'bit' variable access during execution of circuit\n"
            error += f"\t(({line_number}, {i}): {line})"
            raise NotImplementedError(error)

        elif item in translator_utils.math_logic_operators:
            item = translator_utils.math_logic_operators[item]
            item = " " + item + " "

        elif item == ",":
            item = ", "

        if is_array and item == "{":
            item = "["

        if is_array and item == "}":
            item = "]"

        expression += item

    return expression

def get_all_params(line_number, structure_name, line, line_index, translated_code_info, is_custom_gate=False, is_custom_def=False):
    params = []
    amount_params = 0

    if structure_name in stdgates_with_params:
        amount_params = stdgates_with_params[structure_name]

    elif structure_name in translated_code_info[translator_utils.KEY_CUSTOM_GATES]:
        amount_params = translated_code_info[translator_utils.KEY_CUSTOM_GATES][structure_name]

    elif structure_name in translated_code_info[translator_utils.KEY_SUBROUTINES]:
        amount_params = translated_code_info[translator_utils.KEY_SUBROUTINES][structure_name]["amount_params"]

    if amount_params > 0:
        line_index += 1
        for i in range(amount_params):
            param, line_index = get_param(line_number, line, line_index, translated_code_info, is_custom_gate, is_custom_def)
            params.append(param)

    return params, line_index

def get_param(line_number, line, line_index, translated_code_info, is_custom_gate=False, is_custom_def=False):
    param = []
    is_between_square_brackets = False

    for i in range(line_index, len(line)):
        item = line[i]

        if item == "[":
            is_between_square_brackets = True

        if item == "]":
            is_between_square_brackets = False

        if item == ")" or (item == "," and not is_between_square_brackets):
            if is_custom_def:
                return param, i + 1                                                       # +1 because of the ')' or ','
            
            if is_custom_gate:
                return get_expression(line_number, param, translated_code_info), i + 1                 # +1 because of the ')' or ','
            
            else:
                return "{" + get_expression(line_number, param, translated_code_info) + "}", i + 1     # +1 because of the ')' or ','
            
        param.append(item)

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
        is_int = False
        if isinstance(index, int):
        #     error = f"The use of non digit value to index a qubit/bit is not yet supported\n"
        #     error += f"\t({name}[{index} ...)"
        #     raise NotImplementedError(error)
            is_int = True

            # if any(char in translator_utils.math_logic_operators for char in index):
            #     error = f"The use of complex expressions and not number or variable literals to index a qubit/bit register is not supported yet\n"
            #     error += f"\t({name}[{index}])"
            #     raise NotImplementedError(error)
        
        if index != -1:
            index_splitted = str(index).split(":")
            if len(index_splitted) > 1:
                if is_int:
                    indexes = [translated_code_info[key][name]["indexes"][i] for i in range(int(index_splitted[0]), int(index_splitted[1]) + 1)]
                else:
                    error = f"The use of variable range expressions to index a qubit/bit register is not supported yet\n"
                    error += f"\t({name}[{index}])"
                    raise NotImplementedError(error)

            else:
                if is_int:
                    indexes = [translated_code_info[key][name]["indexes"][index]]
                else:
                    indexes = [f"{translated_code_info[key][name]["indexes"][0]} + {index}"]

        else:
            indexes = translated_code_info[key][name]["indexes"]

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

def add_new_gate_matrix(gate, gate_matrix, min_args=0, max_args=0, aliases=[]):
    if aliases:     t_aliases = f", aliases={aliases}"
    else:           t_aliases = ""
    t_overwrite = f", overwrite=True"
    func = f"def add_{gate}():\n"
    func += f"\treturn {gate_matrix}\n"
    func += f"{TranslatorUtils.qsimov_name}.add_gate(\"{gate}\", add_{gate}, {min_args}, {max_args}{t_aliases}{t_overwrite})\n"

    return func

def list_to_string(list):
    return ', '.join(map(str, list))

class DataTypeTranslator:
    def __init__(self):
        pass

    def get_eq_symbol_index(self, line):
        try:        return line.index("=")      # Get '=' occurence index
        except:     return 0                    # Return 0 if it is not in the list

    def get_let_indexes(self, key, line_number, line, line_index, reference_var, translated_code_info, is_quantum=True):
        if line_index + 2 < len(line) and line[line_index + 3] == "{":
            line_index += 4
            slices = []
            slice = line[line_index]

            while slice.isdigit():
                slices.append(int(slice))
                line_index += 2
                slice = line[line_index]

            if is_quantum:
                result = []
                for slice in slices:
                    result += get_indexes(key, reference_var, slice, translated_code_info)

            else:
                result = f" = [{reference_var}[slice] for slice in {slices}]"

        else:
            if is_quantum:
                name, index, _ = get_qu_bit(line, line_index + 1)
                result = get_indexes(key, name, index, translated_code_info)

            else:
                result = f" = {get_expression(line_number, line[line_index + 1:], translated_code_info)}"

        return result

    def translate_qubit(self, line_number, line, translated_code_info):
        '''
        UCs:
        qubit[3] my_var;
        qubit my_var;
        '''

        qubit_amount = 1
        if line[0] == "[":
            qubit_amount = int(line[1])
            
            if line[2] != "]":
                error = f"The use of complex expressions and not number literals to indicate register's size is not supported yet\n"
                error += f"\t(({line_number, 2}): {line})"
                raise NotImplementedError(error)

        var_id = line[self.get_eq_symbol_index(line) - 1]


        registered_qubits = translated_code_info[translator_utils.KEY_QUBITS]
        if registered_qubits: 
            reversed_reg_qubits = reversed(registered_qubits.values())  
            last_qubit = next(reversed_reg_qubits)
            while last_qubit["is_let"]:
                last_qubit = next(reversed_reg_qubits)

            indexes = [i for i in range(last_qubit["next_index"], last_qubit["next_index"] + qubit_amount)]

        else:
            indexes = [i for i in range(0, qubit_amount)]

        translated_code_info[translator_utils.AMOUNT_QUBITS] += qubit_amount
        translated_code_info[translator_utils.KEY_QUBITS][var_id] = {"indexes": indexes, "next_index": indexes[-1] + 1, "is_let": False}
        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "qubit"}

        return ""

    def translate_bit(self, line_number, line, is_global, translated_code_info):
        '''
        UCs:
        bit my_var;
        bit my_var = "1";
        bit[8] my_var;
        bit[8] my_var = "00001111";
        '''

        bit_amount = 1
        if line[0] == "[":
            bit_amount = int(line[1])

            if line[2] != "]":
                error = f"The use of complex expressions and not number literals to indicate register's size is not supported yet\n"
                error += f"\t(({line_number, 2}): {line})"
                raise NotImplementedError(error)
            
        var_id = line[self.get_eq_symbol_index(line) - 1]
        eq_symbol_index = self.get_eq_symbol_index(line)

        if eq_symbol_index == 0:
            if bit_amount > 1:      init_value = [0 for i in range(bit_amount)]
            else:                   init_value = 0
        else:
            if bit_amount > 1:      init_value = [int(char) for char in line[eq_symbol_index + 1] if char.isdigit()]    # char.isdigit() is used to avoid the '"' character
            else:                   init_value = line[eq_symbol_index + 1][1]       # We get the number without the '"', that is why we add '[1]' at the end

        registered_bits = translated_code_info[translator_utils.KEY_BITS]
        if registered_bits:   
            reversed_reg_bits = reversed(registered_bits.values())  
            last_bit = next(reversed_reg_bits)
            while last_bit["is_let"]:
                last_bit = next(reversed_reg_bits)
                
            indexes = [i for i in range(last_bit["next_index"], last_bit["next_index"] + bit_amount)]
        else:
            indexes = [i for i in range(0, bit_amount)]

        # Differenciate between global and local variable definitions
        if is_global:
            translated_code_info[translator_utils.AMOUNT_BITS] += bit_amount
            translated_code_info[translator_utils.KEY_BITS][var_id] = {"indexes": indexes, "next_index": indexes[-1] + 1, "is_let": False}
            translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "bit"}

            if eq_symbol_index != 0:
                translation = ""
                for i, index in enumerate(indexes):
                    bit = init_value[i]

                    if bit == 1:    op = "SET"
                    else:           op = "RESET"
                    translation += f"{TranslatorUtils.QCircuit_name}.add_operation(f\"{op}\", c_targets=[{index}])\n"

                translated_code_info[translator_utils.KEY_BIT_INITS].append(translation)
            
            return ""
        else:
            translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "int"}

            return f"{var_id}: int = {init_value}"

    def translate_int(self, line_number, line, translated_code_info):
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
        t_init_value = ""

        if eq_symbol_index != 0:
            init_value = get_expression(line_number, line[eq_symbol_index + 1:], translated_code_info)
            t_init_value = f" = {init_value}"

        translation = f"{var_id}: int{t_init_value}"

        # if init_value:      value = eval(init_value)
        # else:               value = 0

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "int", "value": 0}

        return translation

    def translate_float(self, line_number, line, translated_code_info):
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
        t_init_value = ""

        if eq_symbol_index != 0:
            init_value = get_expression(line_number, line[eq_symbol_index + 1:], translated_code_info)
            t_init_value = f" = {init_value}"

        translation = f"{var_id}: float{t_init_value}"

        # if init_value:      value = eval(init_value)
        # else:               value = 0

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "float", "value": 0}

        return translation

    def translate_complex(self, line_number, line, translated_code_info):
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
        t_init_value = ""

        if eq_symbol_index != 0:
            init_value = get_expression(line_number, line[eq_symbol_index + 1:], translated_code_info)
            t_init_value = f" = {init_value}"

        translation = f"{var_id}: complex{t_init_value}"

        # if init_value:      value = eval(init_value)
        # else:               value = 0

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "complex", "value": 0}

        return translation

    def translate_bool(self, line_number, line, translated_code_info):
        '''
        UCs:
        bool my_var = true;
        bool my_var = false;
        bool my_var;
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        init_value = ""
        t_init_value = ""

        if eq_symbol_index != 0:
            init_value = get_expression(line_number, line[eq_symbol_index + 1:], translated_code_info)
            t_init_value = f" = {init_value}"

        translation = f"{var_id}: bool{t_init_value}"

        # if init_value:      value = bool(init_value)
        # else:               value = 0

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "bool", "value": 0}

        return translation

    def translate_const(self, line_number, line, translated_code_info):
        '''
        UCs:
        const uint my_var = 32;
        const float[32] my_var = 2.5
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_type = line[0]
        var_id = line[eq_symbol_index - 1].upper()
        init_value = ""
        t_init_value = ""

        if eq_symbol_index != 0:
            init_value = get_expression(line_number, line[eq_symbol_index + 1:], translated_code_info)
            t_init_value = f" = {init_value}"

        translation = f"{var_id}: {var_type}{t_init_value}"

        # if init_value:      value = eval(init_value)
        # else:               value = 0

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": var_type, "value": 0}

        return translation

    def translate_array(self, line_number, line, translated_code_info):
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
        init_value = []
        t_init_value = f" = []"

        if eq_symbol_index != 0:
            init_value = f"np.array({get_expression(line_number, line[eq_symbol_index + 1:], translated_code_info, is_array=True)})"
            t_init_value = f" = {init_value}"

        translation = f"{var_id}: list{t_init_value}"

        # if init_value:      value = eval(init_value)
        # else:               value = 0

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": "array", "value": 0}

        return translation

    def translate_let(self, line_number, line, translated_code_info):
        '''
        UCs:
        qubit[5] q;
        let my_var = q[1:4]
        let my_var = q[{0,3,5}]     # It returns the first, fourth and sixth elements
        '''

        eq_symbol_index = self.get_eq_symbol_index(line)
        
        var_id = line[eq_symbol_index - 1]
        reference_var = line[eq_symbol_index + 1]
        init_value = ""
        translation = ""

        if reference_var in translated_code_info[translator_utils.KEY_QUBITS]:
            type = "qubit"
            result = self.get_let_indexes(translator_utils.KEY_QUBITS, line_number, line, eq_symbol_index, reference_var, translated_code_info)
            translated_code_info[translator_utils.KEY_QUBITS][var_id] = {"indexes": result, "next_index": result[-1] + 1, "is_let": True}

        elif reference_var in translated_code_info[translator_utils.KEY_BITS]:
            type = "bit"
            result = self.get_let_indexes(translator_utils.KEY_BITS, line_number, line, eq_symbol_index, reference_var, translated_code_info)
            translated_code_info[translator_utils.KEY_BITS][var_id] = {"indexes": result, "next_index": result[-1] + 1, "is_let": True}

        else:
            type = translated_code_info[translator_utils.KEY_VARS_REF][reference_var]["type"]
            init_value = self.get_let_indexes(None, line_number, line, eq_symbol_index, reference_var, translated_code_info, is_quantum=False)
            translation = f"{var_id}{init_value}"

        translated_code_info[translator_utils.KEY_VARS_REF][var_id] = {"id": var_id, "type": type}

        return translation

    def translate_duration(self, line_number, line, translated_code_info):
        error = f"There is no support yet for 'duration' type variables\n"
        error += f"\t(({line_number}, 0): {line})"
        raise NotImplementedError(error)
    
    def translate_stretch(self, line_number, line, translated_code_info):
        error = f"There is no support yet for 'stretch' type variables\n"
        error += f"\t(({line_number}, 0): {line})"
        raise NotImplementedError(error)
    
    def translate_input(self, line_number, line, translated_code_info):
        error = f"There is no support yet for 'input' type variables\n"
        error += f"\t(({line_number}, 0): {line})"
        raise NotImplementedError(error)
    
    def translate_output(self, line_number, line, translated_code_info):
        error = f"There is no support yet for 'output' type variables\n"
        error += f"\t(({line_number}, 0): {line})"
        raise NotImplementedError(error)

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

    def translate_p(self, line_number, line, translated_code_info):
        '''
        UC:
        p(pi) my_qubit;
        '''

        # angle, line_index = get_param(line_number, line, 1)     # Start at index 1 to avoid reading first '('
        # qubit_name, qubit_index, line_index = get_qu_bit(line, line_index)

        # targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        # qsimov_gate = stdgates_open_to_qsimov["p"]
        # t_gate = f"f\"{qsimov_gate}({angle})\""

        # return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

        raise NotImplementedError("The 'p' gate is not implemented yet")

    def translate_x(self, line_number, line, translated_code_info):
        '''
        UC:
        x my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["x"]
        t_gate = f"f\"{qsimov_gate}\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_y(self, line_number, line, translated_code_info):
        '''
        UC:
        y my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["y"]
        t_gate = f"f\"{qsimov_gate}\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation
    
    def translate_z(self, line_number, line, translated_code_info):
        '''
        UC:
        z my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["z"]
        t_gate = f"f\"{qsimov_gate}\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_h(self, line_number, line, translated_code_info):
        '''
        UC:
        h my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["h"]
        t_gate = f"f\"{qsimov_gate}\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_s(self, line_number, line, translated_code_info):
        '''
        UC:
        s my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.S_gate_name}\""

        if self.is_S_implemented:
            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_S_implemented = True
            
            translated_code_info[translator_utils.KEY_NEW_MATRICES][self.S_gate_name] = add_new_gate_matrix(self.S_gate_name, self.S_matrix, aliases=self.S_gate_aliases)

            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
            
        return translation
            
    def translate_sdg(self, line_number, line, translated_code_info):
        '''
        UC:
        sdg my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.S_gate_name}-1\""

        if self.is_S_implemented:
            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_S_implemented = True

            translated_code_info[translator_utils.KEY_NEW_MATRICES][self.S_gate_name] = add_new_gate_matrix(self.S_gate_name, self.S_matrix, aliases=self.S_gate_aliases)

            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

        return translation

    def translate_t(self, line_number, line, translated_code_info):
        '''
        UC:
        t my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.T_gate_name}\""

        if self.is_T_implemented:
            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_T_implemented = True

            translated_code_info[translator_utils.KEY_NEW_MATRICES][self.T_gate_name] = add_new_gate_matrix(self.T_gate_name, self.T_matrix, aliases=self.T_gate_aliases)

            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

        return translation

    def translate_tdg(self, line_number, line, translated_code_info):
        '''
        UC:
        tdg my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line, 0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        t_gate = f"f\"{self.T_gate_name}-1\""

        if self.is_T_implemented:
            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        else:
            self.is_T_implemented = True

            translated_code_info[translator_utils.KEY_NEW_MATRICES][self.T_gate_name] = add_new_gate_matrix(self.T_gate_name, self.T_matrix, aliases=self.T_gate_aliases)

            translation = ""
            # if len(targets) > 1:
            for id in targets:
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
            # else:
            #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

        return translation

    def translate_sx(self, line_number, line, translated_code_info):
        '''
        UC:
        sx my_qubit;
        '''

        qubit_name, qubit_index, _ = get_qu_bit(line,0)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["sx"]
        t_gate = f"f\"{qsimov_gate}\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_rx(self, line_number, line, translated_code_info):
        '''
        UC:
        rx my_qubit;
        '''

        angle, line_index = get_param(line_number, line, 1, translated_code_info)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["rx"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_ry(self, line_number, line, translated_code_info):
        '''
        UC:
        ry my_qubit;
        '''

        angle, line_index = get_param(line_number, line, 1, translated_code_info)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["ry"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_rz(self, line_number, line, translated_code_info):
        '''
        UC:
        rz my_qubit;
        '''

        angle, line_index = get_param(line_number, line, 1, translated_code_info)
        qubit_name, qubit_index, _ = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["rz"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_cx(self, line_number, line, translated_code_info):
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

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation

    def translate_cy(self, line_number, line, translated_code_info):
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

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation

    def translate_cz(self, line_number, line, translated_code_info):
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

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation
    
    def translate_cp(self, line_number, line, translated_code_info):
        '''
        UC:
        cp(pi) my_qubit[0], my_qubit[1];
        '''

        # angle, line_index = get_param(line_number, line, 1, translated_code_info)
        # control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        # target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        # controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        # targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        # qsimov_gate = stdgates_open_to_qsimov["cp"]
        # t_gate = f"f\"{qsimov_gate}({angle})\""

        # return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"

        raise NotImplementedError("The 'cp' gate is not implemented yet")

    def translate_crx(self, line_number, line, translated_code_info):
        '''
        UC:
        crx my_qubit[0], my_qubit[1];
        '''

        angle, line_index = get_param(line_number, line, 1, translated_code_info)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["crx"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation

    def translate_cry(self, line_number, line, translated_code_info):
        '''
        UC:
        cry my_qubit[0], my_qubit[1];
        '''

        angle, line_index = get_param(line_number, line, 1, translated_code_info)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["cry"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation

    def translate_crz(self, line_number, line, translated_code_info):
        '''
        UC:
        crz my_qubit[0], my_qubit[1];
        '''

        angle, line_index = get_param(line_number, line, 1, translated_code_info)
        control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["crz"]
        t_gate = f"f\"{qsimov_gate}({angle})\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation

    def translate_ch(self, line_number, line, translated_code_info):
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

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation

    def translate_swap(self, line_number, line, translated_code_info):
        '''
        UC:
        swap my_qubit[0], my_qubit[1];
        '''

        qubit_name_1, qubit_index_1, line_index = get_qu_bit(line, 0)
        qubit_name_2, qubit_index_2, _ = get_qu_bit(line, line_index)

        qsimov_qubit_index_1 = get_indexes(translator_utils.KEY_QUBITS, qubit_name_1, qubit_index_1, translated_code_info)
        qsimov_qubit_index_2 = get_indexes(translator_utils.KEY_QUBITS, qubit_name_2, qubit_index_2, translated_code_info)
        targets = [qsimov_qubit_index_1[0], qsimov_qubit_index_2[0]]

        qsimov_gate = stdgates_open_to_qsimov["swap"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"

    def translate_ccx(self, line_number, line, translated_code_info):
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

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}], controls={controls})\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={controls})"
        
        return translation

    def translate_cswap(self, line_number, line, translated_code_info):
        '''
        UC:
        cswap my_qubit[0], my_qubit[1], my_qubit[2];
        '''

        control_qubit_name, control_qubit_index_1, line_index = get_qu_bit(line, 0)
        target_qubit_name_1, target_qubit_index_1, line_index = get_qu_bit(line, line_index)
        target_qubit_name_2, target_qubit_index_2, _ = get_qu_bit(line, line_index)

        qsimov_control_qubit_index = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index_1, translated_code_info)
        qsimov_target_qubit_index_1 = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name_1, target_qubit_index_1, translated_code_info)
        qsimov_target_qubit_index_2 = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name_2, target_qubit_index_2, translated_code_info)
        targets = [qsimov_target_qubit_index_1[0], qsimov_target_qubit_index_2[0]]

        qsimov_gate = stdgates_open_to_qsimov["cswap"]
        t_gate = f"f\"{qsimov_gate}\""

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets}, controls={qsimov_control_qubit_index})"

    def translate_cu(self, line_number, line, translated_code_info):
        '''
        UC:
        cu(0,0,pi, pi) my_qubit[0], my_qubit[1];
        '''

        # u_angle_1, line_index = get_param(line_number, line, 1, translated_code_info)
        # u_angle_2, line_index = get_param(line_number, line, line_index, translated_code_info)
        # u_angle_3, line_index = get_param(line_number, line, line_index, translated_code_info)
        # p_angle, line_index = get_param(line_number, line, line_index, translated_code_info)
        # control_qubit_name, control_qubit_index, line_index = get_qu_bit(line, line_index)
        # target_qubit_name, target_qubit_index, _ = get_qu_bit(line, line_index)

        # controls = get_indexes(translator_utils.KEY_QUBITS, control_qubit_name, control_qubit_index, translated_code_info)
        # targets = get_indexes(translator_utils.KEY_QUBITS, target_qubit_name, target_qubit_index, translated_code_info)

        # qsimov_gate_p = stdgates_open_to_qsimov["p"]
        # qsimov_gate_u = stdgates_open_to_qsimov["U"]
        # t_gate_p = f"f\"{qsimov_gate_p}({p_angle} - {u_angle_1}/2)\""
        # t_gate_u = f"f\"{qsimov_gate_u}({u_angle_1}, {u_angle_2}, {u_angle_3})\""

        # translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate_p}, targets={controls})"
        # translation += "\n"
        # translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate_u}, targets={targets}, controls={controls})"

        # return translation

        raise NotImplementedError("The 'cu' gate is not implemented yet")

    def translate_u(self, line_number, line, translated_code_info):
        '''
        UC:
        U(0, 0, pi) my_qubit[0];
        '''
        angle_1, line_index = get_param(line_number, line, 1, translated_code_info)
        angle_2, line_index = get_param(line_number, line, line_index, translated_code_info)
        angle_3, line_index = get_param(line_number, line, line_index, translated_code_info)
        qubit_name, qubit_index, line_index = get_qu_bit(line, line_index)

        targets = get_indexes(translator_utils.KEY_QUBITS, qubit_name, qubit_index, translated_code_info)

        qsimov_gate = stdgates_open_to_qsimov["U"]
        t_gate = f"f\"{qsimov_gate}({angle_1}, {angle_2}, {angle_3})\""

        translation = ""
        # if len(targets) > 1:
        for id in targets:
            translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets=[{id}])\n"
        # else:
        #     translation = f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={targets})"
        
        return translation

    def translate_gphase(self, line_number, line, translated_code_info):
        raise NotImplementedError("The 'gphase' gate is not implemented yet")

class GateOperationTranslator:
    def __init__(self):
        pass

    def get_mod_param(self, line_number, line, line_index, translated_code_info):
        param = []
        read = False

        for i in range(line_index, len(line)):
            item = line[i]
            if item == "@":     break
            if item == ")":     return get_expression(line_number, param, translated_code_info), i + 2     # +1 because of the ')' and the '@'
            if read:            param.append(item)
            if item == "(":     read = True

        return "1", line_index + 2

    def pow_gate(self, exp, matrix):
        return matrix.pow(exp)
    
    def invert_gate(self, matrix):
        matrix = matrix.transpose()
        matrix = matrix.conjugate()

        return matrix
    
    def get_modifiers(self, line_number, line, translated_code_info):
        mod_anti_controls = []
        mod_inv_pow = []

        line_index = 0
        mod = line[0]
        while mod in translator_utils.gate_operations:
            param, line_index = self.get_mod_param(line_number, line, line_index, translated_code_info)

            if mod == "ctrl" or mod == "negctrl":
                mod_anti_controls.append((mod, eval(param)))

            else:
                mod_inv_pow.append((mod, eval(param)))

            mod = line[line_index]

        # Remember the gate to apply
        gate = mod
        line_index += 1

        return mod_anti_controls, mod_inv_pow, gate, line_index
        
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
        
    def build_new_gate(self, gate, mod_inv_pow, mod_inv_pow_length, amount_params, translated_code_info):
        if gate in translated_code_info[translator_utils.KEY_CUSTOM_GATES]:
            raise NotImplementedError("Custom gates cannot be used yet when more than two modifiers are applied to the gate")
    
        # Build a name for the new gate
        new_gate = ""
        for i in range(mod_inv_pow_length):
            mod, param = mod_inv_pow[i]
            if mod == "inv":    new_gate += f"{mod}_"
            else:               new_gate += f"{mod}{str(param).replace(".", "_")}_"
        new_gate += gate

        if new_gate not in translated_code_info[translator_utils.KEY_NEW_MATRICES]:
            # Compute the new gate matrix
            matrix = _gate_func[stdgates_open_to_qsimov[gate]]()
            for i in range(mod_inv_pow_length):
                mod, param = mod_inv_pow[-i]

                if mod == "inv":
                    matrix = self.invert_gate(matrix)
                
                else:
                    matrix = self.pow_gate(param, matrix)

            # Add new gate matrix to qsimov
            translated_code_info[translator_utils.KEY_NEW_MATRICES][new_gate] = add_new_gate_matrix(new_gate, matrix, amount_params, amount_params)

        return new_gate
        
    def compute_inv_pow(self, mod_inv_pow, gate, amount_params, translated_code_info):
        mod_inv_pow_length = len(mod_inv_pow)
        is_inv = False
        power = 1

        if mod_inv_pow_length > 1:
            gate = self.build_new_gate(gate, mod_inv_pow, mod_inv_pow_length, amount_params, translated_code_info)

        elif mod_inv_pow_length == 1:
            mod, param = mod_inv_pow[0]

            if mod == "inv":    
                is_inv = True
            else:
                if isinstance(param, int):
                    power = param
                else:
                    gate = self.build_new_gate(gate, mod_inv_pow, mod_inv_pow_length, amount_params, translated_code_info)

        return gate, is_inv, power

    def get_t_gate(self, gate, gate_params, is_inv, amount_params, translated_code_info):
        if gate in stdgates_open_to_qsimov:
            if amount_params > 0:
                if is_inv:      t_gate = f"f\"{stdgates_open_to_qsimov[gate]}({list_to_string(gate_params)})-1\""
                else:           t_gate = f"f\"{stdgates_open_to_qsimov[gate]}({list_to_string(gate_params)})\""
            
            else:
                if is_inv:      t_gate = f"f\"{stdgates_open_to_qsimov[gate]}-1\""
                else:           t_gate = f"f\"{stdgates_open_to_qsimov[gate]}\""

        elif gate in translated_code_info[translator_utils.KEY_CUSTOM_GATES]:
            if amount_params > 0:
                if is_inv:      t_gate = f"{gate}({list_to_string(gate_params)}).invert()"
                else:           t_gate = f"{gate}({list_to_string(gate_params)})"
        
            else:
                if is_inv:      t_gate = f"{gate}().invert()"
                else:           t_gate = f"{gate}()"

        else:
            if amount_params > 0:
                t_gate = f"f\"{gate}\"({list_to_string(gate_params)})"
            
            else:
                t_gate = f"f\"{gate}\""

        return t_gate

    def get_t_targets_controls(self, mod_qu_bits, q_controls, q_anticontrols, c_controls, c_anticontrols):
        # qubits = []
        # for qubit in mod_qu_bits:
        #     qubits += qubit[0]

        # targets = set(qubits) - set(q_controls)
        # targets -= set(q_anticontrols)
        # targets -= set(c_controls)
        # targets -= set(c_anticontrols)
        # targets = list(targets)
        targets = mod_qu_bits[-1][0]

        # In case we are calling a custom function, we need to rewrite the controls and anticontrols using their ids
        if TranslatorUtils.is_custom_def:
            q_controls, q_anticontrols, c_controls, c_anticontrols, _ = self.rewrite_anti_controls(q_controls, q_anticontrols, c_controls, c_anticontrols, targets)

        # t_targets = f"targets={targets}"
        t_controls = f", controls={q_controls}"                         if q_controls       else ""
        t_anticontrols = f", anticontrols={q_anticontrols}"             if q_anticontrols   else ""
        t_c_controls = f", c_controls={c_controls}"                     if c_controls       else ""
        t_c_anticontrols = f", c_anticontrols={c_anticontrols}"         if c_anticontrols   else ""

        return targets, t_controls, t_anticontrols, t_c_controls, t_c_anticontrols

    def translate_mod(self, line_number, line, translated_code_info):
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
        mod_anti_controls, mod_inv_pow, gate, line_index = self.get_modifiers(line_number, line, translated_code_info)

        # Get the gate's parameters, if it has
        gate_params, line_index = get_all_params(line_number, gate, line, line_index, translated_code_info)
        amount_params = len(gate_params)

        # Get in order the qubits/bits used as controls or anticontrols
        mod_qu_bits, line_index = self.get_mod_qu_bits(line, line_index, translated_code_info)

        # Differentiate between q/c controls/anticontrols according to the order of the modifiers
        self.get_q_c_controls_anticontrols(mod_anti_controls, mod_qu_bits, q_controls, c_controls, q_anticontrols, c_anticontrols)

        # Compute 'inv' and 'pow' modifiers
        gate, is_inv, power = self.compute_inv_pow(mod_inv_pow, gate, amount_params, translated_code_info)

        # Compute translation components
        t_gate = self.get_t_gate(gate, gate_params, is_inv, amount_params, translated_code_info)
        targets, t_controls, t_anticontrols, t_c_controls, t_c_anticontrols = self.get_t_targets_controls(mod_qu_bits, q_controls, q_anticontrols, c_controls, c_anticontrols)

        # Build the translation
        translation = ""

        if len(targets) > 1:
            for id in targets:
                t_targets = f"targets=[{id}]"
                for i in range(power):
                    translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, {t_targets}{t_controls}{t_anticontrols}{t_c_controls}{t_c_anticontrols})\n"
        else:
            t_targets = f"targets=[{targets[0]}]"
            for i in range(power):
                translation += f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, {t_targets}{t_controls}{t_anticontrols}{t_c_controls}{t_c_anticontrols})\n"

        return translation[:-1]

    def translate_gate(self, line_number, line, translated_code_info):
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
                param, line_index = get_param(line_number, line, line_index, translated_code_info, True)
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

    def translate_custom_gate(self, line_number, line, translated_code_info):
        gate = line[0]
        gate_params, line_index = get_all_params(line_number, gate, line, 1, translated_code_info, is_custom_gate=True)     # starting line_index = 1 to avoid reading '(' as the function also adds 1 to the variable
        qubits, line_index = self.get_mod_qu_bits(line, line_index, translated_code_info)
        # As the previus methods returns a list of tuples formed by qubit and key, we need to get just the qubits in this case
        t_qubits = []
        for qubit in qubits:
            t_qubits += qubit[0]
        
        t_gate = f"{gate}({list_to_string(gate_params)})"     if gate_params      else    f"{gate}()"

        return f"{TranslatorUtils.QCircuit_name}.add_operation({t_gate}, targets={t_qubits})"

    def translate_reset(self, line_number, line, translated_code_info):
        '''
        UC:

        reset target;
        reset targets[0];
        reset targets;
        '''

        # error = f"The builtin function 'reset' is not supported yet\n"
        # error += f"\t(({line_number}, {0}): {line})"
        # raise NotImplementedError(error)
        return ""

    def translate_measure(self, line_number, line, translated_code_info):
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

    def translate_barrier(self, line_number, line, translated_code_info):
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
    result = array.copy()
    for i in range(distance):
        first = result.pop(0)
        result.append(first)
    return result
        '''
        return func
    
    def rotr(self):
        func = '''
def rotr(array, distance):
    result = array.copy()
    for i in range(distance):
        first = result.pop(0)
        result.insert(0, first)
    return result
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

    def get_bit(self, line_number, line, line_index, var_id, translated_code_info):
        if line_index >= len(line):
            index = -1

        elif line[line_index] == "[":
            index = int(line[line_index + 1])
            line_index += 3
        else:
            index = -1

        bit_index = get_indexes(translator_utils.KEY_BITS, var_id, index, translated_code_info)

        if len(bit_index) > 1:    
            error = f"We only support bit operations of length 1 bit. Cannot operate whole registers\n"
            error += f"\t(({line_number}, {line_index-1}): {line})"
            raise NotImplementedError(error)
        
        return bit_index, line_index

    def get_operator(self, line_number, line, line_index, translated_code_info):
        var_id = line[line_index]
        if var_id.isdigit():    is_digit = True
        else:                   is_digit = False
        line_index += 1

        if var_id not in translated_code_info[translator_utils.KEY_BITS] and not is_digit:
            error = f"Bit operations only support 'bit' variables or single digits as operators\n"
            error += f"\t(({line_number}, {line_index}): {line})"
            raise NotImplementedError(error)

        if is_digit:
            if len(var_id) > 1:
                error = f"We only support bit operations of length 1 bit. Cannot operate whole registers\n"
                error += f"\t(({line_number}, {line_index-1}): {line})"
                raise NotImplementedError(error)

            else:
                operator_bit = [var_id]
                line_index += 1

        else:
            operator_bit, line_index = self.get_bit(line_number, line, line_index, var_id, translated_code_info)

        operator_bit[0] = int(operator_bit[0])
        return operator_bit, line_index, is_digit

    def is_NOT(self, line_number, line, line_index, first_operator_bit, is_digit, output_bit):
        if is_digit:
            error = f"'NOT' operations is only supported with 'bit' type variables, not digits"
            error += f"\t(({line_number}, {line_index}): {line})"
            raise NotImplementedError(error)
        
        else:
            translation = f"{TranslatorUtils.QCircuit_name}.add_operation(f\"NOT\", c_targets={first_operator_bit}, outputs={output_bit})"
            return translation

    def assignation(self, line_number, line, line_index, first_operator_bit, is_digit, output_bit):
        if is_digit:
            if first_operator_bit[0] == 1:
                translation = f"{TranslatorUtils.QCircuit_name}.add_operation(f\"SET\", c_targets={output_bit})"
                
            elif first_operator_bit[0] == 0:
                translation = f"{TranslatorUtils.QCircuit_name}.add_operation(f\"RESET\", c_targets={output_bit})"

            else:
                error = f"The bit value used is not compatible\n"
                error += f"\t(({line_number}, {line_index - 1}): {line})"
                raise ValueError(error)
            
            return translation
        
        else:
            error = f"There is no support yet to 'bit' variable access during execution of circuit\n"
            error += f"\t(({line_number}, {line_index - 1}): {line})"
            raise NotImplementedError(error)

    def translate_var_operation(self, line_number, line, key, translated_code_info):
        var_id = line[0]

        if translated_code_info[key][var_id]["type"] == "bit":
            if TranslatorUtils.is_custom_def:
                error = f"Bitwise operations are not supported yet within the scope of a custom def\n"
                error += f"\t(({line_number}, 0): {line})"
                raise NotImplementedError(error)

            # Get output bit
            line_index = 1
            output_bit, line_index = self.get_bit(line_number, line, line_index, var_id, translated_code_info)
            
            # We only give support to '=' operation
            if line[line_index] != "=":
                error = f"We only support '=' operation for classic bits\n"
                error += f"\t(({line_number}, {line_index}): {line})"
                raise NotImplementedError(error)
            
            # Check if is 'NOT' operation
            line_index += 1
            is_NOT = False
            if line[line_index] == "~":
                is_NOT = True
                line_index += 1

            # Get first bit operator
            first_operator_bit, line_index, is_digit = self.get_operator(line_number, line, line_index, translated_code_info)

            if is_NOT:
                return self.is_NOT(line_number, line,line_index, first_operator_bit, is_digit, output_bit)

            # If it is just a normal assignation, there is no operation (AND, OR, XOR) right after, then we must check if the value to assign is a number or a variable
            if line_index >= len(line):
                return self.assignation(line_number, line, line_index, first_operator_bit, is_digit, output_bit)
            
            # Get mathematical/logical operator
            operator = line[line_index]
            if operator == "|":     op = "OR"
            elif operator == "&":   op = "AND"
            elif operator == "^":   op = "XOR"
            else:
                error = f"The only supported bit operations are 'OR', 'AND', 'NOT', 'XOR'\n"
                error += f"\t(({line_number}, {line_index}): {line})"
                raise NotImplementedError(error)

            # Get second bit operator
            line_index += 1
            second_operator_bit, line_index, is_digit = self.get_operator(line_number, line, line_index, translated_code_info)

            # Make the translation
            c_targets = [first_operator_bit[0], second_operator_bit[0]]

            translation = f"{TranslatorUtils.QCircuit_name}.add_operation(f\"{op}\", c_targets={c_targets}, outputs={output_bit})"
            return translation
            
        return get_expression(line_number, line, translated_code_info)
    
    def translate_rotl(self, line_number, line, translated_code_info):
        # translation = ""

        # if not self.is_rotl_defined:
        #     self.is_rotl_defined = True

        #     translation = self.rotl()
        #     translation += "\n"

        # translation += "rotl" + get_expression(line_number, line, translated_code_info)
        # return translation

        error = f"'The builtin function 'rotl' is not supported yet\n"
        error += f"\t(({line_number}, {0}): {line})"
        raise NotImplementedError(error)

    def translate_rotr(self, line_number, line, translated_code_info):
        # translation = ""

        # if not self.is_rotr_defined:
        #     self.is_rotr_defined = True

        #     translation = self.rotr()
        #     translation += "\n"

        # translation += "rotr" + get_expression(line_number, line, translated_code_info)
        # return translation

        error = f"'The builtin function 'rotr' is not supported yet\n"
        error += f"\t(({line_number}, {0}): {line})"
        raise NotImplementedError(error)
    
    def translate_if_else(self, line_number, line, translated_code_info):
        return get_expression(line_number, line, translated_code_info) + ":"

    def translate_for(self, line_number, line, translated_code_info):
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
            range = get_expression(line_number, line[i+1:], translated_code_info)       # Here i points to keyword 'in'

        translation = f"for {var_id} in {range}:"

        return translation

    def translate_while(self, line_number, line, translated_code_info):
        return get_expression(line_number, line, translated_code_info) + ":"

    def translate_def(self, line_number, line, translated_code_info):
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

    def translate_break(self, line_number, line, translated_code_info):
        return "break"
    
    def translate_continue(self, line_number, line, translated_code_info):
        return "continue"
    
    def translate_return(self, line_number, line, translated_code_info):
        return f"return {get_expression(line_number, line[1:], translated_code_info)}"

    def translate_end(self, line_number, line, translated_code_info):
        return f"{TranslatorUtils.QCircuit_name}.add_operation(\"END\")"

    def translate_custom_def(self, line_number, line, translated_code_info):
        def_name = line[0]

        if line[1] != "(":      raise ValueError("The call to a custom function must be done using brackets to indicate the parameters")

        params, _ = get_all_params(line_number, def_name, line, 1, translated_code_info, is_custom_def=True)
        t_params = ""
        is_first_param = True
        
        for param in params:
            if param[0] in translated_code_info[translator_utils.KEY_QUBITS]:
                qu_bit_name, index, _ = get_qu_bit(param, 0)
                t_param = get_indexes(translator_utils.KEY_QUBITS, qu_bit_name, index, translated_code_info)

            elif param[0] in translated_code_info[translator_utils.KEY_BITS]:
                qu_bit_name, index, _ = get_qu_bit(param, 0)
                t_param = get_indexes(translator_utils.KEY_BITS, qu_bit_name, index, translated_code_info)

            else:
                t_param = get_expression(line_number, param, translated_code_info)

            if is_first_param:
                is_first_param = False
                t_params += f"{t_param}"
            else:
                t_params += f", {t_param}"            

        return f"{def_name}({t_params})"
