// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IVerification} from "./interfaces/IVerification.sol";
import {Header} from "./types/Common.sol";

/**
 * @title OIDCVerifier
 * @dev A simple verifier for OIDC tokens (JWT tokens from Google Cloud)
 * This is a simplified implementation for testing purposes
 */
contract OIDCVerifier is IVerification {
    /**
     * @dev Returns the token type this verifier handles
     * @return bytes The token type identifier
     */
    function tokenType() external pure override returns (bytes memory) {
        return bytes("OIDC");
    }
    
    /**
     * @dev Verifies the signature of a JWT token
     * This is a simplified implementation that always returns true for testing
     * In a real implementation, this would verify the RSA signature
     * @param header The JWT header
     * @param payload The JWT payload
     * @param signature The JWT signature
     * @param parsedHeader The parsed header structure
     * @return verified Boolean indicating if the signature is valid
     * @return digest The hash of the verified data
     */
    function verifySignature(
        bytes calldata header,
        bytes calldata payload,
        bytes calldata signature,
        Header memory parsedHeader
    ) external pure override returns (bool verified, bytes32 digest) {
        // In a real implementation, this would verify the RSA signature
        // For testing, we just return true and a hash of the header and payload
        
        // Create a digest from the header and payload
        digest = keccak256(abi.encodePacked(header, ".", payload));
        
        // Always return true for testing
        verified = true;
        
        return (verified, digest);
    }
}
