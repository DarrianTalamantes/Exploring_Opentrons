import math
import json
import numpy as np
a = 23 // 6
print(a)
plate_array = np.zeros((14, 21), dtype='U25')
alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
for col in range(0, 21):
    for row in range(0, 14):
        plate_array[row, col] = alphabate[row + 1] + str(col + 2)
print(plate_array)

tube_rack_array = np.zeros((4, 6), dtype='U25')
for col1 in range(0, 6):
    for row1 in range(0, 4):
        tube_rack_array[row1, col1] = alphabate[row1] + str(col1 + 1)
print(tube_rack_array)