# Teler Cartesia Bridge

A reference integration between **Teler** and **Cartesia**, based on media streaming over WebSockets.

## About

This project is a reference implementation to bridge **Teler** and **Cartesia**. It enables real-time media streaming over WebSockets, facilitating live audio interactions.

---

## Features

- Post request to Cartesia to get the Join URL (websocket URL)
- Real-time streaming of media via WebSockets
- Bi-directional communication between Teler client and Cartesia
- Sample structure for deployment (Docker, environment variables)
- Basic error handling and connection management

---

### Prerequisites

Ensure you have the following installed / available:

- Docker
- Valid API credentials / access:
  - Teler account / API key / endpoints (frejun account)
  - Cartesia API access

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

| Variable            | Description            | Default  |
| ------------------- | ---------------------- | -------- |
| `CARTESIA_API_KEY`  | Your Cartesia API key  | Required |
| `CARTESIA_WS_URL`   | Cartesia Websocket URL | Required |
| `TELER_API_KEY`     | Your Teler API key     | Required |
| `CHUNK_BUFFER_SIZE` | Chunks buffer size     | 10       |
| `SERVER_PORT`       | Port Number            | 8000     |
| `CHUNK_BUFFER_SIZE` | Chunks buffer size     | 10       |
| `NGROK_AUTHTOKEN`   | Your ngrok auth token  | Required |

## API Endpoints

- `GET /` - Health check with server domain
- `GET /health` - Service status
- `GET /ngrok-status` - Current ngrok status and URL
- `POST /api/v1/calls/initiate-call` - Start a new call with dynamic phone numbers
- `POST /api/v1/calls/flow` - Get call flow configuration
- `WebSocket /api/v1/calls/media-stream` - Audio streaming between teler and cartesia
- `POST /api/v1/webhooks/receiver` - Teler → Cartesia webhook receiver

### Call Initiation Example

```bash
curl -X POST "http://your-domain/api/v1/calls/initiate-call" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+1234567890",
    "to_number": "+0987654321"
  }'
```
