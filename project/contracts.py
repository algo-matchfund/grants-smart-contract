from pyteal import *

"""Grants Application for Individual Project in PyTeal"""

def approval_program():
    owner_address_key = Bytes("owner_address")
    start_time_key = Bytes("start_time")
    end_time_key = Bytes("end_time")
    match_key = Bytes("match")
    total_fund_key = Bytes("total_fund")
    contributors_key = Bytes("contributors")

    #create project
    on_create_start_time = Btoi(Txn.application_args[1])
    on_create_end_time = Btoi(Txn.application_args[2])
    on_create = Seq(
        App.globalPut(owner_address_key, Txn.application_args[0]),
        App.globalPut(start_time_key, on_create_start_time),
        App.globalPut(end_time_key, on_create_end_time),
        App.globalPut(match_key, Int(0)),
        App.globalPut(total_fund_key, Int(0)),
        App.globalPut(contributors_key, Int(0)),
        # Assert(
        #     And(
        #         # Global.latest_timestamp() < on_create_start_time,
        #         on_create_start_time < on_create_end_time
        #     )
        # ),
        Approve(),
    )

    handle_optin = Approve()

    handle_closeout = Reject()

    handle_updateapp = Reject()

    handle_deleteapp = Reject()

    
    amount = Btoi(Txn.application_args[1])
    scratchTotalFund = ScratchVar(TealType.uint64)
    scratchMatch = ScratchVar(TealType.uint64)
    scratchContributors = ScratchVar(TealType.uint64)
    funded_amount_key = Bytes("funded_amount")
    get_funded_amount = App.localGetEx(Int(0), Txn.application_id(), funded_amount_key)
    on_set_donation = Seq(
        Assert(
            And(
                # the round has started
                # App.globalGet(start_time_key) <= Global.latest_timestamp(),
                # the round has not ended
                Global.latest_timestamp() < App.globalGet(end_time_key),
                amount > Int(0),
            ),
        ),
        scratchTotalFund.store(App.globalGet(total_fund_key)),
        scratchMatch.store(App.globalGet(match_key)),
        scratchContributors.store(App.globalGet(contributors_key)),
        get_funded_amount,
        If(scratchContributors.load() == Int(0))
        .Then(
            # first donation to the project
            Seq(
                App.globalPut(total_fund_key, amount),
                # for first donation to project, deliberately equate match to donation amount
                App.globalPut(match_key, amount),
                App.globalPut(contributors_key, Int(1)),
                App.localPut(Int(0), funded_amount_key, amount),
            )
        )
        .Else(
            Seq(
                If(get_funded_amount.hasValue())
                .Then(
                    If(scratchContributors.load() == Int(1))
                    # Fund again by the only funder in the project
                    .Then(
                        Seq(
                            App.globalPut(total_fund_key, amount + get_funded_amount.value()),
                            App.globalPut(match_key, amount + get_funded_amount.value()),
                        ),
                    )
                    # Fund again to project with donation from others
                    .Else(
                        Seq(
                            App.globalPut(total_fund_key, scratchTotalFund.load() + amount),
                            App.globalPut(match_key, (Sqrt(scratchMatch.load() + scratchTotalFund.load()) - Sqrt(get_funded_amount.value())
                            + Sqrt(amount)) ** Int(2) - (scratchTotalFund.load() + amount)),
                        )
                    )
                )
                # First time funding from this user, project has other donations
                .Else(
                    Seq(
                        App.globalPut(total_fund_key, scratchTotalFund.load() + amount),
                        App.globalPut(match_key, (Sqrt(scratchMatch.load() + scratchTotalFund.load())
                        + Sqrt(amount)) ** Int(2) - (scratchTotalFund.load() + amount)),
                        App.globalPut(contributors_key, scratchContributors.load() + Int(1)),
                    )
                ),
                App.localPut(Int(0), funded_amount_key, amount + get_funded_amount.value()),
            )
        ),
        Approve(),
    )

    on_call = Cond(
        [Txn.application_args[0] == Bytes("set_donation"), on_set_donation],
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, on_call]
    )
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=5)

def clear_state_program():
    program = Return(Int(1))
    # Mode.Application specifies that this is a smart contract
    return compileTeal(program, Mode.Application, version=5)


if __name__ == "__main__":
    # compile program to TEAL assembly
    with open("./approval.teal", "w") as f:
        approval_program_teal = approval_program()
        f.write(approval_program_teal)


    # compile program to TEAL assembly
    with open("./clear.teal", "w") as f:
        clear_state_program_teal = clear_state_program()
        f.write(clear_state_program_teal)
