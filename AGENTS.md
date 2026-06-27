# AGENTS.md — Caja Inteligente Backend

## Project Context

This project is the backend for **Caja Inteligente Bolivia**, a hackathon MVP.

Caja Inteligente helps a credit advisor structure financial information from informal merchants. The advisor uses a small React frontend to create a credit application, register customer data, upload evidence images such as QR payment receipts, notebook photos, purchase receipts, or expense notes, and review the extracted financial information.

The backend receives the credit application data and evidence images, preprocesses images with OpenCV, sends them to Gemini Flash for financial extraction, stores the extracted transactions, and returns a summary that the frontend can render.

The MVP is intentionally simple.

There is no authentication.
There are no users.
There are no advisors.
There are no organizations.
There is no WhatsApp integration.
There is no sync engine.
There is no background job system.

The system assumes an anonymous credit advisor is using the frontend.

---

## Tech Stack

Use:

* Python 3.12+
* FastAPI
* uv
* MySQL 8
* SQLAlchemy 2 async
* asyncmy
* Alembic
* Pydantic v2
* Pydantic Settings
* OpenCV headless
* Pillow
* Google GenAI SDK
* python-multipart
* pytest
* pytest-asyncio
* ruff
* mypy

Do not use:

* PostgreSQL
* SQLite for the main app
* Django
* Flask
* Celery
* Redis
* Firebase
* Supabase
* WhatsApp SDKs
* Twilio
* MessageBird

---

## Main Goal

Build a clean, typed, hackathon-friendly backend that supports this flow:

1. The credit advisor creates a credit application from the React frontend.
2. The request includes customer data, requested loan amount, business description, and optional evidence images.
3. The backend creates:

   * customer
   * management
   * media assets for uploaded files
   * transactions extracted from evidence images, when images are provided
4. The backend preprocesses images with OpenCV.
5. The backend sends processed images to Gemini Flash.
6. Gemini returns structured financial extraction data.
7. The backend validates the AI output with Pydantic.
8. The backend stores extracted transactions.
9. The backend calculates:

   * total income
   * total expense
   * net balance
   * confidence score
   * evidence quality
   * preliminary risk
   * alerts
10. The frontend can list applications by status.
11. The frontend can view full application detail.
12. The advisor can add more evidence images later.
13. The advisor can manually add a transaction as failover.
14. The advisor can correct or reject transactions.
15. The advisor can save notes and change application status.

---

## Non-Goals

Do not implement:

* Authentication
* Login
* Registration
* JWT
* Roles
* Permissions
* Advisor table
* Organization table
* User profile
* WhatsApp integration
* External messaging integrations
* Push notifications
* Background tasks
* Celery
* Redis
* WebSockets
* Credit scoring model
* Loan approval engine
* SIAT/tax integration
* Payment integrations
* Multi-tenant architecture
* Complex audit logs
* Complex reporting
* Overengineered domain-driven design

This MVP structures financial evidence. It does not approve or reject loans.

---

## Package Root

Use this package root:

```txt
src/app
```

Do not create:

```txt
src/caja_inteligente
```

All imports should use `app`.

Example:

```python
from app.services.management_service import ManagementService
from app.schemas.management_schema import ManagementDetailResponse
from app.domain.enums import ManagementStatus
```

---

## Folder Structure

Use this structure:

```txt
src/
└── app/
    ├── __init__.py
    ├── main.py
    ├── controllers/
    │   ├── __init__.py
    │   ├── health_controller.py
    │   ├── managements_controller.py
    │   └── transactions_controller.py
    ├── core/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── database.py
    │   ├── exceptions.py
    │   └── logging.py
    ├── domain/
    │   ├── __init__.py
    │   ├── enums.py
    │   ├── errors.py
    │   └── money.py
    ├── models/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── customer.py
    │   ├── management.py
    │   ├── media_asset.py
    │   └── transaction.py
    ├── schemas/
    │   ├── __init__.py
    │   ├── common.py
    │   ├── customer_schema.py
    │   ├── management_schema.py
    │   ├── media_asset_schema.py
    │   ├── transaction_schema.py
    │   └── extraction_schema.py
    ├── repositories/
    │   ├── __init__.py
    │   ├── customer_repository.py
    │   ├── management_repository.py
    │   ├── media_asset_repository.py
    │   └── transaction_repository.py
    ├── services/
    │   ├── __init__.py
    │   ├── management_service.py
    │   ├── image_preprocessing_service.py
    │   ├── ai_extraction_service.py
    │   ├── evidence_processing_service.py
    │   ├── transaction_service.py
    │   └── summary_service.py
    ├── providers/
    │   ├── __init__.py
    │   ├── ai/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── gemini_provider.py
    │   └── storage/
    │       ├── __init__.py
    │       ├── base.py
    │       └── local_storage_provider.py
    └── utils/
        ├── __init__.py
        ├── dates.py
        ├── files.py
        └── images.py
```

