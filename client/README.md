## 현재 zeth에서 지원되는 명령어
- deploy : smart contract를 blockchain에 넣는 명령어. 그리고, zeth에 해당하는 공용 parameter값도 생성해서 zeth_instance file로 저장한다.
- gen-address : zeth secret key와 public address를 생성한다. 
- mix : user EOA와 mix에 있는 note들 사이에 transaction을 만든다. 즉 transfer함수
- sync : blockchain에 있는 내용을 download받아서 local wallet에 저장한다.
- ls-notes, ls-commits : local wallet에 저장된 내용을 display한다.

## zklay에서 지원되어야 하는 명령어 (client/zeth/cli에 명령어 추가 및 제거, client/test_commands 및 tests 수정 필요)
- deploy : zeth와 동일. 추가적으로 zklay에 필요한 공용 parameter 생성
- audit-key-gen : auditor secret key와 public key를 생성한다. auditor public key는 공용 parameter와 함께 사용된다. 
- key-gen : gen-address에 동일. user의 public key들을 생성한다. 이때 private key file을 제공해 주어야 한다.
- deposit : EOA등 user account에서 zklay 내부 ena (encrypted account)로 klay나 token을 transfer한다.
- withdraw : ena에서 외부 user account로 klay나 token을 transfer한다.
- anon-transfer : anonymous transfer. It tranfers between ena and mixer
- sync, ls-notes, ls-commits : zeth와 동일

## Smart contract 부분 (zeth_contracts/contracts 디렉토리에서)
- Zklay.sol에 ena 내용을 mapping으로 추가
- function mix를 anonTransfer로 하고, snark verify도 수정
- deposit, withdraw 함수를 MixerBase.sol에 추가
- public value에 관련된 함수 수정 제거

## 대체 가능 익명 토큰 표준 (KIP-27)
- 대체 가능한 익명 토큰은 균등성, 가분성, 익명성을 가진 토큰입니다. 각 토큰 단위는 동일한 가치를 가지며 모든 가용 토큰은 서로 호환됩니다. 각 토큰은 값은 암호화되어 저장되며 전달됩니다. 익명성을 제공하는 기본적인 암호 화폐에 필수적인 기능을 담고 있습니다. 대체 가능 토큰 표준인 KIP-7의 익명화 토큰 표준입니다. KIP-7와 결합하여 익명화 토큰을 만들 수 있습니다.

```
// IKIP27
// event AnonTransfer(uint256 hashed);

function encBalanceOf(address account) external view returns (ciphertext);  // It returns a ciphertext of (u, v, addr)
function anonTransfer(uint256 rt, uint256 sn, uint256 commit, uint256 hashed, ciphertext ct, proof pi) external returns (bool);

// IKIP27Exchangeable
function deposit(address recipient, uint256 amount, proof pi); 
function withdraw(address sender, uint256 amount, ciphertext ct, proof pi);

```


# Python client to interact with the prover

## Structure of the directory

### `zeth`

```
zeth
 |_ api
 |_ cli
 |_ core
 |_ helper
```

This directory contains the API code for the Zeth client (`api`), its backend implementation (`core`), the code for the client CLI (`cli`), and the code of an "helper" CLI - providing useful functionalities to support the use of Zeth on Ethereum-like networks (`helper`).

### `test_commands`

This directory contains a list of useful commands to help run the tests, as well as some minimal testing scenarios acting as integration tests.

### `tests`

The `tests` folder contains the unit tests of the `zeth` package.

## Setup

Ensure that the following are installed:

