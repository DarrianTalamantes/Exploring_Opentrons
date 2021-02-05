from opentrons import protocol_api
import math

# metadata
metadata = {
    'protocolName': 'Proto Example',
    'author': 'Roy II <darrianrtalamantes6@gmail.com>',
    'description': 'A protocol to learn the basics of python API for opentrons',
    'apiLevel': '2.9'
}

aliquot_volume = 30

def run(protocol: protocol_api.ProtocolContext):
    # labware
    # This link will show the names of all the opentrons standard labware
    # https://labware.opentrons.com/?category=reservoir
    # Variable name = protocol.load_labware('name of labware', 'slot on machine')
    plate = protocol.load_labware('opentrons_96_aluminumblock_biorad_wellplate_200ul', '5')
    tiprack = protocol.load_labware('opentrons_96_tiprack_300ul', '1')
    dna_rack = protocol.load_labware('opentrons_24_aluminumblock_nest_1.5ml_snapcap', '3')
    reservoirs = protocol.load_labware('usascientific_12_reservoir_22ml', '2')

    # pipettes
    # This link will show all pipette models
    # https://docs.opentrons.com/v2/new_pipette.html#new-pipette
    # protocol.load_instrument(pipette model, left or right, tip_racks=[tip rack variable])
    right_pipette = protocol.load_instrument('p300_multi', 'right', tip_racks=[tiprack])


    # protocol run function. the part after the colon lets your editor know
    # where to look for autocomplete suggestions



    # commands

    # right_pipette.transfer(50, reservoirs.wells(), plate.wells())
    # The above code will transfer 50 ul from reservoirs well 1 to plate well 1, reservoirs well 2 to plate
    # well 2, and so forth untill no more wells are left and it'll put pipettes in trash.

    # right_pipette.transfer(30, reservoirs.wells(11), plate.wells())
    # The above code will transfer 30 ul from reservoirs well 11 to every well in the plate

    # right_pipette.transfer(50, reservoirs.wells(9), plate.wells())
    # This command will transfer 50 ul from res well 9 to plate well 0. Only works with plate well 0 ???????
    # The command below this one is better

    # right_pipette.transfer(50, reservoirs.wells(4), plate.columns_by_name()['4'])
    # The above command is how you should write a transfer from one col in res to another single col in plate.

    # right_pipette.distribute(30, reservoirs.wells(0), plate.wells())
    # The command above will pickup 300 ul from reservoirs well 1 and dispense it to plate wells until
    # it does not have 30 ul left. It will then dispense into the trash and pick up more liquid from
    # reservoirs well 1.

    # right_pipette.transfer(30, reservoirs.wells(11), plate.wells(), mix_after=(3, 30))
    # This command will grab 30 ul from reservoirs dispense it to plate and then mix pipette mix 3 times.
    # Without replacing the tip it then picks up more from reservoirs and continues down the wells of plate.

    # right_pipette.transfer(30, reservoirs.wells(11), plate.wells(),  mix_before=(3, 30))
    # same code as before but with the mix_before. This command mixes before aspirating.
    # Basically it mixes in the reservoir. Can be useful if you need to resuspend everytime.

    # right_pipette.transfer(30, reservoirs.wells(), plate.wells(), trash=False, new_tip='always')
    # This will grab tips from res well 1 transfer 30 ul to plate well 1, put the tips back in tip rack well 1,
    # grab tips from tip rack well 2, do its commands, return the tips and get new ones from tip rack well 3

    # right_pipette.distribute(30, reservoirs.wells(0), plate.wells(), blow_out=True, blowout_location='source well')
    # This will use the distribute command like before but will return excess reagent back to its source well.
    # This is honestly how it should be used most of the time

    # right_pipette.transfer(
    #     50,
    #     [reservoirs.columns_by_name()[col_name] for col_name in ['1', '11', '10']],
    #     [plate.columns_by_name()[col_name] for col_name in ['1', '1', '1']],
    #     new_tip='never')
    # The above command will change tips every time before aspirating. Very useful to stop contamination

    # right_pipette.pick_up_tip()
    # right_pipette.transfer(
    #     50,
    #     [reservoirs.columns_by_name()[col_name] for col_name in ['1', '11', '10']],
    #     [plate.columns_by_name()[col_name] for col_name in ['1', '1', '1']],
    #     new_tip='never')
    # right_pipette.drop_tip()
    # The above code is to force the machine to never change the pipette. Contamination central.

    # right_pipette.transfer(
    #     50,
    #     [reservoirs.columns_by_name()[col_name] for col_name in ['1', '11', '10']],
    #     [plate.columns_by_name()[col_name] for col_name in ['1', '1', '1']],
    #     )
    # The above command does the exact same thing as the previous.

    right_pipette.transfer(
        300,
        [reservoirs.columns_by_name()[col_name] for col_name in ['2']],
        [reservoirs.columns_by_name()[col_name] for col_name in ['3']],
        mix_after=(5, 200), blow_out=True, blowout_location='source well', trash=False
        )
    right_pipette.transfer(
        300,
        [reservoirs.columns_by_name()[col_name] for col_name in ['3']],
        [reservoirs.columns_by_name()[col_name] for col_name in ['2']],
        mix_after=(5, 200), blow_out=True, blowout_location='source well', trash=False
        )
    # The above code is what I call a wash cycle. It will transfer 300 ul from res 2 to res 3. It then
    # mixes 200 ul 5 times. Blows out any extra water in res 2 and puts tips back into box. Then does the
    # same with the next set of tips but from res 3 to res 2

    # right_pipette.distribute(
    #     [20, 0, 60],
    #     reservoirs.wells(7),
    #     [plate.columns_by_name()[col_name] for col_name in ['1', '2', '3']],
    #     blow_out=True, blowout_location='source well', trash=False
    #     )
    # The above code will take liquid from res well 7 and put 20 ul into plate 1 skip plate 2 and
    # add 60 ul to plate 3. NOTICE!!! I use wells instead of columns_by_name to select a single col



# Helpfull commands
# pipette.mix(repetitions, volume, location)
# Pipette mixes a well
# pipette.distribute(Amount to distribute, location of pick up, location to dispense)
# example pipette.distribute(30, reservoir.wells_by_name()['A1'], plate.rows_by_name()['A'])
# this would pick up from A1 in the reservoir and dispense aliquots of 30 into 'A' row of plate
# trash=False add this to the end of any command to return tips to their position in tip box
# new_tip='always' This modifier will make the .transfer command pick up new tips every time
# Pipettes I use
# p300_multi
# p20_single_gen2

# Lab equipment I use
# usascientific_12_reservoir_22ml
# opentrons_96_tiprack_300ul
# opentrons_24_aluminumblock_nest_1.5ml_snapcap
# The biorad well plate is the best default thing they offer
# opentrons_96_aluminumblock_biorad_wellplate_200ul
