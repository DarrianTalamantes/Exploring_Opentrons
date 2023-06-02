import math
import json
import numpy as np

def main():
# Creating an array for tip rack
    plate_array = np.zeros((14, 22), dtype='U25')
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    for col in range(0, 22):
        for row in range(0, 14):
            plate_array[row, col] = alphabate[row + 1] + str(col + 2)
    print(plate_array)
# Plating things
    master_mix_loaded = False
    loaded_samples = 60
    starting_sample2 = 1
    if not master_mix_loaded:
        for s in range(0, loaded_samples):
            duplicate_samples = get_plate_positions(starting_sample2, plate_array)
            print(duplicate_samples)
            starting_sample2 += 1

def get_plate_positions(current_sample, plate_array):
    where_to_plate = np.zeros(2, dtype='U25')
    start_num = current_sample * 2 % 22
    start_letter_finder = current_sample * 2 // 22
    for x in range(0, 2):
        where_to_plate[x] = plate_array[start_letter_finder, start_num]
        start_num += 1
    return where_to_plate

main()