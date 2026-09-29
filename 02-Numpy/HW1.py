import numpy as np

a = np.array([1, 3, 5, 15, 30, 25])

def homework(a):
    mask = ((a % 5) == 0) & (a %2 != 0)
    return a[mask]

print(homework(a))