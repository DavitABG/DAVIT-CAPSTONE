from typing import Dict, List

from pydantic import BaseModel


class ModelParams(BaseModel):
    pnbd_params: Dict[str, float]
    gg_params: Dict[str, float]


class Summary(BaseModel):
    frequency: float
    recency: float
    T: float
    monetary_value: float


class ProbabilityAlive(BaseModel):
    customer_id: str
    prob_alive: float


class ExpectedConditional(BaseModel):
    customer_id: str
    periods: int
    expected: float


class ExpectedCumulative(BaseModel):
    customer_id: str
    periods: int
    cumulative: List[float]


class ExpectedAvgValue(BaseModel):
    customer_id: str
    expected_avg_value: float


class CustomerLifetimeValue(BaseModel):
    customer_id: str
    time: int
    clv: float