Do not create an `api/` folder.

In this project:

* HTTP endpoints live in `controllers/`.
* External integrations live in `providers/`.
* Business use cases live in `services/`.
* Database access lives in `repositories/`.

---

## Architecture Rules

Use a simple layered architecture.

Dependency direction:

```txt
controllers -> services -> repositories -> models
controllers -> services -> providers
services -> schemas/domain
repositories -> models
providers -> external SDKs
```

Do not create circular imports.

Do not make lower layers depend on higher layers.

---

## Layer Responsibilities

### Controllers

Controllers expose FastAPI endpoints.

Controllers may:

* Receive HTTP requests.
* Parse query parameters.
* Receive multipart form data.
* Receive uploaded files.
* Call services.
* Return Pydantic response schemas.

Controllers must not:

* Contain business logic.
* Access SQLAlchemy directly.
* Call Gemini directly.
* Use OpenCV directly.
* Calculate totals directly.
* Save files directly.
* Build SQL queries directly.

---

### Services

Services contain business use cases.

Services may:

* Orchestrate repositories.
* Call providers.
* Apply business rules.
* Calculate financial totals.
* Determine review status.
* Coordinate image preprocessing and AI extraction.
* Build response DTOs.

Services must not:

* Receive raw FastAPI `Request` objects.
* Return ORM models directly to controllers.
* Depend on HTTP details.
* Build SQL queries directly.

---

### Repositories

Repositories are the only layer allowed to access the database.

Repositories must:

* Use SQLAlchemy 2 async.
* Encapsulate database queries.
* Return ORM models or typed data needed by services.
* Be explicit and descriptive.

Repositories must not:

* Call services.
* Call external APIs.
* Use OpenCV.
* Call Gemini.
* Perform business orchestration.

---

### Models

Models are SQLAlchemy ORM tables.

Models answer:

```txt
How is this stored in MySQL?
```

Models must not contain business orchestration logic.

---

### Schemas

Schemas are Pydantic DTOs.

Schemas answer:

```txt
What data enters or leaves the API?
```

Use schemas for:

* Request payloads.
* Response payloads.
* AI structured output.
* Internal validated DTOs when helpful.

Do not return ORM models directly from controllers.

---

### Domain

Domain contains pure business concepts.

Use it for:

* Enums
* Value objects
* Domain errors
* Small pure business rules

Domain must not depend on:

* FastAPI
* SQLAlchemy
* Gemini
* OpenCV
* HTTP clients

Keep domain small. Do not overengineer.

---

### Providers

Providers encapsulate external systems.

Use providers for:

* Gemini integration
* Local file storage
* Future external APIs if needed

Providers hide SDK details from services.

Example:

```txt
AIExtractionService -> FinancialExtractionProvider -> Gemini SDK
```

The service should not know Gemini SDK internals.

This allows tests to use fake providers without calling real Gemini.

---

## Database

Use MySQL 8.

Use SQLAlchemy async with `asyncmy`.

Use Alembic for migrations.

Use `CHAR(36)` UUID strings for IDs.

Use `DECIMAL(14, 2)` for money.

Use `DECIMAL(5, 4)` for confidence scores.

Use MySQL `JSON` columns for flexible AI analysis fields.

Do not use floats for money.

Do not use PostgreSQL-only features.

---

## Required Tables

Use exactly these main tables:

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
sync_queue
```

---

## Table: customers

Represents the informal merchant/customer.

Columns:

```txt
id CHAR(36) PRIMARY KEY

full_name VARCHAR(180) NOT NULL
phone_number VARCHAR(40) NULL
business_name VARCHAR(180) NULL
business_type VARCHAR(120) NULL
business_description TEXT NULL
market_location VARCHAR(180) NULL

created_at DATETIME NOT NULL
updated_at DATETIME NOT NULL
```

Indexes:

```txt
idx_customers_full_name
idx_customers_phone_number
```

---

## Table: managements

Represents a credit application / credit management request.

This is the central table of the MVP.

Columns:

```txt
id CHAR(36) PRIMARY KEY
customer_id CHAR(36) NOT NULL FK customers.id

application_code VARCHAR(40) NOT NULL

requested_amount DECIMAL(14, 2) NOT NULL
currency VARCHAR(10) NOT NULL DEFAULT 'BOB'

status VARCHAR(40) NOT NULL

submitted_at DATETIME NOT NULL
visit_date DATE NULL

advisor_notes TEXT NULL

total_income DECIMAL(14, 2) NOT NULL DEFAULT 0
total_expense DECIMAL(14, 2) NOT NULL DEFAULT 0
net_balance DECIMAL(14, 2) NOT NULL DEFAULT 0
confidence_score DECIMAL(5, 4) NULL

analysis_summary JSON NULL
alerts JSON NULL

error_message TEXT NULL

