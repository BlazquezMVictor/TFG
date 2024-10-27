import qsimov as qj

print(qj.get_available_gates())
qc = qj.QCircuit(2, 2, "Entaglement", ancilla=(0, 0))
qc.add_operation("H", targets=0)
qc.add_operation("X", targets=1, controls=0)

