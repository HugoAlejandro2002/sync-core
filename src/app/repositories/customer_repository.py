from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, customer: Customer) -> Customer:
        self.session.add(customer)
        await self.session.flush()
        return customer

    async def get_by_id(self, customer_id: str) -> Customer | None:
        return await self.session.get(Customer, customer_id)
