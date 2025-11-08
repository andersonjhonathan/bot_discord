# Aplicação Bot

## Overview
A Python Discord bot application built with discord.py. The bot provides basic command handling, message responses, and welcome messages for new server members.

## Recent Changes
- **2025-11-08**: Initial project setup
  - Created Discord bot with discord.py
  - Implemented basic commands (!ping, !info, !ajuda)
  - Added welcome message system for new members
  - Set up project structure and dependencies

## Project Architecture
- **main.py**: Main bot file with command handlers and event listeners
- **requirements.txt**: Python dependencies
- **.env.example**: Template for environment variables

## Commands
- `!ping` - Check bot latency
- `!info` - Display bot information
- `!ajuda` - Show available commands

## Setup Instructions
1. Create a Discord Bot at https://discord.com/developers/applications
2. Enable the following intents in the Discord Developer Portal:
   - Message Content Intent
   - Server Members Intent
3. Add your bot token to Replit Secrets as `DISCORD_BOT_TOKEN`
4. Invite the bot to your server using the OAuth2 URL generator
5. Run the bot with `python main.py`

## Dependencies
- discord.py 2.3.2
- python-dotenv 1.0.0
- aiohttp 3.9.1

## User Preferences
- Language: Portuguese (BR)
- Bot prefix: !
