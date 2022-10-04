from opentrons import protocol_api
import math
import json
import numpy as np
import pandas as pd

# metadata
metadata = {
    'protocolName': '1.5ml to 1.5ml dilution',
    'author': 'Roy II <darrianrtalamantes6@gmail.com>',
    'description': 'This protocol will take an excel file with a single column of concentrations '
                   'and use that to dilute your samples down to X. Goes from 1.5ml tube to a new 1.5ml tube. Final '
                   'volume will be 100 ul',
    'apiLevel': '2.9'
}
# Input CSV
csv_raw = '''
89.12
84.04
105.4
75.02
96.84
96.72
101.16
109.5
90.76
82.38
113.48
77.36
101.6
77.72
83.5
65.44
92.26
66.6
59.8
55.94
86.9
88.56
89.26
70.14
48.92
78.92
65.5
99.38
73.54
102.3
79.86
41.58
99.16
27.68
111
97.22
85.38
84.72
86.56
37.22
108.42
31.34
56.46
111.42
89.12
42.04
31.64
52.76
56.74
41.92
54.08
38.16
'''
csv_data = csv_raw.splitlines()[1:]
concentrations = np.array(csv_data, dtype=float)

# Here you input location of labware
tip_rack_20_loc = 9  # tip rack for p20 single channel
tip_rack_300_loc = 6  # tip rack for p300 single channel
tube_rack_15ml_loc = 3  # tube rack 15ml with water in A1
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
    water_location = "A1"  # Location of water on tube_rack_15ml
    water_location_2 = "A2"  # Location of water 2 on tube_rack_15ml
    water_loaded = False  # if you have already loaded the water for some reason this turns to True
    # Need to add a specification on what tip rack column to start on
    ############################################# Code that allows stuff to work ##########################################

    # # Creating an array for the sample plate
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    tube_rack_array = np.zeros((4, 6), dtype='U25')
    for col1 in range(0, 6):
        for row1 in range(0, 4):
            tube_rack_array[row1, col1] = alphabate[row1] + str(col1 + 1)

    # #  labware
    tiprack_20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20_loc)
    tip_rack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', tip_rack_300_loc)
    tube_rack_15ml = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', tube_rack_15ml_loc)
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
    water_well = tube_rack_15ml.wells_by_name()[water_location]

    # # formatting data better
    aspirations = set_up_data(concentrations, target_con)

    ################################################## commands ######################################################

    # Loading water
    if not water_loaded:
        right_pipette.pick_up_tip()
        for i in range(0, len(aspirations)):
            if i == 49:
                water_well = tube_rack_15ml.wells_by_name()[water_location_2]
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
    pipette_array_water = np.empty([sample_num], dtype=float)
    pipette_array_dna = np.empty([sample_num], dtype=float)

    for i in range(0, sample_num):
        sample_num_array[i] = i + 1

    # # Filling in arrays for the machine to know how much water and sample is needed
    for i in range(0, sample_num):
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
