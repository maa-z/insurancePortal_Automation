import json
import logging
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from openai import AsyncOpenAI
from ..schemas.portal import FieldSnapshot
from ..schemas.ai import ProposedAnswerSchema
from ..patient_data.service import PatientService
from ..config import settings
from .base import BaseAIProvider
from .mock_provider import MockAIProvider

logger = logging.getLogger(__name__)


class GroqAIProvider(BaseAIProvider):
    """
    Open-source high-speed AI reasoning provider powered by Groq and LangChain (ChatGroq).
    Uses fast inference models like llama-3.3-70b-versatile, llama-3.1-8b-instant, or openai/gpt-oss-120b.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self._fallback_provider = MockAIProvider()

    async def propose_answer(
        self,
        patient_id: str,
        field: FieldSnapshot,
        patient_service: PatientService
    ) -> ProposedAnswerSchema:
        # If no API key is provided, log warning and gracefully use deterministic mock provider
        if not self.api_key or self.api_key.strip() == "":
            logger.info("GROQ_API_KEY not configured. Delegating to deterministic mock provider.")
            return await self._fallback_provider.propose_answer(patient_id, field, patient_service)

        try:
            evidence_records = patient_service.search_patient_evidence(patient_id, query=field.question_text)
            diagnoses = patient_service.get_diagnoses(patient_id)
            biomarkers = patient_service.get_biomarkers(patient_id)
            plan = patient_service.get_treatment_plan(patient_id)
            demographics = patient_service.get_demographics(patient_id)

            system_prompt = (
                "You are an oncology prior-authorization AI reasoning engine.\n"
                "Your role is to evaluate visible portal questions and propose structured, evidence-backed answers.\n"
                "RULES:\n"
                "- Do NOT click or submit directly.\n"
                "- Propose values ONLY using the provided patient evidence.\n"
                "- Never guess or extrapolate unsupported data.\n"
                "- If evidence is missing, set decision='INSUFFICIENT_EVIDENCE' and populate missing_information.\n"
                "- If conflicting evidence exists, set decision='CONFLICT_REQUIRES_REVIEW' and populate conflicts.\n"
                "- Match the answer to one of the allowed values if provided.\n"
                "You must respond with valid JSON strictly conforming to ProposedAnswerSchema with keys:\n"
                "- patient_id (str)\n"
                "- page_id (str)\n"
                "- field_id (str)\n"
                "- question_text (str)\n"
                "- normalized_concept (str)\n"
                "- answer_type (str: text, single_select, multi_select, numeric, date, boolean)\n"
                "- proposed_value (string, number, boolean, or list of strings)\n"
                "- allowed_value_match (bool)\n"
                "- evidence (list of objects with record_id, source_type, event_date, supporting_text, directness)\n"
                "- conflicts (list of strings)\n"
                "- missing_information (list of strings)\n"
                "- validation_requirements (list of strings)\n"
                "- risk_level (str: green, yellow, orange, red)\n"
                "- decision (str: PROPOSED, INSUFFICIENT_EVIDENCE, CONFLICT_REQUIRES_REVIEW, IDENTITY_MISMATCH)\n"
                "- reason (str: clinical justification)\n"
                "Respond with raw JSON only, no markdown wrapping, no explanation outside JSON."
            )

            docs = patient_service.get_patient_documents(patient_id)
            doc_summaries = [
                {
                    "filename": d["filename"],
                    "document_type": d["file_type"],
                    "title": d["title"],
                    "content_excerpt": d["content"][:2500]
                }
                for d in docs
            ]

            user_data = {
                "patient_id": patient_id,
                "portal_field": {
                    "field_id": field.field_id,
                    "page_id": field.page_id,
                    "question_text": field.question_text,
                    "input_type": field.input_type,
                    "allowed_values": field.allowed_values,
                    "required": field.required,
                },
                "retrieved_evidence": {
                    "demographics": demographics.model_dump(),
                    "diagnoses": [d.model_dump() for d in diagnoses],
                    "biomarkers": [b.model_dump() for b in biomarkers],
                    "treatment_plan": plan.model_dump(),
                    "matched_evidence_search": evidence_records[:8],
                    "clinical_source_documents": doc_summaries,
                }
            }

            llm = ChatGroq(
                model=self.model,
                groq_api_key=self.api_key,
                temperature=0.1,
                max_tokens=1024,
                model_kwargs={"response_format": {"type": "json_object"}},
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "{user_input}")
            ])

            chain = prompt | llm | StrOutputParser()
            raw_content = await chain.ainvoke({"user_input": json.dumps(user_data)})

            # Clean markdown code fences if any
            cleaned = raw_content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            return ProposedAnswerSchema(**parsed)

        except Exception as e:
            logger.error(f"Groq LLM invocation failed: {e}. Falling back to deterministic provider.")
            return await self._fallback_provider.propose_answer(patient_id, field, patient_service)


class OpenAIAIProvider(BaseAIProvider):
    """Fallback / alternative OpenAI AI provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self._fallback_provider = MockAIProvider()

    async def propose_answer(
        self,
        patient_id: str,
        field: FieldSnapshot,
        patient_service: PatientService
    ) -> ProposedAnswerSchema:
        if not self.api_key or self.api_key.strip() == "":
            logger.info("OPENAI_API_KEY not configured. Delegating to deterministic mock provider.")
            return await self._fallback_provider.propose_answer(patient_id, field, patient_service)

        try:
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

            evidence_records = patient_service.search_patient_evidence(patient_id, query=field.question_text)
            diagnoses = patient_service.get_diagnoses(patient_id)
            biomarkers = patient_service.get_biomarkers(patient_id)
            plan = patient_service.get_treatment_plan(patient_id)
            demographics = patient_service.get_demographics(patient_id)

            system_prompt = (
                "You are an oncology prior-authorization AI reasoning engine.\n"
                "Your role is to evaluate visible portal questions and propose structured, evidence-backed answers.\n"
                "RULES:\n"
                "- Do NOT click or submit directly.\n"
                "- Propose values ONLY using the provided patient evidence.\n"
                "- Never guess or extrapolate unsupported data.\n"
                "- If evidence is missing, set decision='INSUFFICIENT_EVIDENCE' and populate missing_information.\n"
                "- If conflicting evidence exists, set decision='CONFLICT_REQUIRES_REVIEW' and populate conflicts.\n"
                "- Match the answer to one of the allowed values if provided.\n"
                "You must respond with valid JSON strictly conforming to ProposedAnswerSchema."
            )

            docs = patient_service.get_patient_documents(patient_id)
            doc_summaries = [
                {
                    "filename": d["filename"],
                    "document_type": d["file_type"],
                    "title": d["title"],
                    "content_excerpt": d["content"][:2500]
                }
                for d in docs
            ]

            user_prompt = {
                "patient_id": patient_id,
                "portal_field": {
                    "field_id": field.field_id,
                    "page_id": field.page_id,
                    "question_text": field.question_text,
                    "input_type": field.input_type,
                    "allowed_values": field.allowed_values,
                    "required": field.required,
                },
                "retrieved_evidence": {
                    "demographics": demographics.model_dump(),
                    "diagnoses": [d.model_dump() for d in diagnoses],
                    "biomarkers": [b.model_dump() for b in biomarkers],
                    "treatment_plan": plan.model_dump(),
                    "matched_evidence_search": evidence_records[:8],
                    "clinical_source_documents": doc_summaries,
                }
            }

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_prompt)},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                timeout=25.0,
            )

            raw_content = response.choices[0].message.content or "{}"
            parsed = json.loads(raw_content)
            return ProposedAnswerSchema(**parsed)

        except Exception as e:
            logger.error(f"Real LLM invocation failed: {e}. Falling back to deterministic provider.")
            return await self._fallback_provider.propose_answer(patient_id, field, patient_service)
