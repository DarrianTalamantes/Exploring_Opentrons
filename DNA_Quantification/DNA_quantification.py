from opentrons import protocol_api
import math
import json
import numpy as np

# metadata
metadata = {
    'protocolName': '96 sample fluorescent Quantification',
    'author': 'Darrian Talamantes <darrianrtalamantes6@gmail.com>',
    'description': 'Protocol to use black plate for fluorescent quantification',
    'apiLevel': '2.9'
}

# Here you input location of labware
black_plate_loc = 3
tip_rack_20ul_1_loc = 10
tip_rack_200ul_loc = 7
tube_rack_1_loc = 4
tube_rack_2_loc = 5
tube_rack_3_loc = 1
tube_rack_4_loc = 2
reservoir_15ml_loc = 6


# Here I am putting in the custom labware


######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    loaded_samples = 96  # This is the amount of samples loaded into the machine
    Master_mix_Loaded = False  # Is the master mix loaded already? False or True
    current_tip_200 = 2  # Where the P300 multi should start on tip box  *** This is the thing youll usually change***
    master_mix_loc = 1  # what well is the mastermix in?
    current_tip_20 = "A1"  # Where the 20 ul pipette starts on tips

    # Need to add a specification on what tip rack column to start on
    ############################################# Code that allows stuff to work ##########################################
    # This makes things start at 1 instead of 0
    current_tip_200 -= 1
    master_mix_loc -= 1
    # labware

    black_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', black_plate_loc)
    tip_rack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20ul_1_loc)
    tip_rack_200ul = protocol.load_labware('opentrons_96_filtertiprack_200ul', tip_rack_200ul_loc)
    tube_rack_1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_1_loc)
    tube_rack_2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_2_loc)
    tube_rack_3 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_3_loc)
    tube_rack_4 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_4_loc)
    reservoir_15ml = protocol.load_labware('nest_12_reservoir_15ml', reservoir_15ml_loc)

    # pipettes
    right_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=[tip_rack_200ul])
    left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tip_rack_20ul_1])
    # Set starting tip
    left_pipette.starting_tip = tip_rack_20ul_1.wells_by_name()[current_tip_20]
    right_pipette.starting_tip = tip_rack_200ul.wells()[current_tip_200]

    # Making arrays
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    # Array for the 24 hole tube rack
    tube_rack_array = np.zeros((4, 6), dtype='U25')
    for col1 in range(0, 6):
        for row1 in range(0, 4):
            tube_rack_array[row1, col1] = alphabate[row1] + str(col1 + 1)
    # Making an array for the 96 well plate
    well_96_array = np.zeros((8, 12), dtype='U25')
    for col1 in range(0, 12):
        for row1 in range(0, 8):
            well_96_array[row1, col1] = alphabate[row1] + str(col1 + 1)
    # setting master mix in correct spot
    master_mix_well = reservoir_15ml.wells()[master_mix_loc]

    # commands
    if not Master_mix_Loaded:
        right_pipette.pick_up_tip()
        for i in range(0, 12):
            right_pipette.transfer(95, master_mix_well, black_plate.columns(i),
                                   new_tip='never', air_gap=5)
        right_pipette.drop_tip()

    for s in range(0, loaded_samples):
        sample_pickup = get_sample_positions(s, tube_rack_array)
        sample_dropoff = get_plate_positions(s, well_96_array)
        if (s > 71) & (s <= 95):
            left_pipette.transfer(5, tube_rack_4.wells_by_name()[sample_pickup],
                                  black_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)
        if (s > 47) & (s <= 71):
            left_pipette.transfer(5, tube_rack_3.wells_by_name()[sample_pickup],
                                  black_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)
        if (s > 23) & (s <= 47):
            left_pipette.transfer(5, tube_rack_2.wells_by_name()[sample_pickup],
                                  black_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)
        if (s >= 0) & (s <= 23):
            left_pipette.transfer(5, tube_rack_1.wells_by_name()[sample_pickup],
                                  black_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)


######################################## methods to be used in protocol ############################################


def get_sample_positions(position, sample_array):
    row = position % 6
    col = position // 6
    if col >= 8:
        col -= 8
    if col >= 4:
        col -= 4
    grab_this = sample_array[col][row]
    return (grab_this)


def get_plate_positions(current_sample, well_96_array):
    if current_sample >= 96:
        plate_num = current_sample // 96
        subtracted = plate_num * 96
        current_sample = current_sample - subtracted
    col = current_sample % 12
    row = current_sample // 12
    grab_this = well_96_array[row][col]
    return (grab_this)
