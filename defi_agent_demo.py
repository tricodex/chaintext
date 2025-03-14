#!/usr/bin/env python3
"""
AI x DeFi (DeFAI) Demo Script

This script provides a guided demonstration of the AI x DeFi system,
with clear instructions and talking points for each step.

Usage:
    python defi_agent_demo.py

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
    """Demo script for AI x DeFi (DeFAI)"""
    
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
        self.print_header("AI x DeFi (DeFAI) Demo")
        
        print(f"{Fore.WHITE}This script will guide you through demonstrating the AI x DeFi system.")
        print(f"{Fore.WHITE}Follow the instructions and talking points for each step.")
        print(f"{Fore.WHITE}Press Enter to advance to the next step.")
        
        self.wait_for_keypress()
        
        # Introduction
        self.clear_screen()
        self.print_section("1. Introduction")
        
        self.print_step("Introduce the project")
        self.print_talking_point("Welcome to the demonstration of our AI x DeFi (DeFAI) system, a production-ready autonomous AI agent for the Flare ecosystem.")
        self.print_talking_point("This agent transforms imperative commands into declarative blockchain instructions, enabling multimodal blockchain interaction methods.")
        self.print_talking_point("The key innovation is reducing the knowledge burden on end users to understand and execute safe on-chain interactions.")
        
        self.wait_for_keypress()
        
        # System Architecture
        self.clear_screen()
        self.print_section("2. System Architecture")
        
        self.print_step("Explain the system architecture")
        self.print_talking_point("Our DeFAI system consists of several key components:")
        self.print_talking_point("1. TEE Security Layer: Runs in a Google Cloud Confidential VM with vTPM attestations.")
        self.print_talking_point("2. Natural Language Processing: Interprets user commands and translates them to blockchain operations.")
        self.print_talking_point("3. Secure Wallet Management: Handles key storage and transaction signing in a secure enclave.")
        self.print_talking_point("4. Risk Assessment Engine: Evaluates transactions for potential risks before execution.")
        self.print_talking_point("5. DeFi Protocol Integrations: Connects with Flare ecosystem applications like SparkDEX and Cyclo.")
        self.print_talking_point("6. Attestation System: Provides cryptographic proof that the agent is operating securely.")
        
        self.wait_for_keypress()
        
        # Verify Services
        self.clear_screen()
        self.print_section("3. Verify Services")
        
        self.print_step("Check that all services are running")
        self.print_command("docker-compose ps")
        self.print_talking_point("As you can see, all our services are up and running:")
        self.print_talking_point("- API service: Handles requests and coordinates other services")
        self.print_talking_point("- MongoDB: Stores transaction history and user preferences")
        self.print_talking_point("- Redis: Caches frequently accessed data and protocol ABIs")
        self.print_talking_point("- Qdrant: Vector database for semantic search of DeFi operations")
        self.print_talking_point("- DeFi Agent: The main service that processes user commands and executes transactions")
        
        self.wait_for_keypress()
        
        # Health Check
        self.clear_screen()
        self.print_section("4. Health Check")
        
        self.print_step("Check the health of the API")
        self.print_command("curl -s http://localhost:8000/api/health | jq")
        self.print_talking_point("The health endpoint confirms that our API is operational.")
        self.print_talking_point("This endpoint is used by monitoring systems to check the status of the service.")
        
        self.wait_for_keypress()
        
        # Wallet Management
        self.clear_screen()
        self.print_section("5. Wallet Management")
        
        self.print_step("Demonstrate secure wallet management")
        self.print_command("curl -s http://localhost:8000/api/defi/wallet-status | jq")
        self.print_talking_point("Our system includes secure wallet management capabilities.")
        self.print_talking_point("The wallet is managed entirely within the TEE, ensuring that private keys never leave the secure environment.")
        self.print_talking_point("We can see the current wallet status, including:")
        self.print_talking_point("1. The wallet address (public information)")
        self.print_talking_point("2. Current balances of various tokens")
        self.print_talking_point("3. Transaction history")
        self.print_talking_point("4. Connected DeFi protocols")
        
        self.wait_for_keypress()
        
        # Natural Language Interface
        self.clear_screen()
        self.print_section("6. Natural Language Interface")
        
        self.print_step("Process a natural language command")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"command\": \"Swap 10 FLR for ETH on SparkDEX\"}' http://localhost:8000/api/defi/process-command | jq")
        self.print_talking_point("The core of our system is the natural language interface for DeFi operations.")
        self.print_talking_point("Users can express their intent in plain English, and the system will:")
        self.print_talking_point("1. Parse the command to identify the operation type (swap, provide liquidity, etc.)")
        self.print_talking_point("2. Extract relevant parameters (token amounts, protocols, etc.)")
        self.print_talking_point("3. Translate this into a structured transaction")
        self.print_talking_point("4. Perform risk assessment before execution")
        self.print_talking_point("5. Present a confirmation with clear explanations of what will happen")
        
        self.wait_for_keypress()
        
        # SparkDEX Integration
        self.clear_screen()
        self.print_section("7. SparkDEX Integration")
        
        self.print_step("Demonstrate SparkDEX integration")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"command\": \"What is the current liquidity of FLR/ETH pair on SparkDEX?\"}' http://localhost:8000/api/defi/process-command | jq")
        self.print_talking_point("Our system integrates with SparkDEX, a decentralized exchange on the Flare network.")
        self.print_talking_point("Users can query information about trading pairs, liquidity pools, and perform trades.")
        self.print_talking_point("The system handles all the complexities of interacting with the SparkDEX contracts, including:")
        self.print_talking_point("1. Fetching current prices and liquidity information")
        self.print_talking_point("2. Calculating optimal swap routes")
        self.print_talking_point("3. Estimating gas costs and slippage")
        self.print_talking_point("4. Executing trades with appropriate parameters")
        
        self.wait_for_keypress()
        
        # Cyclo Integration
        self.clear_screen()
        self.print_section("8. Cyclo Integration")
        
        self.print_step("Demonstrate Cyclo integration")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"command\": \"What is my current position in Cyclo?\"}' http://localhost:8000/api/defi/process-command | jq")
        self.print_talking_point("Our system also integrates with Cyclo, a lending and borrowing protocol on Flare.")
        self.print_talking_point("Users can check their positions, supply assets, borrow against collateral, and repay loans.")
        self.print_talking_point("The system simplifies these complex operations by:")
        self.print_talking_point("1. Tracking user positions across multiple markets")
        self.print_talking_point("2. Monitoring health factors to prevent liquidations")
        self.print_talking_point("3. Suggesting optimal strategies based on current rates")
        self.print_talking_point("4. Executing transactions with appropriate safety margins")
        
        self.wait_for_keypress()
        
        # Risk Assessment
        self.clear_screen()
        self.print_section("9. Risk Assessment")
        
        self.print_step("Demonstrate risk assessment")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"command\": \"Swap all my FLR for ETH on SparkDEX\"}' http://localhost:8000/api/defi/process-command | jq")
        self.print_talking_point("A critical component of our system is the risk assessment engine.")
        self.print_talking_point("Before executing any transaction, the system evaluates potential risks, including:")
        self.print_talking_point("1. Slippage and price impact analysis")
        self.print_talking_point("2. Smart contract security considerations")
        self.print_talking_point("3. Portfolio concentration risks")
        self.print_talking_point("4. Unusual transaction patterns")
        self.print_talking_point("In this example, the system flagged the 'swap all' command as high risk due to portfolio concentration concerns.")
        self.print_talking_point("It suggests alternatives like swapping a specific amount or percentage instead.")
        
        self.wait_for_keypress()
        
        # Transaction Execution
        self.clear_screen()
        self.print_section("10. Transaction Execution")
        
        self.print_step("Execute a transaction")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"command\": \"Swap 5 FLR for ETH on SparkDEX\", \"confirm\": true}' http://localhost:8000/api/defi/execute-transaction | jq")
        self.print_talking_point("Once a command passes risk assessment, the system can execute the transaction.")
        self.print_talking_point("The execution process includes:")
        self.print_talking_point("1. Building the transaction with appropriate parameters")
        self.print_talking_point("2. Signing the transaction within the TEE")
        self.print_talking_point("3. Broadcasting the transaction to the network")
        self.print_talking_point("4. Monitoring for confirmation")
        self.print_talking_point("5. Updating the user's portfolio and transaction history")
        self.print_talking_point("All of this happens securely within the TEE, with attestations proving the integrity of the process.")
        
        self.wait_for_keypress()
        
        # vTPM Attestation
        self.clear_screen()
        self.print_section("11. vTPM Attestation")
        
        self.print_step("Test vTPM attestation")
        self.print_command("source .venv/bin/activate && python test_vTPM.py")
        self.print_talking_point("One of the key features of our DeFAI system is its use of Trusted Execution Environments (TEEs) with vTPM attestations.")
        self.print_talking_point("The system runs in a Google Cloud Confidential VM with AMD SEV for hardware-level security.")
        self.print_talking_point("The vTPM generates cryptographic attestations that prove the system's integrity.")
        self.print_talking_point("These attestations can be verified on-chain through Flare's vTPM Attestation contract.")
        self.print_talking_point("This ensures that the system is operating in a secure environment with the expected configuration.")
        self.print_talking_point("Most importantly, it provides verifiable proof that user funds and private keys are handled securely.")
        
        self.wait_for_keypress()
        
        # Multimodal Interaction
        self.clear_screen()
        self.print_section("12. Multimodal Interaction")
        
        self.print_step("Demonstrate multimodal interaction")
        self.print_command("python test_multimodal.py")
        self.print_talking_point("Our system supports multimodal interaction methods beyond just text commands.")
        self.print_talking_point("Users can interact with the system through:")
        self.print_talking_point("1. Voice commands (processed through speech-to-text)")
        self.print_talking_point("2. QR code scanning for address input")
        self.print_talking_point("3. Image recognition for token identification")
        self.print_talking_point("4. Interactive charts for visual decision-making")
        self.print_talking_point("This makes DeFi more accessible to users with different preferences and abilities.")
        
        self.wait_for_keypress()
        
        # Conclusion
        self.clear_screen()
        self.print_section("13. Conclusion")
        
        self.print_step("Summarize the demonstration")
        self.print_talking_point("In this demonstration, we've seen how our DeFAI system provides:")
        self.print_talking_point("1. Secure wallet management within a TEE")
        self.print_talking_point("2. Natural language processing for DeFi operations")
        self.print_talking_point("3. Integration with multiple Flare ecosystem applications")
        self.print_talking_point("4. Comprehensive risk assessment for user protection")
        self.print_talking_point("5. Multimodal interaction methods for accessibility")
        self.print_talking_point("Our DeFAI system addresses the core problem of high knowledge barriers in DeFi.")
        self.print_talking_point("By leveraging TEEs and natural language processing, we make complex DeFi operations accessible to everyone while maintaining the highest security standards.")
        
        self.wait_for_keypress()
        
        # End
        self.clear_screen()
        self.print_header("Demo Complete")
        print(f"{Fore.WHITE}Thank you for watching the AI x DeFi (DeFAI) demonstration.")
        print(f"{Fore.WHITE}For more information, please refer to the documentation and the submission.md file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI x DeFi (DeFAI) Demo Script")
    args = parser.parse_args()
    
    demo = DemoScript()
    demo.run_demo() 