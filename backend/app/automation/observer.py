import hashlib
import logging
from typing import List, Dict, Any, Optional
from playwright.async_api import Page
from ..schemas.portal import FieldSnapshot, PageSnapshot
from ..validation.risk import classify_field_risk

logger = logging.getLogger(__name__)


class PortalObserver:
    @classmethod
    async def observe_current_page(cls, page: Page) -> PageSnapshot:
        """Inspect currently visible DOM elements and extract structured field snapshots."""
        # Check active page container
        page_elem = page.locator("[data-page-id]").first
        page_id = "unknown"
        if await page_elem.count() > 0:
            page_id = await page_elem.get_attribute("data-page-id") or "unknown"

        # Check current step
        main_elem = page.locator("[data-current-step]").first
        step_str = "1"
        if await main_elem.count() > 0:
            step_str = await main_elem.get_attribute("data-current-step") or "1"
        current_step = int(step_str) if step_str.isdigit() else 1

        # Check page version
        version_attr = "v-init"
        if await main_elem.count() > 0:
            version_attr = await main_elem.get_attribute("data-page-version") or "v-init"

        # Execute JavaScript in page DOM to extract visible controls accurately and quickly
        js_extractor = """
        () => {
            const fields = [];
            const container = document.querySelector('[data-page-id]');
            if (!container) return fields;

            // Find all form-groups and branch-panels visible
            const formGroups = container.querySelectorAll('.form-group, .branch-panel');
            
            formGroups.forEach(group => {
                // If group is hidden, skip
                if (group.offsetParent === null && !group.closest('.branch-panel')) return;

                // 1. Check for select controls
                const select = group.querySelector('select');
                if (select && select.offsetParent !== null) {
                    const label = group.querySelector('label');
                    const labelText = label ? label.innerText.replace('*', '').trim() : (select.name || select.id);
                    const options = Array.from(select.options).map(o => o.value).filter(v => v !== '');
                    const testId = select.getAttribute('data-testid') || '';
                    const fieldId = testId.replace('field-', '') || select.id.replace('field-', '');

                    fields.push({
                        field_id: fieldId,
                        question_text: labelText,
                        input_type: 'select',
                        allowed_values: options,
                        required: select.hasAttribute('required'),
                        visible: true,
                        current_value: select.value || null,
                        test_id: testId
                    });
                    return;
                }

                // 2. Check for radio groups
                const radios = group.querySelectorAll('input[type="radio"]');
                if (radios.length > 0 && radios[0].offsetParent !== null) {
                    const label = group.querySelector('.form-label');
                    const labelText = label ? label.innerText.replace('*', '').trim() : radios[0].name;
                    const options = Array.from(radios).map(r => r.value);
                    const checkedRadio = Array.from(radios).find(r => r.checked);
                    const fieldId = radios[0].name;

                    fields.push({
                        field_id: fieldId,
                        question_text: labelText,
                        input_type: 'radio',
                        allowed_values: options,
                        required: true,
                        visible: true,
                        current_value: checkedRadio ? checkedRadio.value : null,
                        test_id: `field-${fieldId}`
                    });
                    return;
                }

                // 3. Check for multi-select checkbox chip containers
                const chipContainer = group.querySelector('.checkbox-grid');
                if (chipContainer && chipContainer.offsetParent !== null) {
                    const label = group.querySelector('.form-label');
                    const labelText = label ? label.innerText.replace('*', '').trim() : 'Multi-Select';
                    const checkboxes = chipContainer.querySelectorAll('input[type="checkbox"]');
                    const options = Array.from(checkboxes).map(c => c.closest('label').innerText.trim());
                    const selected = Array.from(checkboxes).filter(c => c.checked).map(c => c.closest('label').innerText.trim());
                    const testId = chipContainer.getAttribute('data-testid') || 'field-metastasis_sites';
                    const fieldId = testId.replace('field-', '');

                    fields.push({
                        field_id: fieldId,
                        question_text: labelText,
                        input_type: 'multi-select',
                        allowed_values: options,
                        required: true,
                        visible: true,
                        current_value: selected,
                        test_id: testId
                    });
                    return;
                }

                // 4. Check for textareas
                const textarea = group.querySelector('textarea');
                if (textarea && textarea.offsetParent !== null) {
                    const label = group.querySelector('label');
                    const labelText = label ? label.innerText.replace('*', '').trim() : textarea.name;
                    const testId = textarea.getAttribute('data-testid') || '';
                    const fieldId = testId.replace('field-', '') || textarea.id.replace('field-', '');

                    fields.push({
                        field_id: fieldId,
                        question_text: labelText,
                        input_type: 'textarea',
                        allowed_values: null,
                        required: textarea.hasAttribute('required'),
                        visible: true,
                        current_value: textarea.value || null,
                        test_id: testId
                    });
                    return;
                }

                // 5. Check for standard inputs (text, number, date, checkbox)
                const input = group.querySelector('input:not([type="radio"]):not([type="checkbox"])');
                if (input && input.offsetParent !== null) {
                    const label = group.querySelector('label');
                    const labelText = label ? label.innerText.replace('*', '').trim() : (input.name || input.id);
                    const testId = input.getAttribute('data-testid') || '';
                    const fieldId = testId.replace('field-', '') || input.id.replace('field-', '');
                    const inputType = input.type || 'text';

                    fields.push({
                        field_id: fieldId,
                        question_text: labelText,
                        input_type: inputType,
                        allowed_values: null,
                        required: input.hasAttribute('required'),
                        visible: true,
                        current_value: input.value || null,
                        test_id: testId
                    });
                }
            });

            // Also check for Step 7 human submission approval checkbox if on step 7
            const submissionCheckbox = document.querySelector('[data-testid="field-human_submission_approved"]');
            if (submissionCheckbox && submissionCheckbox.offsetParent !== null) {
                fields.push({
                    field_id: 'human_submission_approved',
                    question_text: 'Clinical human attestation approval',
                    input_type: 'checkbox',
                    allowed_values: ['true', 'false'],
                    required: true,
                    visible: true,
                    current_value: submissionCheckbox.checked,
                    test_id: 'field-human_submission_approved'
                });
            }

            return fields;
        }
        """

        raw_fields = await page.evaluate(js_extractor)
        snapshots: List[FieldSnapshot] = []

        for f in raw_fields:
            risk = classify_field_risk(f["field_id"])
            snapshot = FieldSnapshot(
                field_id=f["field_id"],
                page_id=page_id,
                question_text=f["question_text"],
                input_type=f["input_type"],
                allowed_values=f["allowed_values"],
                required=f["required"],
                visible=f["visible"],
                current_value=f["current_value"],
                risk_category="clinical" if risk != "green" else "administrative",
                page_version=version_attr
            )
            snapshots.append(snapshot)

        return PageSnapshot(
            page_id=page_id,
            current_step=current_step,
            page_version=version_attr,
            visible_fields=snapshots
        )
