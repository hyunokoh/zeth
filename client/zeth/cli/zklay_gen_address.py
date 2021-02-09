# Copyright (c) 2015-2020 Clearmatics Technologies Ltd
#
# SPDX-License-Identifier: LGPL-3.0+

from zeth.core.zklay_address import generate_zklay_address
from zeth.core.zklay_audit_address import AuditAddressPub
from zeth.cli.utils import get_zklay_address_file, pub_address_file, \
    write_zklay_address_secret, write_zklay_address_public, \
    load_zklay_audit_address_public
from click import command, pass_context, ClickException, Context
from os.path import exists


@command()
@pass_context
def gen_address(ctx: Context) -> None:
    """
    Generate a new Zklay secret key and public address
    """
    client_ctx = ctx.obj
    addr_file = get_zklay_address_file(client_ctx)
    if exists(addr_file):
        raise ClickException(f"ZklayAddress file {addr_file} exists")

    pub_addr_file = pub_address_file(addr_file)
    if exists(pub_addr_file):
        raise ClickException(f"ZklayAddress pub file {pub_addr_file} exists")

#    audit_pub_addr_file = pub_address_file(get_zklay_audit_address_file(client_ctx))
#    if !exists(audit_pub_addr_file):
#        raise ClickException(f"ZklayAuditAddress file {audit-address.pub} does not exist")

    audit_pk = load_zklay_audit_address_public(client_ctx)

    zklay_address = generate_zklay_address(audit_pk)
    write_zklay_address_secret(zklay_address.addr_sk, addr_file)
    print(f"ZklayAddress Secret key written to {addr_file}")
    write_zklay_address_public(zklay_address.addr_pk, pub_addr_file)
    print(f"Public ZklayAddress written to {pub_addr_file}")
