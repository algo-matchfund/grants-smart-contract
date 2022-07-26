# Grants Smart Contract

This repository is for creating smart contracts on the Algorand blockchain to record amount of funds and matches to projects in the Grants application.

## Usage

The file `project/contracts.py` contains the smart contract code written with the PyTeal library. All of the on-chain value transfer logic of the smart contract is stored here.

The file `project/operations.py` provides a set of functions that can be used to create and interact with the project. See that file for documentation.

To generate the compiled programs `approval.teal` and `clear.teal` that are used to deploy and interact with the smart contracts, run `python3 project/contracts.py`.

## Development Setup

This repo requires Python 3.6 or higher.

Set up venv (one time):
 * `python3 -m venv venv`

Active venv:
 * `. venv/bin/activate`

Install dependencies:
* `pip install -r requirements.txt`

Deploy contract and run commands:
* First, start an instance of [sandbox](https://github.com/algorand/sandbox) (requires Docker): `./sandbox up`
* Run `python3 example.py` to deploy a smart contract and interact with it by running a set of predefined calls.
* When finished, the sandbox can be stopped with `./sandbox down`

Caveat:
* Using `Global.latest_timestamp()` in local sandbox environment seems to be buggy. It seems to be inaccurate (it causes incorrect time comparison), resulting in failure in deploying the smart contract due to timeout.
