from opentrons import protocol_api
import math
import json
import numpy as np

# metadata
metadata = {
    'protocolName': '96 sample fluorescent Quantification',
    'author': 'Darrian Talamantes <darrianrtalamantes6@gmail.com>',
    'description': 'Protocol to use black plate for fluorescent quantification. Samples start in 96 well plate'
                   'and end in a black corning black',
    'apiLevel': '2.9'
}

# Here you input location of labware
sample_96_plate_loc = 1
dilution_plate_loc = 2
black_plate_loc = 3
tip_rack_200ul_loc1 = 4
tip_rack_200ul_loc2 = 5
reservoir_15ml_loc = 6



# Here I am putting in the custom labware


######################################## Protocol code starts here #################################################

def run(protocol: protocol_api.ProtocolContext):
    ################################ Variable input below ######################################################
    # Sample information
    cloumns_loaded = 12  # This is how many columns are loaded with samples. Include partially loaded ones.
    Master_mix_Loaded = False  # Is the master mix loaded already? False or True
    current_tip_200 = 1  # Where the P300 multi should start on tip_rack_200ul_1
    te_loc = 1  # what well is the TE buffer in?
    water_loc = 3  # what well is the water in?
    water_loc2 = 4  #second location for water
    dilution = 15  # input your dilution level

    ############################################# Code that allows stuff to work ##########################################
    # # This makes things start at 1 instead of 0
    current_tip_200 -= 1
    te_loc -= 1
    water_loc -= 1
    water_loc2 -= 1
    # # Creating water and DNA amounts for dilutions
    sample_amount = round(200/dilution, 2)
    water_amount = 200 - sample_amount
    # # Labware

    sample_96_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', sample_96_plate_loc)
    black_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', black_plate_loc)
    tip_rack_200ul_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', tip_rack_200ul_loc1)
    tip_rack_200ul_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', tip_rack_200ul_loc2)
    reservoir_15ml = protocol.load_labware('nest_12_reservoir_15ml', reservoir_15ml_loc)
    dilution_plate = protocol.load_labware('opentrons_96_aluminumblock_generic_pcr_strip_200ul', dilution_plate_loc)


    # pipettes
    right_pipette = protocol.load_instrument('p300_multi_gen2', 'right', tip_racks=[tip_rack_200ul_1, tip_rack_200ul_2])
    # Set starting tip
    right_pipette.starting_tip = tip_rack_200ul_1.wells()[current_tip_200]

    # # setting master mix in correct spot
    te_well = reservoir_15ml.wells()[te_loc]
    water_well = reservoir_15ml.wells()[water_loc]

    ########################### commands ##################################
    # # Loads master mix into wells of black plate
    if not Master_mix_Loaded:
        right_pipette.pick_up_tip()
        for i in range(0, cloumns_loaded):
            right_pipette.transfer(95, te_well, black_plate.columns(i),
                                   new_tip='never', air_gap=5)
        right_pipette.drop_tip()

    # # Dilute sample and mix then put into black plate
    water = 0
    right_pipette.pick_up_tip()
    for col in range(0, cloumns_loaded):
        right_pipette.transfer(water_amount, water_well, dilution_plate.columns(col),
                               new_tip='never', air_gap=10)
        water += water_amount * 8
        if water > 10000:
            water_well = reservoir_15ml.wells()[water_loc2]
    right_pipette.drop_tip()

    for col in range(0, cloumns_loaded):
        right_pipette.pick_up_tip()
        right_pipette.transfer(sample_amount, sample_96_plate.columns(col), dilution_plate.columns(col),
                               new_tip='never', mix_before=(2, 50), air_gap=10,  mix_after=(3, 75))
        right_pipette.transfer(5, dilution_plate.columns(col), black_plate.columns(col),
                               new_tip='never', air_gap=10, mix_after=(5, 100))
        right_pipette.drop_tip()

######################################## methods to be used in protocol ############################################
