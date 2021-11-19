import math
import json
import numpy as np

plate_array = np.zeros((4, 6), dtype='U25')
alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
for col in range(0, 6):
    for row in range(0, 4):
        plate_array[row, col] = alphabate[row] + str(col + 1)
print(plate_array)