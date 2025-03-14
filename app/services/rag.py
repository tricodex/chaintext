import json
import hashlib
import time
from typing import Dict, List, Any, Optional
import asyncio
from loguru import logger
import numpy as np

from app.core.config import settings
from app.core.genai import gemini_client
from app.services.trust import TrustScoreCalculator
from app.services.tee import TEEAttestationGenerator

class EmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(self, redis_client=None):
        """Initialize the embedding service"""
        self.redis = redis_client
        logger.info("Initialized Embedding Service")
    
    async def set_redis_client(self, redis_client):
        """Set Redis client after initialization"""
        self.redis = redis_client
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using Gemini embeddings model"""
        if not text:
            return [0.0] * 768  # Return zero vector for empty text
            
        try:
            # Check cache first if Redis is available
            if self.redis:
                cache_key = f"embedding:{hashlib.md5(text.encode()).hexdigest()}"
                cached = await self.redis.get(cache_key)
                
                if cached:
                    return json.loads(cached)
            
            # Generate embedding using Gemini
            embedding = await gemini_client.embed_text(text)
            
            # Cache the result if Redis is available
            if self.redis and embedding:
                await self.redis.set(
                    cache_key, 
                    json.dumps(embedding), 
                    ex=86400  # 24 hour cache
                )
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return zero vector on error
            return [0.0] * 768
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch"""
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
            
        a = np.array(embedding1)
        b = np.array(embedding2)
        
        # Handle zero vectors
        if np.all(a == 0) or np.all(b == 0):
            return 0.0
            
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class ChainContextRAG:
    """Retrieval-Augmented Generation with Trust Scores"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        trust_calculator: TrustScoreCalculator,
        tee_attestation: TEEAttestationGenerator,
        mongodb=None,
        qdrant_client=None,
        redis_client=None
    ):
        """Initialize the RAG service"""
        self.embedding_service = embedding_service
        self.trust_calculator = trust_calculator
        self.tee_attestation = tee_attestation
        self.mongodb = mongodb
        self.qdrant_client = qdrant_client
        self.redis = redis_client
        
        logger.info("Initialized ChainContext RAG service")
    
    async def set_db_clients(self, mongodb, qdrant_client, redis_client):
        """Set database clients after initialization"""
        self.mongodb = mongodb
        self.qdrant_client = qdrant_client
        self.redis = redis_client
        await self.embedding_service.set_redis_client(redis_client)
    
    async def answer_query(self, query: str, user_id: Optional[str] = None) -> Dict:
        """
        Answer a query using RAG with trust scores
        
        Args:
            query: The user's query
            user_id: Optional user identifier for tracking
            
        Returns:
            A response object with answer, confidence, sources, and attestation
        """
        query_id = hashlib.md5(f"{query}-{time.time()}".encode()).hexdigest()
        logger.info(f"Processing query: {query} (ID: {query_id})")
        
        try:
            start_time = time.time()
            
            # Generate embedding for the query
            query_embedding = await self.embedding_service.embed_text(query)
            
            # For the hackathon, we'll simulate retrieving context
            # In a real implementation, we would search the vector database
            context_results = await self._retrieve_simulated_context(query, query_embedding)
            
            # Calculate trust scores for each context piece
            context_with_trust = []
            for result in context_results:
                trust_score = self.trust_calculator.calculate_trust_score(result)
                context_with_trust.append({
                    "id": result.get("id", hashlib.md5(result["content"].encode()).hexdigest()),
                    "text": result["content"],
                    "source": result["source"],
                    "timestamp": result["timestamp"],
                    "trust_score": trust_score,
                    "url": result.get("url", "")
                })
            
            # Sort and filter by trust score
            high_trust_context = [c for c in context_with_trust if c["trust_score"] > 0.6]
            medium_trust_context = [c for c in context_with_trust if 0.4 <= c["trust_score"] <= 0.6]
            low_trust_context = [c for c in context_with_trust if c["trust_score"] < 0.4]
            
            # Build prompt with trust-weighted context
            prompt = self._build_prompt(query, high_trust_context, medium_trust_context, low_trust_context)
            
            # Generate answer with Gemini
            response = await self._generate_answer(prompt)
            
            # Generate attestation for the response
            attestation = await self.tee_attestation.generate_attestation(
                query, context_with_trust, response
            )
            
            # Create the final response object
            result = {
                "query_id": query_id,
                "query": query,
                "answer": response["answer"],
                "confidence": response["confidence"],
                "reasoning": response.get("reasoning", ""),
                "sources": self._format_sources(context_with_trust),
                "attestation": attestation,
                "processing_time": time.time() - start_time
            }
            
            # Save query and result to database if MongoDB is available
            if self.mongodb:
                await (await self.mongodb.queries).insert_one({
                    "query_id": query_id,
                    "query": query,
                    "user_id": user_id,
                    "result": result,
                    "timestamp": int(time.time())
                })
            
            logger.info(f"Completed query {query_id} in {result['processing_time']:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return {
                "query_id": query_id,
                "query": query,
                "answer": "I encountered an error while processing your query. Please try again later.",
                "confidence": 0.0,
                "sources": [],
                "attestation": {},
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    async def _retrieve_simulated_context(self, query: str, query_embedding: List[float]) -> List[Dict]:
        """
        Simulate context retrieval for the hackathon
        In a real implementation, this would search the vector database
        
        Args:
            query: The user's query
            query_embedding: The embedding of the query
            
        Returns:
            A list of context documents
        """
        # For the hackathon, we'll return simulated context based on the query
        contexts = []
        current_time = int(time.time())
        
        # Simulate different types of content based on query keywords
        query_lower = query.lower()
        
        # FTSO-related context
        if any(word in query_lower for word in ["ftso", "price", "feed", "data"]):
            contexts.append({
                "id": "ftso-overview",
                "content": "The Flare Time Series Oracle (FTSO) is a decentralized data provisioning system that provides reliable, secure, and timely price feeds for various cryptocurrency pairs. It uses a delegated proof of stake mechanism where data providers submit price estimates, and a time-weighted median is used to determine the final price.",
                "source": "flare_docs",
                "timestamp": current_time - 3600 * 24 * 2,  # 2 days ago
                "url": "https://docs.flare.network/tech/ftso/"
            })
            contexts.append({
                "id": "ftso-2s-feed",
                "content": "FTSO 2-second feeds provide near real-time price data for use in DeFi applications. These feeds have minimal latency but may occasionally include outliers during periods of high volatility.",
                "source": "ftso_2s",
                "timestamp": current_time - 60,  # 1 minute ago
                "onchain_verified": True
            })
            contexts.append({
                "id": "ftso-90s-feed",
                "content": "FTSO 90-second feeds provide anchor price data that is more stable than the 2-second feeds. These anchor feeds use time-weighted medians over a longer period and are less susceptible to short-term price manipulation.",
                "source": "ftso_90s",
                "timestamp": current_time - 360,  # 6 minutes ago
                "onchain_verified": True
            })
        
        # Network status context
        if any(word in query_lower for word in ["network", "status", "blockchain", "block"]):
            contexts.append({
                "id": "flare-network-status",
                "content": "The Flare network is currently operating normally with average block times of 1.0 seconds. Gas prices are stable at around 25 gwei, and network utilization is at 35% of capacity.",
                "source": "blockchain_state",
                "timestamp": current_time - 120,  # 2 minutes ago
                "onchain_verified": True
            })
            contexts.append({
                "id": "flare-network-upgrade",
                "content": "A planned network upgrade to improve FTSO data distribution is scheduled for next month. This upgrade will reduce response latency and improve the accuracy of price feeds.",
                "source": "twitter_official",
                "timestamp": current_time - 3600 * 24 * 5,  # 5 days ago
                "url": "https://twitter.com/FlareNetworks/status/1234567890"
            })
        
        # General Flare information
        contexts.append({
            "id": "flare-overview",
            "content": "Flare is a blockchain specifically designed to support data intensive use cases, including Machine Learning/AI, RWA tokenization, gaming and social. With decentralized oracles enshrined in the network, Flare is the only smart contract platform optimized for decentralized data acquisition.",
            "source": "flare_docs",
            "timestamp": current_time - 3600 * 24 * 30,  # 30 days ago
            "url": "https://docs.flare.network/tech/flare/"
        })
        
        # Add some tweets based on query
        if "community" in query_lower or "social" in query_lower:
            contexts.append({
                "id": "community-tweet-1",
                "content": "The Flare community is growing rapidly! Just crossed 100,000 active wallets on the network. #FlareNetwork #Blockchain",
                "source": "twitter_community",
                "timestamp": current_time - 3600 * 24 * 3,  # 3 days ago
                "url": "https://twitter.com/FlareUser123/status/1234567891"
            })
            contexts.append({
                "id": "community-tweet-2",
                "content": "Having some issues with FTSO delegation today. Anyone else experiencing longer confirmation times?",
                "source": "twitter_community",
                "timestamp": current_time - 3600 * 2,  # 2 hours ago
                "url": "https://twitter.com/FlareUser456/status/1234567892"
            })
        
        # Add GitHub content if relevant
        if "code" in query_lower or "developer" in query_lower or "github" in query_lower:
            contexts.append({
                "id": "github-code-example",
                "content": "// Example for querying FTSO prices from a smart contract\nfunction getFTSOPrice(string memory symbol) public view returns (uint256) {\n    return IFTSORegistry(ftsoRegistry).getCurrentPrice(symbol);\n}",
                "source": "github_code",
                "timestamp": current_time - 3600 * 24 * 14,  # 14 days ago
                "url": "https://github.com/flare-foundation/examples/blob/main/ftso.sol"
            })
            contexts.append({
                "id": "github-issue",
                "content": "Issue #123: FTSO delegation returns incorrect rewards calculation in specific edge cases. This occurs when a delegation is split across multiple data providers and one provider misses a submission window.",
                "source": "github_issues",
                "timestamp": current_time - 3600 * 24 * 10,  # 10 days ago
                "url": "https://github.com/flare-foundation/flare/issues/123"
            })
        
        # Filter to most relevant (would normally use vector search here)
        # For simplicity, we'll return all contexts for the hackathon
        return contexts
    
    def _build_prompt(
        self, 
        query: str, 
        high_trust_context: List[Dict], 
        medium_trust_context: List[Dict],
        low_trust_context: List[Dict] = None
    ) -> str:
        """
        Build a prompt for Gemini 2.0 Flash with trust-weighted context
        
        Gemini 2.0 Flash has a 1M token context window, allowing us to include
        significantly more context than previous models. This implementation
        takes advantage of this larger context window for improved answers.
        
        Args:
            query: The user's query
            high_trust_context: Context with high trust scores (>0.6)
            medium_trust_context: Context with medium trust scores (0.4-0.6)
            low_trust_context: Context with low trust scores (<0.4)
            
        Returns:
            A structured prompt for the Gemini model
        """
        prompt = f"""You are ChainContext, a knowledgeable assistant specializing in the Flare blockchain ecosystem.
        
