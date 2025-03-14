#!/usr/bin/env python3
"""
Social AI Agent Demo Script

This script provides a guided demonstration of the Social AI Agent system,
with clear instructions and talking points for each step.

Usage:
    python social_agent_demo.py

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
    """Demo script for Social AI Agent"""
    
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
        self.print_header("Social AI Agent Demo")
        
        print(f"{Fore.WHITE}This script will guide you through demonstrating the Social AI Agent system.")
        print(f"{Fore.WHITE}Follow the instructions and talking points for each step.")
        print(f"{Fore.WHITE}Press Enter to advance to the next step.")
        
        self.wait_for_keypress()
        
        # Introduction
        self.clear_screen()
        self.print_section("1. Introduction")
        
        self.print_step("Introduce the project")
        self.print_talking_point("Welcome to the demonstration of our Social AI Agent, a verifiable autonomous agent for the Flare ecosystem.")
        self.print_talking_point("This agent can seamlessly engage with the community on Flare's social media accounts while providing cryptographic proof of secure execution through vTPM attestations.")
        self.print_talking_point("The key innovation is that our agent operates with verifiable autonomy, addressing concerns around financial operations and decision-making processes.")
        
        self.wait_for_keypress()
        
        # System Architecture
        self.clear_screen()
        self.print_section("2. System Architecture")
        
        self.print_step("Explain the system architecture")
        self.print_talking_point("Our Social AI Agent consists of several key components:")
        self.print_talking_point("1. TEE Security Layer: Runs in a Google Cloud Confidential VM with vTPM attestations.")
        self.print_talking_point("2. Social Media Monitoring Pipeline: Continuously monitors X (Twitter) for relevant content.")
        self.print_talking_point("3. Vector Embedding Models: Intelligently classifies tweets for appropriate responses.")
        self.print_talking_point("4. Response Generation System: Creates contextually appropriate responses using Gemini 2.0 Flash.")
        self.print_talking_point("5. Safety Filters: Ensures all generated content adheres to community guidelines.")
        self.print_talking_point("6. Attestation System: Provides cryptographic proof that the agent is operating autonomously.")
        
        self.wait_for_keypress()
        
        # Verify Services
        self.clear_screen()
        self.print_section("3. Verify Services")
        
        self.print_step("Check that all services are running")
        self.print_command("docker-compose ps")
        self.print_talking_point("As you can see, all our services are up and running:")
        self.print_talking_point("- API service: Handles requests and coordinates other services")
        self.print_talking_point("- MongoDB: Stores tweet data and response history")
        self.print_talking_point("- Redis: Caches frequently accessed data and embeddings")
        self.print_talking_point("- Qdrant: Vector database for semantic search of tweets")
        self.print_talking_point("- Social Agent: The main service that monitors and responds to social media")
        
        self.wait_for_keypress()
        
        # Health Check
        self.clear_screen()
        self.print_section("4. Health Check")
        
        self.print_step("Check the health of the API")
        self.print_command("curl -s http://localhost:8000/api/health | jq")
        self.print_talking_point("The health endpoint confirms that our API is operational.")
        self.print_talking_point("This endpoint is used by monitoring systems to check the status of the service.")
        
        self.wait_for_keypress()
        
        # Tweet Monitoring
        self.clear_screen()
        self.print_section("5. Tweet Monitoring")
        
        self.print_step("Check recent monitored tweets")
        self.print_command("curl -s http://localhost:8000/api/social/recent-tweets | jq")
        self.print_talking_point("Our system continuously monitors X (Twitter) for relevant content about Flare.")
        self.print_talking_point("Here we can see the most recent tweets that have been captured by our monitoring system.")
        self.print_talking_point("Each tweet is analyzed for sentiment, topic, and relevance to determine if a response is needed.")
        
        self.wait_for_keypress()
        
        # Tweet Classification
        self.clear_screen()
        self.print_section("6. Tweet Classification")
        
        self.print_step("Analyze a specific tweet")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"tweet_text\": \"How do I stake my FLR tokens? #Flare\"}' http://localhost:8000/api/social/analyze-tweet | jq")
        self.print_talking_point("Our system uses vector embedding models to classify tweets into different categories.")
        self.print_talking_point("This helps determine the appropriate response strategy for each tweet.")
        self.print_talking_point("The classification includes:")
        self.print_talking_point("1. Topic identification (e.g., staking, governance, technical support)")
        self.print_talking_point("2. Sentiment analysis (positive, negative, neutral)")
        self.print_talking_point("3. Urgency assessment (high, medium, low)")
        self.print_talking_point("4. Response requirement (yes/no)")
        
        self.wait_for_keypress()
        
        # Response Generation
        self.clear_screen()
        self.print_section("7. Response Generation")
        
        self.print_step("Generate a response to a tweet")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"tweet_id\": \"1234567890\", \"tweet_text\": \"How do I stake my FLR tokens? #Flare\", \"user_handle\": \"@flare_enthusiast\"}' http://localhost:8000/api/social/generate-response | jq")
        self.print_talking_point("Based on the classification, our system generates an appropriate response.")
        self.print_talking_point("The response is crafted using Gemini 2.0 Flash, which has been fine-tuned on Flare-specific content.")
        self.print_talking_point("Before being sent, the response passes through multiple safety filters to ensure it is:")
        self.print_talking_point("1. Accurate and helpful")
        self.print_talking_point("2. Respectful and professional")
        self.print_talking_point("3. Compliant with platform guidelines")
        self.print_talking_point("4. Free from potentially harmful content")
        
        self.wait_for_keypress()
        
        # Safety Filters
        self.clear_screen()
        self.print_section("8. Safety Filters")
        
        self.print_step("Demonstrate safety filters")
        self.print_command("curl -X POST -H \"Content-Type: application/json\" -d '{\"response_text\": \"You should immediately invest all your money in FLR tokens!\"}' http://localhost:8000/api/social/safety-check | jq")
        self.print_talking_point("Our safety filters are a critical component of the system.")
        self.print_talking_point("They ensure that all responses are appropriate and do not contain:")
        self.print_talking_point("1. Financial advice or investment recommendations")
        self.print_talking_point("2. Misleading or incorrect information")
        self.print_talking_point("3. Offensive or inappropriate language")
        self.print_talking_point("4. Personally identifiable information")
        self.print_talking_point("In this example, the safety filter correctly identified and blocked inappropriate financial advice.")
        
        self.wait_for_keypress()
        
        # Live Interaction
        self.clear_screen()
        self.print_section("9. Live Interaction")
        
        self.print_step("Demonstrate live interaction with a test account")
        self.print_command("python test_social_interaction.py")
        self.print_talking_point("Now we'll demonstrate a live interaction with a test account.")
        self.print_talking_point("This simulation shows how our agent would respond to real-world scenarios.")
        self.print_talking_point("The test includes multiple types of interactions, including:")
        self.print_talking_point("1. General questions about Flare")
        self.print_talking_point("2. Technical support inquiries")
        self.print_talking_point("3. Community engagement")
        self.print_talking_point("4. Handling of potentially problematic content")
        
        self.wait_for_keypress()
        
        # vTPM Attestation
        self.clear_screen()
        self.print_section("10. vTPM Attestation")
        
        self.print_step("Test vTPM attestation")
        self.print_command("source .venv/bin/activate && python test_vTPM.py")
        self.print_talking_point("One of the key features of our Social AI Agent is its use of Trusted Execution Environments (TEEs) with vTPM attestations.")
        self.print_talking_point("The system runs in a Google Cloud Confidential VM with AMD SEV for hardware-level security.")
        self.print_talking_point("The vTPM generates cryptographic attestations that prove the agent's integrity and autonomy.")
        self.print_talking_point("These attestations can be verified on-chain through Flare's vTPM Attestation contract.")
        self.print_talking_point("This ensures that the agent is operating in a secure environment with the expected configuration.")
        self.print_talking_point("Most importantly, it provides verifiable proof that the agent is operating autonomously without human intervention.")
        
        self.wait_for_keypress()
        
        # Onchain Interaction
        self.clear_screen()
        self.print_section("11. Onchain Interaction")
        
        self.print_step("Demonstrate onchain interaction")
        self.print_command("python test_onchain_interaction.py")
        self.print_talking_point("As a bonus feature, our agent can perform onchain interactions based on specific conditions.")
        self.print_talking_point("For example, if the agent detects a significant increase in negative sentiment about Flare, it can:")
        self.print_talking_point("1. Generate an onchain alert transaction")
        self.print_talking_point("2. Temporarily pause automated responses")
        self.print_talking_point("3. Notify the Flare team through a smart contract event")
        self.print_talking_point("This creates a verifiable record of the agent's decision-making process and actions.")
        
        self.wait_for_keypress()
        
        # Conclusion
        self.clear_screen()
        self.print_section("12. Conclusion")
        
        self.print_step("Summarize the demonstration")
        self.print_talking_point("In this demonstration, we've seen how our Social AI Agent provides:")
        self.print_talking_point("1. Verifiable autonomy through TEE attestations")
        self.print_talking_point("2. Intelligent tweet classification and response generation")
        self.print_talking_point("3. Comprehensive safety filters to ensure appropriate content")
        self.print_talking_point("4. Live interaction capabilities with social media platforms")
        self.print_talking_point("5. Onchain interaction for enhanced transparency and security")
        self.print_talking_point("Our Social AI Agent addresses the core problem of verifiable autonomy in AI systems.")
        self.print_talking_point("By leveraging TEEs and attestations, we provide cryptographic proof that the agent operates independently while adhering to predefined safety guidelines.")
        
        self.wait_for_keypress()
        
        # End
        self.clear_screen()
        self.print_header("Demo Complete")
        print(f"{Fore.WHITE}Thank you for watching the Social AI Agent demonstration.")
        print(f"{Fore.WHITE}For more information, please refer to the documentation and the submission.md file.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Social AI Agent Demo Script")
    args = parser.parse_args()
    
    demo = DemoScript()
    demo.run_demo() 