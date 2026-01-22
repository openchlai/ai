# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OPENCHS is a comprehensive case management and helpline system designed for children's helpline operations. It integrates call handling (SIP), case processing, real-time monitoring, AI-powered insights, and quality assurance into a unified Vue.js interface.

## Development Commands

All commands must be run from the `finalui/` directory:

```bash
cd finalui
npm install          # Install dependencies
npm run dev          # Start dev server (http://localhost:5173)
npm run build        # Production build
npm run preview      # Preview production build
```

## Tech Stack

- **Framework**: Vue 3 with Composition API (`<script setup>` syntax)
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS v4 (@tailwindcss/vite)
- **State Management**: Pinia
- **Routing**: Vue Router with permission-based guards
- **HTTP Client**: Axios with interceptors
- **VoIP**: SIP.js for call handling
- **Real-time**: WebSocket for live updates
- **Icons**: Iconify via unplugin-icons (auto-imported)
- **Components**: Auto-imported via unplugin-vue-components

## Project Structure

```
finalui/src/
├── components/          # Feature-specific components
│   ├── base/           # Shared base components
│   ├── cases/          # Case management components
│   ├── calls/          # Call history/recording components
│   ├── dashboard/      # Dashboard widgets
│   ├── messages/       # Messaging components
│   ├── qa*/            # Quality assurance components
│   ├── users/          # User management components
│   └── wallboard/      # Real-time monitoring components
├── pages/              # Route-level view components
├── stores/             # Pinia state stores (auth, cases, calls, etc.)
├── composables/        # Vue composition functions
├── router/             # Vue Router configuration
├── layout/             # App layout components
├── utils/              # Helper functions (axios, formatters)
└── assets/             # Static assets and global styles
```

## Authentication & Permissions

### Authentication Flow
- Uses session-based authentication with localStorage persistence
- Login requires username/password via Basic Auth
- Server returns session data: `[sessionId, userId, username, userRole]`
- **CRITICAL**: All four fields must be present for valid authentication
- Session-Id header is automatically added to all API requests via axios interceptor

### Role System
Seven roles with different permission levels:
1. **Counsellor** (ID: 1) - dashboard, cases, calls, messages, wallboard, faqs
2. **Supervisor** (ID: 2) - adds qa, reports
3. **Case Manager** (ID: 3) - same as Supervisor
4. **Case Worker** (ID: 4) - dashboard, cases, faqs only
5. **Partner** (ID: 5) - dashboard only
6. **Media Account** (ID: 6) - dashboard only
7. **Administrator** (ID: 99) - full access including users, activities

### Permission Guards
Routes use `meta.permission` to restrict access:
```javascript
{
  path: '/users',
  meta: { requiresAuth: true, permission: 'users' }
}
```
Router guard (`router/index.js:123-174`) checks authentication and permissions before navigation.

## API Configuration

### Axios Setup
- **Base URL**: `/api-proxy` (proxied in dev, configured in nginx for production)
- **Dev Proxy**: Vite proxies `/api-proxy` → `https://demo-openchs.bitz-itc.com/helpline`
- **Interceptors**:
  - Request: Adds `Session-Id` header from localStorage
  - Request: Adds `X-API-Key: 08m9cujgjlk0epqqms1q99bbvc` for `/cases/` endpoints
  - Response: Redirects to `/login` on 401 Unauthorized

### API Instance
Import from `@/utils/axios.js`:
```javascript
import axiosInstance from '@/utils/axios'
```

## Key Architectural Patterns

### State Management (Pinia)
Each store manages a specific domain:
- `auth.js` - Authentication, user session, permissions
- `cases.js` - Case records and lifecycle
- `calls.js` - Call history and recordings
- `clients.js` - Client (child) information
- `reporters.js` - Reporter/caller information
- `perpetrators.js` - Perpetrator records
- `activities.js` - Activity logging
- `users.js` - User management
- `qas.js` - Quality assurance evaluations
- `files.js` - File uploads and management
- `messages.js` - SMS/messaging
- `categories.js` - Case categories/classifications

### Composables
Reusable composition functions in `composables/`:
- `useTheme.js` - Dark/light mode management
- `useApiData.js` - Generic API data fetching
- `useCounsellorData.js` - Counsellor-specific data
- `useWebSocketConnection.js` - WebSocket management for wallboard

### Auto-Imports
- **Icons**: Use any Iconify icon without imports: `<i-mdi-home />` for Material Design Icons
- **Components**: Base components auto-import (configured in vite.config.js)

### Real-time Updates
WebSocket connection (`useWebSocketConnection.js`) provides live channel/call data for wallboard monitoring. Handles reconnection logic and parses channel state arrays.

## Design System

### Color Palette
- **Primary**: Amber/Gold (customized amber tones)
- **Backgrounds**: Black (dark mode) / White-Gray (light mode)
- **Focus**: High contrast, clarity in typography
- **Aesthetic**: Borderless design with depth via shadows and elevation

### Theme Toggle
Dark/light mode managed via `useTheme()` composable, persisted in localStorage.

## Common Patterns

### Creating New Pages
1. Create page component in `src/pages/`
2. Add route in `src/router/index.js` with appropriate `meta.permission`
3. Create feature-specific components in `src/components/<feature>/`
4. Add Pinia store if complex state needed in `src/stores/<feature>.js`

### Adding API Endpoints
1. Use `axiosInstance` from `@/utils/axios`
2. Implement in relevant store's actions
3. Session-Id header added automatically
4. Handle errors in store with try/catch

### Component Structure
Use Vue 3 Composition API with `<script setup>`:
```vue
<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const data = ref([])

// Component logic...
</script>
```

### Icon Usage
Auto-import from Iconify (Material Design Icons collection):
```vue
<i-mdi-account class="w-5 h-5" />
<i-mdi-phone class="text-blue-500" />
```

## VoIP/SIP Integration

The application includes SIP.js (v0.21.2) for handling voice calls. SIP agent functionality is integrated for counsellors to receive and manage calls directly in the interface.

## Important Notes

- All development work happens in the `finalui/` directory
- Use `@/` alias for imports (resolves to `finalui/src/`)
- Authentication state initializes on app mount via `authStore.initializeAuth()`
- Incomplete authentication data triggers automatic logout and redirect
- API responses may return errors array: `response.data.errors[0][1]`
- Console logging is verbose (uses emoji prefixes) for debugging auth flow
