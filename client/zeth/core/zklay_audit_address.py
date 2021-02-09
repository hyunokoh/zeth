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
    Public AuditAddress.  addr_pk = (k_pk)
    """
    def __init__(self, k_pk: EncryptionPublicKey):
        self.k_pk: EncryptionPublicKey = k_pk

    def __str__(self) -> str:
        """
        Write the address as "<ownership-key-hex>:<encryption_key_hex>".
        (Technically the ":" is not required, since the first key is written
        with fixed length, but a separator provides some limited sanity
        checking).
        """
        k_pk_hex = encryption_public_key_as_hex(self.k_pk)
        return f"{k_pk_hex}"

    @staticmethod
    def parse(key_hex: str) -> AuditAddressPub:
        owner_enc = key_hex.split(":")
        if len(owner_enc) != 1:
            raise Exception("invalid JoinSplitPublicKey format")
        k_pk = encryption_public_key_from_hex(owner_enc[0])
        return AuditAddressPub(k_pk)


class AuditAddressPriv:
    """
    Secret AuditAddress. addr_sk = (k_sk)
    """
    def __init__(self, k_sk: EncryptionSecretKey):
        self.k_sk: EncryptionSecretKey = k_sk

    def to_json(self) -> str:
        return json.dumps(self._to_json_dict())

    @staticmethod
    def from_json(key_json: str) -> AuditAddressPriv:
        return AuditAddressPriv._from_json_dict(json.loads(key_json))

    def _to_json_dict(self) -> Dict[Any]:
        return {
            "k_sk": encryption_secret_key_as_hex(self.k_sk),
        }

    @staticmethod
    def _from_json_dict(key_dict: Dict[str, Any]) -> AuditAddressPriv:
        return AuditAddressPriv(
            encryption_secret_key_from_hex(key_dict["k_sk"]))


class AuditAddress:
    """
    Secret and public keys for auditor encryption 
    """
    def __init__(
            self,
            k_pk: EncryptionPublicKey,
            k_sk: EncryptionSecretKey):
        self.addr_pk = AuditAddressPub(k_pk)
        self.addr_sk = AuditAddressPriv(k_sk)

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
            js_public.k_pk, js_secret.k_sk)


def generate_audit_address() -> AuditAddress:
    encryption_keypair = generate_encryption_keypair()
    return AuditAddress.from_key_pairs(encryption_keypair)

def generate_zklay_address() -> AuditAddress:
    encryption_keypair = generate_encryption_keypair()
    return AuditAddress.from_key_pairs(encryption_keypair)
