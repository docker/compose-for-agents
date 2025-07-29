package main

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	dmcpg "github.com/testcontainers/testcontainers-go/modules/dockermcpgateway"
	"github.com/testcontainers/testcontainers-go/modules/dockermodelrunner"
)

const (
	modelNamespace = "ai"
	modelName      = "gemma3-qat"
	modelTag       = "latest"
	fqModelName    = modelNamespace + "/" + modelName + ":" + modelTag
)

func TestChat(t *testing.T) {
	ctx := context.Background()

	// Docker Model Runner container, which talks to Docker Desktop's model runner
	dmrCtr, err := dockermodelrunner.Run(ctx, dockermodelrunner.WithModel(fqModelName))
	testcontainers.CleanupContainer(t, dmrCtr)
	require.NoError(t, err)

	// Docker MCP Gateway container, which talks to the MCP servers, in this case DuckDuckGo
	mcpgCtr, err := dmcpg.Run(
		ctx, "docker/mcp-gateway:latest",
		dmcpg.WithTools("duckduckgo", []string{"search", "fetch_content"}),
	)
	testcontainers.CleanupContainer(t, mcpgCtr)
	require.NoError(t, err)

	mcpGatewayURL, err := mcpgCtr.GatewayEndpoint(ctx)
	require.NoError(t, err)

	question := "Does Golang support the Model Context Protocol? Please provide some references."

	answer, err := chat(question, mcpGatewayURL, "no-apiKey", dmrCtr.OpenAIEndpoint(), fqModelName)
	require.NoError(t, err)
	require.NotEmpty(t, answer)
	require.Contains(t, answer, "https://github.com/modelcontextprotocol/go-sdk")
}
