import math
import json
import numpy as np


def main():
    # vairbales
    current_sample = 1
    loaded_samples = 100
    current_sample -= 1
    # Creating an array for 384 plate
    plate_array = np.zeros((14, 21), dtype='U25')
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    for col in range(0, 21):
        for row in range(0, 14):
            plate_array[row, col] = alphabate[row + 1] + str(col + 2)

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

    ##### Testing Portion
    Primers = 3
    for p in range(0, Primers):
        primer_location = get_sample_positions(p, tube_rack_array)
        for col in range(0, 15):
            mastermix_deposit_loc = get_deposit_location(p, col, plate_array)
            print(primer_location, mastermix_deposit_loc)

    print("######################")
    for col in range(0,15):
        remainder = col % 5
        if col < 5:
            for p in range(0, Primers):
                dilution_pickup = get_dilution_locations(0, remainder, tube_rack_array)
                deposit_loc = get_deposit_location(p, col, plate_array)
                print(col, dilution_pickup, deposit_loc)

        if (col < 10) & (col >= 5):
            for p in range(0, Primers):
                dilution_pickup = get_dilution_locations(1, remainder, tube_rack_array)
                deposit_loc = get_deposit_location(p, col, plate_array)
                print(col, dilution_pickup, deposit_loc)

        if (col < 15) & (col >= 10):
            for p in range(0, Primers):
                dilution_pickup = get_dilution_locations(2, remainder, tube_rack_array)
                deposit_loc = get_deposit_location(p, col, plate_array)
                print(col, dilution_pickup, deposit_loc)


# Functions for the code below here

def get_dilution_locations(group, dilution, tube_rack_array):
    position = tube_rack_array[group, dilution]
    return position


def get_deposit_location(primer, column, plate_array):
    position = plate_array[primer, column]
    return position


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
