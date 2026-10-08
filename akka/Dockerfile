FROM maven:3.9.15-eclipse-temurin-25
WORKDIR /app
COPY pom.xml .
RUN --mount=type=cache,target=/root/.m2/repository \
    mvn -B -q -DskipTests dependency:go-offline
COPY src ./src
COPY <<EOF entrypoint.sh
#!/bin/sh
if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi
exec mvn compile exec:java
EOF

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
