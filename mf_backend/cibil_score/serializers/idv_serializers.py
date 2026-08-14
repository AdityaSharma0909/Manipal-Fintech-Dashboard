import requests
import json
from dataclasses import dataclass, asdict, field
from typing import List, Optional

@dataclass
class Name:
    firstName: str
    middleName: str = ""
    lastName: str = ""

@dataclass
class ValueField:
    value: str

@dataclass
class Document:
    number: str

@dataclass
class Address:
    line1: str
    line2: str = ""
    line3: str = ""
    line4: str = ""
    line5: str = ""
    city: str = ""
    pinCode: str = ""
    stateCode: str = ""

@dataclass
class IDVerificationData:
    name: Name
    gender: ValueField
    dob: ValueField
    mobilePhone: List[Document]
    gstStateCode: ValueField
    pan: Optional[List[Document]] = field(default_factory=list)
    passport: Optional[List[Document]] = field(default_factory=list)
    voter: Optional[List[Document]] = field(default_factory=list)
    dl: Optional[List[Document]] = field(default_factory=list)
    rationcard: Optional[List[Document]] = field(default_factory=list)
    aadhar: Optional[List[Document]] = field(default_factory=list)
    account: Optional[List[Document]] = field(default_factory=list)
    residentAddress: Optional[List[Address]] = field(default_factory=list)
    permanentAddress: Optional[List[Address]] = field(default_factory=list)
    scoreType: Optional[ValueField] = None
    purpose: Optional[ValueField] = None
    amount: Optional[ValueField] = None

    def to_dict(self):
        return asdict(self)