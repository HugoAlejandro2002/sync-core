from pydantic import BaseModel


class CustomerResponse(BaseModel):
    id: str
    full_name: str
    phone_number: str | None = None
    nit: str | None = None
    business_name: str | None = None
    business_type: str | None = None
    business_description: str | None = None
    market_location: str | None = None


class CustomerMini(BaseModel):
    full_name: str
    phone_number: str | None = None
    business_name: str | None = None
    business_type: str | None = None
    nit: str | None = None
    market_location: str | None = None
