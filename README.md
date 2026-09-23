# Bajaj Earths -- Google Sheets ↔ Web Sync

A React single-page application that provides near-real-time two-way
synchronization between a web table and Google Sheets.

## Tech Stack

-   **Frontend:** React + Vite
-   **Backend:** Python + FastAPI
-   **Realtime:** Node.js + Socket.IO
-   **Data Source:** Google Sheets API
-   **Deployment:** Docker Compose + Nginx on AWS EC2

## Architecture

``` text
React SPA
   │
   ├── REST ───────────────► FastAPI
   │                           │
   │                           ▼
   │                     Google Sheets API
   │                           │
   │                     Google Sheet
   │
   └── Socket.IO ◄──────── Node.js
                              ▲
                              │
                         FastAPI
                       change events
```

Nginx is the public entry point:

``` text
/             → React
/api/         → FastAPI
/socket.io/   → Node.js
```

## Setup

### 1. Clone

``` bash
git clone https://github.com/udaymordharya/BajajProject1.git
cd BajajProject1
```

### 2. Configure environment variables

Create:

``` text
backend/.env
realtime-service/.env
```

Do **not** commit these files.

### 3. Run with Docker

``` bash
docker compose up -d --build
```

Check services:

``` bash
docker compose ps
```

Open:

``` text
http://<SERVER_IP>
```

For a frontend-only source change, rebuild the frontend:

``` bash
docker compose build --no-cache frontend
docker compose up -d frontend
```

## EC2 Deployment

The application is deployed as Docker containers on an Ubuntu EC2
instance.

### Deployment flow

``` text
GitHub Repository
       ↓
Ubuntu EC2
       ↓
git clone / git pull
       ↓
Docker Compose
       ↓
┌──────────┬──────────┬──────────┬──────────┐
│ Frontend │ FastAPI  │ Node.js  │  Nginx   │
│ React    │ Python   │ Socket.IO│  :80     │
└──────────┴──────────┴──────────┴──────────┘
       ↓
Google Sheets API
       ↓
Google Sheet
```

### EC2 deployment steps

After creating the Ubuntu EC2 instance:

``` bash
ssh ubuntu@<EC2_PUBLIC_IP>

git clone https://github.com/udaymordharya/BajajProject1.git
cd BajajProject1
```

Create the server-side environment files:

``` text
backend/.env
realtime-service/.env
```

Then build and start the containers:

``` bash
docker compose build
docker compose up -d
```

Check the deployment:

``` bash
docker compose ps
curl http://localhost/health
curl http://localhost/api/sheet
```

Nginx exposes the application publicly on port `80`. FastAPI (`8000`),
Node.js (`3001`) and the React container's internal port (`80`) are
connected through the Docker network and are not directly exposed to the
Internet.

When code is updated:

``` bash
git pull origin main
docker compose build --no-cache frontend
docker compose up -d
```

For backend or realtime changes, rebuild the relevant service or the
complete stack:

``` bash
docker compose build
docker compose up -d
```

## Hosting Cost / AWS Free Tier

The application does not require a paid application server architecture. It runs all four
application components on one EC2 instance using Docker Compose.
The EC2 deployment can be **₹0 additional hosting cost while the AWS
account and resources remain within an applicable AWS Free Tier offer or
available AWS credits**

Therefore, the deployment should be described as:

> **Hosted on AWS EC2 using the applicable AWS Free Tier/credits, with
> Docker Compose running the complete application stack on a single
> instance.**

To avoid unexpected charges, verify the EC2 instance type and Free Tier
eligibility in the AWS Billing/EC2 console and monitor Free Tier usage. Eg: Instance type
c7i-flex.large(I used this one it is free)
AWS notes that charges can apply when usage exceeds the applicable
limits or after eligibility expires. citeturn0search0turn0search11

### Cost-saving design

This project keeps infrastructure small by:

-   Running React, FastAPI, Node.js and Nginx as containers on one EC2
    instance.
-   Using Google Sheets instead of deploying a separate database.
-   Using Nginx as the single public entry point.
-   Keeping FastAPI and Node.js internal to the Docker network.
   
## Google Cloud Configuration

1.  Create/select a Google Cloud project.
2.  Enable the **Google Sheets API**.
3.  Create a **Service Account**.
4.  Create a service-account key and keep it private.
5.  Share the target Google Sheet with the service-account email as an
    **Editor**.
6.  Configure the Sheet ID and range in `backend/.env`.

The application uses the service account only from the backend. Google
credentials are never placed in React source code.

## Environment Variables

### `backend/.env`

``` env
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_CLIENT_EMAIL=service-account-email
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
GOOGLE_SHEET_ID=your-spreadsheet-id
GOOGLE_SHEET_RANGE=Sheet1!A:C

REALTIME_SERVICE_URL=http://realtime:3001
BACKEND_API_KEY=your-internal-api-key

SYNC_INTERVAL_SECONDS=2
FRONTEND_ORIGINS=http://your-server-ip
```

### `realtime-service/.env`

``` env
PORT=3001
FRONTEND_URL=http://your-server-ip
BACKEND_API_KEY=your-internal-api-key
```

The frontend uses same-origin production routing through Nginx, so the
API and Socket.IO services do not need to be publicly exposed.

## How Synchronization Works

### Website → Google Sheet

``` text
React
  ↓
PUT /api/sheet/{row}
  ↓
FastAPI
  ↓
Google Sheets API
  ↓
Google Sheet
```

After the update, FastAPI reads the refreshed Sheet and broadcasts the
latest data through Socket.IO.

### Google Sheet → Website

FastAPI polls the Sheet approximately every **2 seconds**.

``` text
Google Sheet
  ↓
FastAPI polling
  ↓
Dataset hash comparison
  ↓
Change detected
  ↓
Node.js / Socket.IO
  ↓
React UI
```

The website updates without a manual page refresh.

### Conflict Protection

Each dataset has a hash. When an update is submitted, FastAPI can
compare the client's expected hash with the current Sheet hash. If the
Sheet changed externally first, the API returns **409 Conflict** instead
of overwriting newer data.

## Security

-   Google credentials are stored only in server-side environment
    variables.
-   `.env` files are excluded from Git.
-   Backend and realtime ports are internal to Docker.
-   Nginx is the public entry point.
-   FastAPI → Node.js communication uses an internal API key.
-   Never commit service-account private keys or API keys.


## Future Plans:
- Google OAuth 2.0 Authentication: Implement Google login to support secure multi-user authentication and manage individual user sessions.
- User-Specific Google Drive & Sheets Access: Use Google Cloud Console and OAuth permissions to allow each authenticated user to connect and access their own Google Drive files and Google Sheets instead of using a shared service account.
- CI/CD Automation: Implement a CI/CD pipeline using GitHub Actions to automatically test the application, build Docker images, and prepare releases whenever changes are pushed to GitHub.
- Automated Deployment: Extend the CI/CD pipeline to automatically deploy validated changes to the EC2 server, eliminating the current manual process of SSH, pulling the latest code, rebuilding containers, and restarting the application.
