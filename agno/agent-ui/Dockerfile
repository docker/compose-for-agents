FROM node

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
