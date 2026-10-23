FROM node:26.12.1-bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && \
    dpkg --compare-versions "$(dpkg-query -W -f='${Version}' ca-certificates)" ge '20250419~deb12u2' && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY .npmrc .
RUN npm install --global corepack@latest
RUN corepack enable pnpm 

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

EXPOSE 3000

# Use npm, pnpm doesn't handle exiting gracefully
CMD ["npm", "run", "start"]
