import json
from opentrons import protocol_api, types

# This code is to test the custom labware Sorenson 384 well plate for q-pcr

# metadata
metadata = {
    'protocolName': 'Sorenson 384 Test',
    'author': 'Roy II <darrianrtalamantes6@gmail.com>',
    'description': 'A protocol to learn the basics of python API for opentrons',
    'apiLevel': '2.9'
}

# labware slots. Input slots were labware is located
tip_rack_slot = '1'
Axygen_25_ml_slot = '10'
plate_slot = '3'

# labware being used. Here you input the opentrons name of the labware
tip_rack_name = 'opentrons_96_filtertiprack_200ul'
plate_name = 'opentrons_96_aluminumblock_biorad_wellplate_200ul'

LABWARE_DEF_JSON = """{"ordering":[["A1"]],"brand":{"brand":"Axygen","brandId":["RES-V-25-S"]},"metadata":{"displayName":"Axygen 1 Reservoir 25 µL","displayCategory":"reservoir","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.5,"yDimension":85.5,"zDimension":41.5},"wells":{"A1":{"depth":23.1,"totalLiquidVolume":25,"shape":"rectangular","xDimension":18.31,"yDimension":106.7,"x":64.8,"y":60.77,"z":18.4}},"groups":[{"metadata":{"wellBottomShape":"v"},"wells":["A1"]}],"parameters":{"format":"irregular","quirks":["centerMultichannelOnWells","touchTipDisabled"],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"axygen_1_reservoir_25ul"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0}}"""
LABWARE_DEF = json.loads(LABWARE_DEF_JSON)
LABWARE_LABEL = LABWARE_DEF.get('metadata', {}).get(
    'displayName', 'test labware')

# pipette being used
Right_pipette = 'p300_multi'


def run(protocol: protocol_api.ProtocolContext):

    # load the labware into the protocol
    Axygen_25_ml = protocol.load_labware_from_definition(
        LABWARE_DEF,
        Axygen_25_ml_slot,
        LABWARE_LABEL,
    )
    tiprack = protocol.load_labware(tip_rack_name, tip_rack_slot)
    plate = protocol.load_labware(plate_name, plate_slot)

    # pipettes
    right_pipette = protocol.load_instrument(Right_pipette, 'right', tip_racks=[tiprack])

    #commands
    right_pipette.distribute(30, Axygen_25_ml.wells(0), plate.wells(), blow_out=True, blowout_location='source well')

























