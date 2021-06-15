import math
import json
import numpy as np


def main():
    # vairbales
    current_sample = 1
    loaded_samples = 4
    current_sample -= 1
    # Creating an array for 384 plate
    plate_array = np.zeros((16, 24), dtype='U25')
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    for col in range(0, 24):
        for row in range(0, 16):
            plate_array[row, col] = alphabet[row] + str(col + 1)
    # Creating an array for the sample plate
    sample_array = np.zeros((4, 4), dtype='U25')
    col2 = 0
    for col in range(0, 4):
        col2 += 1
        if col2 == 3:
            col2 += 2
        for row in range(0, 4):
            sample_array[row, col] = alphabet[row] + str(col2)


    for s in range(0, loaded_samples):
        a = get_plate_positions(current_sample, alphabet)
        sample_position = get_sample_positions(s, sample_array)
        print(a)
        print(sample_position)
        current_sample += 1

def get_plate_positions(current_sample, alphabate):
    where_to_plate = np.zeros(3, dtype='U25')
    start_num = current_sample * 3 % 24
    start_letter_finder = current_sample * 3 // 24
    start_letter = alphabate[start_letter_finder]
    for x in range(0, 3):
        where_to_plate[x] = start_letter + str(start_num + 1)
        start_num += 1
    return where_to_plate


def get_sample_positions(positioin, sample_array):
    row = positioin % 4
    col = positioin // 4
    grab_this = sample_array[col][row]
    return(grab_this)


main()
