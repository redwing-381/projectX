# Requirements Document

## Introduction

Refactor ProjectX to use CrewAI for multi-agent orchestration. Replace the current single direct-OpenAI classifier with a proper CrewAI crew consisting of specialized agents that collaborate to monitor, classify, and alert on urgent emails.

## Glossary

- **System**: The ProjectX application
- **Crew**: A CrewAI crew that orchestrates multiple agents
- **Monitor_Agent**: Agent responsible for analyzing email metadata and context
- **Classifier_Agent**: Agent that determines email urgency based on content analysis
- **Alert_Agent**: Agent that decides alert formatting and delivery
- **Task**: A CrewAI task assigned to an agent
- **Email**: A Gmail message to be processed

## Requirements

### Requirement 1: CrewAI Integration

**User Story:** As a developer, I want the system to use CrewAI framework, so that I can leverage multi-agent orchestration capabilities.

#### Acceptance Criteria

1. THE System SHALL use CrewAI library for agent orchestration
2. THE System SHALL configure CrewAI to use OpenRouter API with GPT-4o-mini model
3. THE System SHALL maintain backward compatibility with existing /check endpoint

### Requirement 2: Monitor Agent

**User Story:** As a user, I want an agent to analyze email metadata, so that context is gathered before classification.

#### Acceptance Criteria

1. THE Monitor_Agent SHALL analyze email sender, subject, and timestamp
2. THE Monitor_Agent SHALL identify sender patterns (known contacts, domains, frequency)
3. THE Monitor_Agent SHALL output a context summary for the Classifier_Agent

### Requirement 3: Classifier Agent

**User Story:** As a user, I want an agent to classify email urgency, so that only important emails trigger alerts.

#### Acceptance Criteria

1. THE Classifier_Agent SHALL receive context from Monitor_Agent
2. THE Classifier_Agent SHALL analyze email content for urgency indicators
3. THE Classifier_Agent SHALL return urgency: URGENT or NOT_URGENT
4. THE Classifier_Agent SHALL provide a one-line reason for the classification

### Requirement 4: Alert Agent

**User Story:** As a user, I want an agent to format alerts, so that SMS messages are concise and informative.

#### Acceptance Criteria

1. THE Alert_Agent SHALL receive classification results from Classifier_Agent
2. WHEN urgency is URGENT, THE Alert_Agent SHALL format an SMS message
3. THE Alert_Agent SHALL ensure SMS message is under 160 characters
4. THE Alert_Agent SHALL include sender and subject in the message

### Requirement 5: Crew Orchestration

**User Story:** As a developer, I want agents to work together as a crew, so that email processing is coordinated.

#### Acceptance Criteria

1. THE Crew SHALL execute agents in sequence: Monitor → Classifier → Alert
2. THE Crew SHALL pass context between agents via task outputs
3. THE Crew SHALL return a structured result matching PipelineResult schema
4. IF any agent fails, THEN THE Crew SHALL handle the error gracefully and continue

