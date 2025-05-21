def iterative_fibonacci(n):
    if n < 0:  # reject negative numbers
        return "Invalid input. Please enter a non-negative integer."
    elif n == 0:
        return 0
    elif n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n + 1):  # iterate from 1 to n + 1
        a, b = b, a + b

    return b

print(iterative_fibonacci(10))