"""Telegram userbot service for monitoring personal messages.

Uses Telethon (MTProto API) to monitor all incoming messages
across all chats and classify them for urgency.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, Callable

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from src.config import get_settings
from src.models.schemas import TelegramMessage

logger = logging.getLogger(__name__)

settings = get_settings()


class TelegramUserbot:
    """Userbot that monitors all incoming Telegram messages."""
    
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_string: str = "",
        on_message: Optional[Callable] = None,
    ):
        """Initialize the userbot.
        
        Args:
            api_id: Telegram API ID from my.telegram.org
            api_hash: Telegram API hash from my.telegram.org
            session_string: Optional session string for persistent login
            on_message: Callback function when message is received
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_string = session_string
        self.on_message = on_message
        self.client: Optional[TelegramClient] = None
        self._running = False
    
    async def start(self, phone: str = None):
        """Start the userbot client.
        
        Args:
            phone: Phone number for first-time authentication
        """
        # Use string session if available, otherwise create new session
        if self.session_string:
            session = StringSession(self.session_string)
        else:
            session = StringSession()
        
        self.client = TelegramClient(session, self.api_id, self.api_hash)
        
        # Connect first
        await self.client.connect()
        
        # Check if already authorized (session string should handle this)
        if not await self.client.is_user_authorized():
            if phone:
                await self.client.start(phone=phone)
            else:
                raise ValueError("Not authorized and no phone number provided. Generate a session string first.")
        
        # Save session string for future use
        new_session = self.client.session.save()
        if new_session != self.session_string:
            logger.info(f"New session string generated. Save this for future use:")
            logger.info(f"TELEGRAM_SESSION={new_session}")
        
        # Register message handler
        @self.client.on(events.NewMessage(incoming=True))
        async def handle_new_message(event):
            await self._process_message(event)
        
        self._running = True
        logger.info("Telegram userbot started successfully")
        
        # Get user info
        me = await self.client.get_me()
        logger.info(f"Logged in as: {me.first_name} (@{me.username})")
    
    async def _process_message(self, event):
        """Process incoming message."""
        try:
            message = event.message
            sender = await event.get_sender()
            chat = await event.get_chat()
            
            # Skip messages from self
            me = await self.client.get_me()
            if sender and sender.id == me.id:
                return
            
            # Build sender name
            sender_name = "Unknown"
            sender_username = None
            if sender:
                sender_name = getattr(sender, 'first_name', '') or ''
                if getattr(sender, 'last_name', ''):
                    sender_name += f" {sender.last_name}"
                sender_username = getattr(sender, 'username', None)
            
            # Get chat name for context
            chat_name = getattr(chat, 'title', None) or sender_name
            
            # Create TelegramMessage
            tg_message = TelegramMessage(
                id=str(message.id),
                sender=sender_name,
                sender_username=sender_username,
                text=message.text or "",
                timestamp=message.date,
                is_forwarded=message.forward is not None,
                original_sender=None,  # Could extract from forward if needed
                chat_id=str(chat.id),
            )
            
            logger.info(f"New message from {sender_name} in {chat_name}: {(message.text or '')[:50]}...")
            
            # Call the callback if set
            if self.on_message:
                await self.on_message(tg_message, chat_name)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def run_forever(self):
        """Run the client until disconnected."""
        if self.client:
            await self.client.run_until_disconnected()
    
    async def stop(self):
        """Stop the userbot."""
        self._running = False
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram userbot stopped")
    
    def get_session_string(self) -> str:
        """Get the current session string."""
        if self.client:
            return self.client.session.save()
        return self.session_string


async def generate_session():
    """Interactive script to generate a session string.
    
    Run this once to get a session string, then save it as
    TELEGRAM_SESSION environment variable.
    """
    api_id = int(input("Enter your API ID: "))
    api_hash = input("Enter your API hash: ")
    phone = input("Enter your phone number (with country code, e.g. +1234567890): ")
    
    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.start(phone=phone)
    
    session_string = client.session.save()
    print("\n" + "="*50)
    print("SUCCESS! Save this session string:")
    print("="*50)
    print(f"\nTELEGRAM_SESSION={session_string}\n")
    print("="*50)
    print("Add this to your .env file or Railway environment variables.")
    
    await client.disconnect()


if __name__ == "__main__":
    # Run session generator
    asyncio.run(generate_session())
