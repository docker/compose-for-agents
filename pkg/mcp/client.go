package mcp

import (
	"context"
	"fmt"
	"time"

	"github.com/docker/compose-agents-demo/pkg/docker"
	"github.com/mark3labs/mcp-go/mcp"
)

type Client struct {
	image   string
	pull    bool
	env     []string
	args    []string
	command []string

	c *StdioMCPClient
}

func NewClientArgs(image string, pull bool, env []string, args []string, command []string) *Client {
	return &Client{
		image:   image,
		pull:    pull,
		env:     env,
		args:    args,
		command: command,
	}
}

func (cl *Client) Start(ctx context.Context) error {
	if cl.c != nil {
		return fmt.Errorf("already started %s", cl.image)
	}

	if cl.pull {
		dockerClient, err := docker.NewClient(ctx)
		if err != nil {
			return err
		}

		if err := dockerClient.PullImage(ctx, cl.image); err != nil {
			return fmt.Errorf("pulling image %s: %w", cl.image, err)
		}
	}

	args := []string{"run", "--rm", "-i", "--init", "--pull", "never"}
	args = append(args, cl.args...)
	args = append(args, cl.image)
	args = append(args, cl.command...)
	c := NewMCPClient("docker", cl.env, args...)
	cl.c = c

	initRequest := mcp.InitializeRequest{}
	initRequest.Params.ProtocolVersion = mcp.LATEST_PROTOCOL_VERSION
	initRequest.Params.ClientInfo = mcp.Implementation{
		Name:    "docker",
		Version: "1.0.0",
	}

	ctx, cancel := context.WithTimeout(ctx, 20*time.Second)
	defer cancel()

	if _, err := c.Initialize(ctx, initRequest); err != nil {
		return fmt.Errorf("initializing %s: %w", cl.image, err)
	}
	return nil
}

func (cl *Client) ListTools(ctx context.Context) ([]mcp.Tool, error) {
	if cl.c == nil {
		return nil, fmt.Errorf("listing tools %s: not started", cl.image)
	}

	response, err := cl.c.ListTools(ctx, mcp.ListToolsRequest{})
	if err != nil {
		return nil, fmt.Errorf("listing tools %s: %w", cl.image, err)
	}

	return response.Tools, nil
}

func (cl *Client) CallTool(ctx context.Context, name string, args map[string]any) (*mcp.CallToolResult, error) {
	if cl.c == nil {
		return nil, fmt.Errorf("calling tool %s: not started", name)
	}

	request := mcp.CallToolRequest{}
	request.Params.Name = name
	request.Params.Arguments = args
	if request.Params.Arguments == nil {
		request.Params.Arguments = map[string]any{}
	}
	// MCP servers return an error if the args are empty so we make sure
	// there is at least one argument
	if len(request.Params.Arguments) == 0 {
		request.Params.Arguments["args"] = "..."
	}

	result, err := cl.c.CallTool(ctx, request)
	if err != nil {
		return nil, fmt.Errorf("calling tool %s on %s: %w", name, cl.image, err)
	}

	if name == "list_issues" {
		result.Content[0] = slimListIssuesOutput(result.Content[0])
	}

	return result, nil
}

func (cl *Client) Close() error {
	if cl.c == nil {
		return fmt.Errorf("closing %s: not started", cl.image)
	}
	return cl.c.Close()
}
