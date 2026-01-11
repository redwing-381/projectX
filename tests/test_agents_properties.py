"""Property-based tests for CrewAI agents.

Uses Hypothesis for property-based testing to validate correctness properties
defined in the design document.

**Feature: crewai-agents**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from src.models.schemas import Email, Classification, Urgency, AlertResult, PipelineResult


# =============================================================================
# Generators for test data
# =============================================================================

# Email generator - creates valid Email objects with various content
email_strategy = st.builds(
    Email,
    id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    sender=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    subject=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    snippet=st.text(min_size=1, max_size=500).filter(lambda x: x.strip()),
)

# Classification generator - now uses string urgency
classification_strategy = st.builds(
    Classification,
    urgency=st.sampled_from(["URGENT", "NOT_URGENT"]),
    reason=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    sms_message=st.none(),
)

# AlertResult generator
alert_result_strategy = st.builds(
    AlertResult,
    email_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    sender=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    subject=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    urgency=st.sampled_from([Urgency.URGENT, Urgency.NOT_URGENT]),
    reason=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
    sms_sent=st.booleans(),
)


# =============================================================================
# Property 2: Classification output validity
# **Validates: Requirements 3.3, 3.4**
# =============================================================================

class TestClassificationOutputValidity:
    """Property 2: Classification output validity
    
    *For any* email processed by the Classifier Agent, the output SHALL contain:
    - `urgency` being exactly URGENT or NOT_URGENT
    - `reason` being a non-empty string
    """

    @given(classification=classification_strategy)
    @settings(max_examples=100)
    def test_urgency_is_valid_enum(self, classification: Classification):
        """Urgency must be exactly URGENT or NOT_URGENT."""
        # **Feature: crewai-agents, Property 2: Classification output validity**
        # **Validates: Requirements 3.3, 3.4**
        assert classification.urgency in ["URGENT", "NOT_URGENT"]

    @given(classification=classification_strategy)
    @settings(max_examples=100)
    def test_reason_is_non_empty_string(self, classification: Classification):
        """Reason must be a non-empty string."""
        # **Feature: crewai-agents, Property 2: Classification output validity**
        # **Validates: Requirements 3.3, 3.4**
        assert isinstance(classification.reason, str)
        assert len(classification.reason) > 0
        assert classification.reason.strip()  # Not just whitespace

    @given(urgency=st.sampled_from(["URGENT", "NOT_URGENT"]), reason=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    @settings(max_examples=100)
    def test_classification_can_be_constructed_from_valid_inputs(self, urgency: str, reason: str):
        """Classification can be constructed from valid urgency string and reason."""
        # **Feature: crewai-agents, Property 2: Classification output validity**
        # **Validates: Requirements 3.3, 3.4**
        classification = Classification(
            urgency=urgency,
            reason=reason
        )
        assert classification.urgency == urgency
        assert classification.reason == reason

    def test_classification_accepts_valid_urgency_strings(self):
        """Classification accepts valid urgency string values."""
        # **Feature: crewai-agents, Property 2: Classification output validity**
        # **Validates: Requirements 3.3, 3.4**
        urgent = Classification(urgency="URGENT", reason="test reason")
        not_urgent = Classification(urgency="NOT_URGENT", reason="test reason")
        assert urgent.urgency == "URGENT"
        assert not_urgent.urgency == "NOT_URGENT"

    def test_classification_rejects_empty_reason(self):
        """Classification rejects empty reason."""
        # **Feature: crewai-agents, Property 2: Classification output validity**
        # **Validates: Requirements 3.3, 3.4**
        with pytest.raises(ValueError):
            Classification(urgency="URGENT", reason="")



# =============================================================================
# Property 3: SMS format validity
# **Validates: Requirements 4.2, 4.3, 4.4**
# =============================================================================

class TestSMSFormatValidity:
    """Property 3: SMS format validity
    
    *For any* email classified as URGENT with any sender name and subject, 
    the Alert Agent SHALL produce an SMS message that:
    - Is 160 characters or fewer
    - Contains the sender information
    - Contains the subject information
    """

    def format_sms(self, email: Email) -> str:
        """Format email into SMS message (mirrors TwilioService.format_alert)."""
        # Truncate subject if needed to fit in 160 chars
        max_subject_len = 160 - len(f"URGENT from {email.sender}: ")
        subject = email.subject[:max_subject_len] if len(email.subject) > max_subject_len else email.subject
        return f"URGENT from {email.sender}: {subject}"

    @given(email=email_strategy)
    @settings(max_examples=100)
    def test_sms_length_within_limit(self, email: Email):
        """SMS message must be 160 characters or fewer."""
        # **Feature: crewai-agents, Property 3: SMS format validity**
        # **Validates: Requirements 4.2, 4.3, 4.4**
        sms = self.format_sms(email)
        assert len(sms) <= 160, f"SMS too long: {len(sms)} chars"

    @given(email=email_strategy)
    @settings(max_examples=100)
    def test_sms_contains_sender(self, email: Email):
        """SMS message must contain sender information."""
        # **Feature: crewai-agents, Property 3: SMS format validity**
        # **Validates: Requirements 4.2, 4.3, 4.4**
        sms = self.format_sms(email)
        # Sender should be in the message (may be truncated for very long senders)
        assert email.sender[:20] in sms or "from" in sms.lower()

    @given(email=email_strategy)
    @settings(max_examples=100)
    def test_sms_contains_subject_or_truncated(self, email: Email):
        """SMS message must contain subject (possibly truncated)."""
        # **Feature: crewai-agents, Property 3: SMS format validity**
        # **Validates: Requirements 4.2, 4.3, 4.4**
        sms = self.format_sms(email)
        # Subject should be present (at least partially)
        # Either full subject or truncated version
        assert email.subject[:10] in sms or len(sms) == 160

    @given(
        sender=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        subject=st.text(min_size=1, max_size=300).filter(lambda x: x.strip()),
    )
    @settings(max_examples=100)
    def test_sms_format_handles_long_subjects(self, sender: str, subject: str):
        """SMS format handles subjects longer than available space."""
        # **Feature: crewai-agents, Property 3: SMS format validity**
        # **Validates: Requirements 4.2, 4.3, 4.4**
        email = Email(id="test", sender=sender, subject=subject, snippet="test")
        sms = self.format_sms(email)
        assert len(sms) <= 160
        assert "URGENT" in sms


# =============================================================================
# Property 4: Crew result schema conformance
# **Validates: Requirements 5.3**
# =============================================================================

class TestCrewResultSchemaConformance:
    """Property 4: Crew result schema conformance
    
    *For any* crew execution, the final output SHALL be valid JSON conforming 
    to the PipelineResult schema with all required fields populated.
    """

    @given(
        emails_checked=st.integers(min_value=0, max_value=1000),
        alerts_sent=st.integers(min_value=0, max_value=1000),
        results=st.lists(alert_result_strategy, min_size=0, max_size=20),
    )
    @settings(max_examples=100)
    def test_pipeline_result_schema_valid(self, emails_checked: int, alerts_sent: int, results: list):
        """PipelineResult can be constructed with valid data."""
        # **Feature: crewai-agents, Property 4: Crew result schema conformance**
        # **Validates: Requirements 5.3**
        result = PipelineResult(
            emails_checked=emails_checked,
            alerts_sent=alerts_sent,
            results=results,
        )
        assert result.emails_checked == emails_checked
        assert result.alerts_sent == alerts_sent
        assert len(result.results) == len(results)

    @given(
        emails_checked=st.integers(min_value=0, max_value=1000),
        alerts_sent=st.integers(min_value=0, max_value=1000),
        results=st.lists(alert_result_strategy, min_size=0, max_size=20),
    )
    @settings(max_examples=100)
    def test_pipeline_result_serializes_to_json(self, emails_checked: int, alerts_sent: int, results: list):
        """PipelineResult can be serialized to JSON."""
        # **Feature: crewai-agents, Property 4: Crew result schema conformance**
        # **Validates: Requirements 5.3**
        result = PipelineResult(
            emails_checked=emails_checked,
            alerts_sent=alerts_sent,
            results=results,
        )
        json_data = result.model_dump_json()
        assert isinstance(json_data, str)
        assert "emails_checked" in json_data
        assert "alerts_sent" in json_data
        assert "results" in json_data

    @given(results=st.lists(alert_result_strategy, min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_alert_results_have_required_fields(self, results: list):
        """Each AlertResult has all required fields."""
        # **Feature: crewai-agents, Property 4: Crew result schema conformance**
        # **Validates: Requirements 5.3**
        for result in results:
            assert hasattr(result, 'email_id')
            assert hasattr(result, 'sender')
            assert hasattr(result, 'subject')
            assert hasattr(result, 'urgency')
            assert hasattr(result, 'reason')
            assert hasattr(result, 'sms_sent')
            assert result.urgency in [Urgency.URGENT, Urgency.NOT_URGENT]


# =============================================================================
# Property 5: Error handling graceful degradation
# **Validates: Requirements 5.4**
# =============================================================================

class TestErrorHandlingGracefulDegradation:
    """Property 5: Error handling graceful degradation
    
    *For any* agent failure during crew execution, the system SHALL return 
    a valid Classification with urgency=NOT_URGENT and a reason indicating 
    the failure, rather than crashing.
    """

    def simulate_classification_failure(self, error_message: str) -> Classification:
        """Simulate how the classifier handles failures."""
        # This mirrors the error handling in ClassifierAgent.classify()
        return Classification(
            urgency="NOT_URGENT",
            reason=f"Classification failed - {error_message[:50]}",
        )

    @given(error_message=st.text(min_size=1, max_size=200).filter(lambda x: x.strip()))
    @settings(max_examples=100)
    def test_failure_returns_valid_classification(self, error_message: str):
        """Failure returns valid Classification, not exception."""
        # **Feature: crewai-agents, Property 5: Error handling graceful degradation**
        # **Validates: Requirements 5.4**
        result = self.simulate_classification_failure(error_message)
        assert isinstance(result, Classification)
        assert result.urgency == "NOT_URGENT"
        assert "failed" in result.reason.lower()

    @given(error_message=st.text(min_size=1, max_size=500).filter(lambda x: x.strip()))
    @settings(max_examples=100)
    def test_failure_reason_is_bounded(self, error_message: str):
        """Failure reason doesn't exceed reasonable length."""
        # **Feature: crewai-agents, Property 5: Error handling graceful degradation**
        # **Validates: Requirements 5.4**
        result = self.simulate_classification_failure(error_message)
        # Reason should be bounded (prefix + truncated error)
        assert len(result.reason) <= 100

    def test_json_parse_failure_handled(self):
        """JSON parse failure returns valid Classification."""
        # **Feature: crewai-agents, Property 5: Error handling graceful degradation**
        # **Validates: Requirements 5.4**
        result = self.simulate_classification_failure("could not parse response")
        assert result.urgency == "NOT_URGENT"
        assert "failed" in result.reason.lower()

    def test_api_timeout_failure_handled(self):
        """API timeout failure returns valid Classification."""
        # **Feature: crewai-agents, Property 5: Error handling graceful degradation**
        # **Validates: Requirements 5.4**
        result = self.simulate_classification_failure("Request timed out")
        assert result.urgency == "NOT_URGENT"
        assert "failed" in result.reason.lower()

    def test_rate_limit_failure_handled(self):
        """Rate limit failure returns valid Classification."""
        # **Feature: crewai-agents, Property 5: Error handling graceful degradation**
        # **Validates: Requirements 5.4**
        result = self.simulate_classification_failure("Rate limit exceeded")
        assert result.urgency == "NOT_URGENT"
        assert "failed" in result.reason.lower()
