"""
apps/common/dtos/base_dto.py
=============================
Base DTO (Data Transfer Object) classes.

DTOs carry data between layers without exposing ORM model internals.
Used for:
  - Deserializing/validating inbound API request bodies (RequestDTO)
  - Structuring outbound responses from service layer (ResponseDTO)

Rules:
  - DTOs are plain Python dataclasses or Pydantic-style classes
  - DRF Serializers handle HTTP serialization; DTOs handle inter-layer data
  - Business layer accepts and returns DTOs, never raw request.data
  - DTOs are defined per-module

Usage:
    from apps.common.dtos.base_dto import BaseRequestDTO, BaseResponseDTO
    from dataclasses import dataclass, field

    @dataclass
    class CreateCustomerRequestDTO(BaseRequestDTO):
        name: str = ""
        email: str = ""
        phone: str = ""
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class BaseRequestDTO:
    """
    Base class for all inbound request DTOs.

    Provides:
      - to_dict(): serialize to plain dict for logging/debugging
      - from_serializer(): class method to build DTO from DRF serializer.validated_data
    """

    def to_dict(self) -> Dict[str, Any]:
        """Serialize DTO fields to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_serializer(cls, validated_data: Dict[str, Any]) -> "BaseRequestDTO":
        """
        Construct a DTO from DRF serializer.validated_data.
        Subclasses should override for custom field mapping if needed.
        """
        return cls(**{
            k: v for k, v in validated_data.items()
            if k in cls.__dataclass_fields__
        })


@dataclass
class BaseResponseDTO:
    """
    Base class for all outbound response DTOs.

    Returned by service layer to the API (view) layer.
    The view layer then serializes this to JSON via DRF serializers or directly.
    """

    def to_dict(self) -> Dict[str, Any]:
        """Serialize DTO fields to a plain dictionary."""
        return asdict(self)


@dataclass
class PaginatedResponseDTO(BaseResponseDTO):
    """
    DTO for paginated list responses.

    Attributes:
        items   : List of items (each item can be a BaseResponseDTO or dict)
        total   : Total number of records across all pages
        page    : Current page number (1-indexed)
        page_size: Number of items per page
    """
    items: list = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        import math
        return math.ceil(self.total / self.page_size)
