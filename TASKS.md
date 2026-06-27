# TASKS.md — Caja Inteligente Backend Implementation Plan

## General rule for the agent

Work task by task.
Do not move on to the next task until the current one compiles, passes basic linting, and has a clear implementation.

After each task, report:

1. Files created/modified.
2. Technical decisions made.
3. How to test it.
4. What remains pending.

Do not implement features that were not requested.

---

# Task 0 — Initialize project

## Objective

Create the base FastAPI project with `uv`, using `src/app` as the root package.

## Instructions

* Initialize Python project with `uv`.
* Create base structure `src/app`.
* Create `pyproject.toml`.
* Install main dependencies.
* Create `.env.example`.
* Create minimal `README.md`.
* Create folders defined in `AGENTS.md`.
* Do not create an `api/` folder.
* Do not create authentication.
* Do not create users.

## Required dependencies

```bash
uv add fastapi --extra standard
uv add pydantic-settings
uv add sqlalchemy asyncmy alembic
uv add python-multipart
uv add opencv-python-headless pillow
uv add google-genai
uv add httpx tenacity structlog
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy
```

## Acceptance criteria

* `src/app/main.py` exists.
* `.env.example` exists.
* The project runs with:

```bash
uv run fastapi dev src/app/main.py
```

* The `src/app/api` folder does not exist.

---

# Task 1 — Base FastAPI configuration

## Objective

Create a minimal FastAPI app and health endpoint.

## Instructions

Create:

```txt
src/app/main.py
src/app/core/config.py
src/app/core/logging.py
src/app/controllers/health_controller.py
```

Implement:

```http
GET /api/v1/health
```

Response:

```json
{
  "status": "ok",
  "service": "Caja Inteligente API"
}
```

Configure CORS from `.env`.

## Acceptance criteria

* `/api/v1/health` responds correctly.
* CORS reads `CORS_ORIGINS` from settings.
* There is no business logic in `main.py`.

---

# Task 2 — Domain and enums

## Objective

Create the core business enums.

## Instructions

Create:

```txt
src/app/domain/enums.py
src/app/domain/money.py
```

Required enums:

* `ManagementStatus`
* `MediaAssetStatus`
* `DocumentType`
* `TransactionSourceType`
* `TransactionType`
* `PaymentMethod`
* `TransactionStatus`
* `RiskLevel`
* `SalesFrequency`
* `DocumentaryEvidenceLevel`

Add helpers for Spanish labels.

Example:

```python
get_management_status_label("pending") -> "Pendiente"
```

## Acceptance criteria

* All statuses have a Spanish label.
* The backend does not depend on the frontend to translate labels.
* `Decimal` is used for money helpers.

---

# Task 3 — MySQL and SQLAlchemy configuration

## Objective

Configure async connection to MySQL.

## Instructions

Create:

```txt
src/app/core/database.py
src/app/models/base.py
```

Configure:

* `AsyncSession`
* `create_async_engine`
* dependency for getting a session
* SQLAlchemy declarative base

Use:

```env
DATABASE_URL="mysql+asyncmy://root:password@localhost:3306/caja_inteligente"
```

## Acceptance criteria

* Clean DB configuration exists.
* PostgreSQL is not used.
* SQLite is not used for the main app.
* There are no queries in controllers.

---

# Task 4 — SQLAlchemy models

## Objective

Create the 4 official MVP tables.

## Instructions

Create models:

```txt
src/app/models/customer.py
src/app/models/management.py
src/app/models/media_asset.py
src/app/models/transaction.py
```

Tables:

```txt
customers
managements
media_assets
transactions
```

Do not create:

```txt
users
advisors
organizations
roles
permissions
extraction_jobs
daily_summaries
audit_logs
```

Use:

* `CHAR(36)` for IDs.
* `DECIMAL(14, 2)` for money.
* `DECIMAL(5, 4)` for confidence.
* `JSON` for `analysis_summary`, `alerts`, `ai_raw_response`.
* `DATETIME` for timestamps.

