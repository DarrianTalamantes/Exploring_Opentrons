import math
import json
import numpy as np

def main():
# Creating an array for tip rack
    tip_array = np.zeros((8, 12), dtype='U25')
    for col in range(0, 12):
        for row in range(0, 8):
            tip_array[row, col] = alphabate[row] + str(col + 1)
    print(tip_array)

def get_tiprack_positions(current_tip, tip_array):
    print('help')


main()