Answer the following query based on the provided context information.
Each piece of context has a trust score (0-1) indicating its reliability.

QUERY: {query}

HIGHLY TRUSTED CONTEXT (Trust Score > 0.6):
"""
        
        # Add high trust context
        if high_trust_context:
            for i, ctx in enumerate(high_trust_context):
                prompt += f"\n[{i+1}] Source: {ctx['source']} (Trust: {ctx['trust_score']:.2f})\n{ctx['text']}\n"
        else:
            prompt += "\nNo highly trusted context available.\n"
        
        if medium_trust_context:
            prompt += "\nMEDIUM TRUSTED CONTEXT (Trust Score 0.4-0.6):\n"
            
            # Add medium trust context
            for i, ctx in enumerate(medium_trust_context):
                prompt += f"\n[{i+1}] Source: {ctx['source']} (Trust: {ctx['trust_score']:.2f})\n{ctx['text']}\n"
        
        if low_trust_context:
            prompt += "\nLOW TRUSTED CONTEXT (Trust Score < 0.4) - Use with caution:\n"
            
            # Add low trust context
            for i, ctx in enumerate(low_trust_context):
                prompt += f"\n[{i+1}] Source: {ctx['source']} (Trust: {ctx['trust_score']:.2f})\n{ctx['text']}\n"
        
        prompt += """
