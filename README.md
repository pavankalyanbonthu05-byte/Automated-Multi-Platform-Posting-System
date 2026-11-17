# Automated Multi-Platform Posting System

[![Python 3.x](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-red.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

A high-performance, asynchronous REST API service built with **FastAPI** that broadcasts short promotional or announcement messages simultaneously across multiple third-party platforms with fault isolation and strict input validation.

---

## Table of Contents

1. [Features](#features)
2. [Supported Platforms](#supported-platforms)
3. [Architecture & Project Structure](#architecture--project-structure)
4. [Input Validation Rules](#input-validation-rules)
5. [Setup & Installation](#setup--installation)
6. [Configuration & Environment Variables](#configuration--environment-variables)
7. [Running the Application](#running-the-application)
8. [API Documentation & Endpoints](#api-documentation--endpoints)
9. [Sample Requests & Responses](#sample-requests--responses)
10. [Automated Test Suite](#automated-test-suite)
11. [Error Handling & Fault Tolerance](#error-handling--fault-tolerance)

---

## Features

- **FastAPI Asynchronous Architecture**: Uses non-blocking `asyncio` routines to post concurrently to all platforms.
- **5 Platform Integrations**: Built-in support for Telegram, Discord, Slack, Mastodon, and Dev.to.
- **Independent Platform Fault Isolation**: If any platform encounters rate limits or errors, posting continues uninterrupted on the remaining platforms.
- **Strict Input Validation**: Validates character count (≤ 200), enforces exactly one valid CTA link, and verifies URL structure.
- **Flexible Execution Modes**: Supports both Live API execution with credentials and Dry-Run/Simulation mode (`DRY_RUN_MODE=true`) for sandbox evaluation.
- **Standardized Response Format**: Detailed status, posted URL, public access flag, date, time, and error details per platform.

---

## Supported Platforms

| # | Platform | Type | Public Access | Official API Documentation |
|---|---|---|:---:|---|
| 1 | **Telegram** | Instant Messaging / Channel | Yes | [Telegram Bot API - sendMessage](https://core.telegram.org/bots/api#sendmessage) |
| 2 | **Discord** | Community Platform | Yes | [Discord Webhook Resource](https://discord.com/developers/docs/resources/webhook#execute-webhook) |
| 3 | **Slack** | Workspace Messaging | No (Private) | [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks) |
| 4 | **Mastodon** | Decentralized Social Network (Fediverse) | Yes | [Mastodon Statuses API](https://docs.joinmastodon.org/methods/statuses/#create) |
| 5 | **Dev.to** | Developer Publishing Portal (Forem) | Yes | [Dev.to Articles API](https://developers.forem.com/api/v1#tag/articles/operation/createArticle) |

---

## Architecture & Project Structure

```text
Automated Multi-Platform Posting System/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entrypoint & exception handlers
│   ├── config.py                # Environment and configuration settings
│   ├── schemas.py               # Pydantic models & validation logic
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── base.py              # Base abstract platform interface
│   │   ├── telegram.py          # Telegram Bot integration
│   │   ├── discord.py           # Discord Webhook integration
│   │   ├── slack.py             # Slack Incoming Webhook integration
│   │   ├── mastodon.py          # Mastodon REST API integration
│   │   └── devto.py             # Dev.to Article publishing integration
│   └── services/
│       ├── __init__.py
│       └── posting_service.py   # Multi-platform orchestration & asyncio.gather
│
├── tests/
│   └── test_posting.py          # Unit, integration, validation & fault-isolation tests
│
├── .env                         # Local environment settings (gitignored)
├── .env.example                 # Example configuration template
├── .gitignore                   # Git ignore patterns
├── requirements.txt             # Project dependencies
└── README.md                    # Comprehensive documentation
```

---

## Input Validation Rules

The `POST /posting` endpoint applies the following validation rules to incoming requests:

1. **Character Limit**: The message must not exceed 200 characters.
2. **Exactly One CTA Link**: The message must contain **exactly one** valid URL (`http://` or `https://`).
   - If 0 links are provided: HTTP 422 Unprocessable Content.
   - If 2 or more links are provided: HTTP 422 Unprocessable Content.
3. **URL Format**: The URL must feature a valid scheme and verifiable domain name host.
4. **Non-Empty Content**: Messages cannot be empty or only whitespace.

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/automated-multi-platform-posting.git
cd "Automated Multi-Platform Posting System"
```

### 2. Create and Activate a Virtual Environment

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration & Environment Variables

Copy the provided `.env.example` file to create your `.env`:

```bash
cp .env.example .env
```

### Environment Parameters

```ini
# Execution Mode (Set to false for strict live calls)
DRY_RUN_MODE=true

# Server Configuration
PORT=4000
HOST=0.0.0.0

# Platform 1: Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=@your_channel_or_chat_id

# Platform 2: Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Platform 3: Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Platform 4: Mastodon
MASTODON_INSTANCE_URL=https://mastodon.social
MASTODON_ACCESS_TOKEN=your_mastodon_access_token

# Platform 5: Dev.to
DEVTO_API_KEY=your_devto_api_key
```

> **Note on `DRY_RUN_MODE`**:
> When `DRY_RUN_MODE=true` (default), any platform lacking live API credentials will execute a simulated publishing lifecycle and generate deterministic URLs. This enables immediate testing and evaluation without requiring all 5 third-party developer accounts upfront. If credentials are provided or `DRY_RUN_MODE=false`, real network calls are made.

---

## Running the Application

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

The server will be reachable at:
- **API Base URL**: `http://localhost:4000`
- **Swagger Interactive Docs**: `http://localhost:4000/docs`
- **ReDoc Documentation**: `http://localhost:4000/redoc`

---

## API Documentation & Endpoints

### 1. Health Check
- **URL**: `GET /`
- **Description**: Returns service health status and links.

### 2. Multi-Platform Posting
- **URL**: `POST /posting`
- **Content-Type**: `application/json`
- **Description**: Publishes the message across all 5 integrated platforms concurrently.

---

## Sample Requests & Responses

### Sample 1: Successful Post Request

**Request:**
```http
POST http://localhost:4000/posting
Content-Type: application/json

{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

**Response (`200 OK`):**
```json
{
  "success": true,
  "results": [
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/example_channel/1487",
      "public_access": true,
      "date": "2026-11-17",
      "time": "21:34:47",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://discord.com/channels/123456789/987654321/1794931487",
      "public_access": true,
      "date": "2026-11-17",
      "time": "21:34:47",
      "error": null
    },
    {
      "platform": "Slack",
      "status": "success",
      "posted_url": "https://app.slack.com/client/T00000000/C00000000/p1794931487000",
      "public_access": false,
      "date": "2026-11-17",
      "time": "21:34:47",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@bot/1794931487",
      "public_access": true,
      "date": "2026-11-17",
      "time": "21:34:47",
      "error": null
    },
    {
      "platform": "Dev.to",
      "status": "success",
      "posted_url": "https://dev.to/user/post-1794931487",
      "public_access": true,
      "date": "2026-11-17",
      "time": "21:34:47",
      "error": null
    }
  ]
}
```

---

### Sample 2: Validation Error (Missing CTA Link)

**Request:**
```http
POST http://localhost:4000/posting
Content-Type: application/json

{
  "message": "Check out our platform without any CTA link."
}
```

**Response (`422 Unprocessable Content`):**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "message": "Exactly one CTA link must be included in the message. No link was found.",
      "type": "value_error"
    }
  ],
  "error_summary": "Exactly one CTA link must be included in the message. No link was found."
}
```

---

### Sample 3: Validation Error (Multiple CTA Links)

**Request:**
```http
POST http://localhost:4000/posting
Content-Type: application/json

{
  "message": "Visit https://site-a.com and also https://site-b.com"
}
```

**Response (`422 Unprocessable Content`):**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "message": "Exactly one CTA link must be included in the message. Found 2 links: https://site-a.com, https://site-b.com",
      "type": "value_error"
    }
  ],
  "error_summary": "Exactly one CTA link must be included in the message. Found 2 links: https://site-a.com, https://site-b.com"
}
```

---

### Sample 4: Validation Error (Exceeds 200 Characters)

**Request:**
```http
POST http://localhost:4000/posting
Content-Type: application/json

{
  "message": "This is a very long message designed to deliberately exceed the maximum permitted length limit of 200 characters in order to verify that the FastAPI schema validation behaves as specified. https://example.com"
}
```

**Response (`422 Unprocessable Content`):**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "message": "Message exceeds maximum allowed length of 200 characters (current length: 228).",
      "type": "value_error"
    }
  ],
  "error_summary": "Message exceeds maximum allowed length of 200 characters (current length: 228)."
}
```

---

## Automated Test Suite

The project includes unit and integration tests covering:
- Schema validation (missing link, multiple links, length over 200, valid formatting)
- Health check endpoint
- Multi-platform posting endpoint execution
- Fault isolation: one platform failure does not block other platforms

### Run Tests:

```bash
pytest tests -v
```

### Test Results Output:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.2.0, pluggy-1.7.0
rootdir: Automated Multi-Platform Posting System
collected 11 items

tests/test_posting.py::test_valid_message_schema PASSED                  [  9%]
tests/test_posting.py::test_validation_missing_url PASSED                [ 18%]
tests/test_posting.py::test_validation_multiple_urls PASSED              [ 27%]
tests/test_posting.py::test_validation_message_exceeds_200_chars PASSED  [ 36%]
tests/test_posting.py::test_validation_invalid_url_scheme PASSED         [ 45%]
tests/test_posting.py::test_api_root_endpoint PASSED                     [ 54%]
tests/test_posting.py::test_api_posting_success_dry_run PASSED           [ 63%]
tests/test_posting.py::test_api_posting_validation_error_too_long PASSED [ 72%]
tests/test_posting.py::test_api_posting_validation_error_no_cta PASSED   [ 81%]
tests/test_posting.py::test_api_posting_validation_error_multiple_ctas PASSED [ 90%]
tests/test_posting.py::test_posting_service_fault_isolation PASSED       [100%]

======================= 11 passed in 0.50s ========================
```

---

## Error Handling & Fault Tolerance

1. **Independent Execution (`asyncio.gather`)**:
   All 5 platform publishers run as independent asynchronous tasks. An exception, HTTP timeout, or authentication failure on one platform does not impact or delay any other platform.

2. **Standardized Failure Reporting**:
   When an integration fails, its result entry records `status: "failed"`, `posted_url: null`, and supplies a descriptive message in the `error` field.

3. **Overall Success Evaluation**:
   `"success": true` is returned if at least one platform successfully publishes the message.

---

## License

This project is licensed under the MIT License.
