# Copyright (c) 2021-2021 Zkrypto Inc
#
# SPDX-License-Identifier: LGPL-3.0+

from __future__ import annotations
#from zeth.core.ownership import OwnershipPublicKey, OwnershipSecretKey, \
#    OwnershipKeyPair, ownership_key_as_hex, gen_ownership_keypair, \
#    ownership_public_key_from_hex, ownership_secret_key_from_hex
from zeth.core.encryption import \
    EncryptionKeyPair, EncryptionPublicKey, EncryptionSecretKey, \
    generate_encryption_keypair, encryption_public_key_as_hex, \
    encryption_public_key_from_hex, encryption_secret_key_as_hex, \
    encryption_secret_key_from_hex
import json
from typing import Dict, Any


class AuditAddressPub:
    """
    Public AuditAddress.  addr_pk = (addr_pk)
    """
    def __init__(self, addr_pk: EncryptionPublicKey):
        self.addr_pk: EncryptionPublicKey = addr_pk

    def __str__(self) -> str:
        """
        Write the address as "<ownership-key-hex>:<encryption_key_hex>".
        (Technically the ":" is not required, since the first key is written
        with fixed length, but a separator provides some limited sanity
        checking).
        """
        addr_pk_hex = encryption_public_key_as_hex(self.addr_pk)
        return f"{addr_pk_hex}"

    @staticmethod
    def parse(key_hex: str) -> AuditAddressPub:
        #owner_enc = key_hex.split(":")
        #if len(owner_enc) != 1:
        #    raise Exception("invalid JoinSplitPublicKey format")
        addr_pk = encryption_public_key_from_hex(key_hex)
        return AuditAddressPub(addr_pk)


class AuditAddressPriv:
    """
    Secret AuditAddress. addr_sk = (addr_sk)
    """
    def __init__(self, addr_sk: EncryptionSecretKey):
        self.addr_sk: EncryptionSecretKey = addr_sk

    def to_json(self) -> str:
        return json.dumps(self._to_json_dict())

    @staticmethod
    def from_json(key_json: str) -> AuditAddressPriv:
        return AuditAddressPriv._from_json_dict(json.loads(key_json))

    def _to_json_dict(self) -> Dict[Any]:
        return {
            "addr_sk": encryption_secret_key_as_hex(self.addr_sk),
        }

    @staticmethod
    def _from_json_dict(key_dict: Dict[str, Any]) -> AuditAddressPriv:
        return AuditAddressPriv(
            encryption_secret_key_from_hex(key_dict["addr_sk"]))


class AuditAddress:
    """
    Secret and public keys for auditor encryption 
    """
    def __init__(
            self,
            addr_pk: EncryptionPublicKey,
            addr_sk: EncryptionSecretKey):
        self.addr_pk = AuditAddressPub(addr_pk)
        self.addr_sk = AuditAddressPriv(addr_sk)

    @staticmethod
    def from_key_pairs(
            encryption: EncryptionKeyPair) -> AuditAddress:
        return AuditAddress(
            encryption.k_pk,
            encryption.k_sk)

    @staticmethod
    def from_secret_public(
            js_secret: AuditAddressPriv,
            js_public: AuditAddressPub) -> AuditAddress:
        return AuditAddress(
            js_public.addr_pk, js_secret.addr_sk)


def generate_audit_address() -> AuditAddress:
    encryption_keypair = generate_encryption_keypair()
    return AuditAddress.from_key_pairs(encryption_keypair)

def generate_zklay_address() -> AuditAddress:
    encryption_keypair = generate_encryption_keypair()
    return AuditAddress.from_key_pairs(encryption_keypair)
