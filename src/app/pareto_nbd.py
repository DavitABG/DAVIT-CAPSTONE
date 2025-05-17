from datetime import datetime

import pandas as pd
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data
from sqlalchemy.orm import Session

from src.models import Transaction, Product


class PNBDEngine:
    def __init__(self, penalizer_coef: float = 0.5):
        self.pnbd = BetaGeoFitter(penalizer_coef=penalizer_coef)
        self.gg = GammaGammaFitter(penalizer_coef=penalizer_coef)
        self.fitted = False

    def _load_transaction_df(self, db: Session) -> pd.DataFrame:
        # join quantity × product price into a single amount column
        q = (
            db.query(
                Transaction.customer_id,
                Transaction.date,
                (Transaction.qty * Product.price).label("amount")
            )
            .join(Product, Transaction.product_id == Product.product_id)
        )
        df = pd.DataFrame([{"customer_id": r.customer_id,
                            "date": r.date,
                            "amount": r.amount}
                           for r in q])
        if df.empty:
            raise ValueError("No transactions in database")
        df["date"] = pd.to_datetime(df["date"])
        return df

    def fit(self, db: Session):
        df = self._load_transaction_df(db)

        # produce the RFM summary table
        summary = summary_data_from_transaction_data(
            df,
            customer_id_col="customer_id",
            datetime_col="date",
            monetary_value_col="amount",
            observation_period_end=datetime.now()
        )

        # fit Pareto/NBD
        self.pnbd.fit(
            frequency=summary["frequency"],
            recency=summary["recency"],
            T=summary["T"]
        )

        # fit Gamma–Gamma
        self.gg.fit(
            frequency=summary["frequency"],
            monetary_value=summary["monetary_value"]
        )

        self.fitted = True
        return {
            "pnbd_params": self.pnbd.params_.to_dict(),
            "gg_params": self.gg.params_.to_dict()
        }

    def customer_summary(self, db: Session, customer_id: str):
        """Return the R, F, T, M summary for a single customer."""
        df = self._load_transaction_df(db)
        cust = df[df["customer_id"] == customer_id]
        if cust.empty:
            return {"frequency": 0, "recency": 0, "T": 0, "monetary_value": 0.0}

        # lifetimes expects the full summary table, but we can construct a single-row
        tmp = summary_data_from_transaction_data(
            cust,
            customer_id_col="customer_id",
            datetime_col="date",
            monetary_value_col="amount",
            observation_period_end=datetime.now()
        )
        row = tmp.iloc[0]
        return {
            "frequency": float(row["frequency"]),
            "recency": float(row["recency"]),
            "T": float(row["T"]),
            "monetary_value": float(row["monetary_value"])
        }

    def probability_alive(self, db: Session, customer_id: str) -> float:
        if not self.fitted:
            raise RuntimeError("Model not fitted yet")
        s = self.customer_summary(db, customer_id)
        return self.pnbd.conditional_probability_alive(
            frequency=s["frequency"],
            recency=s["recency"],
            T=s["T"]
        )

    def conditional_expected_transactions(self, db: Session, customer_id: str, periods: int) -> float:
        if not self.fitted:
            raise RuntimeError("Model not fitted yet")
        s = self.customer_summary(db, customer_id)
        return self.pnbd.conditional_expected_number_of_purchases_up_to_time(
            periods,
            frequency=s["frequency"],
            recency=s["recency"],
            T=s["T"]
        )

    def expected_cumulative_transactions(self, db: Session, customer_id: str, periods: int) -> pd.Series:
        """Returns a pandas Series indexed 1…periods of cumulative expected transactions."""
        if not self.fitted:
            raise RuntimeError("Model not fitted yet")
        s = self.customer_summary(db, customer_id)
        frequency, recency, T = s["frequency"], s["recency"], s["T"]
        return self.pnbd.conditional_expected_number_of_purchases_up_to_time(list(range(1, periods + 1)), frequency,
                                                                             recency, T)

    def expected_average_value(self, db: Session, customer_id: str) -> float:
        """Gamma-Gamma: expected average transaction value."""
        if not self.fitted:
            raise RuntimeError("Model not fitted yet")
        s = self.customer_summary(db, customer_id)
        return self.gg.conditional_expected_average_profit(
            frequency=s["frequency"],
            monetary_value=s["monetary_value"]
        )

    def customer_lifetime_value(self, db: Session, customer_id: str, time: int, freq: str = "D") -> float:
        """CLV (monetary) over `time` periods at frequency `freq`."""
        if not self.fitted:
            raise RuntimeError("Model not fitted yet")
        s = self.customer_summary(db, customer_id)
        return self.gg.customer_lifetime_value(
            self.pnbd,
            frequency=pd.Series([s["frequency"]]),
            recency=pd.Series([s["recency"]]),
            T=pd.Series([s["T"]]),
            monetary_value=pd.Series([s["monetary_value"]]),
            time=time,
            freq=freq
        )
