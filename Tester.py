import math
import json
import numpy as np


def main():
    # vairbales
    current_sample = 1
    loaded_samples = 100
    current_sample -= 1
    # Creating an array for 384 plate
    plate_array = np.zeros((16, 24), dtype='U25')
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    for col in range(0, 24):
        for row in range(0, 16):
            plate_array[row, col] = alphabate[row] + str(col + 1)

    # Creating an array for the sample plate
    tube_rack_array = np.zeros((4, 6), dtype='U25')
    for col1 in range(0, 6):
        for row1 in range(0, 4):
            tube_rack_array[row1, col1] = alphabate[row1] + str(col1 + 1)

    # creating array for 96 well plate
    well_96_array = np.zeros((8, 12), dtype='U25')
    for col1 in range(0, 12):
        for row1 in range(0, 8):
            well_96_array[row1, col1] = alphabate[row1] + str(col1 + 1)

    # Testing sample array
    # for s in range(0, loaded_samples):
    #     sample_position = get_sample_positions(s, tube_rack_array)
    #     print(sample_position)

    for s in range(0, loaded_samples):
        plate_positions = get_plate_positions(s, well_96_array)
        print(plate_positions)


def get_plate_positions(current_sample, well_96_array):
    if current_sample >= 96:
        plate_num = current_sample // 96
        subtracted = plate_num * 96
        current_sample = current_sample - subtracted
    col = current_sample % 12
    row = current_sample // 12
    grab_this = well_96_array[row][col]
    return (grab_this)


def get_sample_positions(position, sample_array):
    row = position % 6
    col = position // 6
    if col >= 8:
        col -= 8
    if col >= 4:
        col -= 4
    grab_this = sample_array[col][row]
    return (grab_this)


main()
