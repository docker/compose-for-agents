package main

import (
	"context"
	"encoding/json"
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	dmcpg "github.com/testcontainers/testcontainers-go/modules/dockermcpgateway"
	"github.com/testcontainers/testcontainers-go/modules/dockermodelrunner"
	"github.com/tmc/langchaingo/agents"
	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/schema"
	"github.com/tmc/langchaingo/vectorstores"
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

func TestChat_embeddings(t *testing.T) {
	embeddingModel, dmrBaseURL := buildEmbeddingsModel(t)

	embedder, err := embeddings.NewEmbedder(embeddingModel)
	require.NoError(t, err)

	reference := `Golang does have an official Go SDK for Model Context Protocol servers and clients, which is maintained in collaboration with Google.
It's URL is https://github.com/modelcontextprotocol/go-sdk`

	// calculate the embeddings for the reference answer
	referenceEmbeddings, err := embedder.EmbedDocuments(context.Background(), []string{reference})
	require.NoError(t, err)

	ctx := context.Background()

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
	answer, err := chat(question, mcpGatewayURL, "no-apiKey", dmrBaseURL, fqModelName)
	require.NoError(t, err)
	require.NotEmpty(t, answer)

	t.Logf("answer: %s", answer)

	// calculate the embeddings for the answer of the model
	answerEmbeddings, err := embedder.EmbedDocuments(context.Background(), []string{answer})
	require.NoError(t, err)

	// calculate the cosine similarity between the reference and the answer
	cosineSimilarity := cosineSimilarity(t, referenceEmbeddings[0], answerEmbeddings[0])
	t.Logf("cosine similarity: %f", cosineSimilarity)

	// Define a threshold for the cosine similarity: this is a team decision to accept or reject the answer
	// within the given threshold.
	require.Greater(t, cosineSimilarity, float32(0.8))
}

func TestChat_rag(t *testing.T) {
	const question = "Does Golang support the Model Context Protocol? Please provide some references."

	embeddingModel, dmrBaseURL := buildEmbeddingsModel(t)

	embedder, err := embeddings.NewEmbedder(embeddingModel)
	require.NoError(t, err)

	reference := `Golang does have an official Go SDK for Model Context Protocol servers and clients, which is maintained in collaboration with Google.
It's URL is https://github.com/modelcontextprotocol/go-sdk`

	// create a new Weaviate store to store the reference answer
	store, err := NewStore(t, embedder)
	require.NoError(t, err)

	_, err = store.AddDocuments(context.Background(), []schema.Document{
		{
			PageContent: reference,
		},
	})
	require.NoError(t, err)

	optionsVector := []vectorstores.Option{
		vectorstores.WithScoreThreshold(0.80), // use for precision, when you want to get only the most relevant documents
		vectorstores.WithEmbedder(embedder),   // use when you want add documents or doing similarity search
	}

	relevantDocs, err := store.SimilaritySearch(context.Background(), question, 1, optionsVector...)
	require.NoError(t, err)
	require.NotEmpty(t, relevantDocs)

	ctx := context.Background()

	// Docker MCP Gateway container, which talks to the MCP servers, in this case DuckDuckGo
	mcpgCtr, err := dmcpg.Run(
		ctx, "docker/mcp-gateway:latest",
		dmcpg.WithTools("duckduckgo", []string{"search", "fetch_content"}),
	)
	testcontainers.CleanupContainer(t, mcpgCtr)
	require.NoError(t, err)

	mcpGatewayURL, err := mcpgCtr.GatewayEndpoint(ctx)
	require.NoError(t, err)

	answer, err := chat(
		question,
		mcpGatewayURL,
		"no-apiKey",
		dmrBaseURL,
		fqModelName,
		agents.WithPromptSuffix(fmt.Sprintf("Use the following relevant documents to answer the question: %s", relevantDocs[0].PageContent)),
	)
	require.NoError(t, err)
	require.NotEmpty(t, answer)

	t.Logf("answer: %s", answer)
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
