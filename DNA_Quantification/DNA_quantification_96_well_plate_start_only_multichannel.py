from opentrons import protocol_api
import math
import json
import numpy as np

# metadata
metadata = {
    'protocolName': '96 sample fluorescent Quantification',
    'author': 'Darrian Talamantes <darrianrtalamantes6@gmail.com>',
    'description': 'Protocol to use black plate for fluorescent quantification. Samples start in 96 well plate'
                   'and end in a black corning black. columns 1 and 2 are filled with satandard that you load yourself',
    'apiLevel': '2.9'
}

# Here you input location of labware
sample_96_plate_loc = 1
dilution_plate_loc = 2
black_plate_loc = 3
tip_rack_200ul_loc1 = 4
reservoir_15ml_loc = 6
tip_rack_20ul_loc_1 = 8
tip_rack_20ul_loc_2 = 9


# Here I am putting in the custom labware


######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    sample_columns = [1, 2]  # input the 10 columns used for samples. (2 are used for standards)
    Master_mix_Loaded = False  # Is the master mix loaded already? False or True
    current_tip_200 = 2  # column the P300 multi should start on tip_rack_200ul_1
    mater_mix_loc = 1  # what well is the TE buffer in?
    te_loc = 3  # what well is the TE in? load a little bit more than 12 ml of te in these wells
    te_loc2 = 4  # second location for TE
    dilution = 20  # input your dilution level
    current_tip_20 = 1  # Where the 20 ul pipette starts on tips

    ############################################# Code that allows stuff to work ##########################################
    # # This makes things start at 1 instead of 0
    current_tip_200 -= 1
    current_tip_20 -= 1
    mater_mix_loc -= 1
    te_loc -= 1
    te_loc2 -= 1
    sample_columns = [x - 1 for x in sample_columns]

    # # Creating TE and DNA amounts for dilutions
    sample_amount = round(200 / dilution, 2)
    te_amount = 200 - sample_amount

    # # Lab ware

    sample_96_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', sample_96_plate_loc)
    black_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', black_plate_loc)
    tip_rack_200ul_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', tip_rack_200ul_loc1)
    reservoir_15ml = protocol.load_labware('nest_12_reservoir_15ml', reservoir_15ml_loc)
    dilution_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', dilution_plate_loc)
    tip_rack_20ul_1 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20ul_loc_1)
    tip_rack_20ul_2 = protocol.load_labware('opentrons_96_filtertiprack_20ul', tip_rack_20ul_loc_2)

    # pipettes
    right_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=[tip_rack_200ul_1])
    left_pipette = protocol.load_instrument('p20_multi_gen2', 'left', tip_racks=[tip_rack_20ul_1, tip_rack_20ul_2])

    # Set starting tip
    right_pipette.starting_tip = tip_rack_200ul_1.columns()[current_tip_200][0]
    left_pipette.starting_tip = tip_rack_20ul_1.columns()[current_tip_20][0]

    # # setting master mix in correct spot
    mm_well = reservoir_15ml.wells()[mater_mix_loc]
    te_well = reservoir_15ml.wells()[te_loc]

    # # Making arrays
    alphabate = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']

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
            right_pipette.transfer(95, mm_well, black_plate.columns(i),
                                   new_tip='never', air_gap=10)
        right_pipette.drop_tip()

    #  # Pausing protocol to load standards
    protocol.pause('Please load standards, starting from highest in A1 and A2 to lowest in H1 and H2.')

    # # Transfering TE
    te = 0
    right_pipette.pick_up_tip()
    for col in range(0, sample_col):
        sample_wells = sample_columns[col]
        right_pipette.transfer(te_amount, te_well, dilution_plate.columns(sample_wells),
                               new_tip='never')  # air gap caused inaccuracy 
        te += te_amount * 8
        if te > 10000:
            te_well = reservoir_15ml.wells()[te_loc2]
    right_pipette.drop_tip()

    # # Adding sample to TE
    for col in range(0, sample_col):
        left_pipette.pick_up_tip()
        sample_wells = sample_columns[col]
        left_pipette.transfer(sample_amount, sample_96_plate.columns(sample_wells),
                              dilution_plate.columns(sample_wells),
                               new_tip='never', air_gap=2)
        left_pipette.drop_tip()
    protocol.pause('Please take plate, cover it and vortex. then place plate back where it was.')

    # # Putting diluted sample into black plate
    for col in range(0, sample_col):
        left_pipette.pick_up_tip()
        dilution_wells = sample_columns[col]
        left_pipette.transfer(5, dilution_plate.columns(dilution_wells), black_plate.columns(col+2),
                               new_tip='never', air_gap=2)
        left_pipette.drop_tip()


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
