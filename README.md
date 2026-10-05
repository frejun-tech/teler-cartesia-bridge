# Teler Cartesia Bridge

A reference integration between **Teler** and **Cartesia**, based on media streaming over WebSockets.

## About

This project is a reference implementation to bridge **Teler** and **Cartesia**. It enables real-time media streaming over WebSockets, facilitating live audio interactions.

---

## Features

- Real-time streaming of media via WebSockets
- Bi-directional communication between Teler client and Cartesia
- Automatic audio resampling from Cartesia (16kHz) to Teler (8kHz)
- Sample structure for deployment (Docker, environment variables)
- Basic error handling and connection management

---

## Prerequisites

Ensure you have the following installed / available:

- Docker
- Valid API credentials / access:
  - Teler account / API key (frejun account)
  - Cartesia API access
  - Cartesia Agent ID
  - ngrok auth token

---

## Setup

1. **Clone and configure:**

   ```bash
   git clone https://github.com/frejun-tech/teler-cartesia-bridge.git
   cd teler-cartesia-bridge
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. **Run with Docker:**
   ```bash
   docker compose up --build
   ```

## Environment Variables

| Variable            | Description                                    | Default  |
| ------------------- | ---------------------------------------------- | -------- |
| `CARTESIA_WS_URL`   | Cartesia Websocket URL with agent ID           | Required |
| `CARTESIA_API_KEY`  | Your Cartesia API key                          | Required |
| `TELER_API_KEY`     | Your Teler API key                             | Required |
| `SERVER_DOMAIN`     | Server domain for callbacks                    | Required |
| `SERVER_HOST`       | Server host address                            | 0.0.0.0  |
| `SERVER_PORT`       | Server port                                    | 8000     |
| `LOG_LEVEL`         | Logging level                                  | INFO     |
| `NGROK_AUTHTOKEN`   | Your ngrok authentication token                | Required |
| `CHUNK_BUFFER_SIZE` | Audio chunk buffer size                        | 10       |

## API Endpoints

- `GET /` - Health check
- `GET /health` - Service status
- `GET /ngrok-status` - Current ngrok status and URL
- `POST /api/v1/calls/initiate-call` - Start a new call
- `POST /api/v1/calls/flow` - Get call flow configuration
- `WebSocket /api/v1/calls/media-stream` - Audio streaming
- `POST /api/v1/webhooks/receiver` - Teler webhook receiver

### Call Initiation Example

```bash
curl -X POST "https://your-domain/api/v1/calls/initiate-call" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+1234567890",
    "to_number": "+0987654321"
  }'
```
