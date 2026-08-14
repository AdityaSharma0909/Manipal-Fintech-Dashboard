from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional
from cibil_score.constant import *
from enum import Enum

class ValidationType(Enum):
    SCORE = "SCORE"
    DPD_DAYS = "DPD_DAYS"
    # DPD_AMOUNT = "DPD_AMOUNT"
    SUIT_FILED = "SUIT_FILED"
    WRITTEN_OFF = "WRITTEN_OFF"

class ValidationStatus(Enum):
    FAIL = 0
    PASS = 1
    REVIEW = 2

@dataclass
class ValidationResult:
    type: str
    success: ValidationStatus
    message: str

    def to_dict(self):
        return {
            "type": self.type,
            "success": self.success.value,
            "message": self.message
        }

# ── Criterion 1 : Credit / Bureau Score ──────────────────────────────────────

class BureauScoreValidator:
    """
    Field : SCORE.FCIREXScore
    Rule  : score >= 550
    """
    TYPE = ValidationType.SCORE.value
    def __call__(self, data):
        report = get_report(data)

        #SCORE field is missing
        score_section = report.get("SCORE")
        if not isinstance(score_section, dict):
            return ValidationResult(type=self.TYPE,success=ValidationStatus.REVIEW,message="Score is not a valid score.")

        #FCIREXScore field is missing
        if "FCIREXScore" not in score_section:
            return ValidationResult(type=self.TYPE,success=ValidationStatus.REVIEW,message="Score key is missing.")

        raw = score_section["FCIREXScore"]
        score = to_number(raw, default=None)

        #invalid (non-numeric / None / "?")
        if score is None:
            return ValidationResult(type=self.TYPE,success=ValidationStatus.REVIEW,message="Score is not a valid number.")

        #below threshold
        if score < SCORE_MIN:
            return ValidationResult(type=self.TYPE,success=ValidationStatus.FAIL,message=f"Score {score} is below the minimum of {SCORE_MIN}.")

        return ValidationResult(type=self.TYPE,success=ValidationStatus.PASS,message="Score check passed")


# ── Criterion 2 : DPD on Non-Gold Products (Days-based) ──────────────────────

class DPDDaysValidator:
    """
    Fields    : CAIS_Account_History[*].Days_Past_Due
                CAIS_Account_DETAILS[*].accountTypeDescription
    Rule      : DPD must not exceed 180 days on any non-gold account
    Doubt rule: loan type missing or ambiguous → skip that account
    """
    TYPE = ValidationType.DPD_DAYS.value
    def __call__(self, data):
        report = get_report(data)
        errors = []

        account_list=get_accounts(report)
        if not account_list:
            return ValidationResult(type=self.TYPE,success=ValidationStatus.REVIEW,message="Account list is empty.")

        for acc in account_list:
            loan_type = acc.get("accountTypeDescription", "")
            loan_status = acc.get("accountStatusDescription", "")

            # Skip gold loans and accounts with unknown loan type + others /
            # Skip if card is credit and loan is closed
            if ((not loan_type or is_gold_loan(loan_type) or
                    loan_type.strip().upper() == "OTHERS" or
                    is_credit_card(loan_type)) or
                    is_loan_closed(loan_status)):
                continue

            acc_no = acc.get("Account_Number", "UNKNOWN")

            for entry in (acc.get("CAIS_Account_History") or []):
                dpd = to_number(entry.get("Days_Past_Due"), default=None)
                if dpd is None:
                    continue  # missing DPD is not a violation

                if dpd > DPD_DAYS_MAX:
                    errors.append(
                        f"Account {acc_no} ({loan_type}): "
                        f"DPD {dpd} days in {entry.get('Month')}/{entry.get('Year')} "
                        f"exceeds limit of {DPD_DAYS_MAX} days."
                    )

        if errors:
            return ValidationResult(type=self.TYPE, success=ValidationStatus.FAIL, message="DPD days limit exceeded.")

        return ValidationResult(type=self.TYPE, success=ValidationStatus.PASS, message="DPD days check passed.")

# ── Criterion 3 : DPD on Non-Gold Products (Amount-based) ────────────────────