- Python 3.7 (See `python --version`)
- [venv](https://docs.python.org/3/library/venv.html#module-venv) module.
- gcc
- cmake 설치되어 있어야 함. brew install cmake (맥에서)
- brew tap ethereum/ethereum (맥에서)
- brew install solidity@5 (맥에서)

Execute the following inside the `client` directory.
```console


$ python3 -m venv env
$ source env/bin/activate
(env)$ make setup
```

(It may also be necessary to install solc manually if the `py-solc-x` package
fails to find it. See the instructions below.)

We assume all further commands described here are executed from within the
Python virtualenv.  To enter the virtualenv from a new terminal, re-run
```console
$ source env/bin/activate
```

## Execute unit tests

```console
(env)$ make check
```

## Execute testing client

These are scripts that perform some predetermined transactions between a set of
users: Alice, Bob and Charlie.

Test ether mixing:
```console
(env)$ test_ether_mixing.py [ZKSNARK]
```

Test ERC token mixing:
```console
(env)$ test_erc_token_mixing.py [ZKSNARK]
```

where `[ZKSNARK]` is the zksnark to use (must be the same as the one used on
the server).

## Note on solc compiler installation

Note that `make setup` will automatically install the solidity compiler in `$HOME/.solc`
(if required) and not in the python virtual environment.

# The `zeth` command line interface

The `zeth` command exposes Zeth operations via a command line interface.  A
brief description is given in this section.  More details are available via
`zeth --help`, and example usage can be seen in the [pyclient test
script](../scripts/test_zeth_cli).

## Environment

Depending on the operation being performed, the `zeth` client must:
- interact with an Ethereum RPC host,
- interact with the deployed Zeth contracts,
- request proofs and proof verification keys from `prover_server`, and
- access secret and public data for the current user

Quite a lot of information must be given in order for the client to do this,
and the primary and auxiliary inputs to a Zeth operation are generally very
long. It can therefore be difficult to pass this information to the zeth
commands as command-line arguments. Thus, such data is stored in files with
default file names (which can be overridden on the zeth commands).

The set of files required by Zeth for a single user to interact with a specific
deployment is described below. We recommend creating a directory for each
user/Zeth deployment, containing the following files. In this way, it is very
easy to setup one or more conceptual "users" and invoke `zeth` operations on
behalf of each of them to experiment with the system.

- `eth-address` specifies an Ethereum address from which to transactions should
  be funded. When running the testnet (see [top-level README](../README.md)),
  addresses are created at startup and written to the console. One of these can
  be copy-pasted into this file.
- `zeth-instance` contains the address and ABI for a single instance of the
  zeth contract. This file is created by the deployment step below and should
  be distributed to each client that will use this instance.
- `zeth-address.priv` and `zeth-address.pub` hold the secret and public parts
  of a ZethAddress. These can be generated with the `zeth gen-address` command.
  `zeth-address.pub` holds the public address which can be shared with other
  users, allowing them to privately transfer funds to this client. The secret
  `zeth-address.priv` should **not** be shared.

Note that by default the `zeth` command will also create a `notes`
subdirectory to contain the set of notes owned by this user. These are also
specific to a particular Zeth deployment.

Thereby, in the case of a Zeth user interacting with multiple Zeth deployments
(for example one for privately transferring Ether, and another for an ERC20
token), a directory should be created for each deployment:

```
  MyZethInstances/
      Ether/
          eth-address
          zeth-instance
          zeth-address.priv
          zeth-address.pub
          notes/...
      ERCToken1/
          eth-address
          zeth-instance
          zeth-address.priv
          zeth-address.pub
          notes/...
```

`zeth` commands invoked inside `MyZethInstances/Ether` will target the Zeth
deployment that handles Ether. Similarly, commands executed inside
`MyZethInstances/ERCToken1` will target the deployment that handles the token
"ERCToken1".

## Deployment

Deployment compiles and deploys the contracts and initializes them with
appropriate data to create a new instance of the Zeth mixer. It requires only
an `eth-address` file mentioned above, where the address has sufficient funds.

```console
# Create a clean directory for the deployer
(env)$ mkdir deployer
(env)$ cd deployer

# Specify an eth-address file for an (unlocked) Ethereum account
(env)$ echo 0x.... > eth-address

# Compile and deploy
(env)$ zeth deploy

# Share the instance file with all clients
$ cp zeth-instance <destination>
```

## User setup

To set up her client, Alice must setup all client files mentioned above:
```console
# Create a clean client directory
$ mkdir alice
$ cd alice

# Specify an eth-address file for an (unlocked) Ethereum account
$ echo 0x.... > eth-address

# Copy the instance file (received from the deployer)
$ cp <shared-instance-file> zeth-instance

# Generate new Zeth Address with secret (zeth-address.priv) and
# public address (zeth-address.pub)
$ zeth gen-address

# Share the public address with other users
$ cp zeth-address.pub <destination>
```

## Zklay Auditor setup
```console
# Create a clean directory for the deployer
(env)$ mkdir auditor
(env)$ cd auditor

# Specify an eth-address file for an (unlocked) Ethereum account
(env)$ echo 0x.... > eth-address

# Compile and deploy
(env)$ zklay audit-key-gen

# Share the instance file with all clients
# $ cp zeth-instance <destination>
```

With these files in place, `zeth` commands invoked from inside this directory
can perform actions on behalf of Alice.  We call this Alice's *client directory*
below, and assume that all commands are executed in a directory with these
files.

## Receiving transactions

The following command scans the blockchain for any new transactions which
generate Zeth notes intended for the public address `zeth-address.pub`:

```console
# Check all new blocks for notes addressed to `zeth-address.pub`,
# storing them in the ./notes directory.
# ./notes가 아니라 wallet directory에 저장된다.
(env)$ zeth sync
```

Any notes found are stored in the `./wallet` directory as individual files.
These files contain the secret data required to spend the note.

```console
# List all notes received by this client
$ zeth ls-notes
```
lists information about all known notes belonging to the current user.

## Mix command

The `zeth mix` command is used to interact with a deployed Zeth Mixer instance.
The command accepts the following information:

**Input Notes.** Zeth notes owned by the current client, which should be visible
via `zeth ls-notes`.  Either the integer "address" or the truncated commitment
value (8 hex chars) can be used to specify which notes to use as inputs.

**Output Notes.** Given as pairs of Zeth public address and value, separated by
a comma `,`. The form of the public address is exactly as in the
`zeth-address.pub` file. That is, two 32 byte hex values separated by a colon
`:`.

**Public Input.** Ether or ERC20 token value to deposit in the mixer.

**Public Output.** Ether or ERC20 tokens value to be withdrawn from the mixer.

Some examples are given below

### Depositing funds

A simple deposit consists of some public input (ether or tokens), and the
creation of Zeth notes.

```console
# Deposit 10 ether from `eth-address`, creating Zeth notes owned by Alice
(env)$ zeth mix --out zeth-address.pub,10 --vin 10
# zeth sync를 해 주어야 note가 생긴다.
```

### Privately send a ZethNote to another user

To privately transfer value within the mixer, no public input / output is
required. Unspent notes (inputs) and destination addresses and output note
values are specified.

```console
$ zeth ls-notes
b1a2feaf: value=200, addr=0
eafe5f84: value=100, addr=2

$ zeth mix \
    --in eafe5f84 \                       # "eafe5f84: value=100, addr=2"
    --in 0 \                              # "b1a2feaf: value=200, addr=0"
    --out d77f...0e00:cc7c....7f76,120 \  # 120 to this addr
    --out 3a43...fd3b:9fc8....b838,180    # 180 to this addr
```

### Withdrawing funds from the mixer

Specify the note(s) to be withdrawn, and the total value as public output:
```console
$ zeth mix --in eafe5f84 --vout 100
```

### A note on the `zeth mix` command

As explained above, the `zeth mix` command can be used to deposit funds on the
mixer, transfer notes, and withdraw funds from the mixer. A single command can
perform all of these in one transaction, which greatly improves the privacy
level provided by Zeth. In fact, no exact information about the meaning of a
transaction is ever leaked to an observant attacker.

Here are a few examples of complex payments allowed by `zeth mix`:

```console
$ zeth ls-notes
b1a2feaf: value=200, addr=0
eafe5f84: value=100, addr=2

$ zeth mix \
    --in eafe5f84 \                       # "eafe5f84: value=100, addr=2"
    --vin 5 \
    --out d77f...0e00:cc7c....7f76,103 \  # 103 to this address (e.g. Bob)
    --out 3a43...fd3b:9fc8....b838,2      # 2 to another addr (e.g. my refund)

zeth mix \
    --in eafe5f84 \                       # "eafe5f84: value=100, addr=2"
    --out d77f...0e00:cc7c....7f76,98.5 \ # 98.5 to this address (e.g. Bob)
    --vout 1.5
```

### Async transactions

The `mix` command broadcasts transactions to the Ethereum network and by default
output the transaction ID.  Users can wait for these transactions to be accepted
into the blockchain by passing this ID to the `zeth sync` command via the
`--wait-tx` flag.  This command waits for the transaction to be committed and
then searches for new notes.

Alternatively, the `--wait` flag can be passed to the `mix` command to make it
wait and sync new notes before exiting.

## Docker (Debug/Development only)

A minimal Docker image is provided in order to use the client in a container.
In order to do so, one needs to:
1. Fetch the docker image:
```
$ docker pull clearmatics/zeth-client:latest
```
2. Start the docker container:
```
$ docker run -ti \
    --net=host \
    --name zeth-client-container clearmatics/zeth-client
```

**Important:** Note that, the `clearmatics/zeth-client` image cannot be used
to deploy the *Zeth* contracts (the contracts are not available inside the
container). Instead, this image is only aimed at providing a pre-configured
environment to interact with deployed *Zeth* contracts via a docker container.
Moreover, **we strongly advise against** running the client in the docker
container in any real-life scenario. Proper secret management and backup need
to be carried out for the wallet data to be protected against losses and
adversaries (see section below).

## Limitations - Note and Address management

As proof-of-concept software, these tools are not suitable for use in a
production environment and have several functional limitations. Some of those
limitations are mentioned here.

The `zeth` tool suite does not track which of the client's notes have been
spent by previous operations. In the presence of async transactions and
possible forks in the chain, such tracking logic would greatly increase the
complexity of the client tools and is considered out of scope for this
proof-of-concept. The user must manually track which notes have been spent (for
example by moving their files into a `spent` subdirectory where they will not
be seen by the wallet).

All values that make up the Zeth secret address, and Zeth note data (required
to spend notes) are stored in plaintext. A fully secure client would encrypt
these to protect them from malicious entities that may gain access to the file
system. Such client-side security mechanisms are also beyond the scope of this
proof-of-concept implementation.

Similarly, such address and note data is not automatically backed up or
otherwise protected by these tools.
