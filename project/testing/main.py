from collections import Counter
import sys
import os
# This line will add to the python list of paths to look for modules the path to the project root
MAIN_PARENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if MAIN_PARENT_PATH not in sys.path:
    sys.path.append(MAIN_PARENT_PATH)
    
import qiskit.qasm3
from qiskit import transpile
from qiskit.providers.basic_provider import BasicSimulator

from translator.translator import Translator
from test_codes import stdgates_codes


translator = Translator(shots=1000)

def get_dict(input_list):
    binary_strings = [''.join(['1' if val else '0' for val in reversed(sublist)]) for sublist in input_list]
    counts = Counter(binary_strings)
    return dict(counts)

# code = '''
#     OPENQASM 3.0;
#     include "stdgates.inc";

#     qubit[2] q;
#     bit[2] b;
    
#     reset q[0];
#     reset q[1];

#     h q[0];
#     cx q[0], q[1];

#     reset q[0];

#     b[0] = measure q[0];
#     b[1] = measure q[1];
# '''

i = 0
codes = stdgates_codes.split("::")
while i < len(codes):
    title = codes[i][:-2]
    amount_qubits = codes[i][-2]
    code = codes[i + 1]
    
    print(title)
    # QISKIT
    circ = qiskit.qasm3.loads(code)
    backend = BasicSimulator()
    transpiled_circ = transpile(circ, backend)
    result = backend.run(transpiled_circ, shots=1000).result()
    counts = binary_counts = {format(int(k, 16), f"0{amount_qubits}b"): v for k, v in result.data()['counts'].items()}
    print(counts)

    # QSIMOV
    env = {}
    exec(translator.translate(code), env)
    print(get_dict(env["result"]))

    print()

    i += 2




