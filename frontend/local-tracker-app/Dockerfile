# Stage 1: Build the Angular application
FROM node:18 as build
WORKDIR /usr/src/app
COPY package*.json ./
RUN rm -rf node_modules package-lock.json || true # Remove existing to ensure clean install
RUN npm install --force --omit=dev
RUN npm install @rollup/rollup-linux-x64-gnu || true # Explicitly install missing rollup module
COPY . .
RUN npm run build -- --configuration production

# Stage 2: Serve the application from Nginx
FROM nginx:alpine
# Copy built assets from the build stage
COPY --from=build /usr/src/app/dist/local-tracker-app/browser /usr/share/nginx/html
# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Create Nginx cache directories and set permissions
RUN mkdir -p /var/cache/nginx/client_temp /var/run/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/run/nginx /run && \
    chmod -R 755 /var/cache/nginx /var/run/nginx /run
# Switch to the non-root Nginx user
USER nginx
# Expose port 80
EXPOSE 80
