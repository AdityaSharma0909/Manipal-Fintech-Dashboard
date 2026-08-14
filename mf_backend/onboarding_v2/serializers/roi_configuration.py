from __future__ import annotations
import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from rest_framework import serializers
from onboarding_v2.models import (
    RoiConfiguration,
    RoiConfigurationLeadType,
    RoiConfigurationBank,
    RoiConfigurationLoanRange,
)

# Max LTV percentages by loan range
MAX_LTV_MAP = {
    RoiConfigurationLoanRange.LESS_THAN_2_5_LAKHS: Decimal("82"),
    RoiConfigurationLoanRange.MORE_THAN_2_5_LAKHS: Decimal("72"),
}

# Regex to extract numeric month count from tenure choices like "3_MONTHS", "12_MONTHS"
_TENURE_MONTHS_RE = re.compile(r"(\d+)")


def _parse_tenure_months(tenure_value: str) -> Optional[int]:
    """Extract the integer month count from a tenure choice string."""
    if not tenure_value:
        return None
    m = _TENURE_MONTHS_RE.search(tenure_value)
    return int(m.group(1)) if m else None


class RoiConfigurationSerializer(serializers.ModelSerializer):
    blended_roi = serializers.SerializerMethodField()
    ltv = serializers.SerializerMethodField()

    class Meta:
        model = RoiConfiguration
        fields = "__all__"
        read_only_fields = ("blended_roi", "ltv")

    # ------------------------------------------------------------------
    # Computed fields
    # ------------------------------------------------------------------

    def get_blended_roi(self, obj):
        try:
            bank_roi = obj.get("bank_roi") if isinstance(obj, dict) else getattr(obj, "bank_roi", None)
            manipal_roi = obj.get("manipal_roi") if isinstance(obj, dict) else getattr(obj, "manipal_roi", None)

            if bank_roi is not None and manipal_roi is not None:
                return round((Decimal(str(bank_roi)) * Decimal("0.8")) + (Decimal(str(manipal_roi)) * Decimal("0.2")), 2)
            elif bank_roi is not None:
                return round(Decimal(str(bank_roi)), 2)
            return None
        except Exception:
            return None

    def get_ltv(self, obj):
        """
        LTV = Max LTV / (1 + (Blended ROI × Tenure_months))

        Where:
        - Max LTV: 82% for loans < 2.5 lakhs, 90% for loans > 2.5 lakhs
        - Blended ROI: percentage (e.g. 12 means 12%)
        - Tenure_months: tenure in months (e.g. 6, 9, 12)
        """
        try:
            # Resolve fields from dict or model instance
            if isinstance(obj, dict):
                loan_range = obj.get("loan_range")
                tenure = obj.get("tenure")
                blended_roi_val = obj.get("blended_roi")
            else:
                loan_range = getattr(obj, "loan_range", None)
                tenure = getattr(obj, "tenure", None)
                blended_roi_val = getattr(obj, "blended_roi", None)

            # Determine Max LTV
            max_ltv = MAX_LTV_MAP.get(loan_range)
            if max_ltv is None:
                return None

            # Parse tenure in months
            tenure_months = _parse_tenure_months(tenure)
            if tenure_months is None:
                return None

            # Blended ROI (fall back to computing it if the stored value is empty)
            if blended_roi_val is None:
                blended_roi_val = self.get_blended_roi(obj)
            if blended_roi_val is None:
                return None

            blended_roi = Decimal(str(blended_roi_val))

            # Formula:  LTV = Max LTV / (1 + (Blended ROI / 100 * (Tenure_months / 12)))
            interest_factor = (blended_roi / Decimal("100")) * (Decimal(str(tenure_months)) / Decimal("12"))
            denominator = Decimal("1") + interest_factor

            if denominator == 0:
                return None

            ltv = (max_ltv / denominator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            return float(ltv)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    def validate_lead_type(self, value):
        if value not in {
            RoiConfigurationLeadType.CO_LENDING,
            RoiConfigurationLeadType.SELF_LENDING,
        }:
            raise serializers.ValidationError(
                "Only Co-Lending and Self Lending are selectable."
            )
        return value

    def validate_bank(self, value):
        if value != RoiConfigurationBank.AXIS_BANK and value != RoiConfigurationBank.SIMPLEPAY:
            raise serializers.ValidationError("For now, only Axis Bank and Simplepay are supported.")
        return value
