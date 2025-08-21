package org.springframework.ai.mcp.samples.brave;

import java.util.List;

import io.modelcontextprotocol.client.McpSyncClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.mcp.SyncMcpToolCallbackProvider;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class Application {

	private static final Logger logger = LoggerFactory.getLogger(Application.class);

	public static void main(String[] args) {
		SpringApplication.run(Application.class, args).close();
	}

	@Bean
	public CommandLineRunner predefinedQuestions(ChatClient.Builder chatClientBuilder,
		List<McpSyncClient> mcpSyncClients) {

		return args -> {

			var chatClient = chatClientBuilder
					.defaultToolCallbacks(new SyncMcpToolCallbackProvider(mcpSyncClients))
					.build();

			String question = System.getenv("QUESTION");
			if (question == null || question.isBlank()) {
				throw new IllegalStateException("Environment variable QUESTION must be set and non-empty.");
			}
			logger.info("QUESTION: {}\n", question);
			logger.info("ASSISTANT: {}\n", chatClient.prompt(question).call().content());
		};
	}
}
