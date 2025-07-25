# coding: utf-8

"""
NinjaOne Public API 2.0

NinjaOne Public API documentation.

The version of the OpenAPI document: 2.0.9-draft
Contact: api@ninjarmm.com
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""  # noqa: E501

from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Set
from typing_extensions import Self


class SoftwareProduct(BaseModel):
    """
    SoftwareProduct
    """  # noqa: E501

    id: Optional[StrictStr] = Field(default=None, description="Product identifier")
    vendor_name: Optional[StrictStr] = Field(
        default=None, description="Vendor Name", alias="vendorName"
    )
    product_name: Optional[StrictStr] = Field(
        default=None, description="Product Name", alias="productName"
    )
    installable: Optional[StrictBool] = Field(default=None, description="Installable")
    active: Optional[StrictBool] = Field(default=None, description="Active")
    __properties: ClassVar[List[str]] = [
        "id",
        "vendorName",
        "productName",
        "installable",
        "active",
    ]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of SoftwareProduct from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of SoftwareProduct from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "id": obj.get("id"),
                "vendorName": obj.get("vendorName"),
                "productName": obj.get("productName"),
                "installable": obj.get("installable"),
                "active": obj.get("active"),
            }
        )
        return _obj
