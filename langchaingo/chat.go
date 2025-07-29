package main

import (
	"context"
	"fmt"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/tmc/langchaingo/agents"
	"github.com/tmc/langchaingo/callbacks"
	"github.com/tmc/langchaingo/chains"
)

// chat is the main function that initializes the LLM, MCP tools, and runs the agent.
// It receives the question and the MCP gateway URL, returning the answer from the agent.
func chat(question string, mcpGatewayURL string) (string, error) {
	llm, err := initializeLLM()
	if err != nil {
		return "", fmt.Errorf("initialize LLM: %v", err)
	}

	// Create a new client, with no features.
	client := mcp.NewClient(&mcp.Implementation{Name: "mcp-client", Version: "v1.0.0"}, nil)

	toolBelt, err := initializeMCPTools(client, mcpGatewayURL)
	if err != nil {
		return "", fmt.Errorf("initialize MCP tools: %v", err)
	}

	agent := agents.NewOneShotAgent(llm, toolBelt, agents.WithCallbacksHandler(callbacks.LogHandler{}))
	executor := agents.NewExecutor(agent)

	answer, err := chains.Run(context.Background(), executor, question)
	if err != nil {
		return "", fmt.Errorf("chains run: %v", err)
	}

	return answer, nil
}