## Acceptance criteria

* Relationships are well defined.
* `transactions.media_asset_id` is nullable.
* `managements` has persisted totals.
* `media_assets` stores file and AI metadata.

---

# Task 5 — Alembic and first migration

## Objective

Configure migrations.

## Instructions

* Configure Alembic.
* Make Alembic use the models from `src/app/models`.
* Create the first migration with the 4 tables.
* Validate that the migration runs against MySQL.

## Acceptance criteria

* `alembic upgrade head` creates the tables.
* The migration does not include extra tables.
* Basic indexes are included.

---

# Task 6 — Pydantic schemas

## Objective

Create request/response contracts.

## Instructions

Create:

```txt
src/app/schemas/common.py
src/app/schemas/customer_schema.py
src/app/schemas/management_schema.py
src/app/schemas/media_asset_schema.py
src/app/schemas/transaction_schema.py
src/app/schemas/extraction_schema.py
```

Include schemas for:

* Create management with customer data.
* List cards.
* Full management detail.
* Media asset response.
* Transaction response.
* Create manual transaction.
* Update transaction.
* Update status.
* Update advisor notes.
* Financial summary.
* AI extraction schema.

Rules:

* Money is returned as a string.
* Do not return ORM models.
* Include Spanish labels where applicable.

## Acceptance criteria

* Schemas represent exactly the MVP endpoints.
* There is no unnecessary `Any`.
* `FinancialExtractionSchema` validates Gemini output.

---

# Task 7 — Repositories

## Objective

Create the data access layer.

## Instructions

Create:

```txt
src/app/repositories/customer_repository.py
src/app/repositories/management_repository.py
src/app/repositories/media_asset_repository.py
src/app/repositories/transaction_repository.py
```

Minimum methods:

### CustomerRepository

* `create`
* `get_by_id`

### ManagementRepository

* `create`
* `get_by_id`
* `list`
* `update_status`
* `update_advisor_notes`
* `update_totals`
* `update_analysis`

### MediaAssetRepository

* `create`
* `update_processing_result`
* `mark_failed`
* `list_by_management`

### TransactionRepository

* `create_many`
* `create_manual`
* `get_by_id`
* `list_by_management`
* `update`
* `reject`
* `get_summary_by_management`

## Acceptance criteria

* Only repositories talk to SQLAlchemy.
* Controllers have no queries.
* Services do not build manual SQL.
* Methods have explicit types.

---

# Task 8 — SummaryService

## Objective

Centralize financial calculation.

## Instructions

Create:

```txt
src/app/services/summary_service.py
```

It must calculate:

* `total_income`
* `total_expense`
* `net_balance`
* `confidence_score`
* `sales_frequency`
* `documentary_evidence`
* `preliminary_risk`
* `alerts`

Rules:

* Exclude `rejected` transactions.
* Manual transactions do not affect `confidence_score`.
* If there are no AI transactions, `confidence_score = null`.
* Do not make a final credit decision.

## Acceptance criteria

* Pure and testable service.
* Uses `Decimal`.
* Has basic unit tests.

---

# Task 9 — Create management without images

## Objective

Implement the first functional flow without AI.

## Endpoint

```http
POST /api/v1/managements
```

Initially it must accept customer and application data, without processing files yet.

## Instructions

Create:

```txt
src/app/services/management_service.py
src/app/controllers/managements_controller.py
```

The endpoint must:

1. Create customer.
2. Create management.
3. Generate `application_code`.
4. Return full detail with:

   * customer
   * financial summary at zero
   * empty evidences
   * empty transactions
   * empty alerts

## Acceptance criteria

* An application can be created without images.
* Initial status is `pending`.
* `APP-001`, `APP-002`, etc. is generated.
* The response can already be used to render the detail screen.

---

# Task 10 — List and view managements

## Objective

Allow the frontend to render cards and detail.

## Endpoints

