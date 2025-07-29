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
	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/openai"
)

const (
	// systemMessage is the system message for the strict evaluator.
	systemMessage = `
You are a helpful assistant that evaluates the accuracy of the answer to the question.

You will be given a question and an answer.

You will need to evaluate the accuracy of the answer to the question.

You will need to return a formatted JSON object with the following fields:
- "provided_answer": the answer to the question
- "is_correct": true if the answer is correct, false otherwise
- "reasoning": the reasoning behind the answer

The response should be a valid JSON object.

Example: to the question "What is the capital of France?", the answer is "Paris".
{

	"provided_answer": "Madrid",
	"is_correct": false,
	"reasoning": "The answer is incorrect because the capital of France is not Madrid."
}

Example: to the question "What is the capital of France?", the answer is "Paris".
{
	"provided_answer": "Paris",
	"is_correct": true,
	"reasoning": "The answer is correct because it is the capital of France."
}

Do not include in the JSON response any other text than the JSON object.
- remove all markdown formatting like the backticks for json code blocks
- remove all non-printable characters, like \n, \r, \t, etc.
`

	// userPrompt is the prompt for the user message.
	userMessage = `
Question: %s
Answer: %s
Reference: %s

JSON response:
`
)

// evaluator is the evaluator for the answer to the question.
// It uses a LLM to evaluate the accuracy of the answer to the question.
// For that, it uses a system message and a user message that forces the LLM to return a JSON object with the following fields:
// - "provided_answer": the answer to the question
// - "is_correct": true if the answer is correct, false otherwise
// - "reasoning": the reasoning behind the answer
//
// The response should be a valid JSON object.
type evaluator struct {
	systemMessage string
	userMessage   string
	question      string
	model         string
	apiKey        string
	baseURL       string
}

// NewEvaluator creates a new evaluator.
// The question is the question to evaluate the answer to.
// The model is the model to use for the OpenAI-compatible API.
// The apiKey is the API key to use for the OpenAI-compatible API.
// The baseURL is the base URL to use for the OpenAI-compatible API.
func NewEvaluator(question string, model string, apiKey string, baseURL string) *evaluator {
	return &evaluator{
		systemMessage: systemMessage,
		userMessage:   userMessage,
		question:      question,
		model:         model,
		apiKey:        apiKey,
		baseURL:       baseURL,
	}
}

// Evaluate evaluates the accuracy of the answer to the question.
// It returns the evaluation result as a JSON string.
// The opts are the options for the LLM call.
func (e *evaluator) Evaluate(ctx context.Context, question string, answer string, reference string, opts ...llms.CallOption) (string, error) {
	llm, err := openai.New(
		openai.WithToken(e.apiKey),
		openai.WithBaseURL(e.baseURL),
		openai.WithModel(e.model),
	)
	if err != nil {
		return "", fmt.Errorf("failed to create LLM: %w", err)
	}

	content := []llms.MessageContent{
		llms.TextParts(llms.ChatMessageTypeSystem, e.systemMessage),
		llms.TextParts(llms.ChatMessageTypeHuman, fmt.Sprintf(e.userMessage, question, answer, reference)),
	}

	callOpts := []llms.CallOption{
		llms.WithTemperature(0.00),
		llms.WithTopK(1),
		llms.WithSeed(42),
	}
	callOpts = append(callOpts, opts...)

	completion, err := llm.GenerateContent(ctx, content, callOpts...)
	if err != nil {
		return "", fmt.Errorf("llm generate content: %w", err)
	}

	response := ""
	for _, choice := range completion.Choices {
		response += choice.Content
	}

	return response, nil
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
