package main

import (
	"context"
	"fmt"
	"os"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/tmc/langchaingo/agents"
	"github.com/tmc/langchaingo/callbacks"
	"github.com/tmc/langchaingo/chains"
)

// chat is the main function that initializes the LLM, MCP tools, and runs the agent.
// It receives the question and the MCP gateway URL, returning the answer from the agent.
func chat(question string, mcpGatewayURL string, apiKey string, baseURL string, modelName string, agentOpts ...agents.Option) (string, error) {
	llm, err := initializeLLM(apiKey, baseURL, modelName)
	if err != nil {
		return "", fmt.Errorf("initialize LLM: %v", err)
	}

	// Create a new client, with no features.
	client := mcp.NewClient(&mcp.Implementation{Name: "mcp-client", Version: "v1.0.0"}, nil)

	toolBelt, err := initializeMCPTools(client, mcpGatewayURL)
	if err != nil {
		return "", fmt.Errorf("initialize MCP tools: %v", err)
	}

	if os.Getenv("DEBUG") == "true" {
		agentOpts = append(agentOpts, agents.WithCallbacksHandler(callbacks.LogHandler{}))
	}

	agent := agents.NewOneShotAgent(llm, toolBelt, agentOpts...)
	executor := agents.NewExecutor(agent)

	answer, err := chains.Run(context.Background(), executor, question)
	if err != nil {
		return "", fmt.Errorf("chains run: %v", err)
	}

	return answer, nil
}
