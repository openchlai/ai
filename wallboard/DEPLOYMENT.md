# C-Sema Wallboard Deployment Guide

This guide details how to configure, build, and deploy the C-Sema Wallboard application using Docker.

## 1. Prerequisites
- **Git**: For cloning the repository.
- **Docker & Docker Compose**: Ensure these are installed and running on your deployment server.
- **Network Access**: The server must have access to the backend API (`192.168.10.3` or your configured target).

## 2. Configuration (.env)

The application uses a `.env` file to manage environment-specific variables. Create or update this file in the root directory before building.

### Key Variables
| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `VITE_API_TARGET` | Base URL for the backend API | `http://192.168.10.3` |
| `VITE_WS_TARGET` | WebSocket server URL | `wss://192.168.10.3:8384` |
| `VITE_PROD_WS_URL` | Full WebSocket connection string | `wss://192.168.10.3:8384/ami/sync?c=-2` |
| `VITE_COUNTRY_CODE` | Country code for phone formatting | `255` |
| `VITE_BRAND_COLOR_PRIMARY` | Main dashboard theme color | `#1D3E8A` |
| `VITE_BRAND_COLOR_SECONDARY` | Secondary/Accent color | `#D35400` |
| `VITE_LOGO_URL` | Path or URL to a custom logo | `/src/assets/logo.png` |

---

## 3. Deployment Steps

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd wallboard
```

### Step 2: Configure Environment
Create the `.env` file with your specific network configuration.
```bash
cp .env.example .env
# Edit .env and ensure VITE_API_TARGET points to your actual backend IP
nano .env
```

### Step 3: Build and Run with Docker Compose
To build the container and start it safely in the background:
```bash
docker-compose up --build -d
```

### Step 4: Verify Deployment
The application should now be accessible at:
> **http://<server-ip>:8080**

### Troubleshooting
- **Logs**: View application logs with `docker-compose logs -f wallboard`.
- **Rebuild**: If you change the `.env` file, you MUST rebuild the container:
  ```bash
  docker-compose down
  docker-compose up --build -d
  ```

## 4. Maintenance

### Reloading Nginx Configuration
If you modify `nginx.conf` without rebuilding:
```bash
docker exec -it wallboard_app nginx -s reload
```

### Updating the Application
To update the wallboard code:
1. `git pull origin main`
2. `docker-compose up --build -d`

## 5. Architecture Overview
- **Frontend**: Vue.js 3 (built with Vite)
- **Web Server**: Nginx (serving static files & proxying API requests)
- **Container**: Alpine Linux based image for minimal footprint
