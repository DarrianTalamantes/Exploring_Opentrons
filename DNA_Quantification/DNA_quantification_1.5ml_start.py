from opentrons import protocol_api
import math
import json
import numpy as np

# metadata
metadata = {
    'protocolName': '96 sample fluorescent Quantification',
    'author': 'Darrian Talamantes <darrianrtalamantes6@gmail.com>',
    'description': 'Protocol to use black plate for fluorescent quantification. Does 80 samples plus 16 standards.',
    'apiLevel': '2.9'
}

# Here you input location of labware

reservoir_15ml_loc = 1
dilution_plate_loc = 2
black_plate_loc = 3
tube_rack_3_loc = 4
tube_rack_4_loc = 5
tip_rack_20ul_1_loc = 6
tube_rack_1_loc = 7
tube_rack_2_loc = 8
tip_rack_20ul_2_loc = 9
tip_rack_200ul_1_loc = 10


# Here I am putting in the custom labware


######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    dilution = 20  # input your dilution level
    loaded_standards = 8  # You should never change this, just load your 8 standards in the 1st 8 positions
    loaded_samples = 63  # This is the amount of samples loaded into the machine, max is 80
    Master_mix_Loaded = False  # Is the master mix loaded already? False or True
    current_tip_200 = 2  # Where the P300 multi should start on tip box
    master_mix_loc = 1  # what well is the mastermix in?
    te_loc = 3  # what well is the TE in? load a little bit more than 12 ml of te in these wells
    te_loc2 = 4  # second location for TE
    current_tip_20 = "A1"  # Where the 20 ul pipette starts on tips

    ############################################# Code that allows stuff to work ##########################################
    # This makes things start at 1 instead of 0
    current_tip_200 -= 1
    master_mix_loc -= 1
    te_loc -= 1
    te_loc2 -= 1

    # # Creating TE and DNA amounts for dilutions
    sample_amount = round(200 / dilution, 2)
    te_amount = 200 - sample_amount

    # labware

    black_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', black_plate_loc)
    tip_rack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20ul_1_loc)
    tip_rack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20ul_2_loc)
    tip_rack_200ul = protocol.load_labware('opentrons_96_filtertiprack_200ul', tip_rack_200ul_1_loc)
    tube_rack_1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_1_loc)
    tube_rack_2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_2_loc)
    tube_rack_3 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_3_loc)
    tube_rack_4 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', tube_rack_4_loc)
    reservoir_15ml = protocol.load_labware('nest_12_reservoir_15ml', reservoir_15ml_loc)
    dilution_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', dilution_plate_loc)

    # pipettes
    right_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=[tip_rack_200ul])
    left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tip_rack_20ul_1, tip_rack_20ul_2])
    # Set starting tip
    left_pipette.starting_tip = tip_rack_20ul_1.wells_by_name()[current_tip_20]
    right_pipette.starting_tip = tip_rack_200ul.columns()[current_tip_200][0]

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

    # Making an array for the 96 well plate
    well_96_array_partial = np.zeros((8, 2), dtype='U25')
    for col1 in range(0, 2):
        for row1 in range(0, 8):
            well_96_array_partial[row1, col1] = alphabate[row1] + str(col1 + 1)

    well_96_array_big_partial = np.zeros((8, 10), dtype='U25')
    for col1 in range(0, 10):
        for row1 in range(0, 8):
            well_96_array_big_partial[row1, col1] = alphabate[row1] + str(col1 + 3)

    # # setting master mix in correct spot and TE
    mm_well = reservoir_15ml.wells()[master_mix_loc]
    te_well = reservoir_15ml.wells()[te_loc]
    ###############################################  commands  ######################################################

    # #  This loads the master mix
    if not Master_mix_Loaded:
        right_pipette.pick_up_tip()
        for i in range(0, math.ceil((loaded_standards + loaded_standards + loaded_samples) / 8)):
            right_pipette.transfer(95, mm_well, black_plate.columns(i),
                                   new_tip='never', air_gap=10)
        right_pipette.drop_tip()

    # # This loads the TE buffer into the dilution plate
    te = 0
    sample_col = int(math.ceil(loaded_samples / 8))
    right_pipette.pick_up_tip()
    for col in range(2, sample_col+2):
        right_pipette.transfer(te_amount, te_well, dilution_plate.columns(col),
                               new_tip='never')  # air gap caused inaccuracy
        te += te_amount * 8
        if te > 10000:
            te_well = reservoir_15ml.wells()[te_loc2]
    right_pipette.drop_tip()

    # # Input standards to black plate
    for s in range(0, 8):
        std_pickup = get_sample_positions(s, tube_rack_array)
        numoff = s * 2
        std_dropoff = standard_dropoff_positions(numoff, well_96_array_partial)
        std_dropoff2 = standard_dropoff_positions(numoff + 1, well_96_array_partial)
        left_pipette.distribute(5, tube_rack_1.wells_by_name()[std_pickup],
                                [black_plate.wells_by_name()[well_name] for well_name in [std_dropoff, std_dropoff2]],
                                air_gap=5)

    # # This loads sample into the TE
    for s in range(loaded_standards, loaded_samples + loaded_standards):
        sample_pickup = get_sample_positions(s, tube_rack_array)
        sample_dropoff = sample_dropoff_positions(s-loaded_standards, well_96_array_big_partial)
        if (s > 71) & (s <= 95):
            left_pipette.transfer(5, tube_rack_4.wells_by_name()[sample_pickup],
                                  dilution_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)
        if (s > 47) & (s <= 71):
            left_pipette.transfer(5, tube_rack_3.wells_by_name()[sample_pickup],
                                  dilution_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)
        if (s > 23) & (s <= 47):
            left_pipette.transfer(5, tube_rack_2.wells_by_name()[sample_pickup],
                                  dilution_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)
        if (s >= 0) & (s <= 23):
            left_pipette.transfer(5, tube_rack_1.wells_by_name()[sample_pickup],
                                  dilution_plate.wells_by_name()[sample_dropoff],
                                  air_gap=5)
    # # Pauses the protocol
    protocol.pause('Please take plate, cover it and vortex. then place plate back where it was.')

    # # This will take diluted samples and place into the black plate
    for s in range(loaded_standards, loaded_samples + loaded_standards):
        sample_position = sample_dropoff_positions(s-loaded_standards, well_96_array_big_partial)
        if (s > 71) & (s <= 95):
            left_pipette.transfer(5, dilution_plate.wells_by_name()[sample_position],
                                  black_plate.wells_by_name()[sample_position],
                                  air_gap=5)
        if (s > 47) & (s <= 71):
            left_pipette.transfer(5, dilution_plate.wells_by_name()[sample_position],
                                  black_plate.wells_by_name()[sample_position],
                                  air_gap=5)
        if (s > 23) & (s <= 47):
            left_pipette.transfer(5, dilution_plate.wells_by_name()[sample_position],
                                  black_plate.wells_by_name()[sample_position],
                                  air_gap=5)
        if (s >= 0) & (s <= 23):
            left_pipette.transfer(5, dilution_plate.wells_by_name()[sample_position],
                                  black_plate.wells_by_name()[sample_position],
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
    col = current_sample // 8
    row = current_sample % 8
    grab_this = well_96_array[row][col]
    return (grab_this)


def standard_dropoff_positions(current_sample, well_96_array_partial):
    col = current_sample % 2
    row = current_sample // 2
    shoot_here = well_96_array_partial[row][col]
    return shoot_here


def sample_dropoff_positions(current_sample, well_96_array_big_partial):
    col = current_sample // 8
    row = current_sample % 8
    shoot_here = well_96_array_big_partial[row][col]
    return shoot_here
