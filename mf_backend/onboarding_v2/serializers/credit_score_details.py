from dataclasses import dataclass
from typing import Optional


@dataclass
class CreditScoreDetails:
    range: Optional[str]
    score_color: Optional[str]
    score_band: Optional[str] #Good,Bad,Poor, Excellent
    score_value: Optional[str]