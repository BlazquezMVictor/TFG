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

    float[16] my_var = pi;
    float[16] my_var;
    float my_var = 2.3;
    float my_var;

    angle[16] my_var = pi;
    angle[16] my_var;
    angle my_var = pi;
    angle my_var;

    complex[float[16]] my_var = pi;
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
        bellprep(bp);
        cx io, bp[0];
        h io;
        pf[0] = measure io;
        pf[1] = measure bp[0];
        if (pf[0]==1) {
            z bp[1];
        }
        if (pf[1]==1)   {
            x bp[1];
        }
        let io = bp[1];
    }

    h io;
    output_qubit = measure io;
'''

stdgates = '''
qubit my_qubit;
qubit[3] my_qubits;

x my_qubit;
x my_qubits;

y my_qubit;
y my_qubits;

z my_qubit;
z my_qubits;

h my_qubit;
h my_qubits;

s my_qubit;
s my_qubits;

sdg my_qubit;
sdg my_qubits;

t my_qubit;
t my_qubits;

tdg my_qubit;
tdg my_qubits;

sx my_qubit;
sx my_qubits;

rx(pi) my_qubit;
rx(pi) my_qubits;

ry(pi) my_qubit;
ry(pi) my_qubits;

rz(pi) my_qubit;
rz(pi) my_qubits;

cx my_qubits[0], my_qubits[1];
cx my_qubit, my_qubits;

cy my_qubits[0], my_qubits[1];
cy my_qubit, my_qubits;

cz my_qubits[0], my_qubits[1];
cz my_qubit, my_qubits;

crx(pi) my_qubits[0], my_qubits[1];
crx(pi) my_qubit, my_qubits;

cry(pi) my_qubits[0], my_qubits[1];
cry(pi) my_qubit, my_qubits;

crz(pi) my_qubits[0], my_qubits[1];
crz(pi) my_qubit, my_qubits;

ch my_qubits[0], my_qubits[1];
ch my_qubit, my_qubits;

swap my_qubits[0], my_qubits[1];

ccx my_qubits[0], my_qubits[1], my_qubits[2];
ccx my_qubits[0], my_qubits[1], my_qubits;

cswap my_qubits[0], my_qubits[1], my_qubits[2];

U(pi/4, 0, pi/2) my_qubit;
U(pi/4, 0, pi/2) my_qubits;
'''

gate_operations = '''
qubit target;
qubit[4] targets;
qubit[4] controls;
bit measurement;
bit[4] measurements;

ctrl @ x controls[0], target;
ctrl(2) @ x controls[0], controls[1], target;
negctrl @ x controls[0], target;
negctrl(2) @ x controls[0], controls[1], target;
inv @ x target;
pow(2) @ sx target;

reset target;
measurement = measure target;
measurements[2] = measure targets[3];
measurements = measure targets;
barrier target;
barrier controls;

gate my_crz(pi) c, t {
    ctrl @ rz(pi) c, t;
}
my_crz(pi) controls[0], target;

ctrl @ negctrl @ inv @ pow(2) @ x controls[0], controls[1], target;
ctrl(2) @ negctrl(2) @ inv @ pow(2) @ x controls[0], controls[1], controls[2], controls[3], target;
ctrl @ negctrl @ ctrl @ inv @ pow(2) @ x controls[0], controls[1], controls[2], target;
'''

modifiers = '''
qubit target;
qubit[4] targets;
qubit[4] controls;
bit measurement;
bit[4] measurements;

ctrl @ x controls[0], target;
ctrl(2) @ x controls[0], controls[1], target;
negctrl @ x controls[0], target;
negctrl(2) @ x controls[0], controls[1], target;
inv @ x target;
pow(2) @ sx target;

ctrl @ negctrl @ inv @ pow(2) @ x controls[0], controls[1], target;
ctrl(2) @ negctrl(2) @ inv @ pow(2) @ x controls[0], controls[1], controls[2], controls[3], target;
ctrl @ negctrl @ ctrl @ inv @ pow(2) @ x controls[0], controls[1], controls[2], target;

ctrl @ negctrl(2) @ negctrl @ ctrl(2) @ x measurement, measurements[0], measurements[1], target, controls[0], controls[1], targets[0];
'''

inv_pow_modifiers = '''
qubit target;
qubit control;
bit measurement;
bit[4] measurements;

gate my_gate_2 t1, {
    z t1;
}

inv @ x target;
pow(2) @ sx target;
pow(2.5) @ x target;

inv @ my_gate_2 target;
pow(2) @ my_gate_2 target;

ctrl @ inv @ pow(2) @ x control, target;
ctrl @ inv @ pow(2.5) @ x control, target;
'''

custom_gates = '''
qubit target;
qubit[4] targets;
qubit[4] controls;
bit measurement;
bit[4] measurements;

gate my_gate_1(a1, a2, a3) c1, c2, t {
    ctrl @ rz(a1) c1, t;
    negctrl @ rx(a2) c2, t;
    u(a1, a2, a3) t;
}

z target;

gate my_gate_2 t1, t2 {
    y t1;
    z t2;
}

my_gate_1(pi, 10.8, 5.0) controls[0], controls[1], target;
my_gate_2 target, targets;
ctrl @ my_gate_2 controls[0], target, targets[0];
'''

classic_basic_instructions = '''
int a;
int b = 10;
bit[8] c = "10001111";
bit[8] d = "01110000";
bool e = false;
int f = 1;
int g = 2;
int i = 3;


