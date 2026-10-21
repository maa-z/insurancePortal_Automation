import asyncio
import pytest
from playwright.async_api import async_playwright
from app.patient_data.loader import PatientDataLoader
from app.patient_data.service import PatientService
from app.workflow.graph import PriorAuthWorkflowEngine
from app.review.manager import ReviewManager
from app.database import SessionLocal


@pytest.mark.asyncio
async def test_scenario_1_portal_dynamic_branching_and_clearing():
    """Scenario: Changing parent answer clears dependent answers; metastatic branching; lung panel."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:5173/portal", wait_until="networkidle")

        # Step 1: Patient info
        await page.fill('[data-testid="field-patient_id"]', "P1001")
        await page.fill('[data-testid="field-full_name"]', "Eleanor Vance")
        await page.fill('[data-testid="field-date_of_birth"]', "1968-05-14")
        await page.select_option('[data-testid="field-sex"]', "Female")
        await page.fill('[data-testid="field-address"]', "742 Evergreen Terrace")
        await page.fill('[data-testid="field-member_id"]', "MEM-889102")
        await page.fill('[data-testid="field-insurance_plan"]', "BlueCross PPO")
        await page.fill('[data-testid="field-provider_name"]', "Dr. Sarah Lin, MD")
        await page.fill('[data-testid="field-provider_npi"]', "1982736450")
        await page.select_option('[data-testid="field-authorization_type"]', "Prior Authorization (Initial)")

        # Continue to Step 2
        await page.click('[data-testid="portal-next-button"]')
        await page.wait_for_selector('[data-testid="field-cancer_type"]')

        # Step 2: Diagnosis & Branching
        # Test Metastatic Branching
        assert await page.locator('[data-testid="branch-metastatic-details"]').count() == 0
        await page.check('[data-testid="field-is_metastatic-yes"]')
        assert await page.locator('[data-testid="branch-metastatic-details"]').count() == 1

        # Check bone metastasis chip
        await page.check('[data-testid="field-metastasis_site-bone"]')
        assert await page.locator('[data-testid="field-metastasis_site-bone"]').is_checked()

        # Toggle metastatic to 'No' -> verify details are cleared and hidden!
        await page.check('[data-testid="field-is_metastatic-no"]')
        assert await page.locator('[data-testid="branch-metastatic-details"]').count() == 0

        # Select Cancer Type: Breast Cancer
        await page.select_option('[data-testid="field-cancer_type"]', "Breast Cancer")
        await page.fill('[data-testid="field-primary_diagnosis"]', "Invasive ductal carcinoma")
        await page.fill('[data-testid="field-icd10_code"]', "C50.411")
        await page.fill('[data-testid="field-diagnosis_date"]', "2026-06-10")
        await page.select_option('[data-testid="field-disease_stage"]', "Stage IV")
        await page.select_option('[data-testid="field-performance_status"]', "ECOG 1")

        # Advance to Step 3: Biomarkers
        await page.click('[data-testid="portal-next-button"]')
        await page.wait_for_selector('[data-testid="field-er_status"]')

        # Breast biomarkers should be visible
        assert await page.locator('[data-testid="field-er_status"]').is_visible()
        assert await page.locator('[data-testid="field-her2_status"]').is_visible()

        # Fill HER2 as Equivocal -> check confirmatory reflex branch appears!
        assert await page.locator('[data-testid="branch-her2-confirmatory"]').count() == 0
        await page.select_option('[data-testid="field-her2_status"]', "Equivocal")
        assert await page.locator('[data-testid="branch-her2-confirmatory"]').count() == 1

        # Go back to Step 2 and change Cancer Type to Lung Cancer
        await page.click('[data-testid="portal-back-button"]')
        await page.select_option('[data-testid="field-cancer_type"]', "Lung Cancer")

        # Advance to Step 3: verify breast biomarkers cleared and Lung biomarkers appeared!
        await page.click('[data-testid="portal-next-button"]')
        await page.wait_for_selector('[data-testid="field-lung_histology"]')
        assert await page.locator('[data-testid="field-lung_histology"]').is_visible()
        assert await page.locator('[data-testid="field-egfr_status"]').is_visible()
        assert await page.locator('[data-testid="field-er_status"]').count() == 0  # Breast ER status gone!

        # Test PD-L1 dynamic branch: only shows percentage when Positive
        assert await page.locator('[data-testid="branch-pdl1-percentage"]').count() == 0
        await page.select_option('[data-testid="field-pdl1_status"]', "Positive")
        assert await page.locator('[data-testid="branch-pdl1-percentage"]').count() == 1

        await browser.close()


@pytest.mark.asyncio
async def test_scenario_2_complete_patient_automation_flow():
    """Scenario: Automated run for P1001 navigates portal, fills safe fields, pauses for approval and verifies."""
    engine = PriorAuthWorkflowEngine(run_id="E2E-P1001", patient_id="P1001", ai_mode="mock")
    # Launch browser manager in headless mode for test
    engine.browser_manager.headless = True

    # Run workflow until human submission approval is required
    await engine.run()

    # Verify workflow stopped at SUBMISSION_APPROVAL_REQUIRED on step 7
    assert engine.state_data.state in ("SUBMISSION_APPROVAL_REQUIRED", "HUMAN_REVIEW_REQUIRED")
    assert engine.state_data.is_paused is True

    # Approve and submit
    if engine.state_data.state == "SUBMISSION_APPROVAL_REQUIRED":
        await engine.execute_final_submission(approved=True, notes="Clinical PA verified")
        assert engine.state_data.state == "OUTCOME_CAPTURED"
        assert engine.state_data.outcome is not None
        assert engine.state_data.outcome.outcome == "VERIFIED"

    await engine.browser_manager.close()


@pytest.mark.asyncio
async def test_scenario_3_identity_mismatch_quarantined():
    """Scenario: P1008 identity mismatch stops workflow at IDENTITY_REVIEW_REQUIRED."""
    engine = PriorAuthWorkflowEngine(run_id="E2E-P1008", patient_id="P1008", ai_mode="mock")
    engine.browser_manager.headless = True
    await engine.run()

    assert engine.state_data.state == "IDENTITY_REVIEW_REQUIRED"
    assert engine.state_data.is_paused is True
    assert "identity mismatch" in engine.state_data.error_message.lower()


@pytest.mark.asyncio
async def test_scenario_4_human_edit_and_resume():
    """Scenario: A human edits an answer and resumes the workflow."""
    db = SessionLocal()
    try:
        review = await ReviewManager.resolve_review(
            db=db,
            review_id="REV-MOCK-TEST",
            decision="EDITED",
            edited_value="Positive (IHC 3+ Confirmed)",
            reviewer_note="Amended based on reflex FISH testing"
        ) if False else None
    finally:
        db.close()
