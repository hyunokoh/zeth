# Copyright (c) 2021-2021 Zkrypto Inc.
#
# SPDX-License-Identifier: LGPL-3.0+

from zeth.cli.utils import create_mixer_client_and_mixer_desc, \
    load_zeth_address, open_wallet, parse_output, do_sync, load_eth_address, \
    load_eth_private_key, zeth_note_short_print, create_prover_client
from zeth.core.constants import JS_INPUTS, JS_OUTPUTS
from zeth.core.mixer_client import ZethAddressPub
from zeth.core.utils import EtherValue, from_zeth_units
from zeth.api.zeth_messages_pb2 import ZethNote
from click import command, option, pass_context, ClickException, Context
from typing import List, Tuple, Optional


@command()
@option("--value", default="0", help="deposit value from EOA to Zklay account")
@option("--eth-addr", help="Sender's eth address or address filename")
@option("--eth-private-key", help="Sender's eth private key file")
@option("--wait", is_flag=True, help="Wait for transaction to be mined")
@pass_context
def deposit(
        ctx: Context,
        value: str,
        eth_addr: Optional[str],
        eth_private_key: Optional[str],
        wait: bool) -> None:
    """
    Deposit function
    """

    value_pub = EtherValue(value)
    client_ctx = ctx.obj
    prover_client = create_prover_client(client_ctx)
    zklay_client, mixer_desc = create_deposit(
        client_ctx, prover_client)
    zklay_address = load_zklay_address(client_ctx)
    wallet = open_wallet(
        zklay_client.mixer_instance, zklay_address.addr_sk, client_ctx)

    inputs: List[Tuple[int, ZethNote]] = [
        wallet.find_note(note_id).as_input() for note_id in input_notes]
    outputs: List[Tuple[ZethAddressPub, EtherValue]] = [
        parse_output(out_spec) for out_spec in output_specs]

    # Compute input and output value total and check that they match
    input_note_sum = from_zeth_units(
        sum([int(note.value, 16) for _, note in inputs]))
    output_note_sum = sum([value for _, value in outputs], EtherValue(0))
    if vin_pub + input_note_sum != vout_pub + output_note_sum:
        raise ClickException("input and output value mismatch")

    eth_address = load_eth_address(eth_addr)
    eth_private_key_data = load_eth_private_key(eth_private_key)

    # If instance uses an ERC20 token, tx_value can be 0. Otherwise it should
    # match vin_pub.
    tx_value = EtherValue(0) if mixer_desc.token else vin_pub

    # Create the MixParameters object manually so they can be displayed.
    # TODO: support saving the generated MixParameters to be sent later.
    mix_params, _ = zeth_client.create_mix_parameters_and_signing_key(
        prover_client,
        wallet.merkle_tree,
        zeth_address.ownership_keypair(),
        eth_address,
        inputs,
        outputs,
        vin_pub,
        vout_pub)

    if show_parameters:
        print(f"mix_params={mix_params.to_json()}")

    tx_hash = zeth_client.mix(
        mix_params=mix_params,
        sender_eth_address=eth_address,
        sender_eth_private_key=eth_private_key_data,
        tx_value=tx_value)

    print(tx_hash)
    if wait:
        pp = prover_client.get_configuration().pairing_parameters
        do_sync(zeth_client.web3, wallet, pp, tx_hash, zeth_note_short_print)
