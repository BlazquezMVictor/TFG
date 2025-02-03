# -------------------------
# QISKIT CODES
# -------------------------
stdgates_codes = '''
-- X ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

x q[0];
b[0] = measure q[0];
::
-- Y ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

y q[0];
b[0] = measure q[0];
::
-- Z ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

z q[0];
b[0] = measure q[0];
::
-- H ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

h q[0];
b[0] = measure q[0];
::
-- S ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

s q[0];
b[0] = measure q[0];
::
-- SDG ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

sdg q[0];
b[0] = measure q[0];
::
-- T ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

t q[0];
b[0] = measure q[0];
::
-- TDG ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

tdg q[0];
b[0] = measure q[0];
::
-- SX ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

sx q[0];
b[0] = measure q[0];
::
-- RX(pi) ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

rx(pi) q[0];
b[0] = measure q[0];
::
-- RY(pi) ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

ry(pi) q[0];
b[0] = measure q[0];
::
-- RZ(pi) ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

rz(pi) q[0];
b[0] = measure q[0];
::
-- CX ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
cx q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- CY ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
cy q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- CZ ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
cz q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- CRX(pi) ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
crx(pi) q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- CRY(pi) ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
cry(pi) q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- CRZ(pi) ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
crz(pi) q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- CH ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
ch q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- SWAP ------ 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];
swap q[0], q[1];

b[0] = measure q[0];
b[1] = measure q[1];
::
-- CCX ------ 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

x q[0];
x q[1];
ccx q[0], q[1], q[2];

b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
::
-- CSWAP ------ 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

x q[0];
x q[1];
cswap q[0], q[1], q[2];

b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];

::
-- U ------ 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

U(pi, 10, 0.5) q[0];

b[0] = measure q[0];
'''

gate_operations_codes = '''
-- INV ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

inv @ x q[0];
b[0] = measure q[0];
::
-- POW(2) ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

pow(2) @ sx q[0];
b[0] = measure q[0];
::
-- POW(2.5) ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

pow(2.5) @ sx q[0];
b[0] = measure q[0];
::
-- CTRL ----- 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];

ctrl @ x q[0], q[1];
b[0] = measure q[0];
b[1] = measure q[1];
::
-- NEGCTRL ----- 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

ctrl @ x q[0], q[1];
b[0] = measure q[0];
b[1] = measure q[1];
::
-- CTRL(2) ----- 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

x q[0];
x q[1];

ctrl(2) @ x q[0], q[1], q[2];
b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
::
-- NEGCTRL(2) ----- 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

ctrl(2) @ x q[0], q[1], q[2];
b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
::
-- GATE Q1 ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

gate my_gate q {
    x q;
}

my_gate q[0];
b[0] = measure q[0];
::
-- GATE Q1 Q2 Q3 ----- 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

gate my_gate q1, q2, q3 {
    x q1;
    cswap q1, q2, q3;
}

my_gate q[0], q[1], q[2];
b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
::
-- GATE(P1, P2) Q1 ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

gate my_gate(p1, p2) q {
    rx(p1) q;
    rz(p2) q;
}

my_gate(pi, 10) q[0];
b[0] = measure q[0];
::
-- GATE(P1, P2) Q1 Q2 Q3 ----- 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

gate my_gate(p1, p2) q1, q2, q3 {
    rx(p1) q1;
    rx(p2) q2;
    ccx q1, q2, q3;
}

my_gate(pi, pi) q[0], q[1], q[2];
b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
::
-- INV_POW2 ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

inv @ pow(2) @ sx q[0];
b[0] = measure q[0];
::
-- CTRL_NEGCTRL ----- 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

x q[0];

ctrl @ negctrl @ x q[0], q[1], q[2];
b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
::
-- CTRL_NEGCTRL_INV_POW2 ----- 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

x q[0];

ctrl @ negctrl @ inv @ pow(2) @ sx q[0], q[1], q[2];
b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
::
-- INV_GATE Q ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

gate my_gate q {
    x q;
}

inv @ my_gate q[0];
b[0] = measure q[0];
::
-- POW2_GATE Q ----- 1
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[1] q;
bit[1] b;

reset q[0];

gate my_gate q {
    sx q;
}

pow(2) @ my_gate q[0];
b[0] = measure q[0];
::
-- CTRL_GATE Q ----- 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

x q[0];

gate my_gate q {
    x q;
}

ctrl @ my_gate q[0], q[1];
b[0] = measure q[0];
b[1] = measure q[1];
::
-- NEGCTRL_GATE Q ----- 2
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] b;

reset q[0];
reset q[1];

gate my_gate q {
    x q;
}

ctrl @ my_gate q[0], q[1];
b[0] = measure q[0];
b[1] = measure q[1];
::
-- CTRL_NEGCTRL_INV_POW2_GATE Q ----- 3
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[3] q;
bit[3] b;

reset q[0];
reset q[1];
reset q[2];

x q[0];

gate my_gate q {
    sx q;
}

ctrl @ negctrl @ inv @ pow(2) @ my_gate q[0], q[1], q[2];
b[0] = measure q[0];
b[1] = measure q[1];
b[2] = measure q[2];
'''

