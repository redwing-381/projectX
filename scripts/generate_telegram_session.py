#!/usr/bin/env python3
"""Generate Telegram session string for userbot.

Run this script once to authenticate and get a session string.
Then save the session string as TELEGRAM_SESSION in your .env file.

Usage:
    python scripts/generate_telegram_session.py
"""

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    print("="*60)
    print("Telegram Session Generator")
    print("="*60)
    print()
    print("This will authenticate with your Telegram account and")
    print("generate a session string for the userbot.")
    print()
    
    api_id = input("Enter your API ID (from my.telegram.org): ").strip()
    api_hash = input("Enter your API hash: ").strip()
    phone = input("Enter your phone number (e.g. +1234567890): ").strip()
    
    print()
    print("Connecting to Telegram...")
    
    client = TelegramClient(StringSession(), int(api_id), api_hash)
    await client.start(phone=phone)
    
    # Get user info
    me = await client.get_me()
    print()
    print(f"✓ Logged in as: {me.first_name} (@{me.username})")
    
    # Get session string
    session_string = client.session.save()
    
    print()
    print("="*60)
    print("SUCCESS! Copy this session string:")
    print("="*60)
    print()
    print(f"TELEGRAM_SESSION={session_string}")
    print()
    print("="*60)
    print()
    print("Add this to your .env file or Railway environment variables.")
    print("Keep this secret - it gives full access to your account!")
    print()
    
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
