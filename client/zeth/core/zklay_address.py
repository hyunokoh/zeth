# Copyright (c) 2021-2021 Zkrypto Inc.
#
# SPDX-License-Identifier: LGPL-3.0+

from __future__ import annotations
#from zeth.core.ownership import OwnershipPublicKey, OwnershipSecretKey, \
#    OwnershipKeyPair, ownership_key_as_hex, gen_ownership_keypair, \
#    ownership_public_key_from_hex, ownership_secret_key_from_hex
from zeth.core.zklay_encryption import \
    ZklayEncryptionKeyPair, EncryptionPublicKey, EncryptionSecretKey, \
    generate_zklay_encryption_keypair, encryption_public_key_as_hex, \
    encryption_public_key_from_hex, encryption_secret_key_as_hex, \
    encryption_secret_key_from_hex
import json
from typing import Dict, Any


class ZklayAddressPub:
    """
    Public zklayAddress.  addr_pk = (a_pk, b_pk, u_pk, h_pk). a_pk = H(b_pk, u_pk, h_pk). b_pk : binding key, u_pk : public key, h_pk : auditor helping key
    """
    def __init__(self, a_pk : EncryptionPublicKey, b_pk: EncryptionPublicKey, u_pk: EncryptionPublicKey, h_pk : EncryptionPublicKey):
        self.a_pk: EncryptionPublicKey = a_pk
        self.b_pk: EncryptionPublicKey = b_pk
        self.u_pk: EncryptionPublicKey = u_pk
        self.h_pk: EncryptionPublicKey = h_pk

    def __str__(self) -> str:
        """
        Write the address as "<ownership-key-hex>:<ownership-key-hex>:<encryption_key_hex>:<encryption_key_hex>".
        (Technically the ":" is not required, since the first key is written
        with fixed length, but a separator provides some limited sanity
        checking).
        """
        a_pk_hex = encryption_public_key_as_hex(self.a_pk)
        b_pk_hex = encryption_public_key_as_hex(self.b_pk)
        u_pk_hex = encryption_public_key_as_hex(self.u_pk)
        h_pk_hex = encryption_public_key_as_hex(self.h_pk)
        return f"{a_pk_hex}:{b_pk_hex}:{u_pk_hex}:{h_pk_hex}"

    @staticmethod
    def parse(key_hex: str) -> ZklayAddressPub:
        owner_enc = key_hex.split(":")
        if len(owner_enc) != 4:
            raise Exception("invalid JoinSplitPublicKey format")
        a_pk = ownership_public_key_from_hex(owner_enc[0])
        b_pk = ownership_public_key_from_hex(owner_enc[1])
        u_pk = encryption_public_key_from_hex(owner_enc[2])
        h_pk = encryption_public_key_from_hex(owner_enc[3])
        return ZklayAddressPub(a_pk, b_pk, u_pk, h_pk)


class ZklayAddressPriv:
    """
    Secret zklayAddress. addr_sk = (addr_sk)
    """
    def __init__(self, addr_sk: EncryptionSecretKey):
        self.addr_sk: EncryptionSecretKey = addr_sk

    def to_json(self) -> str:
        return json.dumps(self._to_json_dict())

    @staticmethod
    def from_json(key_json: str) -> ZklayAddressPriv:
        return ZklayAddressPriv._from_json_dict(json.loads(key_json))

    def _to_json_dict(self) -> Dict[Any]:
        return {
            "addr_sk": encryption_secret_key_as_hex(self.addr_sk),
        }

    @staticmethod
    def _from_json_dict(key_dict: Dict[Any]) -> ZklayAddressPriv:
        return ZklayAddressPriv(
            encryption_secret_key_from_hex(key_dict["addr_sk"]))


class ZklayAddress:
    """
    Secret and public keys for both ownership and encryption (referrred to as
    "zklayAddress" in the paper).
    """
    def __init__(
            self,
            addr_sk: EncryptionSecretKey,
            a_pk: EncryptionPublicKey,
            b_pk: EncryptionPublicKey,
            u_pk: EncryptionPublicKey,
            h_pk: EncryptionPublicKey):
        self.addr_pk = ZklayAddressPub(a_pk, b_pk, u_pk, h_pk)
        self.addr_sk = ZklayAddressPriv(addr_sk)

    @staticmethod
    def from_key_pairs(
            encryption: EncryptionKeyPair) -> ZklayAddress:
        return ZklayAddress(
            encryption.addr_sk,
            encryption.a_pk,
            encryption.b_pk,
            encryption.u_pk,
            encryption.h_pk)

def generate_zklay_address(audit_pk : AuditAddressPub) -> ZklayAddress:
    encryption_keypair = generate_zklay_encryption_keypair(audit_pk)
    return ZklayAddress.from_key_pairs(encryption_keypair)
