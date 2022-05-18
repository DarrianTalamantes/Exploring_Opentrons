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
125
83
65
111
45
53
50
73
100
101
120
75
35
62
45
125
83
65
111
45
53
50
73
100
101
120
75
35
62
45
125
83
65
111
45
53
50
73
100
101
120
75
35
62
45
100
'''
csv_data = csv_raw.splitlines()[1:]
concentrations = np.array(csv_data, dtype=float)

# Here you input location of labware
tip_rack_20_loc = 4  # tip rack for p20 single channel
tip_rack_300_loc = 6  # tip rack for p300 single channel
tube_rack_15ml_loc = 3  # tube rack 15ml with water in A1
sample_plate_loc = 1
dilution_plate_loc = 2

# Here I am putting in the custom labware

######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    target_con = 10  # This is the final concentration we are diluting to
    current_tip_20 = "B1"  # Where the P20 single should start on tip box.
    current_tip_300 = "B1"  # Where the p300 single should start on the tip box
    water_location = "A1"  # Location of master mix on tube_rack2
    water_loaded = False  # if you have already loaded the water for some reason this turns to True
    # Need to add a specification on what tip rack column to start on
    ############################################# Code that allows stuff to work ##########################################

    # # Creating an array for the sample plate
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

    well_96_array = np.zeros((8, 12), dtype='U25')
    for col1 in range(0, 12):
        for row1 in range(0, 8):
            well_96_array[row1, col1] = alphabate[row1] + str(col1 + 1)

    # #  labware
    tiprack_20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20_loc)
    tip_rack_300 = protocol.load_labware('opentrons_96_tiprack_300ul', tip_rack_300_loc)
    tube_rack_15ml = protocol.load_labware('opentrons_15_tuberack_falcon_15ml_conical', tube_rack_15ml_loc)
    sample_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', sample_plate_loc)
    dilution_plate = protocol.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul', dilution_plate_loc)


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

    ############################################## commands #########################################################

    # Loading water
    if not water_loaded:
        right_pipette.pick_up_tip()
        for i in range(0, len(aspirations)):
            water_drop = get_plate_positions(i, well_96_array)
            right_pipette.transfer(aspirations[2][i], water_well, dilution_plate.wells_by_name()[water_drop],
                                   new_tip='never', air_gap=5)
        right_pipette.drop_tip()

    # adding sample to water
    for i in range(0, len(aspirations)):
        location = get_plate_positions(i, well_96_array)
        left_pipette.transfer(aspirations[1][i], sample_plate.wells_by_name()[location],
                              dilution_plate.wells_by_name()[location],
                              air_gap=3, mix_after=(5, 18))


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


def get_plate_positions(current_sample, well_96_array):
    if current_sample >= 96:
        plate_num = current_sample // 96
        subtracted = plate_num * 96
        current_sample = current_sample - subtracted
    col = current_sample % 12
    row = current_sample // 12
    grab_this = well_96_array[row][col]
    return (grab_this)
