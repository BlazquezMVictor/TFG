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
        for line in parsed_code:
            # Get the keyword of the instruction to know which kind of translation we have to do
            keyword = line[1][0]

            # Check data type
            if keyword in self.translator_utils.data_types:
                # Get corresponding method for translation
                method = self.translator_utils.data_types[keyword]
                # Translate the line without the keyword as it is not needed now
                translation = getattr(self.data_type_translator, method)(line[1][1:], self.translated_code_info)
                self.translated_code.append(translation)

            # Check std gate
            elif keyword in self.translator_utils.std_gates:
                # Get corresponding method for translation
                method = self.translator_utils.std_gates[keyword]
                # Translate the line without the keyword as it is not needed now
                translation = getattr(self.std_gate_translator, method)(line[1][1:], self.translated_code_info)
                self.translated_code.append(translation)

        return self.translated_code