package main

import (
	"context"
	"encoding/json"
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

func TestChat_stringComparison(t *testing.T) {
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

func TestChat_usingEvaluator(t *testing.T) {
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

	t.Logf("answer: %s", answer)

	// cross the answer with the evaluator
	reference := `There is an official Go SDK for Model Context Protocol servers and clients, which is maintained in collaboration with Google.
It's URL is https://github.com/modelcontextprotocol/go-sdk`

	evaluator := NewEvaluator(question, fqModelName, "no-apiKey", dmrCtr.OpenAIEndpoint())
	evaluation, err := evaluator.Evaluate(ctx, question, answer, reference)
	require.NoError(t, err)
	t.Logf("evaluation: %#v", evaluation)

	type evalResponse struct {
		ProvidedAnswer string `json:"provided_answer"`
		IsCorrect      bool   `json:"is_correct"`
		Reasoning      string `json:"reasoning"`
	}

	var eval evalResponse
	err = json.Unmarshal([]byte(evaluation), &eval)
	require.NoError(t, err)

	t.Logf("evaluation: %#v", eval)
	require.True(t, eval.IsCorrect)
}
