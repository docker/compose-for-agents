package com.example;

import akka.javasdk.testkit.TestKitSupport;
import akka.javasdk.testkit.TestModelProvider;
import akka.javasdk.testkit.TestKit;
import akka.stream.javadsl.Keep;
import akka.stream.javadsl.Sink;
import com.example.application.GreetingAgent;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.concurrent.ExecutionException;

import static org.assertj.core.api.Assertions.assertThat;

public class IntegrationTest extends TestKitSupport {

    private final TestModelProvider greetingModel = new TestModelProvider();

    @Override
    protected TestKit.Settings testKitSettings() {
        return TestKit.Settings.DEFAULT
                .withModelProvider(GreetingAgent.class, greetingModel);
    }

    @Test
    public void testGreetingAgent() throws ExecutionException, InterruptedException {
        String fixedResponse = "Hola (Spanish)\n\nPrevious greetings in this session: None";
        greetingModel.fixedResponse(fixedResponse);
        
        var tokenStream = componentClient
                .forAgent()
                .inSession("test-session")
                .tokenStream(GreetingAgent::ask)
                .source("How do you say hello in Spanish?");

        List<String> tokens = tokenStream
                .toMat(Sink.seq(), Keep.right())
                .run(testKit.getMaterializer())
                .toCompletableFuture()
                .get();
        
        String result = String.join("", tokens);
        assertThat(result).isEqualTo(fixedResponse);
    }
}