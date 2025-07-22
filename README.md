# Modaic

A full-stack application with FastAPI backend and Next.js frontend for repository management and user authentication.

## Architecture

- **Backend**: FastAPI (Python) with PostgreSQL
- **Frontend**: Next.js 15 (TypeScript) with React 19
- **Authentication**: Stytch
- **Database**: PostgreSQL
- **Storage**: AWS S3 (boto3)
- **Analytics**: PostHog, Vercel Analytics
- **Styling**: Tailwind CSS v4, Radix UI components

## Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL instance
- AWS S3 bucket (optional)
- Stytch account

## Project Structure

```
modaic-dev/
├── client/                 # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Next.js pages
│   │   ├── layouts/       # Layout components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility libraries
│   │   ├── stores/        # State management
│   │   ├── types/         # TypeScript types
│   │   └── environment/   # Environment configuration
│   ├── public/           # Static assets
│   └── package.json
├── server/                # FastAPI backend
│   ├── src/
│   │   ├── api/          # API routes
│   │   ├── core/         # Core configuration
│   │   ├── db/           # Database connection
│   │   ├── lib/          # Utility libraries
│   │   ├── models/       # Data models
│   │   ├── service/      # Business logic
│   │   └── utils/        # Helper functions
│   ├── requirements.txt
│   └── main.py
└── Makefile              # Development commands
```

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd modaic-dev
   ```

2. **Set up environment variables**
   
   Copy the example environment files:
   ```bash
   cp client/.env.example client/.env
   cp server/.env.example server/.env
   ```
   
   Fill in the required values:
   
   **Client (.env):**
   ```env
   NEXT_PUBLIC_ENV="dev"
   NEXT_PUBLIC_API_URL="http://localhost:8000"
   NEXT_PUBLIC_CLIENT_URL="http://localhost:3000"
   NEXT_PUBLIC_POSTHOG_KEY="your_posthog_key"
   NEXT_PUBLIC_POSTHOG_HOST="https://us.i.posthog.com"
   NEXT_PUBLIC_STYTCH_TOKEN="your_stytch_public_token"
   ```
   
   **Server (.env):**
   ```env
   ENVIRONMENT="dev"
   STYTCH_PROJECT_ID="your_stytch_project_id"
   STYTCH_SECRET="your_stytch_secret"
   STYTCH_PROJECT_DOMAIN="your_domain"
   ```

3. **Install dependencies**
   ```bash
   # Install client dependencies
   cd client && npm install
   
   # Install server dependencies
   cd ../server
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Start the development servers**
   ```bash
   # From the project root
   make start
   ```
   
   Or start them individually:
   ```bash
   # Backend only (port 8000)
   make start-backend
   
   # Frontend only (port 3000)
   make start-frontend
   ```

## Available Commands

The Makefile provides convenient commands for development:

- `make start` - Start both backend and frontend
- `make start-backend` - Start only the FastAPI server (localhost:8000)
- `make start-frontend` - Start only the Next.js app (localhost:3000)
- `make stop` - Stop all running processes

## Development Notes

1. **Database**: Ensure PostgreSQL is running before starting the backend
2. **Environment**: The backend loads environment variables from `.env` file
3. **CORS**: Currently configured to allow all origins for development
4. **Authentication**: Stytch integration is partially implemented but commented out in the frontend
5. **Styling**: Uses Tailwind CSS v4 with PostCSS configuration

## Deployment

Both client and server include Dockerfiles for containerized deployment:

- **Client**: Uses Next.js standalone output for optimal Docker builds
- **Server**: Standard Python FastAPI container setup

## Troubleshooting

- **Port conflicts**: Default ports are 3000 (frontend) and 8000 (backend)
- **Database connection**: Verify PostgreSQL is running and accessible
- **Environment variables**: Ensure all required variables are set
- **Dependencies**: Run `npm install` or `pip install -r requirements.txt` if modules are missing

For more help, check the individual README files in the client and server directories.