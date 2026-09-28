# --- Base Stage ---
FROM node:24-bookworm-slim AS base
WORKDIR /app

RUN corepack enable && corepack prepare pnpm@11.3.0 --activate

# --- Dependencies Stage ---
FROM base AS dependencies
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

ENV NEXT_TELEMETRY_DISABLED=1

RUN pnpm install --frozen-lockfile

# --- Development Stage ---
FROM dependencies AS development
ENV NODE_ENV=development
COPY . .
EXPOSE 3000
CMD ["pnpm", "dev"]

# --- Production Build Stage ---
FROM dependencies AS builder
ENV NODE_ENV=production
COPY . .
RUN pnpm build

# --- Production Stage ---
FROM node:24-bookworm-slim AS production
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

RUN groupadd --system --gid 1001 nodejs && useradd --system --uid 1001 --gid nodejs nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
CMD ["node", "server.js"]
