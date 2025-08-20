FROM eclipse-temurin:21.0.1_12-jre-jammy
COPY target/docker/helloworld-agent/latest/build/maven/* /maven/

COPY <<EOF entrypoint.sh
#!/bin/sh


if test -f /run/secrets/openai-api-key; then
    export OPENAI_API_KEY=$(cat /run/secrets/openai-api-key)
fi

java -cp "/maven/*" -Dconfig.resource=runtime-standalone.conf kalix.runtime.AkkaRuntimeMain
EOF

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
