// Copyright (c) 2021-2021 Zkrypto Inc.
// Author : H. Oh
//
// SPDX-License-Identifier: LGPL-3.0+

pragma solidity ^0.5.0;
pragma experimental ABIEncoderV2;

import "./Tokens.sol";
import "./OTSchnorrVerifier.sol";
import "./BaseMerkleTree.sol";

/// MixerBase implements the functions shared across all Mixers (regardless
/// which zkSNARK is used)
contract ZklayBase is BaseMerkleTree, ERC223ReceivingContract
{
    // The roots of the different updated trees
    mapping(bytes32 => bool) private _roots;

    // The public list of nullifiers (prevents double spend)
    mapping(bytes32 => bool) private _nullifiers;

    // Auditor's public key
    uint256 internal _auditor_key;

    struct EncAccount {
        uint256 ct;
        uint256 kb;    // binding key = H(k) where k is a secret key
        uint256 ku;    // user public key = A^k where A is an audior public key
        uint256 ka;    // auditor helping key = G^k where G is a group generator 
    }

    // encrypted account
    mapping(address => EncAccount) private ena;

    // Contract variable that indicates the address of the token contract
    // If token = address(0) then the mixer works with ether
    address private _token;

    // JoinSplit description, gives the number of inputs (nullifiers) and
    // outputs (commitments/ciphertexts) to receive and process.
    //
    // IMPORTANT NOTE: We need to employ the same JS configuration than the one
    // used in the cpp prover. Here we use 2 inputs and 2 outputs (it is a 2-2
    // JS).
    uint256 internal constant JSIN = 1; // Number of nullifiers
    uint256 internal constant JSOUT = 1; // Number of commitments/ciphertexts

    uint256 internal constant DIGEST_LENGTH = 256;

    // Number of hash digests in the primary inputs:
    //   1 (the root)
    //   2 * JSIN (nullifier and message auth tag per JS input)
    //   JSOUT (commitment per JS output)
    uint256 internal constant NUM_HASH_DIGESTS = 1 + 2 * JSIN;

    // All code assumes that public values and residual bits can be encoded in
    // a single field element.
    uint256 internal constant NUM_FIELD_RESIDUAL = 1;

    // The number of public inputs are:
    // - 1 (the root)
    // - JSIN (the nullifiers)
    // - JSOUT (the commitments)
    // - 1 (hsig)
    // - JsIn (the message auth. tags)
    // - NUM_FIELD_RESIDUAL (the residual bits not fitting in a single field
    //   element and the in and out public values)
    uint256 internal constant NUM_INPUTS =
        1 + JSOUT + NUM_HASH_DIGESTS + NUM_FIELD_RESIDUAL;

    // The unit used for public values (ether in and out), in Wei. Must match
    // the python wrappers. Use Szabos (10^12 Wei).
    uint64 internal constant PUBLIC_UNIT_VALUE_WEI = 1 szabo;

    event LogMix(
        bytes32 root,
        bytes32[JSIN] nullifiers,
        bytes32[JSOUT] commitments,
        bytes[JSOUT] ciphertexts
    );

    /// Debug only
    event LogDebug(string message);

    /// Constructor
    constructor(uint256 depth, address token_address, uint256[] memory vk)
        public
        BaseMerkleTree(depth)
    {
        bytes32 initialRoot = nodes[0];
        _roots[initialRoot] = true;
        _vk = vk;
        _token = token_address;
    }

    /// Function allowing external users of the contract to retrieve some of
    /// the constants used in the mixer (since the solidity interfaces do not
    /// export this information as-of the current version). The intention is
    /// that external users and contraacts can query this function and ensure
    /// that they are compatible with the mixer configurations.
    ///
    /// Returns the number of input notes, the number of output notes and the
    /// total number of primary inputs.
    function get_constants()
        external
        pure
        returns (
            uint256 js_in_out,
            uint256 js_out_out,
            uint256 num_inputs_out
        )
    {
        js_in_out = JSIN;
        js_out_out = JSOUT;
        num_inputs_out = NUM_INPUTS;
    }

    /// These functions transfer klay and tokens
    function deposit(
        uint256[] proof,
        address toaddress,
        uint256 amount,
        uint256 ciphertext
    }
        public
        payable
    {
        EncAccount account = map[toaddr];

        bytes32 h = sha256(
            uint256(toaddress), account.ct, ciphertext, amount);

        // 2.b Verify the balance proof
        require(
            verify_balance_proof(proof, h),
            "Invalid proof: Unable to verify the balance proof correctly"
        );

        if (_token != address(0)) {
            ERC20 erc20Token = ERC20(_token);
            erc20Token.transferFrom(msg.sender, address(this), amount);
        }

        account.ct = ciphertext;
    }

    # TODO: After verifying deposit, we will implement withdraw.
    function withdraw(
        uint256[] proof,
        address fromaddress,
        uint256 amount,
        uint256 ciphertext
    }
        public
        payable
    {
    }

    /// This function is used to execute payments in zero knowledge.
    /// The format of `proof` is internal to the zk-snark library.
    /// The `inputs` array is the set of scalar inputs to the proof.
    /// We assume that each input occupies a single uint256.
    function anonTransfer(
        uint256[] proof,
        uint256[NUM_INPUTS] inputs,
        uint256 ciphertext
    )
        public
        payable
    {
        // 1. Check the root and  the sn
        bytes32 memory sn;
        check_mkroot_nullifiers_hsig_append_nullifiers_state(
            vk, inputs, sn);

        // 2.a Verify the signature on the hash of data_to_be_signed
        bytes32 h = sha256(
            uint256(_auditor_key), abi.encodePacked(inputs, ciphertext));

        // 2.b Verify the proof
        require(
            verify_zk_proof(proof, h),
            "Invalid proof: Unable to verify the proof correctly"
        );

        // 3. Append the commitments to the tree
        bytes32 memory commitment;
        assemble_commitments_and_append_to_state(inputs, commitment);

        // 4. Add the new root to the list of existing roots
        bytes32 new_merkle_root = recomputeRoot(JSOUT);
        add_merkle_root(new_merkle_root);

        // 5. Emit the all Mix data
        emit LogMix(
            new_merkle_root,
            sn,
            commitment,
            ciphertext
        );

        // 6. Get the public values in Wei and modify the state depending on
        // their values
        process_public_values(inputs);
    }

    /// This function is used to reassemble the nullifiers given the nullifier
    /// index [0, JSIN[ and the primary_inputs To do so, we extract the
    /// remaining bits of the nullifier from the residual field element(S) and
    /// combine them with the nullifier field element
    function assemble_nullifier(
        uint256 index,
        uint256[NUM_INPUTS] memory primary_inputs
    )
        internal
        pure
        returns(bytes32 nf)
    {
        // We first check that the nullifier we want to retrieve exists
        require(index < JSIN, "nullifier index overflow");

        // Nullifier residual bits follow the JSIN message authentication tags.
        return extract_bytes32(
            primary_inputs[1 + JSOUT + index],
            primary_inputs[1 + JSOUT + NUM_HASH_DIGESTS],
            JSIN + index
        );
    }

    // ======================================================================
    // Reminder: Remember that the primary inputs are ordered as follows:
    //
    //   [Root, SN, CommitmentS, NullifierS, Residual Element(s)]
    //
    // ie, below is the index mapping of the primary input elements on the
    // protoboard:
    //
    //   <Merkle Root>               0
    //   <Commitment[0]>             1
    //   ...
    //   <Commitment[JSOUT - 1]>     JSOUT
    //   <Nullifier[0]>              JSOUT + 1
    //   ...
    //   <Nullifier[JSIN]>           JSOUT + JSIN
    //   <h_sig>                     JSOUT + JSIN + 1
    //   <Message Auth Tag[0]>       JSOUT + JSIN + 2
    //   ...
    //   <Message Auth Tag[JSIN]>    JSOUT + 2*JSIN + 1
    //   <Residual Field Elements>   JSOUT + 2*JSIN + 2
    //
    // The Residual field elements are structured as follows:
    //
    //   255                                         128         64           0
    //   |<empty>|<h_sig>|<nullifiers>|<msg_auth_tags>|<v_pub_in>)|<v_pub_out>|
    //
    // where each entry entry after public output and input holds the
    // (curve-specific) number residual bits for the corresponding 256 bit
    // value.
    // ======================================================================
    //
    // Utility function to extract a full uint256 from a field element and the
    // n-th set of residual bits from `residual`. This function is
    // curve-dependent.
    function extract_bytes32(
        uint256 field_element,
        uint256 residual,
        uint256 residual_bits_set_idx
    )
        internal
        pure
        returns(bytes32);

    // Implementations must implement the verification algorithm of the
    // selected SNARK.
    function verify_zk_proof(
        uint256[] memory proof,
        uint256[NUM_INPUTS] memory inputs
    )
        internal
        returns (bool);

    /// This function processes the primary inputs to append and check the root
    /// and nullifiers in the primary inputs (instance) and modifies the state
    /// of the mixer contract accordingly. (ie: Appends the commitments to the
    /// tree, appends the nullifiers to the list and so on).
    function check_mkroot_nullifiers_hsig_append_nullifiers_state(
        uint256[4] memory vk,
        uint256[NUM_INPUTS] memory primary_inputs,
        bytes32[JSIN] memory nfs)
        internal
    {
        // 1. We re-assemble the full root digest and check it is in the tree
        require(
            _roots[bytes32(primary_inputs[0])],
            "Invalid root: This root doesn't exist"
        );

        // 2. We re-assemble the nullifiers (JSInputs) and check they were not
        // already seen.
        for (uint256 i = 0; i < JSIN; i++) {
            bytes32 nullifier = assemble_nullifier(i, primary_inputs);
            require(
                !_nullifiers[nullifier],
                "Invalid nullifier: This nullifier has already been used"
            );
            _nullifiers[nullifier] = true;

            nfs[i] = nullifier;
        }
    }

    function assemble_commitments_and_append_to_state(
        uint256[NUM_INPUTS] memory primary_inputs,
        bytes32[JSOUT] memory comms
    )
        internal
    {
        // We re-assemble the commitments (JSOutputs)
        for (uint256 i = 0; i < JSOUT; i++) {
            bytes32 current_commitment = bytes32(primary_inputs[1 + i]);
            comms[i] = current_commitment;
            insert(current_commitment);
        }
    }

    function add_merkle_root(bytes32 root) internal {
        _roots[root] = true;
    }
}
