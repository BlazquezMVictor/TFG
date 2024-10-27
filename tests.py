beginnig = "qubit"
operation = ""
rest_operation = ""
stop_index = 0

for char in beginnig:
    if not char.isalnum():
        break

    operation += char
    stop_index += 1

try:
    rest_operation = beginnig[stop_index:]
except:
    rest_operation = ""

print(operation)
print(rest_operation)