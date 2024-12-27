data_types = '''
    OPENQASM 3;
    include "stdgates.inc";
    
    qubit[3] my_var;
    qubit my_var;

    bit my_var;
    bit my_var = "1";
    bit[8] my_var;
    bit[8] my_var = "00001111";

    uint[16] my_var = 10;
    uint[16] my_var;
    uint my_var = 10;
    uint my_var;

    int[16] my_var = 10;
    int[16] my_var;
    int my_var = 10;
    int my_var;

    float[16] my_var = π;
    float[16] my_var;
    float my_var = 2.3;
    float my_var;

    angle[16] my_var = π;
    angle[16] my_var;
    angle my_var = π;
    angle my_var;

    complex[float[16]] my_var = π;
    complex[float[16]] my_var;
    complex[float] my_var = 2.3;
    complex[float] my_var;

    bool my_var = true;
    bool my_var = false;
    bool my_var;

    const uint my_var = 32;
    const float[32] my_var = 2.5;

    array[int[32], 5] my_var;
    array[int[32], 5] my_var = {0, 1, 2, 3, 4};
    array[float[32], 3, 2] my_var = {{1.1, 1.2}, {2.1, 2.2}, {3.1, 3.2}};

    qubit[5] q;
    let my_var = q[1:4];
    '''

code = '''
    /*
    * Prepare a parameterized number of Bell pairs
    * and teleport a qubit using them.
    */
    OPENQASM 3;
    include "stdgates.inc";

    const int[32] n_pairs = 10;  // number of teleportations to do

    def bellprep(qubit[2] q) {
    reset q;
    h q[0];
    cx q[0], q[1];
    }

    def xprepare(qubit q) {
    reset q;
    h q;
    }

    qubit input_qubit;
    bit output_qubit;
    qubit[2*n_pairs] q;

    xprepare(input_qubit);
    rz(pi / 4) input_qubit;

    let io = input_qubit;
    for uint i in [0: n_pairs - 1] {
    let bp = q[{2*i, 2*i + 1}];
    bit[2] pf;
    bellprep bp;
    cx io, bp[0];
    h io;
    pf[0] = measure io;
    pf[1] = measure bp[0];
    if (pf[0]==1) z bp[1];
    if (pf[1]==1) x bp[1];
    let io = bp[1];
    }

    h io;
    output_qubit = measure io;  // should get zero
'''

U = '''
include "stdgates.inc";

stretch g;

qubit[3] q;
barrier q;
cx q[0], q[1];
delay[g] q[2];
U(pi/4, 0, pi/2) q[2];
delay[2*g] q[2];
barrier q;
'''

stdgates = '''
qubit my_qubit;
qubit[3] my_qubits;

p(pi) my_qubit;
x my_qubit;
y my_qubit;
z my_qubit;
h my_qubit;
s my_qubit;
sdg my_qubit;
t my_qubit;
tdg my_qubit;
sx my_qubit;
rx(pi) my_qubit;
ry(pi) my_qubit;
rz(pi) my_qubit;
cx my_qubits[0], my_qubits[1];
cy my_qubits[0], my_qubits[1];
cz my_qubits[0], my_qubits[1];
cp(pi) my_qubits[0], my_qubits[1];
crx(pi) my_qubits[0], my_qubits[1];
cry(pi) my_qubits[0], my_qubits[1];
crz(pi) my_qubits[0], my_qubits[1];
ch my_qubits[0], my_qubits[1];
swap my_qubits[0], my_qubits[1];
ccx my_qubits[0], my_qubits[1], my_qubits[2];
cswap my_qubits[0], my_qubits[1], my_qubits[2];
cu(0,0,pi,pi) my_qubits[0], my_qubits[1];
'''