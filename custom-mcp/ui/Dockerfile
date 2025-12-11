FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* /app/
RUN npm install --omit=dev || true
COPY . /app
EXPOSE 8080
ENV PORT=8080
CMD ["npm", "start"]
