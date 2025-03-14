# ChainContext: Verifiable Knowledge System for Flare


## Project Overview


ChainContext is a verifiable knowledge system built for the Flare ecosystem that combines real-time FTSO data feeds with blockchain state information to provide trustworthy answers with transparent confidence assessment. The system runs in a Trusted Execution Environment (TEE) and provides cryptographic proof of secure execution through vTPM attestations.


I wanted to create a solution that addresses the fragmentation of Web3 datasets and the problem of LLM hallucinations when dealing with blockchain data. My goal was to build a system that not only provides accurate information but also makes the trustworthiness of that information transparent and verifiable.


## Technical Implementation


### Core Components


1. **Data Ingestion Pipeline**: Collects data from multiple sources:
   - FTSO data feeds (both 2s and 90s latency)
   - Blockchain state information
   - Documentation from the Flare Developer Hub
   - Social media content


2. **Trust Scoring Mechanism**: Assigns trust scores to information based on:
   - Source reliability (blockchain state > documentation > social media)
   - Information recency
   - Cross-verification across multiple sources
   - On-chain verification status


3. **TEE Security**: Runs in a Google Cloud Confidential VM with vTPM attestations:
   - Uses AMD SEV for hardware-level security
   - Generates cryptographic attestations that prove system integrity
   - Verifiable on-chain through Flare's vTPM Attestation contract


4. **RAG System**: Combines trusted data sources with Gemini 2.0 Flash:
   - Dynamic relevance scoring for context selection
   - Context window optimization
   - Source attribution and verification


5. **API Interface**: Provides endpoints for:
   - Natural language queries with trust-scored responses
   - FTSO data access (both mainnet and testnet)
   - Attestation verification


### Architecture


The system is containerized using Docker and deployed on a Google Cloud Confidential VM. The main components are:


- **API Service**: FastAPI application that handles requests and coordinates the other services
- **MongoDB**: Stores structured data and query history
- **Redis**: Caches frequently accessed data and embeddings
- **Qdrant**: Vector database for semantic search


## Development Journey


### Initial Setup and Challenges


Setting up the TEE environment was my first major challenge. I needed to ensure that the Google Cloud Confidential VM was properly configured to support vTPM attestations. This required:


1. Selecting the right machine type (n2d-standard-2)
2. Configuring the VM to use AMD SEV
3. Setting up the vTPM device


The documentation was somewhat sparse, and I had to experiment with different configurations before finding one that worked reliably.


Another early challenge was accessing the FTSO data feeds. The Flare network's FTSO system provides price feeds, but accessing them required:


1. Understanding the contract ABIs
2. Setting up proper Web3 connections
3. Handling the different data formats between 2s and 90s feeds


I solved this by creating dedicated collector services that could handle both real-time and historical data, with fallback mechanisms for when the network was unavailable.


### RAG Implementation


Building the RAG system presented several challenges:


1. **Data Quality**: Web3 information is often scattered and inconsistent. I addressed this by implementing a multi-source approach that prioritizes on-chain data but supplements it with documentation and social media when needed.


2. **Context Management**: LLMs have limited context windows, so I needed to be selective about what information to include. I implemented a dynamic relevance scoring system that prioritizes information based on:
   - Semantic similarity to the query
   - Trust score of the source
   - Recency of the information


3. **Embedding Generation**: Creating and storing embeddings for all the data sources was computationally expensive. I optimized this by:
   - Using batched processing for initial embedding generation
   - Implementing incremental updates for new data
   - Caching frequently used embeddings in Redis


### TEE Attestation Integration


Integrating the TEE attestations with the Flare contracts was particularly challenging:


1. **Attestation Format**: The vTPM generates attestations in a specific format that needed to be properly parsed and verified.


2. **Contract Interaction**: The Flare vTPM Attestation contract expects specific parameters and formats. I had to ensure that:
   - The attestation JWT was properly split into header, payload, and signature
   - The container image digest matched the expected value in the contract
   - The hardware and software environment matched the expected configuration


3. **Verification Flow**: I implemented a verification flow that:
   - Extracts the necessary information from the attestation
   - Calls the `verifyAndAttest()` function on the contract
   - Handles verification failures gracefully with detailed error messages


