# ChainContext Backend

ChainContext is a verifiable knowledge system that combines real-time FTSO data feeds with comprehensive blockchain state to provide trustworthy answers about Flare's ecosystem, with transparency about each answer's confidence level.

## Overview

This backend implements the core functionality for the ChainContext system, including:

- FTSO data integration
- Trust score calculation
- RAG (Retrieval-Augmented Generation) for answering queries
- TEE (Trusted Execution Environment) for attestations

## Project Structure

```
chaincontext-backend/
├── app/                    # Main application package
│   ├── api/                # API routes
│   ├── core/               # Core functionality (config, db, logging)
│   ├── data/               # Data files (ABIs, etc.)
│   ├── models/             # Data models (Pydantic)
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── .env                    # Environment variables (not in git)
├── .env.example            # Example environment variables
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── run.py                  # Entry point
```

## Requirements

- Python 3.11+
- MongoDB
- Redis
- Qdrant vector database
- Google Gemini API key

## Setup

1. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install uv package manager:
   ```
   pip install uv
   ```

3. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and update the configuration:
   ```
   cp .env.example .env
   ```

5. Set up your Gemini API key in the `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the Server

1. Start the server:
   ```
   python run.py
   ```

2. The API will be available at:
   - API: http://localhost:8000/api
   - Documentation: http://localhost:8000/docs

## Docker Setup

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. The API will be available at http://localhost:8000

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/query` - Submit a natural language query
- `POST /api/verify` - Verify an attestation
- `POST /api/calculate-trust` - Calculate trust score for information
- `GET /api/trust-factors` - Get information about trust factors
- `GET /api/ftso/data` - Get FTSO price data
- `GET /api/ftso/symbols` - Get supported FTSO symbols


## TEE Integration

The system is designed to run in a Trusted Execution Environment (TEE) with vTPM attestations. For local development, the TEE functionality is simulated.

To enable real TEE attestations:
1. Deploy on a Google Cloud Confidential VM with Intel TDX
2. Ensure the TPM device is available at `/dev/tpm0`
3. Deploy the TeeV1Verifier smart contract on Flare
4. Update the `TEE_VERIFIER_ADDRESS` in `.env`

## Project Implementation Notes

- The FTSO data collector integrates with Flare's Time Series Oracle
- The Trust Score system provides transparent confidence assessment
- The RAG system uses Gemini 2.0 Flash for query understanding and answer synthesis
- The TEE attestation provides verifiable proof of execution

## License

This project is developed for the Flare x Google Verifiable AI Hackathon.

# ChainContext API Documentation

This document provides detailed information about the ChainContext API endpoints.

## Base URL

All API requests should be prefixed with the base URL:

```
http://localhost:8000/api
```

## Authentication

Authentication is not required for the hackathon implementation. In a production environment, JWT authentication would be implemented.

## Endpoints

### Health Check

```
GET /health
```

Checks the health and status of the API.

#### Response

```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": 1678912345
}
```

### Query

```
POST /query
```

Submit a natural language query to ChainContext.

#### Request Body

```json
{
  "query": "What is the current status of the Flare network?",
  "user_id": "optional-user-identifier"
}
```

#### Response

```json
{
  "query_id": "a1b2c3d4e5f6g7h8i9j0",
  "query": "What is the current status of the Flare network?",
  "answer": "The Flare network is currently operating normally with average block times of 1.0 seconds. Gas prices are stable at around 25 gwei, and network utilization is at 35% of capacity.",
  "confidence": 0.85,
  "reasoning": "This answer is based on recent blockchain state data that has high trust scores and is verified on-chain.",
  "sources": [
    {
      "text": "The Flare network is currently operating normally with average block times of 1.0 seconds. Gas prices are stable at around 25 gwei, and network utilization is at 35% of capacity.",
      "source": "blockchain_state",
      "source_type": "Blockchain State",
      "trust_score": 0.92,
      "timestamp": 1678912300
    },
    {
      "text": "A planned network upgrade to improve FTSO data distribution is scheduled for next month. This upgrade will reduce response latency and improve the accuracy of price feeds.",
      "source": "twitter_official",
      "source_type": "Official Twitter",
      "trust_score": 0.70,
      "url": "https://twitter.com/FlareNetworks/status/1234567890",
      "timestamp": 1678800000
    }
  ],
  "attestation": {
    "data_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "signature": "base64-signature-data",
    "timestamp": 1678912345,
    "quote": "base64-quote-data",
    "nonce": "hex-nonce-value",
    "simulated": true
  },
  "processing_time": 0.521
}
```

