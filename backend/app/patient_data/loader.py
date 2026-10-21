import json
from typing import Dict, List, Optional
from ..config import settings
from ..schemas.patient import SyntheticPatientSchema


class PatientDataLoader:
    _instance: Optional["PatientDataLoader"] = None
    _patients: Dict[str, SyntheticPatientSchema] = {}

    @classmethod
    def get_instance(cls) -> "PatientDataLoader":
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.load()
        return cls._instance

    def load(self):
        if not settings.DATA_PATH.exists():
            raise FileNotFoundError(f"Patients data file not found at: {settings.DATA_PATH}")

        with open(settings.DATA_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        self._patients = {}
        for p in raw_data.get("patients", []):
            patient_obj = SyntheticPatientSchema(**p)
            self._patients[patient_obj.patient_id] = patient_obj

    def get_all_patients(self) -> List[SyntheticPatientSchema]:
        return list(self._patients.values())

    def get_patient(self, patient_id: str) -> Optional[SyntheticPatientSchema]:
        return self._patients.get(patient_id)
