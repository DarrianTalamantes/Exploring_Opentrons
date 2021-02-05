from opentrons import protocol_api
import math

# metadata
metadata = {
    'protocolName': 'Rainbow Maker',
    'author': 'Roy II <darrianrtalamantes6@gmail.com>',
    'description': 'A protocol to make a rainbow on a 96 well plate',
    'apiLevel': '2.9'
}

# Variable input below

# Here you input the well location of your colors
red = 11
blue = 9
green = 7

# Here you input location of labware
well_plate_loc = 5
tip_rack_loc = 1
res_loc = 2


def run(protocol: protocol_api.ProtocolContext):

    # labware
    plate = protocol.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul', well_plate_loc)
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', tip_rack_loc)
    reservoirs = protocol.load_labware('usascientific_12_reservoir_22ml', res_loc)

    # pipettes
    right_pipette = protocol.load_instrument('p300_multi', 'right', tip_racks=[tiprack])

    # commands
    right_pipette.distribute(
            [100, 70, 30, 50],
            reservoirs.wells(red),
            [plate.columns_by_name()[col_name] for col_name in ['1', '2', '3', '7']],
            blow_out=True, blowout_location='source well'
    )
    right_pipette.distribute(
        [100, 70, 50, 30],
        reservoirs.wells(green),
        [plate.columns_by_name()[col_name] for col_name in ['4', '3', '5', '2']],
        blow_out=True, blowout_location='source well'
    )
    right_pipette.distribute(
        [100, 50, 50, ],
        reservoirs.wells(blue),
        [plate.columns_by_name()[col_name] for col_name in ['6', '5', '7']],
        blow_out=True, blowout_location='source well'
    )






