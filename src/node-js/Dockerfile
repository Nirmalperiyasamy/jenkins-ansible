# --- Stage 1: Build Stage ---
    FROM public.ecr.aws/docker/library/node:20-alpine AS builder

    WORKDIR /usr/src/app
    
    # Install dependencies
    COPY package*.json ./
    RUN npm install
    
    # Copy source code
    
    # Build the app
    RUN npm run build
    
    # --- Stage 2: Runtime Stage ---
    FROM public.ecr.aws/docker/library/node:20-alpine
    
    WORKDIR /usr/src/app
    
    # Only copy necessary files from builder
    COPY --from=builder /usr/src/app/package*.json ./
    COPY --from=builder /usr/src/app/node_modules ./node_modules
    COPY --from=builder /usr/src/app/dist ./dist
    COPY --from=builder /usr/src/app/.env .env
    
    EXPOSE 3000
    
    CMD ["npm", "run", "start"]
    