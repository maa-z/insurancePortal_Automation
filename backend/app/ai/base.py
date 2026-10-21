from abc import ABC, abstractmethod
from ..schemas.portal import FieldSnapshot
from ..schemas.ai import ProposedAnswerSchema
from ..patient_data.service import PatientService


class BaseAIProvider(ABC):
    @abstractmethod
    async def propose_answer(
        self,
        patient_id: str,
        field: FieldSnapshot,
        patient_service: PatientService
    ) -> ProposedAnswerSchema:
        """Propose structured evidence-backed answer for a discovered portal field."""
        pass
