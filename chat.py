#!/usr/bin/env python3
"""
Interactive CLI interface for the Stubborn Chatbot.

Allows users to have real-time conversations with the debate bot
directly from the command line.

Note: This CLI bypasses the HTTP API layer and calls the business logic
(use cases) directly. This provides the fastest user experience while
still testing the core conversation functionality.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.adapters.dependency_injection.container import (
    get_start_conversation_use_case,
    get_continue_conversation_use_case,
    cleanup_redis_connections
)


class ChatbotCLI:
    """Interactive command-line interface for the debate chatbot."""
    
    def __init__(self):
        """Initialize the CLI interface."""
        self.start_use_case = get_start_conversation_use_case()
        self.continue_use_case = get_continue_conversation_use_case()
        self.current_conversation_id: Optional[str] = None
        self.message_count = 0
    
    def print_welcome(self):
        """Print welcome message and instructions."""
        print("=" * 60)
        print("STUBBORN CHATBOT - Interactive Debate Mode")
        print("=" * 60)
        print("I'm a debate bot that loves to argue! Give me any topic")
        print("and I'll take a contrarian stance to challenge your views.")
        print()
        print("Commands:")
        print("  - Type your message and press Enter to chat")
        print("  - Type 'quit' or 'exit' to end the conversation")
        print("  - Type 'new' to start a fresh conversation")
        print("  - Type 'help' to see these commands again")
        print("=" * 60)
        print()
        print("Ready to debate! Type your first message below:")
    
    def print_help(self):
        """Print help message."""
        print("\nAvailable Commands:")
        print("  quit/exit  - End the conversation and exit")
        print("  new        - Start a new conversation (abandon current)")
        print("  help       - Show this help message")
        print("  <message>  - Send a message to the bot")
        print()
        print("Just type your message at the prompt (>>) and press Enter!")
    
    def format_message(self, role: str, content: str, is_new: bool = False) -> str:
        """Format a message for display."""
        if role == "user":
            prefix = "You:" if not is_new else "You (new topic):"
            return f"{prefix} {content}"
        else:  # bot
            prefix = "Bot:" if not is_new else "Bot (new stance):"
            return f"{prefix} {content}"
    
    async def start_new_conversation(self, message: str) -> bool:
        """Start a new conversation with the given message."""
        try:
            print(f"\n{self.format_message('user', message, is_new=True)}")
            print("Thinking... (generating debate topic)")
            
            conversation = await self.start_use_case.execute(message)
            self.current_conversation_id = str(conversation.conversation_id)
            self.message_count = len(conversation.get_recent_messages())
            
            # Get the bot's response
            recent_messages = conversation.get_recent_messages()
            bot_message = recent_messages[-1]  # Last message should be bot's
            
            print(f"{self.format_message('bot', bot_message.content, is_new=True)}")
            print(f"\nConversation started! (ID: {self.current_conversation_id[:8]}...)")
            return True
            
        except Exception as e:
            print(f"Error starting conversation: {e}")
            return False
    
    async def continue_conversation(self, message: str) -> bool:
        """Continue the current conversation with the given message."""
        try:
            print(f"\n{self.format_message('user', message)}")
            print("Thinking... (generating response)")
            
            conversation = await self.continue_use_case.execute(
                self.current_conversation_id, message
            )
            self.message_count = len(conversation.get_recent_messages())
            
            # Get the bot's latest response
            recent_messages = conversation.get_recent_messages()
            bot_message = recent_messages[-1]  # Last message should be bot's
            
            print(f"{self.format_message('bot', bot_message.content)}")
            return True
            
        except Exception as e:
            print(f"Error continuing conversation: {e}")
            return False
    
    def get_user_input(self) -> str:
        """Get user input with a nice prompt."""
        try:
            message_num = self.message_count//2 + 1
            prompt = f"\n[Message {message_num}] >> "
            return input(prompt).strip()
        except (KeyboardInterrupt, EOFError):
            return "quit"
    
    async def run(self):
        """Run the interactive CLI interface."""
        self.print_welcome()
        
        while True:
            user_input = self.get_user_input()
            
            # Handle empty input
            if not user_input:
                print("Please enter a message or command.")
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThanks for debating! See you next time.")
                break
            
            elif user_input.lower() in ['help', 'h']:
                self.print_help()
                continue
            
            elif user_input.lower() in ['new', 'restart']:
                print("\nStarting a new conversation...")
                print("What topic would you like to debate about?")
                self.current_conversation_id = None
                self.message_count = 0
                continue
            
            # Handle conversation
            if self.current_conversation_id is None:
                # Start new conversation
                success = await self.start_new_conversation(user_input)
                if not success:
                    print("Failed to start conversation. Try again or type 'quit' to exit.")
            else:
                # Continue existing conversation
                success = await self.continue_conversation(user_input)
                if not success:
                    print("Failed to continue conversation. Type 'new' to start over or 'quit' to exit.")


async def main():
    """Main entry point for the CLI interface."""
    try:
        cli = ChatbotCLI()
        await cli.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    finally:
        # Clean up Redis connections on exit
        await cleanup_redis_connections()


if __name__ == "__main__":
    print("Starting Stubborn Chatbot CLI...")
    asyncio.run(main())
