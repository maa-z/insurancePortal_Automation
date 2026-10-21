from typing import List, Optional, Dict, Any
from .loader import PatientDataLoader
from ..schemas.patient import (
    SyntheticPatientSchema,
    PatientDemographics,
    PatientInsurance,
    DiagnosisRecord,
    PathologyRecord,
    BiomarkerRecord,
    LabResultRecord,
    TreatmentHistoryRecord,
    TreatmentPlan,
)
from ..config import settings


class PatientService:
    def __init__(self, loader: Optional[PatientDataLoader] = None):
        self.loader = loader or PatientDataLoader.get_instance()

    def _require_patient(self, patient_id: str) -> SyntheticPatientSchema:
        if not patient_id:
            raise ValueError("patient_id is required")
        patient = self.loader.get_patient(patient_id)
        if not patient:
            raise KeyError(f"Patient {patient_id} not found in repository.")
        return patient

    def get_patient_identity(self, patient_id: str) -> Dict[str, Any]:
        """Validate patient identity gate and return registration baseline."""
        patient = self._require_patient(patient_id)
        # Check known identity conflicts (e.g. P1008)
        has_identity_conflict = any(
            c.type == "IDENTITY_MISMATCH" for c in patient.known_conflicts
        )

        return {
            "patient_id": patient.patient_id,
            "full_name": patient.demographics.full_name.model_dump(),
            "date_of_birth": patient.demographics.date_of_birth.model_dump(),
            "sex": patient.demographics.sex.model_dump(),
            "address": patient.demographics.address.model_dump(),
            "identity_verified": not has_identity_conflict,
            "identity_mismatch_warning": "Registration demographics discordant with EMR clinical master index" if has_identity_conflict else None,
        }

    def get_demographics(self, patient_id: str) -> PatientDemographics:
        patient = self._require_patient(patient_id)
        return patient.demographics

    def get_insurance_information(self, patient_id: str) -> PatientInsurance:
        patient = self._require_patient(patient_id)
        return patient.insurance

    def get_diagnoses(self, patient_id: str) -> List[DiagnosisRecord]:
        patient = self._require_patient(patient_id)
        return patient.diagnoses

    def get_pathology(
        self,
        patient_id: str,
        concept: Optional[str] = None,
        date_range: Optional[tuple] = None,
    ) -> List[PathologyRecord]:
        patient = self._require_patient(patient_id)
        results = patient.pathology
        if concept:
            results = [p for p in results if p.concept.upper() == concept.upper()]
        return results

    def get_biomarkers(
        self,
        patient_id: str,
        biomarker_name: Optional[str] = None,
    ) -> List[BiomarkerRecord]:
        patient = self._require_patient(patient_id)
        results = patient.biomarkers
        if biomarker_name:
            results = [
                b for b in results if b.biomarker_name.upper() == biomarker_name.upper()
            ]
        return results

    def get_lab_results(
        self,
        patient_id: str,
        test_name: Optional[str] = None,
        date_range: Optional[tuple] = None,
    ) -> List[LabResultRecord]:
        patient = self._require_patient(patient_id)
        results = patient.laboratory_results
        if test_name:
            results = [
                l for l in results if l.test_name.upper() == test_name.upper()
            ]
        return results

    def get_treatment_history(
        self,
        patient_id: str,
        diagnosis: Optional[str] = None,
    ) -> List[TreatmentHistoryRecord]:
        patient = self._require_patient(patient_id)
        return patient.treatment_history

    def get_treatment_plan(self, patient_id: str) -> TreatmentPlan:
        patient = self._require_patient(patient_id)
        return patient.treatment_plan

    def search_patient_evidence(
        self,
        patient_id: str,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        patient = self._require_patient(patient_id)
        hits = []
        q = (query or "").lower()

        # Search across diagnoses
        for d in patient.diagnoses:
            if not q or q in d.supporting_text.lower() or q in d.primary_diagnosis.lower() or q in d.cancer_type.lower():
                hits.append({
                    "record_id": d.record_id,
                    "source_type": d.source_type,
                    "event_date": d.event_date,
                    "supporting_text": d.supporting_text,
                    "concept": "DIAGNOSIS"
                })

        # Search across biomarkers
        for b in patient.biomarkers:
            if not q or q in b.supporting_text.lower() or q in b.biomarker_name.lower() or q in b.value.lower():
                hits.append({
                    "record_id": b.record_id,
                    "source_type": b.source_type,
                    "event_date": b.event_date,
                    "supporting_text": b.supporting_text,
                    "concept": b.biomarker_name
                })

        # Search across pathology
        for p in patient.pathology:
            if not q or q in p.supporting_text.lower() or q in p.concept.lower() or q in p.value.lower():
                hits.append({
                    "record_id": p.record_id,
                    "source_type": p.source_type,
                    "event_date": p.event_date,
                    "supporting_text": p.supporting_text,
                    "concept": p.concept
                })

        # Search across labs
        for l in patient.laboratory_results:
            if not q or q in (l.supporting_text or "").lower() or q in l.test_name.lower():
                hits.append({
                    "record_id": l.record_id,
                    "source_type": l.source_type,
                    "event_date": l.event_date,
                    "supporting_text": l.supporting_text or f"{l.test_name}: {l.value} {l.unit}",
                    "concept": l.test_name
                })

        # Search across unstructured PDF pathology reports and TXT clinical notes
        docs = self.get_patient_documents(patient_id)
        for doc in docs:
            lines = doc["content"].split("\n")
            for line in lines:
                clean_line = line.strip()
                if clean_line and (not q or q in clean_line.lower()):
                    hits.append({
                        "record_id": f"DOC-{doc['filename']}",
                        "source_type": f"{doc['file_type']}_document",
                        "event_date": patient.diagnoses[0].diagnosis_date if patient.diagnoses else "2026-08-01",
                        "supporting_text": clean_line,
                        "concept": doc["title"]
                    })

        return hits

    def get_patient_documents(self, patient_id: str) -> List[Dict[str, Any]]:
        """Retrieve and parse patient PDF reports and TXT clinical notes."""
        records_dir = settings.DATA_PATH.parent / "records" / patient_id
        if not records_dir.exists():
            return []

        docs = []
        for file_path in records_dir.iterdir():
            if file_path.suffix.lower() == ".txt":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    docs.append({
                        "filename": file_path.name,
                        "file_type": "txt",
                        "title": "Clinical Consultation Note",
                        "content": content
                    })
                except Exception:
                    pass

            elif file_path.suffix.lower() == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(str(file_path))
                    pages_text = []
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            pages_text.append(text)
                    content = "\n".join(pages_text)
                    docs.append({
                        "filename": file_path.name,
                        "file_type": "pdf",
                        "title": "Surgical Pathology & Biomarker Report",
                        "content": content
                    })
                except Exception:
                    pass

        return docs

