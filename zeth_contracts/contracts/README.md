# Zeth smart contracts

## Changes
- ZklayBase.sol 추가 되었음
- ZklayBase.sol에 deposit, withdraw, anonTransfer 함수 구현해야 함
- deposit에 대해서 prototype으로 구현하였음. 하지만 완성된 것은 아님
- mixer_client.py in client/zeth/core에 deposit을 호출하는 함수를 구현해야 함.

The Byzantium hard fork of Ethereum has introduced [precompiled contracts for elliptic curves operations (on bn256)](https://github.com/ethereum/go-ethereum/blob/v1.7.1/core/vm/contracts.go#L57-L59). When configured with `ALT_BN128`, Zeth will use these precompiled contracts (in the client) as part of the transition to new blockchain states.

However, when using other curves such as `BLS12_377` or `BW6_761` for instance (which, at the time of writing, are not supported by the [go-ethereum client](https://github.com/ethereum/go-ethereum/tree/v1.9.25)), one needs to make sure that the underlying client will support precompiled for arithmetic over these curves.
Such extension to the execution environment is supported in [our fork of ganache-cli](https://github.com/clearmatics/ganache-cli/tree/v6.10.1-clearmatics) for testing purposes (check [here](https://github.com/clearmatics/ethereumjs-vm/blob/v4.1.3-clearmatics/lib/evm/precompiles/index.ts#L30-L36) for the addresses of these instructions). Some of the Zeth contracts use these additional precompiled contracts to specify state transitions.
