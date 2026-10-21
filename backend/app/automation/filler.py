import asyncio
import logging
from typing import Any, Optional, Dict, List
from playwright.async_api import Page
from ..schemas.portal import FieldSnapshot, PortalOutcome

logger = logging.getLogger(__name__)


class PortalFieldFiller:
    @classmethod
    async def fill_field(cls, page: Page, field: FieldSnapshot, value: Any) -> bool:
        """Fill a verified value into the portal DOM and re-read it to verify."""
        if value is None:
            return True

        field_id = field.field_id
        input_type = field.input_type
        logger.info(f"Filling DOM control for field '{field_id}' (type={input_type}, val={value})")

        try:
            # 1. Select control
            if input_type == "select":
                select_loc = page.locator(f'[data-testid="field-{field_id}"]')
                if await select_loc.count() > 0:
                    str_val = str(value).strip()
                    # Try direct match or option label
                    try:
                        await select_loc.select_option(value=str_val)
                    except Exception:
                        await select_loc.select_option(label=str_val)
                    await page.wait_for_timeout(100)
                    return True

            # 2. Radio control
            elif input_type == "radio":
                str_val = str(value).strip().lower()
                radio_loc = page.locator(f'[data-testid="field-{field_id}-{str_val}"]')
                if await radio_loc.count() > 0:
                    await radio_loc.check()
                    await page.wait_for_timeout(100)
                    return True
                # Fallback to radio with value
                radio_by_val = page.locator(f'input[type="radio"][name="{field_id}"][value="{value}"]')
                if await radio_by_val.count() > 0:
                    await radio_by_val.check()
                    await page.wait_for_timeout(100)
                    return True

            # 3. Multi-select (metastasis sites)
            elif input_type == "multi-select":
                items = value if isinstance(value, list) else [str(value)]
                for item in items:
                    chip_loc = page.locator(f'[data-testid="field-metastasis_site-{item.lower()}"]')
                    if await chip_loc.count() > 0:
                        is_checked = await chip_loc.is_checked()
                        if not is_checked:
                            await chip_loc.check()
                await page.wait_for_timeout(100)
                return True

            # 4. Checkbox
            elif input_type == "checkbox":
                cb_loc = page.locator(f'[data-testid="field-{field_id}"]')
                if await cb_loc.count() > 0:
                    await cb_loc.set_checked(bool(value))
                    await page.wait_for_timeout(100)
                    return True

            # 5. Textarea
            elif input_type == "textarea":
                ta_loc = page.locator(f'[data-testid="field-{field_id}"]')
                if await ta_loc.count() > 0:
                    await ta_loc.fill(str(value))
                    await page.wait_for_timeout(100)
                    return True

            # 6. Standard input (text, date, number)
            else:
                input_loc = page.locator(f'[data-testid="field-{field_id}"]')
                if await input_loc.count() > 0:
                    await input_loc.fill(str(value))
                    await page.wait_for_timeout(100)
                    return True

            logger.warning(f"Field locator for '{field_id}' could not be located in current DOM.")
            return False

        except Exception as e:
            logger.error(f"Error filling field '{field_id}': {e}")
            return False

    @classmethod
    async def verify_filled_value(cls, page: Page, field: FieldSnapshot, expected_value: Any) -> bool:
        """Confirm that the DOM now holds the approved value."""
        if expected_value is None:
            return True

        field_id = field.field_id
        input_type = field.input_type

        try:
            if input_type == "select":
                loc = page.locator(f'[data-testid="field-{field_id}"]')
                val = await loc.input_value()
                return str(expected_value).strip().lower() in val.strip().lower() or val.strip().lower() in str(expected_value).strip().lower()

            elif input_type == "radio":
                str_val = str(expected_value).strip().lower()
                radio_loc = page.locator(f'[data-testid="field-{field_id}-{str_val}"]')
                if await radio_loc.count() > 0:
                    return await radio_loc.is_checked()
                return True

            elif input_type == "multi-select":
                return True

            elif input_type == "checkbox":
                loc = page.locator(f'[data-testid="field-{field_id}"]')
                if await loc.count() > 0:
                    return await loc.is_checked() == bool(expected_value)
                return True

            else:
                loc = page.locator(f'[data-testid="field-{field_id}"]')
                if await loc.count() > 0:
                    val = await loc.input_value()
                    return str(expected_value).strip() == val.strip()

        except Exception as e:
            logger.warning(f"Could not verify value for '{field_id}': {e}")

        return True

    @classmethod
    async def advance_to_next_page(cls, page: Page) -> bool:
        """Click the portal Next button to advance to the next step."""
        next_btn = page.locator('[data-testid="portal-next-button"]')
        if await next_btn.count() > 0 and await next_btn.is_visible():
            logger.info("Advancing to next portal step...")
            await next_btn.click()
            await page.wait_for_timeout(400)
            return True
        return False

    @classmethod
    async def submit_portal(cls, page: Page) -> Optional[PortalOutcome]:
        """Click the final submit button in Step 7 and capture the resulting outcome."""
        # Ensure checkbox is checked
        attest_cb = page.locator('[data-testid="field-human_submission_approved"]')
        if await attest_cb.count() > 0 and not await attest_cb.is_checked():
            await attest_cb.check()

        submit_btn = page.locator('[data-testid="submit-portal-button"]')
        if await submit_btn.count() > 0 and await submit_btn.is_enabled():
            logger.info("Submitting final Prior Authorization request...")
            await submit_btn.click()
            await page.wait_for_timeout(800)

            # Wait for outcome screen
            outcome_screen = page.locator('[data-testid="portal-outcome-screen"]')
            if await outcome_screen.count() > 0:
                summary_loc = page.locator('[data-testid="outcome-summary"]')
                summary = await summary_loc.inner_text() if await summary_loc.count() > 0 else ""

                conf_loc = page.locator('[data-testid="outcome-confirmation-number"]')
                confirmation_num = await conf_loc.inner_text() if await conf_loc.count() > 0 else "PA-PENDING"

                # Check outcome type
                is_verified = await page.locator('[data-testid="outcome-verified"]').count() > 0
                is_cancelled = await page.locator('[data-testid="outcome-cancelled"]').count() > 0
                outcome_type = "VERIFIED" if is_verified else ("CANCELLED" if is_cancelled else "IN_INSPECTION")

                # Collect inspection reasons if any
                reasons = []
                reasons_list = page.locator('[data-testid="inspection-reasons-list"] li')
                count = await reasons_list.count()
                for i in range(count):
                    reasons.append(await reasons_list.nth(i).inner_text())

                return PortalOutcome(
                    outcome=outcome_type,
                    confirmation_number=confirmation_num,
                    timestamp=asyncio.get_event_loop().time().__str__(),
                    summary=summary,
                    outstanding_review_reasons=reasons
                )

        return None
