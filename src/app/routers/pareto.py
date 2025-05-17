from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.app.pareto_nbd import PNBDEngine
from src.database import get_db
from src.models import Customer
from src.schemas.pareto import (
    ModelParams, Summary, ProbabilityAlive, ExpectedConditional,
    ExpectedCumulative, ExpectedAvgValue, CustomerLifetimeValue
)

router = APIRouter(prefix="/models/pnbd", tags=["pareto-nbd"])
engine = PNBDEngine()


@router.post("/fit",
             response_model=ModelParams,
             summary="Re‐estimate Pareto/NBD & Gamma–Gamma models",
             description=(
                     "Re‐fit both the Pareto/NBD purchase-frequency model and the "
                     "Gamma–Gamma monetary-value model using *all* historical transactions. "
                     "Returns the updated model parameters (r, α, s, β for Pareto/NBD; p, q, v for Gamma–Gamma)."
             ))
def fit_models(db: Session = Depends(get_db)):
    try:
        return engine.fit(db)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.get("/summary/{customer_id}",
            response_model=Summary,
            summary="Retrieve R/F/T/M summary for a customer",
            description=(
                    "Compute and return the Recency (time since last purchase), "
                    "Frequency (# of repeat purchases), "
                    "T (age of customer in the dataset), "
                    "and MonetaryValue (average spend) for the given customer_id. "
                    "404 if the customer does not exist."
            ))
def get_summary(customer_id: str, db: Session = Depends(get_db)):
    if not db.query(Customer).filter(Customer.id == customer_id).first():
        raise HTTPException(404, detail="Customer not found")
    return engine.customer_summary(db, customer_id)


@router.get("/prob_alive/{customer_id}",
            response_model=ProbabilityAlive,
            summary="Estimate customer ‘alive’ probability",
            description=(
                    "Return the probability (0–1) that the specified customer is still \"alive\" "
                    "(i.e., will make another purchase), based on the fitted Pareto/NBD model. "
                    "Raises 400 if the model hasn’t been fit yet."
            ))
def prob_alive(customer_id: str, db: Session = Depends(get_db)):
    try:
        p = engine.probability_alive(db, customer_id)
    except RuntimeError as e:
        raise HTTPException(400, detail=str(e))
    return {"customer_id": customer_id, "prob_alive": p}


@router.get("/conditional/{customer_id}",
            response_model=ExpectedConditional,
            summary="Conditional expected purchases over next N periods",
            description=(
                    "Given a positive integer `periods`, compute the expected number of repeat transactions "
                    "in the next `periods` days *conditional* on the customer still being active. "
                    "Errors if `periods < 1` or the model is uninitialized."
            ), )
def conditional_expected(customer_id: str, periods: int = 30, db: Session = Depends(get_db)):
    if periods < 1:
        raise HTTPException(400, detail="‘periods’ must be a positive integer")
    try:
        exp = engine.conditional_expected_transactions(db, customer_id, periods)
    except RuntimeError as e:
        raise HTTPException(400, detail=str(e))
    return {"customer_id": customer_id, "periods": periods, "expected": exp}


@router.get("/cumulative/{customer_id}",
            response_model=ExpectedCumulative,
            summary="Cumulative expected purchases through period N",
            description=(
                    "Return a list of length `periods` giving the *cumulative* expected counts of future transactions "
                    "from period 1 up to period N for the given customer. Useful for plotting forecast curves."
            ))
def cumulative_expected(customer_id: str, periods: int = 30, db: Session = Depends(get_db)):
    try:
        series = engine.expected_cumulative_transactions(db, customer_id, periods)
    except RuntimeError as e:
        raise HTTPException(400, detail=str(e))
    return {
        "customer_id": customer_id,
        "periods": periods,
        "cumulative": series.tolist()
    }


@router.get("/avg_value/{customer_id}",
            response_model=ExpectedAvgValue,
            summary="Expected average transaction value (Gamma–Gamma)",
            description=(
                    "Using the Gamma–Gamma model, estimate the customer’s expected spend per transaction "
                    "(i.e., the average monetary value), given their historical purchase amounts."
            ))
def avg_value(customer_id: str, db: Session = Depends(get_db)):
    try:
        v = engine.expected_average_value(db, customer_id)
    except RuntimeError as e:
        raise HTTPException(400, detail=str(e))
    return {"customer_id": customer_id, "expected_avg_value": v}


@router.get("/clv/{customer_id}",
            response_model=CustomerLifetimeValue,
            summary="Predict customer lifetime value over horizon",
            description=(
                    "Compute the Customer Lifetime Value (CLV) over the next `time` periods (default 30) by "
                    "combining the Pareto/NBD expected transaction counts with the Gamma–Gamma average spend. "
                    "Returns the present‐value CLV assuming no discounting."
            ))
def clv(customer_id: str, time: int = 30, db: Session = Depends(get_db)):
    try:
        val = engine.customer_lifetime_value(db, customer_id, time)
    except RuntimeError as e:
        raise HTTPException(400, detail=str(e))
    return {"customer_id": customer_id, "time": time, "clv": val}
