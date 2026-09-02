from pydantic import BaseModel

class MetricsSummary(BaseModel):
    total_disputes: int
    auto_contested: int
    escalated: int
    auto_accepted: int
    win_rate: float
    total_amount_contested: int
    false_positive_count: int

class TimelineDataPoint(BaseModel):
    date: str
    count: int
    contested: int
    accepted: int
    escalated: int
