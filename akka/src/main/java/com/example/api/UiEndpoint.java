package com.example.api;

import akka.actor.Cancellable;
import akka.http.javadsl.model.HttpResponse;
import akka.javasdk.agent.SessionHistory;
import akka.javasdk.agent.SessionMemoryEntity;
import akka.javasdk.agent.SessionMessage;
import akka.javasdk.annotations.Acl;
import akka.javasdk.annotations.http.Get;
import akka.javasdk.annotations.http.HttpEndpoint;
import akka.javasdk.client.ComponentClient;
import akka.javasdk.http.HttpResponses;
import akka.stream.javadsl.Source;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Optional;

/**
 * This Http endpoint returns the static UI page located under
 * src/main/resources/static-resources/
 */
@HttpEndpoint
@Acl(allow = @Acl.Matcher(principal = Acl.Principal.ALL))
public class UiEndpoint {

  @Get("/")
  public HttpResponse index() { return HttpResponses.staticResource("index.html"); }
  @Get("/style.css")
  public HttpResponse style() {
    return HttpResponses.staticResource("style.css");
  }
}