# class DPDAmountValidator:
#     """
#     Field     : CAIS_Account_DETAILS[*].Amount_Past_Due
#     Rule      : Amount Past Due must not exceed 10,000 on any non-gold account
#     Doubt rule: loan type missing or ambiguous → skip that account
#     Note      : Current_Balance is normal outstanding — NOT the field being checked.
#     """
#     TYPE = ValidationType.DPD_AMOUNT.value
#     def __call__(self, data):
#
#         return ValidationResult(type=self.TYPE, success=ValidationStatus.PASS, message="DPD amount check passed.")
#
#         # report = get_report(data)
#         # errors = []
#         #
#         # account_list = get_accounts(report)
#         # if not account_list:
#         #     return ValidationResult(type=self.TYPE, success=ValidationStatus.REVIEW, message="Account list is empty.")
#         #
#         # for acc in account_list:
#         #     loan_type = acc.get("accountTypeDescription", "")
#         #
#         #     if not loan_type or is_gold_loan(loan_type) or loan_type.strip().upper() == "OTHERS":
#         #         continue
#         #
#         #     acc_no  = acc.get("Account_Number", "UNKNOWN")
#         #     overdue = to_number(acc.get("Amount_Past_Due"), default=None)
#         #
#         #     if overdue is None:
#         #         continue  # missing value is not a violation
#         #
#         #     if overdue > DPD_AMOUNT_MAX:
#         #         errors.append(
#         #             f"Account {acc_no} ({loan_type}): "
#         #             f"Amount Past Due {overdue:,.0f} exceeds limit of {DPD_AMOUNT_MAX:,}."
#         #         )
#         #
#         # if errors:
#         #     return ValidationResult(type=self.TYPE, success=ValidationStatus.FAIL, message="DPD days limit exceeded.")
#         #
#         # return ValidationResult(type=self.TYPE, success=ValidationStatus.PASS, message="DPD amount check passed.")

# ── Criterion 4 : Suit Filed Account ─────────────────────────────────────────

class SuitFiledValidator:
    """
    Fields    : SuitFiled_WillfulDefault, suitfiledWillfuldefaultDescription,
                LitigationStatusDate, SuitFiledWillfulDefaultWrittenOffStatus
    Rule      : No active suit filed in the last 2 years
    Doubt rule: all suit fields absent → pass (no data to evaluate)
    """
    TYPE = ValidationType.SUIT_FILED.value
    CLEAN = {"no suit filed", ""}  # descriptions that mean no suit

    def __call__(self, data):
        report = get_report(data)
        errors = []
        cutoff = cutoff_date()

        account_list = get_accounts(report)
        if not account_list:
            return ValidationResult(type=self.TYPE, success=ValidationStatus.REVIEW, message="Account list is empty.")

        for acc in account_list:
            loan_status = acc.get("accountStatusDescription", "")
            loan_type = acc.get("accountTypeDescription", "")

            # Skip if loan is closed
            if is_loan_closed(loan_status) or is_credit_card(loan_type):
                continue
            acc_no    = acc.get("Account_Number", "UNKNOWN")
            loan_type = acc.get("accountTypeDescription", "")
            suit_code = acc.get("SuitFiled_WillfulDefault", "")
            suit_desc = (acc.get("suitfiledWillfuldefaultDescription") or "").strip().lower()
            lit_date  = acc.get("LitigationStatusDate", "")
            wo_status = acc.get("SuitFiledWillfulDefaultWrittenOffStatus", "")

            # Benefit of doubt: no suit data present at all
            if not any([suit_code, suit_desc, lit_date, wo_status]):
                continue

            # Explicitly clean — no suit on record
            if suit_desc in self.CLEAN:
                continue

            # Suit indicator found — check if it falls within the lookback window
            litigation_date = parse_date(lit_date)

            if litigation_date:
                if litigation_date >= cutoff:
                    errors.append(
                        f"Account {acc_no} ({loan_type}): "
                        f"Suit/Willful Default on {litigation_date} "
                        f"(within last {LOOKBACK_YEARS} years)."
                    )
            else:
                # Suit present but no date — fail conservatively
                errors.append(
                    f"Account {acc_no} ({loan_type}): "
                    f"Suit indicator '{suit_desc}' present but no LitigationStatusDate."
                )

        if errors:
            return ValidationResult(type=self.TYPE, success=ValidationStatus.FAIL, message="Suit indicator present.")

        return ValidationResult(type=self.TYPE, success=ValidationStatus.PASS, message="No suit filed cases.")

