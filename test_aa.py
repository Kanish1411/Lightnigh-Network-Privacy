def generate_equation(n):
    equation = "x"
    sum_equation = "x"
    
    for i in range(1, n):
        equation = f"({equation})*p{i} + b{i}"
        expanded_equation = equation.replace("x", "(x)")  # Expanding the expression
        sum_equation += f" + {expanded_equation}"
        print(f"Step {i+1}: {expanded_equation}")
    
    print("\nFinal Expanded Equation (Sum of all steps):")
    print(sum_equation)

# Example usage
n = int(input("Enter number of steps: "))
generate_equation(n)
