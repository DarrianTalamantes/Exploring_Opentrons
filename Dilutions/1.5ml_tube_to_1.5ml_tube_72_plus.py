from opentrons import protocol_api
import math
import json
import numpy as np
import pandas as pd

# metadata
metadata = {
    'protocolName': '1.5ml to 1.5ml dilution with water trough 1281-end+Redoes',
    'author': 'Roy II <darrianrtalamantes6@gmail.com>',
    'description': 'This protocol is nearly identical to the 1.5 to 1.5 dilution but uses a 15 ml resiviour to grab '
                   'water from ',
    'apiLevel': '2.9'
}
# Input CSV
csv_raw = '''
98.44
94.44
98.3
87.78
80.32
87.74
36.7
61.62
99.28
95.3
56.52
98.8
84.34
99.94
79.26
16.88
55.26
58.32
19.1
69.62
78.74
57.96
70.36
72.52
0.48
19.76
81.42
88.7
63.3
66.74
60.42
63.62
60.08
-3.76
64.02
88.92
82.76
79.6
81.32
62.84
62.62
59.1
88.6
88
77.66
72.56
67.42
-3.72
75.02
69.56
84.44
101.94
66.88
47.22
69.76
-4.32
56.14
64.76
88.68
97.64
83.94
83.46
85.22
64.78
62.22
24.9
'''
csv_data = csv_raw.splitlines()[1:]
concentrations = np.array(csv_data, dtype=float)

# Here you input location of labware
tip_rack_20_loc = 9  # tip rack for p20 single channel
tip_rack_300_loc = 6  # tip rack for p300 single channel
reservoir_15ml_loc = 3  # tube rack 15ml with water in A1
tube_rack1_loc = 10  # first set of samples goes here
tube_rack2_loc = 11  # first set of dilutions will be here
tube_rack3_loc = 7  # second set of samples will be here
tube_rack4_loc = 8  # second set of dilutions goes here
tube_rack5_loc = 4  # third set of samples goes here
tube_rack6_loc = 5  # third set of dilutions will be here
tube_rack7_loc = 1  # forth set of samples goes here
tube_rack8_loc = 2  # forth set of dilutions will be here


# Here I am putting in the custom labware

######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    target_con = 10  # This is the final concentration we are diluting to
    current_tip_20 = "A1"  # Where the P20 single should start on tip box.
    current_tip_300 = "A1"  # Where the p300 single should start on the tip box
    water_location = 6  # Location of water on reservoir_15ml
    water_loaded = False  # if you have already loaded the water for some reason this turns to True
    # Need to add a specification on what tip rack column to start on
    ############################################# Code that allows stuff to work ##########################################

    # # Making this start at 1 instead of zero
    water_location -= 1
    # # Creating an array for the sample plate
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    tube_rack_array = np.zeros((4, 6), dtype='U25')
    for col1 in range(0, 6):
        for row1 in range(0, 4):
            tube_rack_array[row1, col1] = alphabate[row1] + str(col1 + 1)

    # #  labware
    tiprack_20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20_loc)
    tip_rack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', tip_rack_300_loc)
    reservoir_15ml = protocol.load_labware('nest_12_reservoir_15ml', reservoir_15ml_loc)
    tube_rack1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack1_loc)
    tube_rack2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack2_loc)
    tube_rack3 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack3_loc)
    tube_rack4 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack4_loc)
    tube_rack5 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack5_loc)
    tube_rack6 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack6_loc)
    tube_rack7 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack7_loc)
    tube_rack8 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack8_loc)

    # #  pipettes
    left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20])
    right_pipette = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tip_rack_300])

    # #  Set starting tip
    left_pipette.starting_tip = tiprack_20.wells_by_name()[current_tip_20]
    right_pipette.starting_tip = tip_rack_300.wells_by_name()[current_tip_300]

    # #  setting water location
    water_well = reservoir_15ml.wells()[water_location]

    # # formatting data better
    aspirations = set_up_data(concentrations, target_con)

    ################################################## commands ######################################################

    # Loading water
    if not water_loaded:
        right_pipette.pick_up_tip()
        for i in range(0, len(aspirations)):
            water_drop = get_tube_positions(i, tube_rack_array)
            if (i > 71) & (i <= 95):
                right_pipette.transfer(aspirations[2][i], water_well, tube_rack8.wells_by_name()[water_drop],
                                       new_tip='never', air_gap=5)
            if (i > 47) & (i <= 71):
                right_pipette.transfer(aspirations[2][i], water_well, tube_rack6.wells_by_name()[water_drop],
                                       new_tip='never', air_gap=5)
            if (i > 23) & (i <= 47):
                right_pipette.transfer(aspirations[2][i], water_well, tube_rack4.wells_by_name()[water_drop],
                                       new_tip='never', air_gap=5)
            if (i >= 0) & (i <= 23):
                right_pipette.transfer(aspirations[2][i], water_well, tube_rack2.wells_by_name()[water_drop],
                                       new_tip='never', air_gap=5)
        right_pipette.drop_tip()

    # adding sample to water
    for i in range(0, len(aspirations)):
        tube_position = get_tube_positions(i, tube_rack_array)
        if (i > 71) & (i <= 95):
            left_pipette.transfer(aspirations[1][i], tube_rack7.wells_by_name()[tube_position],
                                  tube_rack8.wells_by_name()[tube_position],
                                  air_gap=3, rate=2.0)
        if (i > 47) & (i <= 71):
            left_pipette.transfer(aspirations[1][i], tube_rack5.wells_by_name()[tube_position],
                                  tube_rack6.wells_by_name()[tube_position],
                                  air_gap=3, rate=2.0)
        if (i > 23) & (i <= 47):
            left_pipette.transfer(aspirations[1][i], tube_rack3.wells_by_name()[tube_position],
                                  tube_rack4.wells_by_name()[tube_position],
                                  air_gap=3, rate=2.0)
        if (i >= 0) & (i <= 23):
            left_pipette.transfer(aspirations[1][i], tube_rack1.wells_by_name()[tube_position],
                                  tube_rack2.wells_by_name()[tube_position],
                                  air_gap=3, rate=2.0)


######################################## methods to be used in protocol ############################################

def set_up_data(concentrations, target_con):
    # #  importing data and creating necessary arrays
    sample_num = len(concentrations)
    sample_num_array = np.empty([sample_num], dtype=float)
    water_array = np.empty([sample_num], dtype=float)
    DNA_array = np.empty([sample_num], dtype=float)

    for i in range(0, sample_num):
        sample_num_array[i] = i + 1

    # # Filling in arrays for the machine to know how much water and sample is needed
    for i in range(0, sample_num):
        if (concentrations[i] <= target_con):
            water_array[i] = 0
            DNA_array[i] = 0
        else:
            dna = round(100 * target_con / concentrations[i], 2)
            water = 100 - dna
            DNA_array[i] = dna
            water_array[i] = water

    # # Combining all the data into one big data frame
    big_data = pd.DataFrame(np.column_stack((sample_num_array, DNA_array, water_array)))
    return big_data


def get_tube_positions(position, sample_array):
    row = position % 6
    col = position // 6
    if col >= 8:
        col -= 8
    if col >= 4:
        col -= 4
    grab_this = sample_array[col][row]
    return (grab_this)
