<<<<<<< HEAD
# Build stage - where we build our VitePress site
=======
# Build stage
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./
<<<<<<< HEAD
RUN npm install
=======
RUN npm ci --no-audit --no-fund
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1

# Copy source and build
COPY . .
RUN npm run build

<<<<<<< HEAD
# Production stage - where we serve the built site
FROM nginx:alpine

# Copy built files to nginx
COPY --from=build /app/docs/.vitepress/dist /usr/share/nginx/html

=======
# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built files
COPY --from=build /app/docs/.vitepress/dist /usr/share/nginx/html

# Set permissions
RUN chown -R nginx:nginx /usr/share/nginx/html

>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]