INSTRUCTIONS:
1. Answer the query using only the provided context.
2. Prioritize information from highly trusted sources.
3. If there are conflicts, explain them and favor higher trust sources.
4. If the context doesn't contain relevant information, state that you don't have sufficient information.
5. Include a confidence assessment in your answer based on the trust scores and completeness of information.
6. Format your answer in JSON with the following structure:
{
  "answer": "Your comprehensive answer goes here",
  "confidence": 0.85, // A number between 0 and 1
  "reasoning": "Brief explanation of how you determined the answer and confidence"
}
"""
        
        return prompt
    
    async def _generate_answer(self, prompt: str) -> Dict:
        """
        Generate answer using Gemini 2.0 Flash
        
        Uses Gemini 2.0 Flash which supports a 1M token context window,
        allowing us to process much more context than previously possible.
        This is particularly valuable for blockchain data which often requires
        integrating information from multiple sources with varying trust levels.
        
        Args:
            prompt: The structured prompt with context
            
        Returns:
            A structured response with answer, confidence, and reasoning
        """
        try:
            # Use system instruction to improve formatting
            system_instruction = "You are ChainContext, a verifiable knowledge system for the Flare blockchain. Always return JSON responses as requested in the user's prompt."
            
            # Generate response with Gemini
            result = await gemini_client.generate_structured_content(
                prompt=prompt,
                schema={
                    "answer": "string",
                    "confidence": "number",
                    "reasoning": "string"
                },
                system_instruction=system_instruction
            )
            
            if result["success"] and result["data"]:
                # Validate the structure of the data
                data = result["data"]
                
                # Ensure required fields are present and of the correct type
                if not isinstance(data.get("answer"), str):
                    data["answer"] = str(data.get("answer", "")) or "No answer provided"
                    
                if not isinstance(data.get("confidence"), (int, float)):
                    try:
                        data["confidence"] = float(data.get("confidence", 0.5))
                    except (ValueError, TypeError):
                        data["confidence"] = 0.5
                        
                # Ensure confidence is between 0 and 1
                data["confidence"] = max(0.0, min(1.0, data["confidence"]))
                
                # Ensure reasoning is a string
                if not isinstance(data.get("reasoning"), str):
                    data["reasoning"] = str(data.get("reasoning", "")) or "No reasoning provided"
                    
                return data
            else:
                # Parse the response manually if structured generation failed
                try:
                    text_response = result.get("text", "")
                    logger.warning(f"Failed to get structured response, trying to parse from text: {text_response[:100]}...")
                    
                    # Try to find JSON block
                    if "```json" in text_response:
                        json_text = text_response.split("```json")[1].split("```")[0].strip()
                        logger.debug("Found JSON code block with explicit json tag")
                    elif "```" in text_response:
                        json_text = text_response.split("```")[1].strip()
                        logger.debug("Found JSON in code block")
                    else:
                        # Try to extract JSON by looking for surrounding braces
                        start_idx = text_response.find('{')
                        end_idx = text_response.rfind('}') + 1
                        
                        if start_idx >= 0 and end_idx > start_idx:
                            json_text = text_response[start_idx:end_idx]
                            logger.debug("Extracted JSON using brace detection")
                        else:
                            json_text = text_response
                            logger.debug("Using raw text as JSON")
                    
                    # Try to parse the JSON
                    parsed_json = json.loads(json_text)
                    
                    # Apply the same validation as above
                    if not isinstance(parsed_json.get("answer"), str):
                        parsed_json["answer"] = str(parsed_json.get("answer", "")) or "No answer provided"
                        
                    if not isinstance(parsed_json.get("confidence"), (int, float)):
                        parsed_json["confidence"] = 0.5
                    else:
                        parsed_json["confidence"] = max(0.0, min(1.0, parsed_json["confidence"]))
                        
                    if not isinstance(parsed_json.get("reasoning"), str):
                        parsed_json["reasoning"] = str(parsed_json.get("reasoning", "")) or "No reasoning provided"
                    
                    return parsed_json
                except Exception as parse_error:
                    logger.error(f"Error parsing Gemini response: {parse_error}")
                    # Return a fallback response using the text if available
                    answer_text = text_response
                    if len(answer_text) > 500:
                        # If the text is very long, use just the first part
                        answer_text = answer_text[:500] + "..."
                        
                    return {
                        "answer": answer_text or "I couldn't generate a structured answer. Please try rephrasing your question.",
                        "confidence": 0.4,
                        "reasoning": "The response could not be structured as JSON."
                    }
        except Exception as e:
            logger.error(f"Error generating answer with Gemini: {e}")
            return {
                "answer": "I encountered an error while generating an answer. This could be due to API limits or connectivity issues. Please try again later.",
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}"
            }
    
    def _format_sources(self, context_with_trust: List[Dict]) -> List[Dict]:
        """
        Format sources for the response
        
        Args:
            context_with_trust: Context items with trust scores
            
        Returns:
            A formatted list of sources for the response
        """
        # Sort by trust score
        sorted_context = sorted(context_with_trust, key=lambda x: x["trust_score"], reverse=True)
        
        # Format for response
        sources = []
        for ctx in sorted_context:
            source_type = self._format_source_type(ctx["source"])
            
            sources.append({
                "text": ctx["text"][:200] + "..." if len(ctx["text"]) > 200 else ctx["text"],
                "source": ctx["source"],
                "source_type": source_type,
                "trust_score": ctx["trust_score"],
                "url": ctx.get("url", ""),
                "timestamp": ctx.get("timestamp", 0)
            })
        
        return sources
    
    def _format_source_type(self, source: str) -> str:
        """Format source type for display"""
        source_types = {
            "ftso_2s": "FTSO 2s Data",
            "ftso_90s": "FTSO 90s Data",
            "blockchain_state": "Blockchain State",
            "flare_docs": "Flare Documentation",
            "github_code": "GitHub Code",
            "github_issues": "GitHub Issues",
            "twitter_official": "Official Twitter",
            "twitter_community": "Community Twitter"
        }
        
        return source_types.get(source, source.replace("_", " ").title())
