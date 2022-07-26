from time import time

from algosdk.future import transaction
from algosdk.v2client import algod
from pyteal import *

from project.contracts import approval_program, clear_state_program
from project.operations import compile_program, create_app, read_global_state, opt_in_app,call_app
from project.resources import getTemporaryAccount


# user declared account mnemonics
creator_mnemonic = "finger rigid hat room course salmon say detect avocado assault awake sea public curious exit valve donkey tired escape dash drink diagram section absent cruise"
# user declared algod connection parameters. Node must have EnableDeveloperAPI set to true in its config
algod_address = "http://localhost:4001"
algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

def main() :
    # initialize an algodClient
    algod_client = algod.AlgodClient(algod_token, algod_address)

    # define private keys
    # creator_private_key = get_private_key_from_mnemonic(creator_mnemonic)
    creator = getTemporaryAccount(algod_client)
    funder = getTemporaryAccount(algod_client)
    funder_2 = getTemporaryAccount(algod_client)
    creator_private_key = creator.getPrivateKey()
    print(creator_private_key)
    print(creator.getAddress())
    funder_private_key = funder.getPrivateKey()
    funder_2_private_key = funder_2.getPrivateKey()

    # declare application state storage (immutable)
    local_ints = 1
    local_bytes = 0
    global_ints = 6
    global_bytes = 1
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)

    approval_program_teal = approval_program()
    clear_state_program_teal = clear_state_program()

    # compile program to binary
    approval_program_compiled = compile_program(algod_client, approval_program_teal)

    # compile program to binary
    clear_state_program_compiled = compile_program(algod_client, clear_state_program_teal)

    print("--------------------------------------------")
    project_id = 1
    print(f"Deploying Grants application for Project {project_id}......")

    # create new application
    startTime = int(time())  # start time is now
    endTime = startTime + 60 * 60 * 24 * 30  # end time is 30 days after start
    app_args = [
        creator.getAddress(),
        startTime.to_bytes(8, "big"),
        endTime.to_bytes(8, "big"),
    ]
    app_id = create_app(algod_client, creator_private_key, approval_program_compiled, clear_state_program_compiled, global_schema, local_schema, app_args)
    # app_id = 868
    # read global state of application
    print("Global state:", read_global_state(algod_client, app_id))

    print("--------------------------------------------")
    print("Funder opts in to Grants application......")
    opt_in_app(algod_client, funder_private_key, app_id)

    print("--------------------------------------------")
    print("Funder calling 'set_donation' in Grants application......")
    fund_amount = 1000000
    app_args = ["set_donation", fund_amount]
    call_app(algod_client, funder_private_key, app_id, app_args)
    # read global state of application
    print("Global state:", read_global_state(algod_client, app_id))

    print("--------------------------------------------")
    print("Funder calling 'set_donation' again in Grants application......")
    fund_amount = 1000000
    app_args = ["set_donation", fund_amount]
    call_app(algod_client, funder_private_key, app_id, app_args)
    # read global state of application
    print("Global state:", read_global_state(algod_client, app_id))

    print("--------------------------------------------")
    print("Funder 2 opts in to Grants application......")
    opt_in_app(algod_client, funder_2_private_key, app_id)

    print("--------------------------------------------")
    print("Funder 2 calling 'set_donation' in Grants application......")
    fund_amount = 2000000
    app_args = ["set_donation", fund_amount]
    call_app(algod_client, funder_2_private_key, app_id, app_args)
    # read global state of application
    print("Global state:", read_global_state(algod_client, app_id))

    print("--------------------------------------------")
    print("Funder 2 calling 'set_donation' again in Grants application......")
    fund_amount = 3000000
    app_args = ["set_donation", fund_amount]
    call_app(algod_client, funder_2_private_key, app_id, app_args)
    # read global state of application
    print("Global state:", read_global_state(algod_client, app_id))


main()
