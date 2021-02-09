# Copyright (c) 2021-2021 Zkrypto Inc.
#
# SPDX-License-Identifier: LGPL-3.0+

from zeth.core.zklay_address import generate_audit_address, generate_zklay_address
from zeth.cli.utils import get_zklay_audit_address_file, pub_address_file, \
    write_zklay_audit_address_secret, write_zklay_audit_address_public
from click import command, pass_context, ClickException, Context
from os.path import exists


@command()
@pass_context
def audit_key_gen(ctx: Context) -> None:
    print("audit_key_gen start")
    """
    Generate a new auditor secret key and public address
    """
    client_ctx = ctx.obj
    addr_file = get_zklay_audit_address_file(client_ctx)
    if exists(addr_file):
        raise ClickException(f"auditAddress file {addr_file} exists")

    pub_addr_file = pub_address_file(addr_file)
    if exists(pub_addr_file):
        raise ClickException(f"auditAddress pub file {pub_addr_file} exists")

    zklay_audit_address = generate_audit_address()
    write_zklay_audit_address_secret(zklay_audit_address.addr_sk, addr_file)
    print(f"AuditAddress Secret key written to {addr_file}")
    write_zklay_audit_address_public(zklay_audit_address.addr_pk, pub_addr_file)
    print(f"Public AuditAddress written to {pub_addr_file}")
