.PHONY: install start-backend start-frontend test test-unit test-e2e build-frontend

install:
	python -m venv venv
	.\venv\Scripts\pip install -r backend\requirements.txt
	.\venv\Scripts\playwright install chromium
	cd frontend && npm install

start-backend:
	.\venv\Scripts\python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --loop app.loop:proactor_loop_factory --reload

start-frontend:
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build

test:
	.\venv\Scripts\pytest backend/tests -v

test-unit:
	.\venv\Scripts\pytest backend/tests/test_patient_service.py backend/tests/test_validation.py backend/tests/test_ai_provider.py backend/tests/test_safety_security.py backend/tests/test_workflow.py -v

test-e2e:
	.\venv\Scripts\pytest backend/tests/test_e2e_scenarios.py -v
