from .type_instr_translator import *
from .translator_utils import TranslatorUtils

class Translator:
    def __init__(self):
        self.init_type_instr_translators()
        self.init_data_structures()

    def init_type_instr_translators(self):
        self.translator_utils = TranslatorUtils()
        self.data_type_translator = DataTypeTranslator()
        self.std_gate_translator = STDGateTranslator()
        self.gate_op_translator = GateOperationTranslator()
        self.classic_inst_translator = ClassicInstTranslator()

    def init_data_structures(self):
        self.translated_code_info = {
            self.translator_utils.KEY_QUBITS:               {},
            self.translator_utils.KEY_BITS:                 {},
            self.translator_utils.KEY_CUSTOM_GATES:         {},
            self.translator_utils.KEY_SUBROUTINES:          {},
            self.translator_utils.KEY_SUBROUTINE_PARAMS:    {},
            self.translator_utils.KEY_VARS_REF:             {}
        }
        self.translated_code = []

    def compute_indent(self, amount_tabs):
        tab = "\t"
        indent = ""
        for i in range(amount_tabs):
            indent += tab

        return indent

    def translate(self, parsed_code):
        custom_gate_init_indent = -1
        custom_def_init_indent = -1
        gate_translation = ""

        for line in parsed_code:
            # Get the keyword of the instruction to know which kind of translation we have to do
            keyword = line[1][0]

            # Check if we have finished translating a custom gate
            if line[0] == custom_gate_init_indent:
                last_line = f"return {self.translator_utils.QGate_name}"
                gate_translation += self.compute_indent(custom_gate_init_indent + 1) + last_line + "\n"

                TranslatorUtils.is_custom_gate = False
                TranslatorUtils.QCircuit_name = self.translator_utils.QCircuit_name
                custom_gate_init_indent = -1

                self.translated_code.append(gate_translation)
                gate_translation = ""

            if line[0] == custom_def_init_indent:
                TranslatorUtils.is_custom_def = False
                custom_def_init_indent = -1
                self.translated_code.append("") # Add a blank line after the custom def

            # Check measurement
            if "measure" in line[1]:
                translation = self.gate_op_translator.translate_measure(line[1], self.translated_code_info)

            # Check custom gate definition
            elif keyword == "gate":
                custom_gate_init_indent = line[0]
                translation = self.gate_op_translator.translate_gate(line[1][1:], self.translated_code_info)

            # Check custom def definition
            elif keyword == "def":
                custom_def_init_indent = line[0]
                translation = self.classic_inst_translator.translate_def(line[1], self.translated_code_info)

            # Check data type
            elif keyword in self.translator_utils.data_types:
                method = self.translator_utils.data_types[keyword]
                translation = getattr(self.data_type_translator, method)(line[1][1:], self.translated_code_info)

            # Check std gate
            elif keyword in self.translator_utils.std_gates:
                method = self.translator_utils.std_gates[keyword]
                translation = getattr(self.std_gate_translator, method)(line[1][1:], self.translated_code_info)

            # Check if we are applying a custom gate
            elif keyword in self.translated_code_info[self.translator_utils.KEY_CUSTOM_GATES]:
                translation = self.gate_op_translator.translate_custom_gate(line[1], self.translated_code_info)

            # Check gate operation
            elif keyword in self.translator_utils.gate_operations:
                method = self.translator_utils.gate_operations[keyword]
                translation = getattr(self.gate_op_translator, method)(line[1], self.translated_code_info)  # This time we maintain the keyword

            # Check variable operation
            elif keyword in self.translated_code_info[self.translator_utils.KEY_VARS_REF] or keyword in self.translated_code_info[self.translator_utils.KEY_SUBROUTINE_PARAMS]:
                translation = self.classic_inst_translator.translate_var_operation(line[1], self.translated_code_info)

            # Check if we are calling a custom function
            elif keyword in self.translated_code_info[self.translator_utils.KEY_SUBROUTINES]:
                translation = self.classic_inst_translator.translate_custom_def(line[1], self.translated_code_info)

            # Check classic instruction
            elif keyword in self.translator_utils.classic_instructions:
                method = self.translator_utils.classic_instructions[keyword]
                translation = getattr(self.classic_inst_translator, method)(line[1], self.translated_code_info)

            # Check if we are translating a custom gate
            if not TranslatorUtils.is_custom_gate and translation:
                indent = self.compute_indent(line[0])
                translation = indent + translation

                self.translated_code.append(translation)
            elif TranslatorUtils.is_custom_gate:
                # Add the translation to the custom gate
                gate_translation += self.compute_indent(line[0]) + translation + "\n"

        return self.translated_code