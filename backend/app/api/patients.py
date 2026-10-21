from typing import List
from fastapi import APIRouter, HTTPException
from ..patient_data.loader import PatientDataLoader
from ..schemas.patient import SyntheticPatientSchema

router = APIRouter()


@router.get("/patients", response_model=List[SyntheticPatientSchema])
def list_patients():
    loader = PatientDataLoader.get_instance()
    return loader.get_all_patients()


@router.get("/patients/{patient_id}", response_model=SyntheticPatientSchema)
def get_patient(patient_id: str):
    loader = PatientDataLoader.get_instance()
    patient = loader.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")
    return patient
