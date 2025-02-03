import sys
import os

# This line will add to the python list of paths to look for modules the path to the project root
MAIN_PARENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if MAIN_PARENT_PATH not in sys.path:
    sys.path.append(MAIN_PARENT_PATH)


from translator.translator import Translator

code = '''
float[64] a = 10;
qubit[3] q;
bit[2] mid;
bit[3] out;

ctrl @ x mid[0], q[0];
'''

# MAIN
if __name__ == "__main__":
    translator = Translator()
    translation = translator.translate(code)

    print(translation)