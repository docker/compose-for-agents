package com.example.api;

import akka.http.javadsl.model.HttpResponse;
import akka.http.javadsl.model.MediaTypes;
import akka.http.javadsl.model.headers.ContentType;
import akka.javasdk.annotations.Acl;
import akka.javasdk.annotations.http.HttpEndpoint;
import akka.javasdk.annotations.http.Post;
import akka.javasdk.http.AbstractHttpEndpoint;
import akka.javasdk.client.ComponentClient;
import akka.javasdk.http.HttpResponses;
import com.example.application.GreetingAgent;

@HttpEndpoint("/chat")
@Acl(allow = @Acl.Matcher(principal = Acl.Principal.ALL))
public class GreetingAgentEndpoint extends AbstractHttpEndpoint {

    private final ComponentClient componentClient;

    public GreetingAgentEndpoint(ComponentClient componentClient) {
        this.componentClient = componentClient;
    }

    public record QueryRequest(String userId, String question) {}

    @Post("/ask")
    public HttpResponse ask(QueryRequest request) {
        var tokenStream = componentClient
                .forAgent()
                .inSession(request.userId())
                .tokenStream(GreetingAgent::ask)
                .source(request.question());

        return HttpResponses.serverSentEvents(tokenStream);
    }
}