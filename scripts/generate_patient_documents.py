import json
import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

BASE_DIR = Path(__file__).resolve().parent.parent
PATIENTS_JSON = BASE_DIR / "data" / "patients.json"
RECORDS_DIR = BASE_DIR / "data" / "records"


def generate_documents():
    with open(PATIENTS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    patients = data.get("patients", [])
    print(f"Generating clinical PDF and TXT documents for {len(patients)} patients...")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748"),
    )
    bold_style = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1A202C"),
    )

    for p in patients:
        p_id = p["patient_id"]
        demo = p["demographics"]
        ins = p["insurance"]
        diag = p.get("diagnoses", [{}])[0]
        biomarkers = p.get("biomarkers", [])
        labs = p.get("laboratory_results", [])
        tx_hist = p.get("treatment_history", [])
        tx_plan = p.get("treatment_plan", {})
        conflicts = p.get("known_conflicts", [])

        p_dir = RECORDS_DIR / p_id
        p_dir.mkdir(parents=True, exist_ok=True)

        full_name = demo.get("full_name", {}).get("value", "Unknown")
        dob = demo.get("date_of_birth", {}).get("value", "Unknown")
        sex = demo.get("sex", {}).get("value", "Unknown")
        addr = demo.get("address", {}).get("value", "Unknown")
        member_id = ins.get("member_id", {}).get("value", "Unknown")
        payer = ins.get("payer_name", {}).get("value", "Unknown")
        provider_name = ins.get("servicing_provider_name", {}).get("value", "Dr. Oncologist")
        provider_npi = ins.get("servicing_provider_npi", {}).get("value", "1234567890")

        # -------------------------------------------------------------
        # 1. TXT Document: Clinical Consultation & EMR Summary
        # -------------------------------------------------------------
        txt_path = p_dir / f"{p_id}_oncology_consult_note.txt"
        with open(txt_path, "w", encoding="utf-8") as tf:
            tf.write("=" * 80 + "\n")
            tf.write("ACADEMIC COMPREHENSIVE CANCER CENTER - DIVISION OF MEDICAL ONCOLOGY\n")
            tf.write("CLINICAL CONSULTATION & PRIOR AUTHORIZATION SUMMARY NOTE\n")
            tf.write("=" * 80 + "\n\n")

            tf.write("PATIENT DEMOGRAPHICS & IDENTIFIERS:\n")
            tf.write(f"  Patient Name:        {full_name}\n")
            tf.write(f"  Medical Record No:   {p_id}\n")
            tf.write(f"  Date of Birth:       {dob}\n")
            tf.write(f"  Biological Sex:      {sex}\n")
            tf.write(f"  Primary Address:     {addr}\n")
            tf.write(f"  Insurance Payer:     {payer} (Member ID: {member_id})\n")
            tf.write(f"  Attending Provider:  {provider_name} (NPI: {provider_npi})\n\n")

            tf.write("-" * 80 + "\n")
            tf.write("ONCOLOGIC DIAGNOSIS & STAGING:\n")
            tf.write(f"  Cancer Type:         {diag.get('cancer_type', 'N/A')}\n")
            tf.write(f"  Primary Diagnosis:   {diag.get('primary_diagnosis', 'N/A')}\n")
            tf.write(f"  ICD-10 Code:         {diag.get('icd10_code', 'N/A')}\n")
            tf.write(f"  Diagnosis Date:      {diag.get('diagnosis_date', 'N/A')}\n")
            tf.write(f"  Stage:               {diag.get('stage', 'N/A')}\n")
            tf.write(f"  Metastatic Disease:  {'Yes' if diag.get('is_metastatic') else 'No'}\n")
            if diag.get("is_metastatic"):
                tf.write(f"  Metastasis Sites:    {', '.join(diag.get('metastasis_sites', []))}\n")
                tf.write(f"  Confirmation Date:   {diag.get('metastasis_confirmation_date', 'N/A')}\n")
            tf.write(f"  Recurrent Disease:   {'Yes' if diag.get('is_recurrent') else 'No'}\n\n")

            tf.write("-" * 80 + "\n")
            tf.write("CLINICAL LABORATORY PARAMETERS (Recent Specimen Draws):\n")
            for lab in labs:
                tf.write(f"  - {lab.get('test_name')}: {lab.get('value')} {lab.get('unit')} (Drawn: {lab.get('event_date')})\n")
                if lab.get("supporting_text"):
                    tf.write(f"    Clinical Context: {lab.get('supporting_text')}\n")
            tf.write("\n")

            tf.write("-" * 80 + "\n")
            tf.write("PRIOR TREATMENT HISTORY & REGIMENS:\n")
            if tx_hist:
                for tx in tx_hist:
                    tf.write(f"  - Modality: {tx.get('treatment_modality')}\n")
                    tf.write(f"    Regimen:  {tx.get('regimen_name', 'N/A')}\n")
                    tf.write(f"    Agents:   {', '.join(tx.get('agents', []))}\n")
                    tf.write(f"    Dates:    {tx.get('start_date', 'N/A')} to {tx.get('end_date', 'N/A')}\n")
                    tf.write(f"    Outcome:  {tx.get('outcome', 'N/A')}\n")
                    if tx.get("discontinuation_reason"):
                        tf.write(f"    Reason Discontinued: {tx.get('discontinuation_reason')}\n")
                    if tx.get("toxicity_details"):
                        tf.write(f"    Toxicity/Adverse Events: {tx.get('toxicity_details')}\n")
            else:
                tf.write("  No previous systemic antineoplastic therapy recorded.\n")
            tf.write("\n")

            tf.write("-" * 80 + "\n")
            tf.write("REQUESTED TREATMENT PLAN (Prior Authorization Request):\n")
            tf.write(f"  Medication:          {tx_plan.get('requested_medication', 'N/A')}\n")
            tf.write(f"  Regimen Name:        {tx_plan.get('regimen_name', 'N/A')}\n")
            tf.write(f"  Line of Therapy:     {tx_plan.get('line_of_therapy', 'N/A')}\n")
            tf.write(f"  Treatment Intent:    {tx_plan.get('treatment_intent', 'N/A')}\n")
            tf.write(f"  Requested Start Date:{tx_plan.get('requested_start_date', 'N/A')}\n")
            tf.write(f"  Planned Cycles:      {tx_plan.get('planned_cycles', 'N/A')}\n")
            tf.write(f"  Clinical Rationale:  {tx_plan.get('clinical_rationale', 'N/A')}\n\n")

            if conflicts:
                tf.write("=" * 80 + "\n")
                tf.write("CLINICAL QUALITY & DISCREPANCY FLAGS:\n")
                for c in conflicts:
                    tf.write(f"  [FLAG] {c.get('type')}: {c.get('description')}\n")
                tf.write("=" * 80 + "\n\n")

            tf.write(f"Physician Attestation: Electronically signed by {provider_name}, MD on {tx_plan.get('requested_start_date', '2026-08-01')}\n")

        # -------------------------------------------------------------
        # 2. PDF Document: Official Surgical Pathology & Molecular Report
        # -------------------------------------------------------------
        pdf_path = p_dir / f"{p_id}_pathology_report.pdf"
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        elements = []

        elements.append(Paragraph("INSTITUTE OF PATHOLOGY & GENOMIC MEDICINE", title_style))
        elements.append(Paragraph("CLINICAL SURGICAL PATHOLOGY & BIOMARKER REPORT", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2B6CB0"), spaceAfter=10))

        # Demographic Header Table
        header_data = [
            [Paragraph("<b>Patient Name:</b>", bold_style), Paragraph(full_name, body_style),
             Paragraph("<b>Record ID (MRN):</b>", bold_style), Paragraph(p_id, body_style)],
            [Paragraph("<b>Date of Birth:</b>", bold_style), Paragraph(dob, body_style),
             Paragraph("<b>Biological Sex:</b>", bold_style), Paragraph(sex, body_style)],
            [Paragraph("<b>Ordering Physician:</b>", bold_style), Paragraph(provider_name, body_style),
             Paragraph("<b>Facility NPI:</b>", bold_style), Paragraph(provider_npi, body_style)],
            [Paragraph("<b>Diagnosis:</b>", bold_style), Paragraph(diag.get("primary_diagnosis", "N/A"), body_style),
             Paragraph("<b>Report Date:</b>", bold_style), Paragraph(diag.get("diagnosis_date", "2026-06-15"), body_style)],
        ]
        t_header = Table(header_data, colWidths=[110, 160, 110, 160])
        t_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_header)
        elements.append(Spacer(1, 12))

        # Gross & Microscopic Description
        elements.append(Paragraph("1. Surgical Pathology Diagnostic Summary", section_style))
        path_text = diag.get("supporting_text", f"Diagnostic biopsy confirming {diag.get('cancer_type', 'malignancy')}. Histologic examination shows invasive carcinoma.")
        elements.append(Paragraph(path_text, body_style))
        elements.append(Spacer(1, 10))

        # Biomarker / Molecular Diagnostics Table
        elements.append(Paragraph("2. Immunohistochemistry & Molecular Biomarker Profile", section_style))
        if biomarkers:
            bio_data = [
                [Paragraph("<b>Biomarker / Gene</b>", bold_style),
                 Paragraph("<b>Result / Status</b>", bold_style),
                 Paragraph("<b>Testing Method</b>", bold_style),
                 Paragraph("<b>Specimen / Clinical Finding</b>", bold_style)]
            ]
            for b in biomarkers:
                bio_data.append([
                    Paragraph(b.get("biomarker_name", "N/A"), bold_style),
                    Paragraph(b.get("value", "N/A"), body_style),
                    Paragraph(b.get("method", "IHC / NGS"), body_style),
                    Paragraph(b.get("supporting_text", "Consistent with clinical evaluation."), body_style),
                ])
            t_bio = Table(bio_data, colWidths=[120, 100, 100, 220])
            t_bio.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EBF8FF")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BEE3F8")),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_bio)
        else:
            elements.append(Paragraph("<i>No standard molecular biomarkers documented in current specimen.</i>", body_style))

        elements.append(Spacer(1, 12))

        # Clinical Sign-off
        elements.append(Paragraph("3. Pathologist Attestation & Molecular Review", section_style))
        elements.append(Paragraph(
            "This diagnostic report has been verified by the attending surgical pathologist. Results are calibrated "
            "against CLIA/CAP accredited laboratory standards and integrated into the master oncology electronic record.",
            body_style
        ))
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=6))
        elements.append(Paragraph(f"<b>Certified By:</b> James Wilson, MD, FCAP (Chief of Molecular Pathology) &bull; Sign-off Date: {diag.get('diagnosis_date', '2026-06-15')}", body_style))

        doc.build(elements)

    print(f"Successfully generated TXT and PDF documents for all {len(patients)} patients under data/records/")


if __name__ == "__main__":
    generate_documents()
