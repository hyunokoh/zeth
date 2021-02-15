# Copyright (c) 2021-2021 Zkrypto Inc.
#
# SPDX-License-Identifier: LGPL-3.0+

from zeth.cli.utils import create_zklay_client_and_zklay_desc, \
    load_zklay_address, open_zklay_wallet, parse_output, load_eth_address, \
    load_eth_private_key, create_prover_client, \
    create_balance_prover_client
from zeth.core.constants import JS_INPUTS, JS_OUTPUTS
from zeth.core.zklay_client import ZethAddressPub
from zeth.core.utils import EtherValue, from_zeth_units
from zeth.api.zeth_messages_pb2 import ZethNote
from click import command, option, pass_context, ClickException, Context
from typing import List, Tuple, Optional


@command()
@option("--value", default="0", help="deposit value from EOA to Zklay account")
@option("--eth-addr", help="Sender's eth address or address filename")
@option("--eth-private-key", help="Sender's eth private key file")
@option("--wait", is_flag=True, help="Wait for transaction to be mined")
@option("--show-parameters", is_flag=True, help="Show the deposit parameters")
@pass_context
def deposit(
        ctx: Context,
        value: str,
        eth_addr: Optional[str],
        eth_private_key: Optional[str],
        wait: bool,
        show_parameters: bool) -> None:
    """
    Deposit function
    """

    value_pub = EtherValue(value)
    client_ctx = ctx.obj
    prover_client = create_balance_prover_client(client_ctx)
    zklay_client, zklay_desc = create_zklay_client_and_zklay_desc(
        client_ctx, prover_client)

    zklay_address = load_zklay_address(client_ctx)
    wallet = open_zklay_wallet(
        zklay_client.mixer_instance, zklay_address.addr_sk, client_ctx)

    eth_address = load_eth_address(eth_addr)
    eth_private_key_data = load_eth_private_key(eth_private_key)

    # If instance uses an ERC20 token, tx_value can be 0. Otherwise it should
    # match vin_pub.
    tx_value = EtherValue(0) if zklay_desc.token else value_pub


    # Create the MixParameters object manually so they can be displayed.
    deposit_params = zklay_client.create_deposit(prover_client, eth_address, eth_private_key_data, zklay_address, value_pub)  

    if show_parameters:
        print(f"deposit_params={deposit_params.to_json()}")

    tx_hash = zklay_client.zklay_deposit(
        deposit_params=deposit_params,
        sender_eth_address=eth_address,
        sender_eth_private_key=eth_private_key_data,
        tx_value=tx_value)

    print(tx_hash)
    if wait:
        pp = prover_client.get_configuration().pairing_parameters
