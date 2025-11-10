# Python Basic Operations

# 1. Printing to console
print("Hello, world!")

# 2. Variables and data types
integer_var = 10
float_var = 20.5
string_var = "GitHub Copilot"
boolean_var = True

print(integer_var, float_var, string_var, boolean_var)

# 3. Lists and list operations
list_var = [1, 2, 3, 4, 5]
list_var.append(6)  # Add an item to the end of the list
print(list_var)

# 4. Control structures
# For loop
for i in list_var:
    print(i)

# If-else condition
if integer_var > 5:
    print("The variable is greater than 5.")
else:
    print("The variable is not greater than 5.")

# 5. Functions
def greet(name):
    return f"Hello, {name}!"

print(greet("GitHub Copilot"))

# 6. Error handling
try:
    print(10 / 0)
except ZeroDivisionError:
    print("You can't divide by zero!")