FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
# Ensuring output mode is 'standalone' in Next.js config before building
RUN echo "/** @type {import('next').NextConfig} */\nconst nextConfig = { output: 'standalone' };\nexport default nextConfig;" > next.config.mjs
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

# Copy standalone output from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