### FTSO Data Access


Working with the FTSO data feeds presented several technical challenges:


1. **Contract ABIs**: The FTSO contracts have complex ABIs that needed to be properly implemented. I created ABI files for:
   - FtsoV2 contract
   - ContractRegistry contract


2. **Feed ID Format**: The FTSO system uses a specific bytes21 format for feed IDs. I had to implement conversion functions to ensure that:
   - String feed IDs were properly converted to bytes21
   - The resulting byte arrays were exactly 21 bytes long


3. **Error Handling**: The FTSO contracts sometimes return errors or no data. I implemented fallback mechanisms that:
   - Try multiple methods to retrieve data (by symbol, by feed ID, from all feeds)
   - Generate simulated data when real data is unavailable
   - Provide clear error messages and logging


## Key Achievements


1. **Verifiable Knowledge System**: Successfully built a system that provides trustworthy information with transparent confidence assessment.


2. **TEE Integration**: Implemented vTPM attestations that can be verified on-chain through Flare's contracts.


3. **Multi-Source RAG**: Created a RAG system that combines multiple data sources with different trust levels.


4. **FTSO Data Access**: Implemented reliable access to FTSO data feeds with proper error handling and fallback mechanisms.


5. **Trust Transparency**: Made information reliability explicit through detailed trust scores and source attribution.


## Challenges and Solutions


### Challenge 1: TEE Configuration


**Problem**: The TEE environment required specific configuration to support vTPM attestations.


**Solution**: After extensive testing, I found that:
- Using the n2d-standard-2 machine type with AMD SEV provided the best results
- Mounting the /dev/tpm0 device to the container was essential
- Setting specific environment variables helped with attestation generation


### Challenge 2: FTSO Data Access


**Problem**: The FTSO contracts sometimes returned errors or no data, especially on the testnet.


**Solution**: I implemented a multi-layered approach:
1. Try to get data directly from the contract
2. If that fails, try alternative methods (by symbol, by feed ID)
3. If all else fails, generate simulated data based on realistic price models
4. Add clear flags to indicate when data is simulated


### Challenge 3: Contract Verification


**Problem**: The on-chain verification process was complex and required specific parameter formats.


**Solution**: I created a dedicated verification service that:
- Properly formats the attestation parameters
- Handles different verification scenarios
- Provides detailed error messages when verification fails
- Implements a simulated verification mode for testing


### Challenge 4: API Stability


**Problem**: The API sometimes became unresponsive due to long-running operations.


**Solution**: I improved stability by:
- Implementing proper async/await patterns
- Adding timeouts to external calls
- Using background tasks for data collection
- Implementing circuit breakers for failing services


## Future Improvements


While the current system meets all the requirements, there are several areas for future improvement:


1. **Data Sources**: Integrate additional data sources from the Flare ecosystem, such as:
   - More comprehensive blockchain state information
   - Governance proposals and voting data
   - Cross-chain data from wrapped assets


2. **Performance Optimization**: Improve the performance of the RAG system by:
   - Implementing more sophisticated embedding techniques
   - Optimizing the vector search algorithms
   - Adding more granular caching strategies


3. **User Interface**: Develop a web-based interface for easier interaction with the system.


4. **Monitoring and Analytics**: Add comprehensive monitoring and analytics to track:
   - Query patterns and user behavior
   - System performance and resource usage
   - Data quality and trust scores over time


## Conclusion


ChainContext demonstrates the power of combining TEE security with RAG systems for Web3 knowledge. By making trust explicit and verifiable, it addresses the core problems of data fragmentation and LLM hallucinations in the blockchain space.


Building this system was challenging but rewarding. The most valuable lesson was the importance of robust error handling and fallback mechanisms when working with blockchain data. By focusing on reliability and transparency, I was able to create a system that provides trustworthy information even when faced with the inherent volatility of Web3 data sources.


The integration with Flare's vTPM attestation contracts shows how on-chain verification can enhance the trustworthiness of off-chain systems, creating a bridge between traditional cloud infrastructure and blockchain technology. 