```http
GET /api/v1/managements?status=all
GET /api/v1/managements/{management_id}
```

## Instructions

List response must include:

* application code
* status and status_label
* submitted_at
* requested_amount
* customer mini info
* financial summary
* evidences_count
* alerts_count

Detail response must include:

* full customer
* full management
* financial summary
* evidences
* transactions
* alerts
* advisor_notes

## Acceptance criteria

* Filter by status works.
* `all` is not saved in DB; it is only used for filtering.
* Detail returns everything needed for the screen.

---

# Task 11 — Manual transaction

## Objective

Add manual failover.

## Endpoint

```http
POST /api/v1/managements/{management_id}/transactions
```

## Instructions

Create:

```txt
src/app/services/transaction_service.py
src/app/controllers/transactions_controller.py
```

It must:

1. Find management.
2. Create transaction with:

   * `source_type = manual`
   * `media_asset_id = null`
   * `status = manual`
   * `confidence_score = null`
3. Recalculate totals.
4. Persist totals in `managements`.
5. Return transaction + financial summary.

## Acceptance criteria

* Manual income can be added.
* Manual expense can be added.
* Totals are updated.
* `net_balance = income - expense`.

---

# Task 12 — Update and reject transactions

## Objective

Allow advisor data correction.

## Endpoints

```http
PATCH /api/v1/transactions/{transaction_id}
POST /api/v1/transactions/{transaction_id}/reject
```

## Rules

When updating:

* If `source_type = ai`, status becomes `corrected`.
* If `source_type = manual`, status remains `manual`.
* Recalculate totals.

When rejecting:

* Do not physically delete.
* Mark `status = rejected`.
* Exclude from totals.

## Acceptance criteria

* Editing a transaction updates the summary.
* Rejecting a transaction updates the summary.
* Rejected transactions remain visible in detail only if we decide to show them; by default, they may be omitted from the summary.

---

# Task 13 — Local storage provider

## Objective

Save images to local disk.

## Instructions

Create:

```txt
src/app/providers/storage/base.py
src/app/providers/storage/local_storage_provider.py
```

It must save:

```txt
storage/media/original/
storage/media/processed/
```

Do not store bytes in MySQL.

## Acceptance criteria

* Saves original file.
* Returns path.
* Handles safe filenames.
* Does not overwrite files with the same name.

---

# Task 14 — ImagePreprocessingService

## Objective

Preprocess images with OpenCV.

## Instructions

Create:

```txt
src/app/services/image_preprocessing_service.py
```

It must:

1. Receive bytes.
2. Decode image.
3. Resize if it is large.
4. Improve contrast.
5. Reduce noise.
6. Try adaptive thresholding.
7. Try perspective correction if there is a clear contour.
8. Return processed bytes.

If contour detection fails, return the enhanced image.

## Acceptance criteria

* Valid image returns bytes.
* Invalid bytes raise a controlled error.
* OpenCV is not used outside this service.

---

# Task 15 — Fake AI provider

## Objective

Implement a fake provider before the real Gemini one.

## Instructions

Create a temporary or test fake implementation that returns:

* document_type
* detected_amount
* raw_text
* transactions
* confidence_score
* warnings

This allows the full flow to be tested without spending Gemini calls.

## Acceptance criteria

* Evidence flow can work with fake provider.
* Tests do not call real Gemini.
* Provider complies with the defined interface.

---

# Task 16 — EvidenceProcessingService

## Objective

Process images and create media assets + transactions.

## Endpoint

```http
POST /api/v1/managements/{management_id}/evidence
```

## Instructions

Create:

```txt
src/app/services/evidence_processing_service.py
```

Flow:

1. Find management.
2. Create media asset in `uploaded`.
3. Save original.
4. Mark `processing`.
5. Preprocess image.
6. Save processed image.
7. Call AI provider.
8. Update media asset:

   * status
   * document_type
   * document_type_label
   * detected_amount
   * extracted_text
   * confidence_score
   * ai_raw_response
