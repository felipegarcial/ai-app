from dataclasses import dataclass, field
from typing import Literal
from enum import Enum


class Phase(str, Enum):
    """Conversation phases"""
    INTAKE = "intake"
    CLARIFICATION = "clarification"
    GENERATION = "generation"
    REVISION = "revision"


class DocumentType(str, Enum):
    """Supported document types"""
    NDA = "NDA"
    EMPLOYMENT = "EMPLOYMENT"
    SERVICE = "SERVICE"
    LEASE = "LEASE"


# Required fields by document type
REQUIRED_FIELDS_BY_DOCTYPE = {
    "NDA": [
        "party_a_name",
        "party_b_name",
        "confidential_info_type",
        "duration",
        "governing_law"
    ],
    "EMPLOYMENT": [
        "employer_name",
        "employer_address",
        "employee_name",
        "employee_address",
        "job_title",
        "job_duties",
        "salary",
        "start_date",
        "governing_law"
    ],
    "SERVICE": [
        "service_provider_name",
        "client_name",
        "scope_of_services",
        "payment_terms",
        "duration",
        "governing_law"
    ],
    "LEASE": [
        "landlord_name",
        "tenant_name",
        "property_address",
        "rent_amount",
        "lease_duration",
        "security_deposit",
        "governing_law"
    ]
}


class Expertise(str, Enum):
    """User expertise levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


@dataclass
class ConversationState:
    """
    Maintains the state of a conversation session.

    Attributes:
        phase: Current conversation phase
        document_type: Type of document being generated
        expertise: Detected or stated user expertise level
        collected_data: Information gathered from user
        missing_fields: Fields still needed
        history: Conversation message history
        current_document: Generated document content
    """
    phase: Phase = Phase.INTAKE
    _document_type: DocumentType = field(default=DocumentType.NDA, repr=False)
    expertise: Expertise = Expertise.INTERMEDIATE
    collected_data: dict = field(default_factory=dict)
    missing_fields: list = field(default_factory=list)
    history: list = field(default_factory=list)
    current_document: str | None = None
    document_metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        """Initialize missing_fields based on document type"""
        if not self.missing_fields:
            self.missing_fields = REQUIRED_FIELDS_BY_DOCTYPE.get(
                self._document_type.value,
                REQUIRED_FIELDS_BY_DOCTYPE["NDA"]
            ).copy()

    @property
    def document_type(self) -> DocumentType:
        return self._document_type

    @document_type.setter
    def document_type(self, value: DocumentType):
        """Update document type and refresh missing fields"""
        old_type = self._document_type
        self._document_type = value

        # If document type changed, update missing fields
        if old_type != value:
            new_required = REQUIRED_FIELDS_BY_DOCTYPE.get(
                value.value,
                REQUIRED_FIELDS_BY_DOCTYPE["NDA"]
            ).copy()

            # Remove fields already collected
            for field_name in list(self.collected_data.keys()):
                if field_name in new_required:
                    new_required.remove(field_name)

            self.missing_fields = new_required

    def to_context(self) -> dict:
        """Convert state to context dict for prompt composition"""
        return {
            "phase": self.phase.value,
            "document_type": self.document_type.value,
            "expertise": self.expertise.value,
            "collected_data": self.collected_data,
            "missing_fields": self.missing_fields,
            "current_document": self.current_document,
            "document_metadata": self.document_metadata
        }

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.history.append({"role": role, "content": content})

    def update_collected_data(self, data: dict):
        """Update collected data and remove from missing fields"""
        self.collected_data.update(data)
        for key in data.keys():
            if key in self.missing_fields:
                self.missing_fields.remove(key)

    def is_intake_complete(self) -> bool:
        """Check if all required information has been collected"""
        return len(self.missing_fields) == 0

    def advance_phase(self):
        """Move to next conversation phase"""
        phase_order = [Phase.INTAKE, Phase.CLARIFICATION, Phase.GENERATION, Phase.REVISION]
        current_index = phase_order.index(self.phase)
        if current_index < len(phase_order) - 1:
            self.phase = phase_order[current_index + 1]