created_at DATETIME NOT NULL
updated_at DATETIME NOT NULL
```

Indexes:

```txt
idx_managements_customer_id
idx_managements_status
idx_managements_submitted_at
idx_managements_application_code
```

Allowed status values:

```txt
pending
in_review
observed
ready_for_analysis
```

Spanish labels:

```txt
pending             -> Pendiente
in_review           -> En revisión
observed            -> Observado
ready_for_analysis  -> Listo para análisis
```

`all` / `Todos` is only a frontend filter. Do not store it in the database.

---

## Table: media_assets

Represents every uploaded image/evidence document.

Columns:

```txt
id CHAR(36) PRIMARY KEY
management_id CHAR(36) NOT NULL FK managements.id
customer_id CHAR(36) NOT NULL FK customers.id

original_filename VARCHAR(255) NOT NULL
mime_type VARCHAR(80) NOT NULL
size_bytes INT NOT NULL

original_path TEXT NOT NULL
processed_path TEXT NULL

document_type VARCHAR(80) NULL
document_type_label VARCHAR(120) NULL

status VARCHAR(40) NOT NULL

detected_amount DECIMAL(14, 2) NULL
extracted_text TEXT NULL
confidence_score DECIMAL(5, 4) NULL

ai_raw_response JSON NULL
error_message TEXT NULL

created_at DATETIME NOT NULL
updated_at DATETIME NOT NULL
```

Indexes:

```txt
idx_media_assets_management_id
idx_media_assets_customer_id
idx_media_assets_status
```

Allowed media status values:

```txt
uploaded
processing
processed
review
failed
```

Spanish labels:

```txt
uploaded   -> Subido
processing -> Procesando
processed  -> Procesado
review     -> Revisar
failed     -> Fallido
```

Allowed document type values:

```txt
sales_notebook
qr_receipt
purchase_receipt
expense_note
mixed
unknown
```

Spanish labels:

```txt
sales_notebook    -> Cuaderno de ventas
qr_receipt        -> Comprobante QR
purchase_receipt  -> Recibo de compra
expense_note      -> Nota de gasto
mixed             -> Mixto
unknown           -> Desconocido
```

---

## Table: transactions

Represents every financial movement.

A transaction may come from AI extraction or be created manually by the advisor.

Columns:

```txt
id CHAR(36) PRIMARY KEY
management_id CHAR(36) NOT NULL FK managements.id
customer_id CHAR(36) NOT NULL FK customers.id
media_asset_id CHAR(36) NULL FK media_assets.id

source_type VARCHAR(40) NOT NULL

transaction_type VARCHAR(40) NOT NULL
amount DECIMAL(14, 2) NOT NULL
currency VARCHAR(10) NOT NULL DEFAULT 'BOB'

description VARCHAR(255) NULL
transaction_date DATE NULL
payment_method VARCHAR(40) NOT NULL
evidence_text TEXT NULL

confidence_score DECIMAL(5, 4) NULL
status VARCHAR(40) NOT NULL

created_at DATETIME NOT NULL
updated_at DATETIME NOT NULL
```

Indexes:

```txt
idx_transactions_management_id
idx_transactions_customer_id
idx_transactions_media_asset_id
idx_transactions_status
idx_transactions_type
```

Allowed source type values:

```txt
ai
manual
```

Allowed transaction type values:

```txt
income
expense
unknown
```

Allowed payment method values:

```txt
qr
cash
transfer
unknown
```

Allowed transaction status values:

```txt
extracted
confirmed
rejected
corrected
manual
```

Rules:

* `media_asset_id` is required for AI-extracted transactions.
* `media_asset_id` is null for manual transactions.
* `source_type = ai` for Gemini extracted transactions.
* `source_type = manual` for advisor-created transactions.
* Rejected transactions must not count in totals.

---

## Relationships

```txt
customers
  └── managements
        ├── media_assets
        │     └── transactions
        └── manual transactions
```

Business meaning:

```txt
A customer has many managements.
A management has many media assets.
A media asset may produce many transactions.
A management may also have manual transactions.
```

---

## Enums

Use `StrEnum` for domain enums.

Create enums in:

```txt
src/app/domain/enums.py
```

Required enums:

```python
from enum import StrEnum


