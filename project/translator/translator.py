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

    def init_data_structures(self):
        self.translated_code_info = {
            self.translator_utils.KEY_QUBITS:       {},
            self.translator_utils.KEY_BITS:         {},
            self.translator_utils.KEY_CUSTOM_GATES: {"amount": 0, "lines": []},
            self.translator_utils.KEY_INSTRUCTIONS: {"amount": 0, "lines": []},
            self.translator_utils.KEY_VARS_REF:     {}
        }
        self.translated_code = []

    def translate(self, parsed_code):
        custom_gate_init_indent = -1
        gate_translation = ""

        for line in parsed_code:
            # Get the keyword of the instruction to know which kind of translation we have to do
            keyword = line[1][0]

            # Check if we have finished translating a custom gate
            if line[0] == custom_gate_init_indent:
                TranslatorUtils.is_custom_gate = False
                TranslatorUtils.QCircuit_name = self.translator_utils.QCircuit_name
                custom_gate_init_indent = -1

                self.translated_code.append(gate_translation)
                gate_translation = ""

            # Check measurement
            if "measure" in line[1]:
                translation = self.gate_op_translator.translate_measure(line[1], self.translated_code_info)

            # Check custom gate definition
            elif keyword == "gate":
                custom_gate_init_indent = line[0]
                # This translation is not the final one but the first two lines of it
                translation = self.gate_op_translator.translate_gate(line[1][1:], self.translated_code_info)

            # Check data type
            elif keyword in self.translator_utils.data_types:
                # Get corresponding method for translation
                method = self.translator_utils.data_types[keyword]
                # Translate the line without the keyword as it is not needed now
                translation = getattr(self.data_type_translator, method)(line[1][1:], self.translated_code_info)

            # Check std gate
            elif keyword in self.translator_utils.std_gates:
                # Get corresponding method for translation
                method = self.translator_utils.std_gates[keyword]
                # Translate the line without the keyword as it is not needed now
                translation = getattr(self.std_gate_translator, method)(line[1][1:], self.translated_code_info)

            # Check gate operation
            elif keyword in self.translator_utils.gate_operations:
                # Get corresponding method for translation
                method = self.translator_utils.gate_operations[keyword]
                # Translate the line without the keyword as it is not needed now
                translation = getattr(self.gate_op_translator, method)(line[1], self.translated_code_info)  # This time we maintain the keyword

            # Check if we are translating a custom gate
            if not TranslatorUtils.is_custom_gate:
                self.translated_code.append(translation)
            else:
                # Compute the indent
                tab = "\t"
                indent = ""
                for i in range(line[0]):
                    indent += tab
                
                # Add the translation to the custom gate
                gate_translation += indent + translation + "\n"

        return self.translated_code