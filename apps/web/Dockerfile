# Production Dockerfile for ResearchForge Web SPA
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY --from=builder /app/dist ./dist
COPY vite.config.ts ./

EXPOSE 5173

CMD ["npx", "vite", "preview", "--port", "5173", "--host", "0.0.0.0"]