class ManagementStatus(StrEnum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    OBSERVED = "observed"
    READY_FOR_ANALYSIS = "ready_for_analysis"


class MediaAssetStatus(StrEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    REVIEW = "review"
    FAILED = "failed"


class DocumentType(StrEnum):
    SALES_NOTEBOOK = "sales_notebook"
    QR_RECEIPT = "qr_receipt"
    PURCHASE_RECEIPT = "purchase_receipt"
    EXPENSE_NOTE = "expense_note"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class TransactionSourceType(StrEnum):
    AI = "ai"
    MANUAL = "manual"


class TransactionType(StrEnum):
    INCOME = "income"
    EXPENSE = "expense"
    UNKNOWN = "unknown"


class PaymentMethod(StrEnum):
    QR = "qr"
    CASH = "cash"
    TRANSFER = "transfer"
    UNKNOWN = "unknown"


class TransactionStatus(StrEnum):
    EXTRACTED = "extracted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CORRECTED = "corrected"
    MANUAL = "manual"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class SalesFrequency(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class DocumentaryEvidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"
```

---

## Label Mapping

Create label mapping helpers in domain or schemas.

All user-facing labels must be in Spanish.

Examples:

```txt
pending -> Pendiente
in_review -> En revisión
observed -> Observado
ready_for_analysis -> Listo para análisis

low -> Bajo
medium -> Media
high -> Alta
unknown -> Desconocido
```

Do not make the frontend guess labels.

The backend should return both raw values and display labels when useful.

---

## Money Rules

Use `Decimal` for money everywhere.

Never use `float` for money.

Response money values must be strings.

Example:

```json
{
  "requested_amount": "8000.00",
  "total_income": "12400.00",
  "total_expense": "8200.00",
  "net_balance": "4200.00"
}
```

Create helper functions in:

```txt
src/app/domain/money.py
```

Useful helpers:

```python
from decimal import Decimal


def zero_money() -> Decimal:
    return Decimal("0.00")


def format_money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'))}"
```

---

## Environment Variables

Create `.env.example`.

Required variables:

```env
APP_NAME="Caja Inteligente API"
APP_ENV="local"
APP_DEBUG=true

DATABASE_URL="mysql+asyncmy://root:password@localhost:3306/caja_inteligente"

GEMINI_API_KEY="replace-me"
GEMINI_MODEL="gemini-3-flash-preview"

MEDIA_STORAGE_DRIVER="local"
LOCAL_MEDIA_DIR="./storage/media"

DEFAULT_CURRENCY="BOB"
TIMEZONE="America/La_Paz"

CORS_ORIGINS="http://localhost:5173,http://localhost:3000"
```

Rules:

* Never hardcode API keys.
* Never hardcode Gemini model names in services.
* Read config through `core/config.py`.
* Use `pydantic-settings`.
* CORS origins must come from config.

---

## Dependencies

Install with uv only.

Do not use pip directly.

Required dependencies:

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

Run commands:

```bash
uv run fastapi dev src/app/main.py
uv run pytest
uv run ruff check .
uv run ruff format .
uv run mypy src
```

---

## API Base Path

All endpoints must be under:

```txt
/api/v1
```

---

## Final MVP Endpoints

Implement only these endpoints:

```txt
GET    /api/v1/health

POST   /api/v1/managements
GET    /api/v1/managements
GET    /api/v1/managements/{management_id}

POST   /api/v1/managements/{management_id}/evidence
POST   /api/v1/managements/{management_id}/transactions

PATCH  /api/v1/transactions/{transaction_id}
POST   /api/v1/transactions/{transaction_id}/reject

PATCH  /api/v1/managements/{management_id}/advisor-notes
PATCH  /api/v1/managements/{management_id}/status
```

Do not create extra endpoints unless explicitly requested.

---

## Endpoint: Health

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

---

## Endpoint: Create Management

```http
POST /api/v1/managements
Content-Type: multipart/form-data
```

This endpoint creates:

* customer
* management
* optional media assets
* optional AI extracted transactions

Fields:

```txt
full_name: string
phone_number: string | optional
business_name: string | optional
business_type: string | optional
business_description: string | optional
market_location: string | optional

requested_amount: decimal
currency: string, default BOB
visit_date: date | optional
advisor_notes: string | optional

files: image[] | optional
```

Supported image MIME types:

```txt
image/jpeg
image/png
image/webp
```

Behavior:

1. Create customer.
2. Generate application code, for example `APP-001`.
3. Create management with status `pending`.
4. If files are provided:

   * Create media assets.
   * Store original files.
   * Preprocess images with OpenCV.
   * Store processed images.
   * Send processed images to Gemini.
   * Validate AI output with Pydantic.
   * Update media asset metadata.
   * Insert extracted transactions.
   * Recalculate management totals.
   * Generate alerts.
   * Generate analysis summary.
5. Return management detail response.

If no files are provided:

* Create customer.
* Create management.
* Totals remain zero.
* Evidences list is empty.
* Transactions list is empty.
* Status remains `pending`.

Response shape:

```json
{
  "id": "uuid",
  "application_code": "APP-001",
  "status": "pending",
  "status_label": "Pendiente",
  "submitted_at": "2026-06-25T05:30:00",
  "requested_amount": "8000.00",
  "currency": "BOB",
  "customer": {
    "id": "uuid",
    "full_name": "María Quispe Huanca",
    "phone_number": "76543210",
    "business_name": "Tienda de abarrotes",
    "business_type": "Abarrotes",
    "business_description": "Tienda de abarrotes en la zona 16 de Julio, El Alto. Vendo productos básicos como arroz, azúcar, aceite y artículos de limpieza. Tengo 5 años en el negocio.",
    "market_location": "Zona 16 de Julio, El Alto"
  },
  "financial_summary": {
    "total_income": "12400.00",
    "total_expense": "8200.00",
    "net_balance": "4200.00",
    "sales_frequency": "Alta",
    "documentary_evidence": "Media",
    "preliminary_risk": "Bajo",
    "confidence_score": 0.87
  },
  "evidences": [
    {
      "id": "uuid",
      "filename": "Cuaderno de ventas junio 2026.jpg",
      "status": "processed",
      "status_label": "Procesado",
      "document_type": "sales_notebook",
      "document_type_label": "Cuaderno de ventas",
      "detected_amount": "12400.00",
      "confidence_score": 0.87,
      "extracted_text": "Ventas junio 2026..."
    }
  ],
  "transactions": [
    {
      "id": "uuid",
      "media_asset_id": "uuid",
      "source_type": "ai",
      "transaction_type": "income",
      "amount": "12400.00",
      "currency": "BOB",
      "description": "Ventas detectadas en cuaderno",
      "transaction_date": "2026-06-25",
      "payment_method": "cash",
      "evidence_text": "Total ventas junio Bs 12.400",
      "confidence_score": 0.87,
      "status": "extracted"
    }
  ],
  "alerts": [
    {
      "level": "warning",
      "message": "El recibo de compra de mercadería tiene baja confianza de lectura (72%). Verificar documento original.",
      "evidence_id": "uuid"
    }
  ],
  "advisor_notes": null
}
```

`evidence_id` is the media asset the alert refers to (the frontend shows it on that
evidence's card), or `null` for management-level alerts not tied to a single evidence.

---

## Endpoint: List Managements

```http
GET /api/v1/managements?status=all
```

Allowed status filter values:

```txt
all
pending
in_review
observed
ready_for_analysis
```

Response for frontend cards:

```json
{
  "items": [
    {
      "id": "uuid",
      "application_code": "APP-001",
      "status": "pending",
      "status_label": "Pendiente",
      "submitted_at": "2026-06-25T05:30:00",
      "requested_amount": "8000.00",
      "currency": "BOB",
      "customer": {
        "full_name": "María Quispe Huanca",
        "phone_number": "76543210",
        "business_name": "Tienda de abarrotes"
      },
      "financial_summary": {
        "total_income": "12400.00",
        "total_expense": "8200.00",
        "net_balance": "4200.00",
        "preliminary_risk": "Bajo",
        "confidence_score": 0.87
      },
      "evidences_count": 3,
      "alerts_count": 2
    }
  ]
}
```

SQL intent:

```sql
SELECT
  m.id,
  m.application_code,
  m.status,
  m.submitted_at,
  m.requested_amount,
  m.currency,
  m.total_income,
  m.total_expense,
  m.net_balance,
  m.confidence_score,
  m.analysis_summary,
  m.alerts,
  c.full_name,
  c.phone_number,
  c.business_name,
  COUNT(DISTINCT ma.id) AS evidences_count
FROM managements m
JOIN customers c ON c.id = m.customer_id
LEFT JOIN media_assets ma ON ma.management_id = m.id
WHERE (:status = 'all' OR m.status = :status)
GROUP BY m.id, c.id
ORDER BY m.submitted_at DESC;
```

---

## Endpoint: Get Management Detail

```http
GET /api/v1/managements/{management_id}
```

Response includes:

* customer
* management/application data
* financial summary
* media assets/evidences
* transactions
* alerts
* advisor notes

Response shape must match the create management response.

---

## Endpoint: Add Evidence to Existing Management

```http
POST /api/v1/managements/{management_id}/evidence
Content-Type: multipart/form-data
```

Form fields:

```txt
files: image[]
```

Behavior:

1. Find management.
2. Create media assets for new files.
3. Store original images.
4. Preprocess images.
5. Store processed images.
6. Send only the new images to Gemini.
7. Validate AI output.
8. Update media asset metadata.
9. Insert new transactions linked to `media_asset_id`.
10. Recalculate management totals.
11. Regenerate alerts and analysis summary.
12. Return full management detail.

Rules:

* Do not delete previous media assets.
* Do not delete previous transactions.
* Only append new evidence and new transactions.
* If one image fails, mark that media asset as `failed` and continue processing the others when possible.

---

## Endpoint: Add Manual Transaction

```http
POST /api/v1/managements/{management_id}/transactions
```

Used as failover when AI extraction fails or the advisor wants to add information manually.

Request:

```json
{
  "transaction_type": "expense",
  "amount": "120.00",
  "currency": "BOB",
  "description": "Transporte para compra de mercadería",
  "transaction_date": "2026-06-25",
  "payment_method": "cash"
}
```

Behavior:

1. Find management.
2. Create transaction with:

   * `source_type = manual`
   * `media_asset_id = null`
   * `status = manual`
   * `confidence_score = null`
3. Recalculate management totals.
4. Return created transaction and updated financial summary.

Response:

```json
{
  "transaction": {
    "id": "uuid",
    "management_id": "uuid",
    "media_asset_id": null,
    "source_type": "manual",
    "transaction_type": "expense",
    "amount": "120.00",
    "currency": "BOB",
    "description": "Transporte para compra de mercadería",
    "transaction_date": "2026-06-25",
    "payment_method": "cash",
    "confidence_score": null,
    "status": "manual"
  },
  "financial_summary": {
    "total_income": "12400.00",
    "total_expense": "8320.00",
    "net_balance": "4080.00",
    "confidence_score": 0.87
  }
}
```

---

## Endpoint: Update Transaction

```http
PATCH /api/v1/transactions/{transaction_id}
```

Works for both AI transactions and manual transactions.

Request:

```json
{
  "transaction_type": "income",
  "amount": "3200.00",
  "description": "Pago QR BCP corregido",
  "transaction_date": "2026-06-25",
  "payment_method": "qr"
}
```

Behavior:

1. Find transaction.
2. Update provided fields.
3. If transaction `source_type = ai`, set status to `corrected`.
4. If transaction `source_type = manual`, keep status as `manual`.
5. Recalculate management totals.
6. Return transaction and updated summary.

---

## Endpoint: Reject Transaction

```http
POST /api/v1/transactions/{transaction_id}/reject
```

Behavior:

1. Find transaction.
2. Set status to `rejected`.
3. Recalculate management totals excluding rejected transactions.
4. Return transaction ID and updated summary.

Do not physically delete rejected transactions.

---

## Endpoint: Update Advisor Notes

```http
PATCH /api/v1/managements/{management_id}/advisor-notes
```

Request:

```json
{
  "advisor_notes": "Cliente con negocio estable. Verificar recibo observado."
}
```

Response:

```json
{
  "management_id": "uuid",
  "advisor_notes": "Cliente con negocio estable. Verificar recibo observado."
}
```

---

## Endpoint: Update Management Status

```http
PATCH /api/v1/managements/{management_id}/status
```

Request:

```json
{
  "status": "ready_for_analysis"
}
```

Response:

```json
{
  "management_id": "uuid",
  "status": "ready_for_analysis",
  "status_label": "Listo para análisis"
}
```

Allowed values:

```txt
pending
in_review
observed
ready_for_analysis
```

---

## Summary Rules

Totals are stored in `managements` and recalculated whenever transactions change.

Recalculate after:

* AI extraction
* Adding evidence
* Adding manual transaction
* Updating transaction
* Rejecting transaction

Only count transactions where:

```txt
status != rejected
```

Rules:

```txt
total_income = sum(amount where transaction_type = income and status != rejected)
total_expense = sum(amount where transaction_type = expense and status != rejected)
net_balance = total_income - total_expense
```

Confidence score:

```txt
Use average confidence of non-rejected AI transactions with non-null confidence.
Manual transactions do not affect confidence_score.
If there are no AI transactions, confidence_score = null.
```

---

## Review and Alert Rules

A management should generate alerts when:

* Any media asset has confidence below 0.75.
* Any transaction has confidence below 0.75.
* Any transaction type is `unknown`.
* Any media asset failed.
* No transactions were found after processing evidence.
* Gemini returns warnings.
* Optional: detected income is much higher than usual within the same management evidence.

Alert shape:

```json
{
  "level": "warning",
  "message": "El recibo de compra de mercadería tiene baja confianza de lectura (72%). Verificar documento original.",
  "evidence_id": "uuid"
}
```

`evidence_id` is the related media asset id when the alert is about a specific evidence
(failed/low-confidence media, Gemini warnings) or the evidence behind a flagged transaction;
it is `null` for management-level alerts (e.g. evidence processed but no transactions found).

Allowed alert levels:

```txt
info
warning
error
```

Status rule:

```txt
Do not automatically set the management status to observed unless the advisor chooses that status.
```

AI may produce alerts, but status changes are advisor-controlled.

Default status after creation:

```txt
pending
```

---

## Analysis Summary Rules

Store analysis summary in `managements.analysis_summary`.

Shape:

```json
{
  "sales_frequency": {
    "value": "high",
    "label": "Alta"
  },
  "documentary_evidence": {
    "value": "medium",
    "label": "Media"
  },
  "preliminary_risk": {
    "value": "low",
    "label": "Bajo"
  }
}
```

Simple MVP rules:

```txt
sales_frequency:
- high if there are many income transactions or strong sales evidence
- medium if there is some income evidence
- low if little income evidence
- unknown if no data

documentary_evidence:
- high if multiple processed evidences have confidence >= 0.85
- medium if evidence exists but some items need review
- low if most evidence failed or confidence is low
- unknown if no evidence

preliminary_risk:
- low if net_balance is positive and evidence quality is medium/high
- medium if net_balance is positive but evidence quality is low or mixed
- high if net_balance is negative or many documents failed
- unknown if insufficient data
```

This is only preliminary guidance for the advisor. It is not a credit decision.

---

## AI Extraction

Use Gemini through a provider.

Do not call Gemini directly from controllers or services that are not AI-specific.

Provider interface:

```python
from typing import Protocol


class FinancialExtractionProvider(Protocol):
    async def extract_from_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        filename: str,
    ) -> "FinancialExtractionSchema":
        ...
```

Use Gemini implementation:

```txt
providers/ai/gemini_provider.py
```

The provider should:

* Read API key from config.
* Read model name from config.
* Send image to Gemini.
* Request structured JSON output.
* Return data validated by Pydantic.

---

## AI Extraction Schema

Create in:

```txt
schemas/extraction_schema.py
```

Use Pydantic v2.

Required schema:

```python
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field


class ExtractedTransactionSchema(BaseModel):
    transaction_type: Literal["income", "expense", "unknown"]
    amount: Decimal = Field(gt=0)
    currency: str = "BOB"
    description: str | None = None
    transaction_date: str | None = None
    payment_method: Literal["qr", "cash", "transfer", "unknown"] = "unknown"
    evidence_text: str | None = None
    confidence_score: float = Field(ge=0, le=1)


class FinancialExtractionSchema(BaseModel):
    document_type: Literal[
        "sales_notebook",
        "qr_receipt",
        "purchase_receipt",
        "expense_note",
        "mixed",
        "unknown",
    ]
    document_type_label: str | None = None
    detected_amount: Decimal | None = None
    raw_text: str | None = None
    transactions: list[ExtractedTransactionSchema] = Field(default_factory=list)
    confidence_score: float = Field(ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)
```

Rules:

* Validate Gemini output with Pydantic.
* If output is invalid, retry once.
* If second attempt fails, mark media asset as failed.
* Store raw AI response in `media_assets.ai_raw_response`.
* Do not insert invalid transactions.
* Do not invent missing data.

---

## Gemini Prompt

Use this prompt as the base instruction:

```txt
You are a financial extraction assistant for informal merchants in Bolivia.

You will receive one image that may contain:
- QR payment receipt
- bank transfer receipt
- notebook page with daily or monthly sales
- notebook page with expenses
- handwritten financial notes
- purchase receipt
- expense receipt
- mixed income and expense records

Extract only information that is visible in the image.

Rules:
1. Do not invent amounts.
2. Do not invent dates.
3. Do not invent names.
4. If a value is not visible, return null.
5. Use currency BOB when the image mentions Bs, Bs., bolivianos, BOB, or when the context is clearly Bolivia.
6. Classify as income when the evidence suggests money received by the merchant.
7. Classify as expense when the evidence suggests purchase, supplier payment, rent, transport, merchandise, debt payment, or money leaving the business.
8. Use unknown when the transaction type is ambiguous.
9. Include evidence_text with the visible text that justifies each transaction.
10. Return only valid structured JSON matching the provided schema.
```

---

## Image Preprocessing

Use OpenCV only inside:

```txt
services/image_preprocessing_service.py
```

The service should:

1. Accept raw image bytes.
2. Decode the image.
3. Resize large images.
4. Convert to grayscale.
5. Improve contrast.
6. Reduce noise.
7. Try adaptive thresholding when useful.
8. Try document contour detection when possible.
9. Correct perspective if a clear rectangular document is found.
10. Return processed image bytes.

Do not overengineer preprocessing.

If document contour detection fails, return the enhanced image.

Fail only when:

* The file is not an image.
* The image cannot be decoded.
* The image is corrupted or empty.

---

## Storage Provider

Use local storage for the MVP.

Storage provider interface:

```python
from typing import Protocol


class StorageProvider(Protocol):
    async def save_bytes(
        self,
        content: bytes,
        filename: str,
        content_type: str,
        folder: str,
    ) -> str:
        ...

    async def read_bytes(self, path: str) -> bytes:
        ...
```

Use:

```txt
providers/storage/local_storage_provider.py
```

Store files under:

```txt
storage/media/original/
storage/media/processed/
```

Do not store file bytes in MySQL.

Only store paths in `media_assets`.

---

## Application Code Generation

Generate `application_code` automatically.

Format:

```txt
APP-001
APP-002
APP-003
```

For MVP, it is acceptable to generate the next number from the current count.

Keep implementation simple.

Avoid complex distributed-safe sequence systems.

---

## Error Handling

Use consistent error responses.

Shape:

```json
{
  "error": {
    "code": "IMAGE_PROCESSING_FAILED",
    "message": "No se pudo procesar la imagen.",
    "details": {}
  }
}
```

All user-facing error messages must be in Spanish.

Examples:

```txt
No se encontró la solicitud.
No se encontró la transacción.
El archivo enviado no es una imagen válida.
No se pudo procesar la imagen.
No se pudo extraer información financiera de la imagen.
El estado enviado no es válido.
```

---

## CORS

Enable CORS for the React frontend.

Allowed origins come from config.

Default:

```txt
http://localhost:5173
http://localhost:3000
```

Do not hardcode CORS inside controllers.

---

## Pydantic Schema Rules

Use Pydantic v2.

All request and response schemas must be explicit.

Do not return ORM models directly.

Use strings for money values in responses.

Use raw enum values and Spanish labels where needed.

Good response field pattern:

```json
{
  "status": "pending",
  "status_label": "Pendiente"
}
```

---

## Coding Standards

Use:

* Type hints everywhere.
* `Decimal` for money.
* `str` UUIDs or `UUID` in schemas.
* `datetime` for timestamps.
* `date` for dates.
* `StrEnum` for enums.
* Pydantic schemas for all request/response contracts.
* SQLAlchemy async sessions.
* Explicit service classes.
* Explicit repository classes.
* Providers for external dependencies.

Do not use:

* `Any` unless absolutely necessary and justified.
* Global mutable state.
* Raw SQL unless strongly justified.
* Business logic in controllers.
* Database access in controllers.
* Gemini calls in controllers.
* OpenCV calls in controllers.
* Vague class names.

Avoid vague names like:

```txt
Manager
Helper
Processor
DataService
AIService
```

Prefer names like:

```txt
EvidenceProcessingService
ImagePreprocessingService
GeminiFinancialExtractionProvider
ManagementRepository
TransactionSummarySchema
FinancialExtractionSchema
```

---

## Testing Requirements

Use pytest.

Do not call real Gemini in tests.

Use fake providers.

Minimum tests:

1. Health endpoint returns ok.
2. Creating a management without files works.
3. Creating a management with invalid file type returns error.
4. Adding manual transaction recalculates totals.
5. Updating transaction recalculates totals.
6. Rejecting transaction excludes it from totals.
7. Adding evidence appends media assets and does not delete previous transactions.
8. Summary service calculates income, expense, and net balance.
9. Image preprocessing rejects invalid bytes.
10. Status update rejects invalid status.

---

## Implementation Order

Follow this order:

1. Create uv project.
2. Install dependencies.
3. Create `src/app` package.
4. Create FastAPI app in `main.py`.
5. Configure settings with `pydantic-settings`.
6. Configure CORS.
7. Configure SQLAlchemy async with MySQL.
8. Create models:

   * CustomerModel
   * ManagementModel
   * MediaAssetModel
   * TransactionModel
9. Configure Alembic.
10. Create first migration.
11. Create domain enums.
12. Create Pydantic schemas.
13. Create repositories.
14. Create health endpoint.
15. Create management creation endpoint without files.
16. Create management list endpoint.
17. Create management detail endpoint.
18. Create local storage provider.
19. Create image preprocessing service.
20. Create fake AI provider for tests/dev.
21. Create Gemini provider.
22. Implement evidence processing flow.
23. Implement add evidence endpoint.
24. Implement manual transaction endpoint.
25. Implement update transaction endpoint.
26. Implement reject transaction endpoint.
27. Implement advisor notes endpoint.
28. Implement status update endpoint.
29. Add tests.
30. Run ruff, mypy, and pytest.

Do not start with Gemini before the core database flow works.

---

## MVP Acceptance Criteria

The MVP is complete when:

1. The backend runs with `uv run fastapi dev src/app/main.py`.
2. MySQL migrations run successfully.
3. The frontend can create a management with customer data.
4. The frontend can optionally upload evidence images during creation.
5. The frontend can list management cards filtered by:

   * Todos
   * Pendiente
   * En revisión
   * Observado
   * Listo para análisis
6. The frontend can open a management detail view.
7. The backend stores media assets for uploaded images.
8. Each AI transaction references its source image through `media_asset_id`.
9. The advisor can add more evidence images to an existing management.
10. Adding evidence does not delete previous evidence or transactions.
11. The advisor can manually add a transaction.
12. The advisor can correct a transaction.
13. The advisor can reject a transaction.
14. Rejected transactions do not count in totals.
15. Financial totals are recalculated after every transaction change.
16. The advisor can save notes.
17. The advisor can change application status.
18. All user-facing messages are in Spanish.
19. Tests pass without calling real Gemini.
20. No authentication or user system exists.

---

## Important Hackathon Principle

Prioritize the working vertical slice:

```txt
Create management
→ upload evidence
→ extract transactions
→ show summary
→ correct/add/reject transactions
→ change status
```

Do not add extra features until this flow works end to end.
