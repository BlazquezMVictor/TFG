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

let aliased = q[0:1];

gate my_gate(a) c, t {
    ry(a) c;
    cx c, t;
}
gate my_phase(a) c, t{
    ctrl @ rz(a) c, t;
}

my_gate(a * 2) aliased[0], q[1];
mid[0] = measure q[0];
mid[1] = measure q[1];

while ("11" == "00") {
    my_gate(a) q[0], q[1];
    my_phase(a - pi/2) q[0], aliased[1];
    mid[0] = measure q[0];
    mid[1] = measure q[1];
}

if (true) {
    let inner_alias = q[0:1];
    x inner_alias[1];
}

out = measure q;
'''

# MAIN
if __name__ == "__main__":
    translator = Translator()
    translation = translator.translate(code)

    for line in translation:
        print(line)