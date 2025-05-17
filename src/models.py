from sqlalchemy import Column, Integer, ForeignKey, Float, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from src.database import Base


class Customer(Base):
    __tablename__ = "Customers"

    id = Column("CustomerId", String, primary_key=True, index=True)
    company_name = Column("CompanyName", String, nullable=False)
    street = Column("Street", String, nullable=True)
    unit = Column("Unit", String, nullable=True)
    country = Column("Country", String, nullable=True)
    city = Column("City", String, nullable=True)
    is_active = Column("IsActive", Boolean, nullable=False)

    sales = relationship(
        "Transaction",
        back_populates="customer",
        foreign_keys="[Transaction.customer_id]"
    )


class Product(Base):
    __tablename__ = "Products"
    product_id = Column("ProductId", Integer, primary_key=True, index=True)
    name = Column("Name", String, nullable=False)
    price = Column("Price", Float, nullable=False)

    # optional backref if you ever need all transactions for a product:
    transactions = relationship("Transaction", back_populates="product")


class Transaction(Base):
    __tablename__ = "Sales"
    id = Column("SaleId", Integer, primary_key=True, index=True)
    date = Column("Date", DateTime, nullable=False)
    business_unit = Column("BusinessUnitId", Integer, ForeignKey("BusinessUnits.BusinessUnitId"))
    customer_id = Column("CustomerId", String, ForeignKey("Customers.CustomerId"))
    location_id = Column("LocationId", Integer, ForeignKey("Locations.LocationId"))
    qty = Column("Qty", Integer)
    product_id = Column("ProductId", Integer, ForeignKey("Products.ProductId"))

    customer = relationship(
        "Customer",
        back_populates="sales",
        foreign_keys=[customer_id]
    )
    product = relationship("Product", back_populates="transactions")