# ── Criterion 5 : Written-off Account ────────────────────────────────────────

class WrittenOffValidator:
    """
    Fields    : Written_Off_Amt_Principal, Written_Off_Amt_Total,
                WriteOffStatusDate, writtenOffSettledStatusDescription
    Rule      : No write-off in the last 2 years
    Doubt rule: amounts 0 + no date → pass (no actual write-off)
                'Restructured Loan' with 0 amounts → pass (restructured != written off)
    """

    TYPE = ValidationType.WRITTEN_OFF.value
    NOT_A_WRITEOFF = {"restructured loan", "restructured", "settled", ""}

    def __call__(self, data):
        report = get_report(data)
        errors = []
        cutoff = cutoff_date()
        account_list = get_accounts(report)
        if not account_list:
            return ValidationResult(type=self.TYPE, success=ValidationStatus.REVIEW, message="Account list is empty.")

        for acc in account_list:
            loan_status = acc.get("accountStatusDescription", "")
            loan_type = acc.get("accountTypeDescription", "")

            # Skip if loan is closed
            if is_loan_closed(loan_status) or is_credit_card(loan_type):
                continue

            acc_no    = acc.get("Account_Number", "UNKNOWN")
            loan_type = acc.get("accountTypeDescription", "")
            principal = to_number(acc.get("Written_Off_Amt_Principal"))
            total     = to_number(acc.get("Written_Off_Amt_Total"))
            wo_date   = acc.get("WriteOffStatusDate", "")
            wo_desc   = (acc.get("writtenOffSettledStatusDescription") or "").strip().lower()

            # No amounts and no date — clearly no write-off
            if principal == 0 and total == 0 and not wo_date:
                continue

            # Known non-write-off label with zero amounts — benefit of doubt
            if wo_desc in self.NOT_A_WRITEOFF and principal == 0 and total == 0:
                continue

            # Actual write-off amount exists — check the date
            writeoff_date = parse_date(wo_date)

            if writeoff_date:
                if writeoff_date >= cutoff:
                    errors.append(
                        f"Account {acc_no} ({loan_type}): "
                        f"Write-off on {writeoff_date} within last {LOOKBACK_YEARS} years "
                        f"(Principal {principal:,.0f}, Total {total:,.0f})."
                    )
            elif principal > 0 or total > 0:
                # Amounts recorded but date missing — fail conservatively
                errors.append(
                    f"Account {acc_no} ({loan_type}): "
                    f"Write-off amounts ({principal:,.0f} / {total:,.0f}) "
                    f"recorded but WriteOffStatusDate is missing."
                )

        if errors:
            return ValidationResult(type=self.TYPE, success=ValidationStatus.FAIL, message="Write-off amounts recorded.")

        return ValidationResult(type=self.TYPE, success=ValidationStatus.PASS, message="No written-off accounts")


# ── Shared helpers ────────────────────────────────────────────────────────────

def get_report(data):
    """Navigate the API envelope to reach jsonExperianReport."""
    return data.get("data", {}).get("jsonExperianReport", data)

def get_accounts(report):
    """Return the list of CAIS_Account_DETAILS (empty list if absent)."""
    return report.get("CAIS_Account", {}).get("CAIS_Account_DETAILS", []) or []

def is_gold_loan(account_type):
    """Gold loans are excluded from DPD checks."""
    return "gold" in (account_type or "").lower()

def is_credit_card(account_type):
    """Credit card are excluded from DPD checks."""
    return "credit card" in (account_type or "").lower()

def is_loan_closed(loan_status):
    """closed loans are excluded from DPD checks."""
    return "closed" in (loan_status or "").lower()

def to_number(value, default: Optional[float] = 0.0) -> Optional[float]:
    """Safely convert a value to float; return default on failure."""
    try:
        return float(value) if value not in (None, "", "?") else default
    except (TypeError, ValueError):
        return default

def parse_date(raw):
    """
    Experian dates are integers or strings in YYYYMMDD format.
    Returns a date object, or None if blank / unparseable.
    """
    if not raw:
        return None
    try:
        return datetime.strptime(str(int(raw)), "%Y%m%d").date()
    except (ValueError, TypeError):
        return None

def cutoff_date():
    """Date that is exactly LOOKBACK_YEARS ago from today."""
    today = date.today()
    return today.replace(year=today.year - LOOKBACK_YEARS)
