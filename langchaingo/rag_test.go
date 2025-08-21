package main

import (
	"context"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	tcweaviate "github.com/testcontainers/testcontainers-go/modules/weaviate"
	"github.com/tmc/langchaingo/embeddings"
	"github.com/tmc/langchaingo/vectorstores/weaviate"
)

// NewStore creates a new Weaviate store. It will use a weaviate container to store the data.
func NewStore(t *testing.T, embedder embeddings.Embedder) (weaviate.Store, error) {
	t.Helper()

	ctx := context.Background()

	c, err := tcweaviate.Run(ctx, "semitechnologies/weaviate:1.32.1")
	testcontainers.CleanupContainer(t, c)
	require.NoError(t, err)

	schema, host, err := c.HttpHostAddress(ctx)
	require.NoError(t, err)

	return weaviate.New(
		weaviate.WithScheme(schema),
		weaviate.WithHost(host),
		weaviate.WithIndexName("Testcontainers"),
		weaviate.WithEmbedder(embedder),
	)
}
