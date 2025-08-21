package main

import (
	"context"
	"testing"

	"github.com/chewxy/math32"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/dockermodelrunner"
	"github.com/tmc/langchaingo/llms/openai"
)

const (
	embeddingsModelName   = "mxbai-embed-large"
	embeddingsModelTag    = "335M-F16"
	fqEmbeddingsModelName = modelNamespace + "/" + embeddingsModelName + ":" + embeddingsModelTag
)

// buildEmbeddingsModel builds an embedding model using Docker Model Runner.
// It returns the LLM and the base URL of the Docker Model Runner container,
// which is an OpenAI-compatible endpoint.
func buildEmbeddingsModel(t *testing.T) (*openai.LLM, string) {
	t.Helper()

	dmrCtr, err := dockermodelrunner.Run(
		context.Background(),
		dockermodelrunner.WithModel(fqEmbeddingsModelName),
	)
	testcontainers.CleanupContainer(t, dmrCtr)
	require.NoError(t, err)

	opts := []openai.Option{
		openai.WithBaseURL(dmrCtr.OpenAIEndpoint()),
		openai.WithEmbeddingModel(fqEmbeddingsModelName),
		openai.WithToken("foo"), // No API key needed for Model Runner
	}

	llm, err := openai.New(opts...)
	require.NoError(t, err)

	return llm, dmrCtr.OpenAIEndpoint()
}

// cosineSimilarity calculates the cosine similarity between two vectors.
// See https://github.com/tmc/langchaingo/blob/238d1c713de3ca983e8f6066af6b9080c9b0e088/examples/cybertron-embedding-example/cybertron-embedding.go#L19
func cosineSimilarity(t *testing.T, x, y []float32) float32 {
	t.Helper()

	require.Equal(t, len(x), len(y))

	var dot, nx, ny float32

	for i := range x {
		nx += x[i] * x[i]
		ny += y[i] * y[i]
		dot += x[i] * y[i]
	}

	return dot / (math32.Sqrt(nx) * math32.Sqrt(ny))
}
