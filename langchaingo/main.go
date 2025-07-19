package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/tmc/langchaingo/agents"
	"github.com/tmc/langchaingo/callbacks"
	"github.com/tmc/langchaingo/chains"
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

	llm, err := initializeLLM()
	if err != nil {
		log.Fatalf("Failed to initialize LLM: %v", err)
	}

	// Create a new client, with no features.
	client := mcp.NewClient(&mcp.Implementation{Name: "mcp-client", Version: "v1.0.0"}, nil)

	toolBelt, err := initializeMCPTools(client)
	if err != nil {
		log.Fatalf("Failed to call tool: %v", err)
	}

	agent := agents.NewOneShotAgent(llm, toolBelt, agents.WithCallbacksHandler(callbacks.LogHandler{}))
	executor := agents.NewExecutor(agent)

	result, err := chains.Run(context.Background(), executor, question)
	if err != nil {
		log.Fatalf("Failed to execute question: %v", err)
	}

	log.Println("ASSISTANT:", result)
}

func initializeLLM() (llms.Model, error) {
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

	// Create OpenAI client
	return openai.New(
		openai.WithToken(apiKey),
		openai.WithBaseURL(baseURL),
		openai.WithModel(modelName),
	)
}

func initializeMCPTools(client *mcp.Client) ([]tools.Tool, error) {
	// Get MCP gateway URL from environment
	mcpGatewayURL := os.Getenv("MCP_GATEWAY_URL")
	if mcpGatewayURL == "" {
		mcpGatewayURL = "http://localhost:8811"
	}

	transport := mcp.NewSSEClientTransport(mcpGatewayURL, nil)

	cs, err := client.Connect(context.Background(), transport)
	if err != nil {
		log.Fatalf("Failed to connect to MCP gateway: %v", err)
	}

	mcpTools, err := cs.ListTools(context.Background(), &mcp.ListToolsParams{})
	if err != nil {
		log.Fatalf("Failed to list tools: %v", err)
	}

	toolBelt := make([]tools.Tool, len(mcpTools.Tools))
	for i, tool := range mcpTools.Tools {
		args := map[string]any{}
		switch tool.Name {
		case "fetch_content":
		case "search":
			args["max_results"] = 3
		default:
			return nil, fmt.Errorf("unsupported tool: %s", tool.Name)
		}

		toolBelt[i] = &DuckDuckGoTool{
			clientSession: cs,
			mcpTool:       tool,
			args:          args,
		}
	}

	return toolBelt, nil
}
