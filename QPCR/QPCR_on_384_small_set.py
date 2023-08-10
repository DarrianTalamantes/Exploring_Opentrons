from opentrons import protocol_api
import math
import json
import numpy as np

# metadata
metadata = {
    'protocolName': '1-94 sample QPCR, set up for 92',
    'author': 'Roy II <darrianrtalamantes6@gmail.com>',
    'description': 'A protocol that will carry out qpcr in tiplicate skipping the first and last row, first column '
                   'and last 2 columns. It uses 1.5 ml tubes to the 384 plate',
    'apiLevel': '2.9'
}

# Here you input location of labware
sorenson384_loc = 3  # This is your 384 plate
tip_rack_20_loc = 8
tip_rack_20_2_loc = 9
tube_rack1_loc = 4  # first 24 samples go here
tube_rack2_loc = 6  # master mix and
tube_rack3_loc = 5  # 2nd 24 samples go here
tube_rack4_loc = 1  # 3rd set of 24 samples go here
tube_rack5_loc = 2  # 4th set of 24 samples go here

######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    starting_sample = 1  # Current sample number. Essentially changes position machine starts on the 384 plate
    # I suggest doing no more than 95 samples. That will be enough for exactly one tip box. Max is 96. (include
    # standards here)
    loaded_samples = 92 # This is how many samples you will be running. Always starts at sample rack1 A1.
    master_mix_loaded = False  # Is the master mix loaded already? False or True
    current_tip_20 = "A1"  # Where the P20 single should start on tip box. Always starts on location 8.
    master_mix_location = "A1"  # Location of master mix on tube_rack2

    # Need to add a specification on what tip rack column to start on
    ############################################# Code that allows stuff to work ##########################################
    starting_sample -= 1  # This makes things start at 1 instead of 0
    # Creating an array for 384  (We skip the A row and the first column along with the last two columns)
    plate_array = np.zeros((14, 21), dtype='U25')
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    for col in range(0, 21):
        for row in range(0, 14):
            plate_array[row, col] = alphabate[row + 1] + str(col + 2)
    print(plate_array)
    # Creating an array for the sample plate
    tube_rack_array = np.zeros((4, 6), dtype='U25')
    for col1 in range(0, 6):
        for row1 in range(0, 4):
            tube_rack_array[row1, col1] = alphabate[row1] + str(col1 + 1)

    # labware
    tiprack_20 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20_loc)
    tiprack_20_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20_2_loc)
    tube_rack1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack1_loc)
    # tube_rack2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack2_loc)
    tube_rack2 = protocol.load_labware('opentrons_15_tuberack_nest_15ml_conical', tube_rack2_loc) # For lots of master mix
    tube_rack3 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack3_loc)
    tube_rack4 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack4_loc)
    tube_rack5 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack5_loc)
    sorenson_384_wellplate_30ul = protocol.load_labware('sorenson_384_wellplate_30ul_v3.json', sorenson384_loc)


    # pipettes
    left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20, tiprack_20_2])
    # Set starting tip
    left_pipette.starting_tip = tiprack_20.wells_by_name()[current_tip_20]

    # commands

    # Loading the master mix
    starting_sample2 = starting_sample
    left_pipette.pick_up_tip()
    if not master_mix_loaded:
        for s in range(0, loaded_samples):
            triplicate_samples = get_plate_positions(starting_sample2, plate_array)
            left_pipette.transfer(15, tube_rack2.wells_by_name()[master_mix_location],
                                  [sorenson_384_wellplate_30ul.wells_by_name()[well_name] for well_name in
                                   triplicate_samples],
                                   new_tip='never', blow_out=False)
            starting_sample2 += 1
    left_pipette.drop_tip()

    # Loading the samples
    tube = 1
    for s in range(0, loaded_samples):
        triplicate_samples = get_plate_positions(starting_sample, plate_array)
        sample_pickup = get_sample_positions(s, tube_rack_array)
        if (tube > 72) & (tube <= 96):
            left_pipette.distribute(5, tube_rack5.wells_by_name()[sample_pickup],
                                    [sorenson_384_wellplate_30ul.wells_by_name()[well_name] for well_name in
                                     triplicate_samples], blow_out=True, air_gap=2)
        if (tube > 48) & (tube <= 72):
            left_pipette.distribute(5, tube_rack4.wells_by_name()[sample_pickup],
                                    [sorenson_384_wellplate_30ul.wells_by_name()[well_name] for well_name in
                                     triplicate_samples], blow_out=True, air_gap=2)
        if (tube > 24) & (tube <= 48):
            left_pipette.distribute(5, tube_rack3.wells_by_name()[sample_pickup],
                                    [sorenson_384_wellplate_30ul.wells_by_name()[well_name] for well_name in
                                     triplicate_samples], blow_out=True, air_gap=2)
        if (tube >= 1) & (tube <= 24):
            left_pipette.distribute(5, tube_rack1.wells_by_name()[sample_pickup],
                                [sorenson_384_wellplate_30ul.wells_by_name()[well_name] for well_name in
                                 triplicate_samples], blow_out=True, air_gap=2)
        starting_sample += 1
        tube += 1


######################################## methods to be used in protocol ############################################

def get_plate_positions(current_sample, plate_array):
    where_to_plate = np.zeros(3, dtype='U25')
    start_num = current_sample * 3 % 21
    start_letter_finder = current_sample * 3 // 21
    for x in range(0, 3):
        where_to_plate[x] = plate_array[start_letter_finder, start_num]
        start_num += 1
    return where_to_plate


def get_sample_positions(position, sample_array):
    row = position % 6
    col = position // 6
    if col >= 8:
        col -= 8
    if col >= 4:
        col -= 4
    grab_this = sample_array[col][row]
    return (grab_this)
