from opentrons import protocol_api
import math
import json
import numpy as np

# metadata
metadata = {
    'protocolName': '96 sample fluorescent Quantification',
    'author': 'Darrian Talamantes <darrianrtalamantes6@gmail.com>',
    'description': 'Protocol to use black plate for fluorescent quantification. Samples start in 96 well plate'
                   'and end in a black corning black. columns 1 and 2 are filled with satandard',
    'apiLevel': '2.9'
}

# Here you input location of labware
sample_96_plate_loc = 1
dilution_plate_loc = 2
black_plate_loc = 3
tip_rack_200ul_loc1 = 4
tip_rack_200ul_loc2 = 5
reservoir_15ml_loc = 6
standard_rack_loc = 8
tip_rack_20ul_loc = 9


# Here I am putting in the custom labware


######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    sample_columns = [3, 4, 5, 6, 7, 8, 9, 10, 11,
                      12]  # input the 10 columns used for samples. (2 are used for standards)
    Master_mix_Loaded = False  # Is the master mix loaded already? False or True
    current_tip_200 = 1  # column the P300 multi should start on tip_rack_200ul_1
    te_loc = 1  # what well is the TE buffer in?
    water_loc = 3  # what well is the water in?
    water_loc2 = 4  # second location for water
    dilution = 15  # input your dilution level
    current_tip_20 = "B1"  # Where the 20 ul pipette starts on tips

    ############################################# Code that allows stuff to work ##########################################
    # # This makes things start at 1 instead of 0
    current_tip_200 -= 1
    te_loc -= 1
    water_loc -= 1
    water_loc2 -= 1
    sample_columns = [x - 1 for x in sample_columns]
    # # Creating water and DNA amounts for dilutions
    sample_amount = round(200 / dilution, 2)
    water_amount = 200 - sample_amount

    # # Lab ware

    sample_96_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', sample_96_plate_loc)
    black_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', black_plate_loc)
    tip_rack_200ul_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', tip_rack_200ul_loc1)
    tip_rack_200ul_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', tip_rack_200ul_loc2)
    reservoir_15ml = protocol.load_labware('nest_12_reservoir_15ml', reservoir_15ml_loc)
    dilution_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', dilution_plate_loc)
    standard_rack = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', standard_rack_loc)
    tip_rack_20ul = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20ul_loc)

    # pipettes
    right_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=[tip_rack_200ul_1, tip_rack_200ul_2])
    left_pipette = protocol.load_instrument('p20_single_gen2', 'left', tip_racks=[tip_rack_20ul])

    # Set starting tip
    right_pipette.starting_tip = tip_rack_200ul_1.wells()[current_tip_200]
    left_pipette.starting_tip = tip_rack_20ul.wells_by_name()[current_tip_20]

    # # setting master mix in correct spot
    te_well = reservoir_15ml.wells()[te_loc]
    water_well = reservoir_15ml.wells()[water_loc]

    # # Making arrays
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    # Array for the 24 hole tube rack
    tube_rack_array = np.zeros((4, 6), dtype='U25')
    for col1 in range(0, 6):
        for row1 in range(0, 4):
            tube_rack_array[row1, col1] = alphabate[row1] + str(col1 + 1)
    # Making an array for the 96 well plate
    well_96_array_partial = np.zeros((8, 2), dtype='U25')
    for col1 in range(0, 2):
        for row1 in range(0, 8):
            well_96_array_partial[row1, col1] = alphabate[row1] + str(col1 + 1)
    ########################### commands ##################################
    sample_col = len(sample_columns)
    # # Loads master mix into wells of black plate
    if not Master_mix_Loaded:
        right_pipette.pick_up_tip()
        for i in range(0, sample_col + 2):
            right_pipette.transfer(95, te_well, black_plate.columns(i),
                                   new_tip='never', air_gap=10)
        right_pipette.drop_tip()

    # Input standards to black plate
    for s in range(0, 8):
        std_pickup = get_standard_positions(s, tube_rack_array)
        numoff = s * 2
        std_dropoff = standard_dropoff_positions(numoff, well_96_array_partial)
        std_dropoff2 = standard_dropoff_positions(numoff + 1, well_96_array_partial)
        left_pipette.distribute(5, standard_rack.wells_by_name()[std_pickup],
                                [black_plate.wells_by_name()[well_name] for well_name in [std_dropoff, std_dropoff2]],
                                air_gap=5)
    # # Mixing the standards
    for s in range(0, 2):
        std_dropoff = standard_dropoff_positions(s, well_96_array_partial)
        right_pipette.pick_up_tip()
        right_pipette.mix(5, 70, black_plate[std_dropoff])
        right_pipette.drop_tip()

    # # Dilute sample and mix then put into black plate
    water = 0
    right_pipette.pick_up_tip()
    for col in range(2, sample_col + 2):
        right_pipette.transfer(water_amount, water_well, dilution_plate.columns(col),
                               new_tip='never', air_gap=10)
        water += water_amount * 8
        if water > 10000:
            water_well = reservoir_15ml.wells()[water_loc2]
    right_pipette.drop_tip()

    for col in range(2, sample_col + 2):
        right_pipette.pick_up_tip()
        right_pipette.transfer(sample_amount, sample_96_plate.columns(col), dilution_plate.columns(col),
                               new_tip='never', mix_before=(2, 50), air_gap=10, mix_after=(3, 75))
        right_pipette.transfer(5, dilution_plate.columns(col), black_plate.columns(col),
                               new_tip='never', air_gap=10, mix_after=(5, 70))
        right_pipette.drop_tip()


######################################## methods to be used in protocol ############################################


def get_standard_positions(position, sample_array):
    row = position % 6
    col = position // 6
    if col >= 8:
        col -= 8
    if col >= 4:
        col -= 4
    grab_this = sample_array[col][row]
    return grab_this


def standard_dropoff_positions(current_sample, well_96_array_partial):
    col = current_sample % 2
    row = current_sample // 2
    shoot_here = well_96_array_partial[row][col]
    return shoot_here
