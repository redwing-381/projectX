# Product Overview

## Product Purpose
ProjectX is a smart notification bridge that monitors your Gmail inbox, uses AI agents to detect urgent messages, and forwards alerts via SMS to a basic keypad phone. It enables developers and students to stay focused during work hours without missing critical communications.

## Target Users
- Developers and software engineers who want to minimize smartphone distractions
- Students who need focus time but can't miss urgent college/work emails
- Anyone who wants to use a basic keypad phone during work but stay reachable for emergencies
- People with small contact circles who receive manageable email volumes

## Key Features
- **Gmail Monitoring**: Real-time email monitoring via Gmail API
- **AI Urgency Detection**: CrewAI agents classify email urgency using LLM
- **SMS Alerts**: Twilio integration sends condensed alerts to keypad phones
- **VIP Sender List**: Whitelist important contacts for automatic priority
- **Keyword Rules**: Custom keywords trigger urgent classification
- **CLI Control**: Terminal commands for quick status checks and control
- **Web Dashboard**: Browser interface for setup, rules configuration, and history

## Business Objectives
- Enable distraction-free work periods
- Ensure critical messages are never missed
- Provide simple, intuitive urgency configuration
- Demonstrate AI agent orchestration for practical use cases

## User Journey
1. **Setup**: User connects Gmail via OAuth on web dashboard
2. **Configure**: User sets VIP senders and urgency keywords
3. **Activate**: System starts monitoring in background
4. **Work**: User works with keypad phone, smartphone away
5. **Alert**: Urgent email arrives → AI classifies → SMS sent
6. **Control**: User can pause/resume via CLI or dashboard
7. **Review**: End of day, check dashboard for full history

## Success Criteria
- Emails classified within 30 seconds of arrival
- SMS delivered within 1 minute of urgent classification
- Zero missed urgent emails (false negatives)
- Low false positive rate (<10% unnecessary alerts)
- CLI commands respond in <2 seconds
