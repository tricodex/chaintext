#!/usr/bin/env python3
"""
ChainContext Demo Script

This script provides a guided demonstration of the ChainContext system,
with clear instructions and talking points for each step.

Usage:
    python demo_script.py

The script will guide you through each step of the demo with clear instructions
on what to say and what commands to run.
"""

import os
import sys
import time
import json
import asyncio
import subprocess
from typing import List, Dict, Any, Optional, Tuple
import argparse
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class DemoScript:
    """Demo script for ChainContext"""
    
    def __init__(self):
        """Initialize the demo script"""
        self.step_count = 0
        self.current_section = ""
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, text: str):
        """Print a header with the given text"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 80}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{text.center(80)}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 80}{Style.RESET_ALL}\n")
    
    def print_section(self, text: str):
        """Print a section header with the given text"""
        self.current_section = text
        print(f"\n{Fore.GREEN}{Style.BRIGHT}{text}")
        print(f"{Fore.GREEN}{Style.BRIGHT}{'-' * len(text)}{Style.RESET_ALL}\n")
    
    def print_step(self, text: str):
        """Print a step with the given text"""
        self.step_count += 1
        print(f"{Fore.YELLOW}{Style.BRIGHT}Step {self.step_count}: {text}{Style.RESET_ALL}")
    
    def print_command(self, command: str):
        """Print a command to run"""
        print(f"\n{Fore.MAGENTA}$ {command}{Style.RESET_ALL}")
    
    def print_talking_point(self, text: str):
        """Print a talking point"""
        print(f"\n{Fore.BLUE}📢 {text}{Style.RESET_ALL}")
    
    def print_note(self, text: str):
        """Print a note"""
        print(f"\n{Fore.RED}📝 Note: {text}{Style.RESET_ALL}")
    
    def wait_for_keypress(self):
        """Wait for a keypress to continue"""
        print(f"\n{Fore.WHITE}{Back.BLACK}[Press Enter to continue...]{Style.RESET_ALL}")
        input()
    
    def run_demo(self):
        """Run the demo script"""
        self.clear_screen()
        self.print_header("ChainContext Demo")
        
        print(f"{Fore.WHITE}This script will guide you through demonstrating the ChainContext system.")
        print(f"{Fore.WHITE}Follow the instructions and talking points for each step.")
        print(f"{Fore.WHITE}Press Enter to advance to the next step.")
        
        self.wait_for_keypress()
        
        # Introduction
        self.clear_screen()
        self.print_section("1. Introduction")
        
        self.print_step("Introduce the project")
        self.print_talking_point("Welcome to the demonstration of ChainContext, a verifiable knowledge system for the Flare ecosystem.")
        self.print_talking_point("ChainContext combines real-time FTSO data feeds with blockchain state information to provide trustworthy answers with transparent confidence assessment.")
        self.print_talking_point("The system runs in a Trusted Execution Environment (TEE) and provides cryptographic proof of secure execution through vTPM attestations.")
        
        self.wait_for_keypress()
        
        # System Architecture
        self.clear_screen()
        self.print_section("2. System Architecture")
        
        self.print_step("Explain the system architecture")
        self.print_talking_point("ChainContext consists of several key components:")
        self.print_talking_point("1. Data Ingestion Pipeline: Collects data from FTSO feeds, blockchain state, documentation, and social media.")
        self.print_talking_point("2. Trust Scoring Mechanism: Assigns trust scores based on source reliability, recency, and cross-verification.")
        self.print_talking_point("3. TEE Security: Runs in a Google Cloud Confidential VM with vTPM attestations.")
        self.print_talking_point("4. RAG System: Combines trusted data with Gemini 2.0 Flash for accurate responses.")
        self.print_talking_point("5. API Interface: Provides endpoints for queries, FTSO data access, and attestation verification.")
        
        self.wait_for_keypress()
        
        # Verify Services
        self.clear_screen()
        self.print_section("3. Verify Services")
        
        self.print_step("Check that all services are running")
        self.print_command("docker-compose ps")
        self.print_talking_point("As you can see, all our services are up and running:")
        self.print_talking_point("- API service: Handles requests and coordinates other services")
        self.print_talking_point("- MongoDB: Stores structured data and query history")
        self.print_talking_point("- Redis: Caches frequently accessed data and embeddings")
        self.print_talking_point("- Qdrant: Vector database for semantic search")
        
        self.wait_for_keypress()
        
        # Health Check
        self.clear_screen()
        self.print_section("4. Health Check")
        
        self.print_step("Check the health of the API")
        self.print_command("curl -s http://localhost:8000/api/health | jq")
        self.print_talking_point("The health endpoint confirms that our API is operational.")
        self.print_talking_point("This endpoint is used by monitoring systems to check the status of the service.")
        
        self.wait_for_keypress()
        
        # FTSO Data Access
        self.clear_screen()
        self.print_section("5. FTSO Data Access")
        
        self.print_step("Check available FTSO symbols")
        self.print_command("curl -s http://localhost:8000/api/ftso/testnet/symbols | jq")
        self.print_talking_point("ChainContext integrates with Flare's FTSO system to provide price data for various cryptocurrencies.")
        self.print_talking_point("Here we can see all the supported symbols, including FLR, BTC, ETH, and others.")
        
        self.wait_for_keypress()
        
        self.print_step("Get price data for Bitcoin")
        self.print_command("curl -s http://localhost:8000/api/ftso/testnet/price/BTC | jq")
        self.print_talking_point("We can retrieve the current price of Bitcoin from the FTSO system.")
        self.print_talking_point("The system automatically handles the conversion between different symbol formats and provides the latest price data.")
        
        self.wait_for_keypress()
        
        self.print_step("Get detailed data for Ethereum")
        self.print_command("curl -s http://localhost:8000/api/ftso/testnet/data/ETH | jq")
        self.print_talking_point("For more detailed information, we can use the data endpoint.")
        self.print_talking_point("This provides not just the price, but also additional metadata like decimals, timestamp, and feed ID.")
        self.print_talking_point("Notice the 'simulated' flag, which indicates whether the data comes directly from the blockchain or is generated by our fallback system.")
        
        self.wait_for_keypress()
        
        # Natural Language Queries
        self.clear_screen()
        self.print_section("6. Natural Language Queries")
        
        self.print_step("Submit a natural language query")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"query\": \"What is the current price of FLR?\"}' http://localhost:8000/api/query | jq")
        self.print_talking_point("ChainContext's core functionality is answering natural language queries about the Flare ecosystem.")
        self.print_talking_point("The response includes:")
        self.print_talking_point("1. The answer to the query")
        self.print_talking_point("2. A confidence score indicating the system's certainty")
        self.print_talking_point("3. Sources with their trust scores, showing transparency in information sourcing")
        self.print_talking_point("4. Attestation information that proves the answer was generated in a secure environment")
        
        self.wait_for_keypress()
        
        self.print_step("Submit a more complex query")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"query\": \"How do FTSO data feeds work on Flare?\"}' http://localhost:8000/api/query | jq")
        self.print_talking_point("For more complex queries, ChainContext combines information from multiple sources.")
        self.print_talking_point("The system prioritizes information based on source reliability, recency, and cross-verification.")
        self.print_talking_point("This ensures that the answers are not only accurate but also transparent about their trustworthiness.")
        
        self.wait_for_keypress()
        
        # Trust Scoring
        self.clear_screen()
        self.print_section("7. Trust Scoring")
        
        self.print_step("Examine the trust scoring system")
        self.print_command("curl -s http://localhost:8000/api/trust-factors | jq")
        self.print_talking_point("ChainContext assigns trust scores to information based on multiple factors:")
        self.print_talking_point("- Source reliability: Blockchain state is more trusted than social media")
        self.print_talking_point("- Information recency: Newer data is more trusted")
        self.print_talking_point("- Cross-verification: Information confirmed by multiple sources gets higher trust")
        self.print_talking_point("- On-chain verification: Verified information gets higher trust")
        self.print_talking_point("This makes the trustworthiness of information explicit and transparent.")
        
        self.wait_for_keypress()
        
        # vTPM Attestation
        self.clear_screen()
        self.print_section("8. vTPM Attestation")
        
        self.print_step("Test vTPM attestation")
        self.print_command("source .venv/bin/activate && python test_vTPM.py")
        self.print_talking_point("One of the key features of ChainContext is its use of Trusted Execution Environments (TEEs) with vTPM attestations.")
        self.print_talking_point("The system runs in a Google Cloud Confidential VM with AMD SEV for hardware-level security.")
        self.print_talking_point("The vTPM generates cryptographic attestations that prove the system's integrity.")
        self.print_talking_point("These attestations can be verified on-chain through Flare's vTPM Attestation contract.")
        self.print_talking_point("The attestation includes information about the hardware model, software environment, and container image digest.")
        self.print_talking_point("This ensures that the system is running in a secure environment with the expected configuration.")
        
        self.wait_for_keypress()
        
        # FTSO Testnet Data Collector
        self.clear_screen()
        self.print_section("9. FTSO Testnet Data Collector")
        
        self.print_step("Test FTSO testnet data collector")
        self.print_command("source .venv/bin/activate && python test_ftso_testnet.py")
        self.print_talking_point("ChainContext includes a dedicated collector for FTSO data from the Flare testnet.")
        self.print_talking_point("This collector handles the complexities of interacting with the FTSO contracts.")
        self.print_talking_point("It includes fallback mechanisms for when the network is unavailable or returns errors.")
        self.print_talking_point("The system can retrieve data by symbol, by feed ID, or collect all feeds at once.")
        self.print_talking_point("When real data is unavailable, it generates simulated data based on realistic price models.")
        self.print_talking_point("This ensures that the system always provides a response, even in challenging network conditions.")
        
        self.wait_for_keypress()
        
        # Conclusion
        self.clear_screen()
        self.print_section("10. Conclusion")
        
        self.print_step("Summarize the demonstration")
        self.print_talking_point("In this demonstration, we've seen how ChainContext provides:")
        self.print_talking_point("1. Verifiable knowledge through TEE attestations")
        self.print_talking_point("2. Transparent trust scoring for information reliability")
        self.print_talking_point("3. Integration with Flare's FTSO system for real-time price data")
        self.print_talking_point("4. Natural language query capabilities with source attribution")
        self.print_talking_point("5. Robust error handling and fallback mechanisms")
        self.print_talking_point("ChainContext addresses the core problems of data fragmentation and LLM hallucinations in the blockchain space.")
        self.print_talking_point("By making trust explicit and verifiable, it provides a foundation for trustworthy AI in the Flare ecosystem.")
        
        self.wait_for_keypress()
        
        # End
        self.clear_screen()
        self.print_header("Demo Complete")
        print(f"{Fore.WHITE}Thank you for watching the ChainContext demonstration.")
        print(f"{Fore.WHITE}For more information, please refer to the documentation and the submission.md file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ChainContext Demo Script")
    args = parser.parse_args()
    
    demo = DemoScript()
    demo.run_demo() 