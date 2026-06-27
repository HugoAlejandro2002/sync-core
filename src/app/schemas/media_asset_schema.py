from pydantic import BaseModel


class EvidenceResponse(BaseModel):
    id: str
    filename: str
    status: str
    status_label: str
    document_type: str | None = None
    document_type_label: str | None = None
    detected_amount: str | None = None
    confidence_score: float | None = None
    extracted_text: str | None = None
