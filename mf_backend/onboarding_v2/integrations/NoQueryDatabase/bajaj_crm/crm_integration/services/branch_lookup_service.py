import json
import logging
import threading
from pathlib import Path

from django.db.models import Q

from crm_integration.models import Branch

logger = logging.getLogger(__name__)


class BranchLookupService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def _branch_to_dict(self, branch: Branch) -> dict:
        return {
            "branch_id": branch.branch_id,
            "branch_name": branch.branch_name,
            "branch_code": branch.branch_code,
            "pincode": branch.pincode,
            "district_id": branch.district_id,
        }

    def get_branch_by_code(self, branch_code):
        try:


            branch = Branch.objects.filter(branch_code=branch_code).first()
            if branch:
                logger.info(f"Branch found by code: {branch_code}")
                return self._branch_to_dict(branch)
        except Exception as ex:
            logger.exception(f"Error fetching branch by code {branch_code}: {ex}")
        return None

    def get_branch_by_name(self, branch_name):
        try:
            branch = Branch.objects.filter(branch_name=branch_name).first()
            if branch:
                logger.info(f"Branch found by name: {branch_name}")
                return self._branch_to_dict(branch)
        except Exception as ex:
            logger.exception(f"Error fetching branch by name {branch_name}: {ex}")
        return None

    def _branch_json_path(self) -> Path:
        return Path(__file__).resolve().parent.parent / "branches.json"

    def _load_branch_json(self) -> list[dict]:
        try:
            with open(self._branch_json_path(), encoding='utf-8') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            logger.warning("Branch JSON file not found at %s", self._branch_json_path())
        except Exception as ex:
            logger.exception(f"Failed to load branch JSON file: {ex}")
        return []

    def _find_branch_in_json(self, branch_identifier):
        if not branch_identifier:
            logger.debug("_find_branch_in_json called with empty branch_identifier")
            return None

        branches = self._load_branch_json()
        if not branches:
            logger.debug("_find_branch_in_json found no branches in JSON")
            return None

        logger.debug(f"_find_branch_in_json loaded {len(branches)} branches from JSON")
        normalized_identifier = branch_identifier.strip().lower()

        for branch in branches:
            code = branch.get("branch_code", "")
            name = branch.get("branch_name", "")
            if code == branch_identifier or name == branch_identifier:
                logger.debug(f"Exact JSON match found for branch_identifier={branch_identifier!r}")
                return self._branch_to_dict_from_json(branch)

        for branch in branches:
            code = branch.get("branch_code", "").lower()
            name = branch.get("branch_name", "").lower()
            if code == normalized_identifier or name == normalized_identifier:
                logger.debug(f"Case-insensitive JSON match found for branch_identifier={branch_identifier!r}")
                return self._branch_to_dict_from_json(branch)

        logger.debug(f"No JSON match found for branch_identifier={branch_identifier!r}")
        return None

    def _branch_to_dict_from_json(self, branch: dict) -> dict:
        return {
            "branch_id": branch.get("branch_id"),
            "branch_name": branch.get("branch_name"),
            "branch_code": branch.get("branch_code"),
            "pincode": branch.get("pincode", ""),
            "district_id": branch.get("district_id")
        }

    def get_branch(self, branch_identifier):
        if not branch_identifier:
            logger.debug("get_branch called with empty branch_identifier")
            return None

        logger.debug(f"get_branch called with branch_identifier={branch_identifier!r}")

        exact_code = self.get_branch_by_code(branch_identifier)
        if exact_code:
            logger.debug(f"Branch lookup by exact code successful: {branch_identifier}")
            return exact_code

        # exact_name = self.get_branch_by_name(branch_identifier)
        # if exact_name:
        #     logger.debug(f"Branch lookup by exact name successful: {branch_identifier}")
        #     return exact_name

        # try:
        #     branch = Branch.objects.filter(
        #         Q(branch_code__iexact=branch_identifier) |
        #         Q(branch_name__iexact=branch_identifier)
        #     ).first()
        #     if branch:
        #         logger.debug(f"Branch found by case-insensitive DB match: {branch_identifier}")
        #         return self._branch_to_dict(branch)
        #     logger.debug(f"No database match found for case-insensitive branch_identifier={branch_identifier!r}")
        # except Exception as ex:
        #     logger.exception(f"Error fetching branch by identifier {branch_identifier}: {ex}")

        # json_branch = self._find_branch_in_json(branch_identifier)
        # if json_branch:
        #     logger.debug(f"Branch found by JSON fallback: {branch_identifier}")
        #     return json_branch

        logger.warning(f"Branch not found: {branch_identifier}")
        return None

    def get_branches_by_district(self, district_name):
        logger.warning("get_branches_by_district is not supported for DB-backed branch lookup")
        return []

    def get_branches_by_district_id(self, district_id):
        try:
            branches = Branch.objects.filter(district_id=district_id).order_by("branch_code")
            return [self._branch_to_dict(branch) for branch in branches]
        except Exception as ex:
            logger.exception(f"Error fetching branches by district_id {district_id}: {ex}")
            return []

    def get_branches_by_pincode(self, pincode: str):
        if not pincode:
            logger.debug("get_branches_by_pincode called with empty pincode")
            return []

        try:
            branches = Branch.objects.filter(pincode=pincode).order_by("branch_code")
            if branches:
                return [self._branch_to_dict(branch) for branch in branches]
        except Exception as ex:
            logger.exception(f"Error fetching branches by pincode {pincode}: {ex}")

        branch_pincode = str(pincode).strip()
        try:
            json_branches = [
                self._branch_to_dict_from_json(branch)
                for branch in self._load_branch_json()
                if str(branch.get("pincode", "")).strip() == branch_pincode
            ]
            if json_branches:
                return json_branches
        except Exception as ex:
            logger.exception(f"Error fetching branch JSON fallback for pincode {pincode}: {ex}")

        return []

    def get_all_branches(self):
        try:
            branches = Branch.objects.all().order_by("branch_code")
            if branches:
                return [self._branch_to_dict(branch) for branch in branches]
        except Exception as ex:
            logger.exception(f"Error fetching all branches: {ex}")

        json_branches = self._load_branch_json()
        if json_branches:
            return [self._branch_to_dict_from_json(branch) for branch in json_branches]

        return []

    def reload(self):
        return self.get_all_branches()
