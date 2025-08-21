package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/openai"
	"github.com/tmc/langchaingo/tools"
)

func main() {
	// Get the question from environment variable
	question := os.Getenv("QUESTION")
	if question == "" {
		log.Fatal("Environment variable QUESTION must be set and non-empty.")
	}

	log.Println("QUESTION:", question)

	// Get MCP gateway URL from environment
	mcpGatewayURL := os.Getenv("MCP_GATEWAY_URL")
	if mcpGatewayURL == "" {
		mcpGatewayURL = "http://localhost:8811"
	}

	// Get OpenAI configuration from environment
	apiKey := os.Getenv("OPENAI_API_KEY")
	if apiKey == "" {
		apiKey = "cannot_be_empty" // Default for local model runner
	}

	baseURL := os.Getenv("OPENAI_BASE_URL")
	if baseURL == "" {
		baseURL = "https://api.openai.com/v1"
	}

	modelName := os.Getenv("OPENAI_MODEL_NAME")
	if modelName == "" {
		modelName = "gpt-3.5-turbo" // Default model
	}

	result, err := chat(question, mcpGatewayURL, apiKey, baseURL, modelName)
	if err != nil {
		log.Fatalf("Failed to chat: %v", err)
	}

	log.Println("ASSISTANT:", result)
}

func initializeLLM(apiKey string, baseURL string, modelName string) (llms.Model, error) {
	// Create OpenAI client
	return openai.New(
		openai.WithToken(apiKey),
		openai.WithBaseURL(baseURL),
		openai.WithModel(modelName),
	)
}

func initializeMCPTools(client *mcp.Client, mcpGatewayURL string) ([]tools.Tool, error) {
	transport := mcp.NewSSEClientTransport(mcpGatewayURL, nil)

	cs, err := client.Connect(context.Background(), transport)
	if err != nil {
		return nil, fmt.Errorf("connect to MCP gateway: %v", err)
	}

	mcpTools, err := cs.ListTools(context.Background(), &mcp.ListToolsParams{})
	if err != nil {
		return nil, fmt.Errorf("list tools: %v", err)
	}

	var errs []error

	toolBelt := make([]tools.Tool, len(mcpTools.Tools))
	for i, tool := range mcpTools.Tools {
		args := map[string]any{}
		switch tool.Name {
		case "fetch_content":
		case "search":
			args["max_results"] = 10
		default:
			errs = append(errs, fmt.Errorf("unsupported tool: %s", tool.Name))
		}

		toolBelt[i] = &DuckDuckGoTool{
			clientSession: cs,
			mcpTool:       tool,
			args:          args,
		}
	}

	if len(errs) > 0 {
		return nil, errors.Join(errs...)
	}

	return toolBelt, nil
}
