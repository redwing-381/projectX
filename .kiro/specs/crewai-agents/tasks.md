# Implementation Plan: CrewAI Agents

## Overview

Refactor ProjectX to use CrewAI for multi-agent orchestration with Monitor, Classifier, and Alert agents.

## Tasks

- [x] 1. Add CrewAI dependency and configuration
  - Add `crewai` to pyproject.toml dependencies
  - Update `src/config.py` to include CrewAI settings
  - Verify OpenRouter API compatibility with CrewAI LLM
  - _Requirements: 1.1, 1.2_

- [x] 2. Create agent definitions
  - [x] 2.1 Create `src/agents/definitions.py` with agent factory functions
    - `create_monitor_agent()` - analyzes email metadata
    - `create_classifier_agent()` - determines urgency
    - `create_alert_agent()` - formats SMS messages
    - _Requirements: 2.1, 3.2, 4.2_

  - [x]* 2.2 Write property test for classification output validity
    - **Property 2: Classification output validity**
    - **Validates: Requirements 3.3, 3.4**

- [x] 3. Create task definitions
  - [x] 3.1 Create `src/agents/tasks.py` with task factory functions
    - `create_monitor_task()` - email analysis task
    - `create_classifier_task()` - urgency classification task
    - `create_alert_task()` - SMS formatting task
    - _Requirements: 2.3, 3.2, 4.3_

  - [x]* 3.2 Write property test for SMS format validity
    - **Property 3: SMS format validity**
    - **Validates: Requirements 4.2, 4.3, 4.4**

- [x] 4. Create crew orchestration
  - [x] 4.1 Create `src/agents/crew.py` with EmailProcessingCrew class
    - Initialize LLM with OpenRouter configuration
    - Create all three agents
    - `process_email()` method to run crew on single email
    - `_parse_result()` to extract Classification from crew output
    - _Requirements: 5.1, 5.2, 5.3_

  - [x]* 4.2 Write property test for crew result schema conformance
    - **Property 4: Crew result schema conformance**
    - **Validates: Requirements 5.3**

  - [x]* 4.3 Write property test for error handling
    - **Property 5: Error handling graceful degradation**
    - **Validates: Requirements 5.4**

- [x] 5. Update pipeline to use CrewAI
  - [x] 5.1 Refactor `src/services/pipeline.py`
    - Replace ClassifierAgent with EmailProcessingCrew
    - Update `run()` method to use crew.process_email()
    - Maintain same PipelineResult output format
    - _Requirements: 1.3, 5.3_

- [x] 6. Update main.py initialization
  - [x] 6.1 Update `src/main.py` to initialize CrewAI crew
    - Create EmailProcessingCrew instead of ClassifierAgent
    - Pass crew to Pipeline
    - Keep existing endpoint signatures
    - _Requirements: 1.3_

- [x] 7. Checkpoint - Verify CrewAI integration works
  - Run locally with `uvicorn src.main:app --reload`
  - Test /health endpoint
  - Test /check endpoint - verify same response format
  - Check logs for agent execution
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Deploy and verify
  - Push to GitHub for Railway auto-deploy
  - Test deployed /check endpoint
  - Verify SMS delivery still works
  - _Requirements: 1.3_

## Notes

- Tasks marked with `*` are optional property tests
- CrewAI requires `crewai` package - ensure it's compatible with Python 3.11+
- OpenRouter API should work with CrewAI's LLM class
- Keep the old ClassifierAgent as fallback during transition
- Monitor Railway logs for any CrewAI-specific issues