9. Create transactions with:

   * `source_type = ai`
   * `media_asset_id = media_asset.id`
   * `status = extracted`
10. Recalculate management.
11. Return full detail.

Rules:

* Adding evidence does not delete previous transactions.
* If an image fails, mark media asset as `failed`.
* If an image fails, try to continue with other images.
* If all images fail, return an error or detail with alerts, but do not break previous data.

## Acceptance criteria

* Multiple images can be added.
* Each AI transaction points to `media_asset_id`.
* Previous evidence is not deleted.
* Totals are recalculated.

---

# Task 17 — Create management with initial images

## Objective

Allow `POST /managements` to also process initial files.

## Instructions

Reuse `EvidenceProcessingService`.

The endpoint:

```http
POST /api/v1/managements
```

Must accept optional `files`.

If there are files:

1. Create customer.
2. Create management.
3. Process files the same way as in add evidence.
4. Return full detail.

If there are no files:

1. Create customer.
2. Create management.
3. Return empty full detail.

## Acceptance criteria

* Evidence logic is not duplicated.
* Image logic lives in `EvidenceProcessingService`.
* Creating with or without images works.

---

# Task 18 — Real Gemini provider

## Objective

Connect real Gemini Flash.

## Instructions

Create:

```txt
src/app/providers/ai/base.py
src/app/providers/ai/gemini_provider.py
src/app/services/ai_extraction_service.py
```

It must:

* Read `GEMINI_API_KEY`.
* Read `GEMINI_MODEL`.
* Send processed image.
* Request structured output.
* Validate with `FinancialExtractionSchema`.
* Retry once if output does not validate.
* Raise a controlled error if it fails.

## Acceptance criteria

* Services do not know the Gemini SDK.
* Provider can be replaced by fake.
* No hardcoded API key.
* Invalid response does not insert invalid transactions.

---

# Task 19 — Advisor notes and status change

## Objective

Allow the advisor’s final actions.

## Endpoints

```http
PATCH /api/v1/managements/{management_id}/advisor-notes
PATCH /api/v1/managements/{management_id}/status
```

## Instructions

Update:

* `advisor_notes`
* `status`

Validate allowed status:

```txt
pending
in_review
observed
ready_for_analysis
```

## Acceptance criteria

* Saving notes works.
* Changing status returns status and status_label.
* Invalid status returns an error in Spanish.

---

# Task 20 — Minimum tests

## Objective

Ensure the main flow.

## Required tests

1. Health endpoint returns ok.
2. Create management without files works.
3. List managements returns created management.
4. Get management detail returns customer and empty evidence.
5. Add manual income recalculates totals.
6. Add manual expense recalculates totals.
7. Update transaction recalculates totals.
8. Reject transaction excludes it from totals.
9. Invalid status is rejected.
10. Invalid image bytes are rejected by ImagePreprocessingService.
11. Adding evidence appends media assets.
12. Adding evidence does not delete previous manual transactions.

## Acceptance criteria

* Tests run with:

```bash
uv run pytest
```

* Tests do not call real Gemini.
* They use fake provider.

---

# Task 21 — Final quality

## Objective

Leave the project clean for demo.

## Instructions

Run:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy src
uv run pytest
```

Fix reasonable errors.

Do not make major last-minute refactors.

## Acceptance criteria

* App runs.
* Tests pass.
* Reasonable lint.
* No important dead imports.
* No folders or features outside the scope.

---

# Recommended execution order

Do not jump straight to Gemini.

Ideal order:

```txt
0. Initialize project
1. Base FastAPI
2. Enums
3. DB
4. Models
5. Alembic
6. Schemas
7. Repositories
8. Summary service
9. Create management without images
10. List/detail managements
11. Manual transaction
12. Update/reject transaction
13. Storage provider
14. Image preprocessing
15. Fake AI provider
16. Evidence processing
17. Create management with images
18. Real Gemini provider
19. Notes/status
20. Tests
21. Final quality
```

