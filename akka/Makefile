
OPENAI_API_KEY := $(shell cat secret.openai-api-key)
export OPENAI_API_KEY

build-and-run:
	docker rmi -f helloworld-agent:latest
	mvn clean install -DskipTests -Pstandalone
	docker compose up