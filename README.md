# Slack Bot Assistant

A Slack bot built with Python that provides conversational assistance using the Slack Bolt framework. Works with [LangGraph Template](https://github.com/ryaneggz/langgraph-template), set the BASE_API_URL

## Prerequisites

- Python 3.10+
- Slack Bot Token
- Base API URL for LLM endpoint

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
BASE_API_URL=http://localhost:8000
```


## Installation

### Local Setup

1. Clone the repository

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

### Docker Run

1. Run app container:
   ```bash
   docker-compose up --build
   ```

### Docker Build

1. Build the Docker image:
   ```bash
   docker build -t slack-bot .
   ```

2. Run the container:
   ```bash
   docker run --env-file .env slack-bot
   ```

## Features

- Conversational memory using thread IDs
- Reset conversation context
- Logging to both file and console
- Responds to:
  - Direct mentions (@bot)
  - "hello" messages
  - "reset" command

## Usage

1. Mention the bot: `@bot <your question>`
2. Reset conversation: `@bot reset` or type `reset`
3. Say hello: Just type `hello` in any channel where the bot is present

## Development

For development, VS Code launch configurations are provided. Use the "Python: Slack Bot" debug configuration to run the bot with debugging enabled.

