import os
import sys

def calculate_average(numbers):
    total = 0
    for n in numbers:
        total += n
    average = total / len(numbers)  # potential ZeroDivisionError
    return average

result = calculate_average([])
print(result)
