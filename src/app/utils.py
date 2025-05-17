import pandas as pd
from sqlalchemy.orm import Session

from src.models import Customer, Transaction


def get_customer(db: Session, customer_id: int):
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_transactions_df(db: Session) -> pd.DataFrame:
    txs = db.query(Transaction).all()
    return pd.DataFrame([
        {"customer_id": t.customer_id, "date": pd.to_datetime(t.date).date(), "amount": t.qty * t.product.price}
        for t in txs
    ])
