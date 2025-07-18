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

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    field_validator,
)
from typing import Any, ClassVar, Dict, List, Optional
from tl_ninjarmm.models.attribute_content_advanced_settings_complexity_rules import (
    AttributeContentAdvancedSettingsComplexityRules,
)
from tl_ninjarmm.models.attribute_content_advanced_settings_date_filters import (
    AttributeContentAdvancedSettingsDateFilters,
)
from tl_ninjarmm.models.attribute_content_advanced_settings_numeric_range import (
    AttributeContentAdvancedSettingsNumericRange,
)
from typing import Set
from typing_extensions import Self


class AttributeContentAdvancedSettings(BaseModel):
    """
    AttributeContentAdvancedSettings
    """  # noqa: E501

    file_max_size: Optional[StrictInt] = Field(default=None, alias="fileMaxSize")
    file_extensions: Optional[List[StrictStr]] = Field(
        default=None, alias="fileExtensions"
    )
    date_filters: Optional[AttributeContentAdvancedSettingsDateFilters] = Field(
        default=None, alias="dateFilters"
    )
    max_characters: Optional[StrictInt] = Field(default=None, alias="maxCharacters")
    complexity_rules: Optional[AttributeContentAdvancedSettingsComplexityRules] = Field(
        default=None, alias="complexityRules"
    )
    numeric_range: Optional[AttributeContentAdvancedSettingsNumericRange] = Field(
        default=None, alias="numericRange"
    )
    org: Optional[List[StrictInt]] = None
    node_class: Optional[List[StrictStr]] = Field(default=None, alias="nodeClass")
    ip_address_type: Optional[StrictStr] = Field(default=None, alias="ipAddressType")
    expand_large_value_on_render: Optional[StrictBool] = Field(
        default=None, alias="expandLargeValueOnRender"
    )
    __properties: ClassVar[List[str]] = [
        "fileMaxSize",
        "fileExtensions",
        "dateFilters",
        "maxCharacters",
        "complexityRules",
        "numericRange",
        "org",
        "nodeClass",
        "ipAddressType",
        "expandLargeValueOnRender",
    ]

    @field_validator("node_class")
    def node_class_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        for i in value:
            if i not in set(
                [
                    "WINDOWS_SERVER",
                    "WINDOWS_WORKSTATION",
                    "LINUX_WORKSTATION",
                    "MAC",
                    "ANDROID",
                    "APPLE_IOS",
                    "APPLE_IPADOS",
                    "VMWARE_VM_HOST",
                    "VMWARE_VM_GUEST",
                    "HYPERV_VMM_HOST",
                    "HYPERV_VMM_GUEST",
                    "LINUX_SERVER",
                    "MAC_SERVER",
                    "CLOUD_MONITOR_TARGET",
                    "NMS_SWITCH",
                    "NMS_ROUTER",
                    "NMS_FIREWALL",
                    "NMS_PRIVATE_NETWORK_GATEWAY",
                    "NMS_PRINTER",
                    "NMS_SCANNER",
                    "NMS_DIAL_MANAGER",
                    "NMS_WAP",
                    "NMS_IPSLA",
                    "NMS_COMPUTER",
                    "NMS_VM_HOST",
                    "NMS_APPLIANCE",
                    "NMS_OTHER",
                    "NMS_SERVER",
                    "NMS_PHONE",
                    "NMS_VIRTUAL_MACHINE",
                    "NMS_NETWORK_MANAGEMENT_AGENT",
                    "UNMANAGED_DEVICE",
                    "MANAGED_DEVICE",
                ]
            ):
                raise ValueError(
                    "each list item must be one of ('WINDOWS_SERVER', 'WINDOWS_WORKSTATION', 'LINUX_WORKSTATION', 'MAC', 'ANDROID', 'APPLE_IOS', 'APPLE_IPADOS', 'VMWARE_VM_HOST', 'VMWARE_VM_GUEST', 'HYPERV_VMM_HOST', 'HYPERV_VMM_GUEST', 'LINUX_SERVER', 'MAC_SERVER', 'CLOUD_MONITOR_TARGET', 'NMS_SWITCH', 'NMS_ROUTER', 'NMS_FIREWALL', 'NMS_PRIVATE_NETWORK_GATEWAY', 'NMS_PRINTER', 'NMS_SCANNER', 'NMS_DIAL_MANAGER', 'NMS_WAP', 'NMS_IPSLA', 'NMS_COMPUTER', 'NMS_VM_HOST', 'NMS_APPLIANCE', 'NMS_OTHER', 'NMS_SERVER', 'NMS_PHONE', 'NMS_VIRTUAL_MACHINE', 'NMS_NETWORK_MANAGEMENT_AGENT', 'UNMANAGED_DEVICE', 'MANAGED_DEVICE')"
                )
        return value

    @field_validator("ip_address_type")
    def ip_address_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(["ALL", "IPV4", "IPV6"]):
            raise ValueError("must be one of enum values ('ALL', 'IPV4', 'IPV6')")
        return value

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
        """Create an instance of AttributeContentAdvancedSettings from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of date_filters
        if self.date_filters:
            _dict["dateFilters"] = self.date_filters.to_dict()
        # override the default output from pydantic by calling `to_dict()` of complexity_rules
        if self.complexity_rules:
            _dict["complexityRules"] = self.complexity_rules.to_dict()
        # override the default output from pydantic by calling `to_dict()` of numeric_range
        if self.numeric_range:
            _dict["numericRange"] = self.numeric_range.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of AttributeContentAdvancedSettings from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "fileMaxSize": obj.get("fileMaxSize"),
                "fileExtensions": obj.get("fileExtensions"),
                "dateFilters": AttributeContentAdvancedSettingsDateFilters.from_dict(
                    obj["dateFilters"]
                )
                if obj.get("dateFilters") is not None
                else None,
                "maxCharacters": obj.get("maxCharacters"),
                "complexityRules": AttributeContentAdvancedSettingsComplexityRules.from_dict(
                    obj["complexityRules"]
                )
                if obj.get("complexityRules") is not None
                else None,
                "numericRange": AttributeContentAdvancedSettingsNumericRange.from_dict(
                    obj["numericRange"]
                )
                if obj.get("numericRange") is not None
                else None,
                "org": obj.get("org"),
                "nodeClass": obj.get("nodeClass"),
                "ipAddressType": obj.get("ipAddressType"),
                "expandLargeValueOnRender": obj.get("expandLargeValueOnRender"),
            }
        )
        return _obj
