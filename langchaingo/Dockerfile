# ---- Stage 1: Build the app ----
FROM golang:1.24.1-alpine AS builder

WORKDIR /build

# Install ca-certificates for HTTPS requests
RUN apk --no-cache add ca-certificates

# Only copy metadata first to cache dependencies
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# Now copy the rest of the app
COPY . .

# Build statically linked binary
# `-tags timetzdata` embeds zone info from the "time/tzdata" package.
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags '-extldflags "-static"' -tags timetzdata -o app .

# ---- Stage 2: Runtime image ----
FROM alpine:3.19 AS app

# Install ca-certificates for HTTPS requests and timezone data
RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app

# Copy only the built jar from the builder stage
COPY --from=builder /build/app app

# Copy ca-certificates from builder
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Create entrypoint script
COPY <<EOF entrypoint.sh
#!/bin/sh

if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

if test -n "\${OPENAI_API_KEY}"; then
    echo "Using OpenAI with \${MODEL_NAME}"
    export OPENAI_BASE_URL=https://api.openai.com/v1
else
    export OPENAI_BASE_URL=\${MODEL_RUNNER_URL}
    export OPENAI_MODEL_NAME=\${MODEL_RUNNER_MODEL}
    export OPENAI_API_KEY=cannot_be_empty
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL} in \${MODEL_RUNNER_URL}"
fi

exec ./app
EOF
RUN chmod +x entrypoint.sh

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Change ownership and switch to non-root user
RUN chown -R appuser:appgroup /app
USER appuser

ENTRYPOINT ["./entrypoint.sh"]