### Verify Attestation

```
POST /verify
```

Verify an attestation from a query response.

#### Request Body

```json
{
  "attestation": {
    "data_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "signature": "base64-signature-data",
    "timestamp": 1678912345,
    "quote": "base64-quote-data",
    "nonce": "hex-nonce-value"
  }
}
```

#### Response

```json
{
  "verified": true,
  "simulated": true,
  "timestamp": 1678912400,
  "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
}
```

### Calculate Trust Score

```
POST /calculate-trust
```

Calculate a trust score for a piece of information.

#### Request Body

```json
{
  "information": {
    "source": "flare_docs",
    "timestamp": 1678900000,
    "content": "The Flare network supports EVM-compatible smart contracts.",
    "onchain_verified": true,
    "cross_verifications": 2
  }
}
```

#### Response

```json
{
  "trust_score": 0.85,
  "factors": {
    "recency": 0.92,
    "source_reliability": 0.85,
    "cross_verification": 0.76,
    "onchain_verification": 0.20,
    "overall_score": 0.85
  }
}
```

### Get Trust Factors

```
GET /trust-factors
```

Get information about the trust factors used in the system.

#### Response

```json
{
  "factors": {
    "recency": {
      "description": "How recent the information is",
      "weight": 0.3
    },
    "source_reliability": {
      "description": "Pre-configured reliability of the source",
      "weight": 0.2
    },
    "cross_verification": {
      "description": "How many sources confirm this information",
      "weight": 0.2
    },
    "onchain_verification": {
      "description": "Whether the information is verifiable on-chain",
      "weight": 0.2
    },
    "base": {
      "description": "Base score for all information",
      "weight": 0.1
    }
  },
  "source_reliability": {
    "ftso_2s": 0.95,
    "ftso_90s": 0.9,
    "blockchain_state": 0.95,
    "flare_docs": 0.85,
    "github_code": 0.8,
    "github_issues": 0.6,
    "twitter_official": 0.7,
    "twitter_community": 0.4
  }
}
```

### Get FTSO Data

```
GET /ftso/data
```

Get current FTSO price data.

#### Query Parameters

- `symbol` (optional): Filter by specific symbol (e.g. "FLR")

#### Response

```json
{
  "data": {
    "FLR": {
      "price": 0.035,
      "timestamp": 1678912340,
      "source": "ftso_2s",
      "symbol": "FLR",
      "decimals": 6
    },
    "BTC": {
      "price": 65420.75,
      "timestamp": 1678912340,
      "source": "ftso_2s",
      "symbol": "BTC",
      "decimals": 6
    }
  },
  "timestamp": 1678912345
}
```

### Get FTSO Symbols

```
GET /ftso/symbols
```

Get supported FTSO symbols.

#### Response

```json
{
  "symbols": ["FLR", "BTC", "ETH", "XRP", "USDC", "USDT", "ALGO", "DOGE", "ADA"],
  "count": 9,
  "timestamp": 1678912345
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200 OK`: The request was successful
- `400 Bad Request`: The request was invalid
- `404 Not Found`: The requested resource was not found
- `500 Internal Server Error`: An error occurred on the server

Error responses include a detail message:

```json
{
  "detail": "Error message explaining what went wrong"
}
```

## Rate Limiting

Rate limiting is not implemented for the hackathon. In a production environment, the API would include rate limiting to prevent abuse.

## Pagination

Pagination is not implemented for the hackathon. In a production environment, endpoints returning multiple results would support pagination.

