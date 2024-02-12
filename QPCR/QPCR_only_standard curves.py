from opentrons import protocol_api
import math
import json
import numpy as np

# metadata
metadata = {
    'protocolName': 'QPCR of standard curves',
    'author': 'Roy II <darrianrtalamantes6@gmail.com>',
    'description': 'A protocol that will carry out the testing of multiple standard curves. Uses 3 sets of a 5 part '
                   'dilution',
    'apiLevel': '2.9'
}

# Here you input location of labware
sorenson384_loc = 3  # This is your 384 plate
tip_rack_20_loc = 8
tip_rack_20_2_loc = 9
tube_rack_dilutions = 2  # first 24 samples go here
tube_rack_primers = 6  # master mix of various primers goes here


######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    starting_sample = 1  # Current sample number. Essentially changes position machine starts on the 384 plate
    # I suggest doing no more than 95 samples. That will be enough for exactly one tip box. Max is 96. (include
    # standards here)
    Primers = 3  # This is how many different primers you are testing.
    master_mix_loaded = False  # Is the master mix loaded already? False or True
    current_tip_20 = "A1"  # Where the P20 single should start on tip box. Always starts on location 8.
    master_mix_location = "A1"  # Location of master mix on tube_rack2

    # Need to add a specification on what tip rack column to start on
    ############################################# Code that allows stuff to work ##########################################
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
    tube_rack1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_2ml_safelock_snapcap', tube_rack_dilutions)
    tube_rack2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_primers)
    sorenson_384_wellplate_30ul = protocol.load_labware('sorenson_384_wellplate_30ul_v3.json', sorenson384_loc)

    # pipettes
    left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tiprack_20, tiprack_20_2])
    # Set starting tip
    left_pipette.starting_tip = tiprack_20.wells_by_name()[current_tip_20]

    # commands

    # Loading the master mix
    # Idea here is to load the master mix of each primer set into seperate rows. Each row loading 15 columns
    if not master_mix_loaded:
        for p in range(0, Primers):
            primer_location = get_sample_positions(p, tube_rack_array)
            left_pipette.pick_up_tip()
            for col in range(0, 15):
                mastermix_deposit_loc = get_deposit_location(p, col, plate_array)
                left_pipette.transfer(15, tube_rack2.wells_by_name()[primer_location],
                                      [sorenson_384_wellplate_30ul.wells_by_name()[mastermix_deposit_loc]],
                                      new_tip='Never', blow_out=False)
            left_pipette.drop_tip()

    # Loading the dilutions
        for col in range(0, 15):
            remainder = col % 5
            if col < 5:
                for p in range(0, Primers):
                    dilution_pickup = get_dilution_locations(0, remainder, tube_rack_array)
                    deposit_loc = get_deposit_location(p, col, plate_array)
                    left_pipette.transfer(5, tube_rack1.wells_by_name()[dilution_pickup],
                                          [sorenson_384_wellplate_30ul.wells_by_name()[deposit_loc]]
                                          , blow_out=True, air_gap=2)
            if (col < 10) & (col >= 5):
                for p in range(0, Primers):
                    dilution_pickup = get_dilution_locations(1, remainder, tube_rack_array)
                    deposit_loc = get_deposit_location(p, col, plate_array)
                    left_pipette.transfer(5, tube_rack1.wells_by_name()[dilution_pickup],
                                          [sorenson_384_wellplate_30ul.wells_by_name()[deposit_loc]]
                                          , blow_out=True, air_gap=2)
            if (col < 15) & (col >= 10):
                for p in range(0, Primers):
                    dilution_pickup = get_dilution_locations(2, remainder, tube_rack_array)
                    deposit_loc = get_deposit_location(p, col, plate_array)
                    left_pipette.transfer(5, tube_rack1.wells_by_name()[dilution_pickup],
                                          [sorenson_384_wellplate_30ul.wells_by_name()[deposit_loc]]
                                          , blow_out=True, air_gap=2)


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


def get_dilution_locations(group, dilution, tube_rack_array):
    position = tube_rack_array[group, dilution]
    return position


def get_deposit_location(primer, column, plate_array):
    position = plate_array[primer, column]
    return position
