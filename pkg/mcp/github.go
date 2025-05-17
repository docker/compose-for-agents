package mcp

import (
	"encoding/json"

	"github.com/mark3labs/mcp-go/mcp"

	"github.com/google/go-github/v55/github"
)

func slimListIssuesOutput(content mcp.Content) mcp.Content {
	textContent, ok := mcp.AsTextContent(content)
	if !ok {
		return content
	}
	var results []*github.Issue
	if err := json.Unmarshal([]byte(textContent.Text), &results); err != nil {
		return content
	}
	for _, result := range results {
		result.ID = nil
		if result.User != nil {
			result.User = &github.User{Login: result.User.Login}
		}
		result.Labels = nil
		result.Assignee = nil
		if result.ClosedBy != nil {
			result.ClosedBy = &github.User{Login: result.ClosedBy.Login}
		}
		result.URL = nil
		result.HTMLURL = nil
		result.CommentsURL = nil
		result.EventsURL = nil
		result.LabelsURL = nil
		result.RepositoryURL = nil
		result.Milestone = nil
		result.PullRequestLinks = nil
		result.Repository = nil
		result.Reactions = nil
		result.Assignees = nil
		result.NodeID = nil
		result.TextMatches = nil
	}
	result, err := json.Marshal(results)
	if err != nil {
		return content
	}
	return mcp.NewTextContent(string(result))
}
