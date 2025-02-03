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
'''
