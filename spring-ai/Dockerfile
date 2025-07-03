# ---- Stage 1: Build the app ----
FROM eclipse-temurin:17-jdk AS builder

WORKDIR /build

# Only copy metadata first to cache dependencies
COPY pom.xml ./
COPY .mvn .mvn
COPY mvnw ./
RUN ./mvnw dependency:go-offline -B

# Now copy the rest of the app
COPY src ./src
RUN ./mvnw package -DskipTests -B

# ---- Stage 2: Runtime image ----
FROM eclipse-temurin:17-jre AS app

WORKDIR /app

# Copy only the built jar from the builder stage
COPY --from=builder /build/target/*.jar app.jar

ENV SPRING_PROFILES_ACTIVE=prod
COPY <<EOF entrypoint.sh
#!/bin/sh

if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

if test -n "\${OPENAI_API_KEY}"; then
    echo "Using OpenAI with \${MODEL_NAME}"
    export OPENAI_BASE_URL=https://api.openai.com/v1
else
    echo "Using Docker Model Runner with \${MODEL_RUNNER_MODEL}"
    export OPENAI_BASE_URL=\${MODEL_RUNNER_URL}
    export OPENAI_MODEL_NAME=\${MODEL_RUNNER_MODEL}
    export OPENAI_API_KEY=cannot_be_empty
fi

# spring.ai expects the base URL to omit the /v1/? suffix
export OPENAI_BASE_URL=\${OPENAI_BASE_URL%/}
export OPENAI_BASE_URL=\${OPENAI_BASE_URL%/v1}
exec java -jar app.jar
EOF
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