a = b;
b = 0;
a == b;
a == 10;

popcount(d);

e == false;
e == bool(f);
f >= b;
f == pi;
f == float(b);

g * i;
i / g;
i % g;
g ** i;
g += 4;
'''

classic_if_instruction = '''
int a = 0;
int b = 1;
int c = 0;
qubit[5] targets;
qubit[5] controls;

if  ((a == b) && (a == c)) {
    c = 2;
    if (c >= b) {
        h targets[0];
        ctrl @ x controls[0], targets[1];
    } else {
        c = 7;
    }
} else {
    a = 2;
}

if (a == b) {
    if (c == 0) {
        a = 3;
    }
}
else { 
    a = 2;
}
'''

classic_for_instruction = '''
int[32] d = 0;
qubit[5] targets;
qubit[5] controls;

for int[32] i in {1, 5, 10} {
    if (i == 1) {
        d += 5;
    }

    d += 1;
}

for int i in [0:2:20] {
    x targets[0];
}

for uint[64] i in [4294967296:4294967306] {
    d += 1;
}

array[float[64], 4] my_floats = {1.2, -3.4, 0.5, 9.8};
    for float[64] f in my_floats {
    d += 1;
}
'''

classic_while_instruction = '''
int[32] i = 0;
int d = 2;
qubit[5] targets;
qubit[5] controls;

while ((i < 10) || (d <= 5)) {
    if (i == 5) {
        for int j in {1, 2, 3} {
            d += j;
        }
    }

    i += 1;
    x targets[0];
    ctrl(2) @ h controls[0], controls[1], targets[0];

    if (d >= 2) {
        break;
    }

    if (i == 3) {
        continue;
    }
}

while (true)
    d += 1;
'''

classic_def_no_qubit_instruction = '''
def my_subroutine(int a1, float a2) -> int {
    if (a1 >= 2) {
        return 0;
    }

    if (a2 <= 2) {
        return 0;
    }

    return 1;
}

const int n = 10;
def parity(bit[n] cin) -> bit {
    bit c;
    for int i in [0: n - 1] {
        c ^= cin[i];
    }
    return c;
}

def array_sub(readonly array[int[8], 2, 10] arr1, mutable array[int[8], #dim = 1] arr2) {
    arr2[2] = 10;
    uint[32] dim1  = sizeof(arr1, 1);
    uint[32] dim2  = sizeof(arr1[0], 0);
}

int result = my_subroutine(1, 5);

// parity
qubit q;
qubit r;
bit c;
bit c2;
c = measure q;
c2 = measure r;
bit[2] param;
param[0] = c;
param[1] = c2;
bit result;
result = parity(param);


array[int[8], 3, 5] my_arr1;
array[int[8], 5] my_arr2;
array_sub(my_arr1, my_arr2);
'''

classic_def_instruction = '''
qubit qb;
qubit[5] qbs;
bit cb;
bit[5] cbs;
int test = 20;

def f1(qubit q) {
    x q;
}

def f2(qubit q1, qubit q2) {
    h q1;
    ctrl @ x q1, q2;
}

def f3(qubit[5] q) {
    for int i in [0 : 4] {
        z q[i];
    }
}

def f4(qubit[5] q, bit[5] b) -> bit {
    ctrl @ x b[0], q[0];
    ctrl @ x b[1], q[1];

    b[2] = measure q2;

    return b[2];
}

def f5(qubit q, int v, bit b) -> int{
    b = measure q;

    if (b == 0) {
        v += 10;
    } else {
        v -= 10;
    }

    return v;
}

f1(qb);
f2(qbs[0], qbs[1]);
f3(qbs);
cb = f4(qbs, cbs);
int var = f5(qb, test, cbs[3]);
'''

program = '''
float[64] a = 10;
qubit[3] q;
bit[2] mid;
bit[3] out;

let aliased = q[0:1];

gate my_gate(a) c, t {
    ry(a) c;
    cx c, t;
}
gate my_phase(a) c {
    ctrl @ rz(a) c;
}

my_gate(a * 2) q[0], q[0];
mid[0] = measure q[0];
mid[1] = measure q[1];

while (mid == "00") {
    reset q[0];
    reset q[1];
    my_gate(a) q[0], q[1];
    my_phase(a - pi/2) q[1];
    mid[0] = measure q[0];
    mid[1] = measure q[1];
}

if (mid[0]) {
    let inner_alias = q[0:1];
}

out = measure q;
'''

bit_ops = '''
bit[5] b1;
bit b2;
bit b3;

b2 = b3 | b1[0];
b2 = b3 & b1[0];
b2 = b3 ^ b1[0];
b2 = ~b3;
b2 = ~b1[0];
'''

let = '''
qubit[5] q1;
qubit[5] qq1;
bit[5] b1;
array[int, 5] i1;

let q2 = qq1[{0,2,4}];
let q3 = q1[1:3];
let b2 = b1[{0,2,4}];
let b3 = b1[1:3];
let i2 = i1[{0,2,4}];
let i3 = i1[1:3];

x q2[1];
x q3[0];
b1[1] = ~b2[1];
b1[1] = ~b3[0];
i1[1] = i2[1] + 5;
i1[1] = i3[0] + 5;
'''
