---
name: Leon Personal Assistant
description: Rules for managing and configuring Leon, the open-source personal assistant.
version: 1.0
owner: Georg
tags: [leon, assistant, core, brain]
allowed-tools: ["run_command", "read_url_content"]
---

# Leon Personal Assistant

## Role

Leon is the **"Virtual Brain"** foundation of The Beast.
He acts as the primary interface for voice and chat interactions, orchestrating other modules (Simply, AnythingLLM) when necessary.

## Core Responsibilities

1. **Privacy First**: Leon runs locally. No data leaves the server without explicit permission.
2. **Orchestrator**: Leon determines if a request is a simple command (e.g., "Set alarm") or a complex task requiring The Beast's agents (e.g., "Research this topic").
3. **Personality**: Leon shares the same "Brand Voice" as The Beast but is more conversational and service-oriented.

## Configuration Guidelines

- **Modules**: Enable modules selectively to keep the footprint light.
- **NLU**: Use the local NLU engine.
- **TTS/STT**: Use offline or privacy-focused cloud fallbacks (only if necessary).

## Integration Points

- **Ollama**: Leon should use Ollama for general conversation (fallback from specific modules).
- **AnythingLLM**: Leon queries AnythingLLM for knowledge retrieval.
