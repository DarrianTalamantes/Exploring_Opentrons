from opentrons import protocol_api

# metadata
metadata = {
    'protocolName': 'My Protocol',
    'author': 'Name <email@address.com>',
    'description': 'Simple protocol to get started using OT2',
    'apiLevel': '2.9'
}

# protocol run function. the part after the colon lets your editor know
# where to look for autocomplete suggestions
def run(protocol: protocol_api.ProtocolContext):

    # labware
    plate = protocol.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul', '2')
    tiprack = protocol.load_labware('opentrons_96_filtertiprack_20ul', '1')

    # pipettes
    left_pipette = protocol.load_instrument(
         'p20_single_gen2', 'left', tip_racks=[tiprack])

    # commands
    left_pipette.pick_up_tip()
    left_pipette.aspirate(10, plate['A1'])
    left_pipette.dispense(10, plate['B2'])
    left_pipette.drop_tip()