# complex_codes = '''
# -- ADDER ----- 10
# ::
# OPENQASM 3.0;
# include "stdgates.inc";

# gate majority a, b, c {
#     cx c, b;
#     cx c, a;
#     ccx a, b, c;
# }

# gate unmaj a, b, c {
#     ccx a, b, c;
#     cx c, a;
#     cx a, b;
# }

# qubit[1] cin;
# qubit[4] a;
# qubit[4] b;
# qubit[1] cout;
# bit[5] ans;
# int[4] a_in = 1;  // a = 0001
# int[4] b_in = 15; // b = 1111
# // initialize qubits
# reset cin;
# reset a;
# reset b;
# reset cout;

# // set input states
# for int i in [0: 3] {
#     if(bool(a_in[i])) {
#         x a[i];
#     }

#     if(bool(b_in[i])) {
#         x b[i];
#     }
# }
# // add a to b, storing result in b
# majority cin[0], b[0], a[0];
# for int i in [0: 2] {
#     majority a[i], b[i + 1], a[i + 1]; 
# }
# cx a[3], cout[0];
# for int i in [2: -1: 0] {
#     unmaj a[i],b[i+1],a[i+1]; 
# }
# unmaj cin[0], b[0], a[0];
# ans[0:3] = measure b[0:3];
# ans[4] = measure cout[0];
complex_codes = '''
-- INVERSEQFT1 ----- 4
::
OPENQASM 3.0;
include "stdgates.inc";

qubit[4] q;
bit[4] c;

reset q[0];
reset q[1];
reset q[2];
reset q[3];

h q[0];
h q[1];
h q[2];
h q[3];

barrier q[0];
barrier q[1];
barrier q[2];
barrier q[3];

h q[0];
c[0] = measure q[0];

negctrl(3) @ ctrl @ rz(pi / 2) c[3], c[2], c[1], c[0], q[1];

h q[1];
c[1] = measure q[1];

negctrl(3) @ ctrl @ rz(pi / 4) c[3], c[2], c[1], c[0], q[2];
negctrl(2) @ ctrl @ negctrl @ rz(pi / 2) c[3], c[2], c[1], c[0], q[2];
negctrl(2) @ ctrl(2) @ rz(pi / 2 + pi / 4) c[3], c[2], c[1], c[0], q[2];

h q[2];
c[2] = measure q[2];

negctrl(3) @ ctrl @ rz(pi / 8) c[3], c[2], c[1], c[0], q[3];
negctrl(2) @ ctrl @ negctrl @ rz(pi / 4) c[3], c[2], c[1], c[0], q[3];
negctrl(2) @ ctrl(2) @ rz(pi/4+pi/8) c[3], c[2], c[1], c[0], q[3];
negctrl @ ctrl @ negctrl(2) @ rz(pi / 2) c[3], c[2], c[1], c[0], q[3];
negctrl @ ctrl @ negctrl @ ctrl @ rz(pi / 2 + pi / 8) c[3], c[2], c[1], c[0], q[3];
negctrl @ ctrl(2) @ negctrl @ rz(pi / 2+ pi / 4) c[3], c[2], c[1], c[0], q[3];
negctrl @ ctrl(3) @ rz(pi / 2 + pi / 4 + pi / 8) c[3], c[2], c[1], c[0], q[3];

h q[3];
c[3] = measure q[3];
'''