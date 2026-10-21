import pytest
from app.patient_data.service import PatientService


def test_patient_loader_contains_10_patients(patient_loader):
    patients = patient_loader.get_all_patients()
    assert len(patients) >= 10
    ids = [p.patient_id for p in patients]
    assert "P1001" in ids
    assert "P1002" in ids
    assert "P1006" in ids
    assert "P1007" in ids
    assert "P1008" in ids


def test_get_patient_identity_valid(patient_service):
    identity = patient_service.get_patient_identity("P1001")
    assert identity["patient_id"] == "P1001"
    assert identity["full_name"]["value"] == "Eleanor Vance"
    assert identity["identity_verified"] is True
    assert identity["identity_mismatch_warning"] is None


def test_get_patient_identity_mismatch_detected(patient_service):
    identity = patient_service.get_patient_identity("P1008")
    assert identity["patient_id"] == "P1008"
    assert identity["identity_verified"] is False
    assert "discordant" in identity["identity_mismatch_warning"].lower()


def test_nonexistent_patient_raises_key_error(patient_service):
    with pytest.raises(KeyError):
        patient_service.get_patient_identity("P9999_NONEXISTENT")


def test_patient_scoped_retrieval_isolation(patient_service):
    # P1001 is Breast Cancer, P1002 is Lung Cancer
    p1_diag = patient_service.get_diagnoses("P1001")
    p2_diag = patient_service.get_diagnoses("P1002")

    assert p1_diag[0].cancer_type == "Breast Cancer"
    assert p2_diag[0].cancer_type == "Lung Cancer"
    assert p1_diag[0].patient_id == "P1001"
    assert p2_diag[0].patient_id == "P1002"


def test_search_patient_evidence(patient_service):
    hits = patient_service.search_patient_evidence("P1001", query="HER2")
    assert len(hits) > 0
    assert any("HER2" in h["supporting_text"] for h in hits)
    # Check that evidence from another patient is NOT returned
    p2_hits = patient_service.search_patient_evidence("P1002", query="EGFR")
    assert len(p2_hits) > 0
    assert all("P1002" in h["record_id"] or "BIO-1002" in h["record_id"] for h in p2_hits)
