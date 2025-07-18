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
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
)
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Set
from typing_extensions import Self


class Policy(BaseModel):
    """
    Assigned policy (overrides organization and location policy mapping)
    """  # noqa: E501

    id: Optional[StrictInt] = Field(default=None, description="Policy identifier")
    parent_policy_id: Optional[StrictInt] = Field(
        default=None, description="Parent Policy identifier", alias="parentPolicyId"
    )
    name: Optional[StrictStr] = Field(default=None, description="Name")
    description: Optional[StrictStr] = Field(default=None, description="Description")
    node_class: Optional[StrictStr] = Field(
        default=None, description="Node Class", alias="nodeClass"
    )
    updated: Optional[Union[StrictFloat, StrictInt]] = Field(
        default=None, description="Last update timestamp"
    )
    node_class_default: Optional[StrictBool] = Field(
        default=None,
        description="Is Default Policy for Node Class",
        alias="nodeClassDefault",
    )
    tags: Optional[List[StrictStr]] = Field(default=None, description="Tags")
    fields: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None, description="Custom Fields"
    )
    __properties: ClassVar[List[str]] = [
        "id",
        "parentPolicyId",
        "name",
        "description",
        "nodeClass",
        "updated",
        "nodeClassDefault",
        "tags",
        "fields",
    ]

    @field_validator("node_class")
    def node_class_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(
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
                "must be one of enum values ('WINDOWS_SERVER', 'WINDOWS_WORKSTATION', 'LINUX_WORKSTATION', 'MAC', 'ANDROID', 'APPLE_IOS', 'APPLE_IPADOS', 'VMWARE_VM_HOST', 'VMWARE_VM_GUEST', 'HYPERV_VMM_HOST', 'HYPERV_VMM_GUEST', 'LINUX_SERVER', 'MAC_SERVER', 'CLOUD_MONITOR_TARGET', 'NMS_SWITCH', 'NMS_ROUTER', 'NMS_FIREWALL', 'NMS_PRIVATE_NETWORK_GATEWAY', 'NMS_PRINTER', 'NMS_SCANNER', 'NMS_DIAL_MANAGER', 'NMS_WAP', 'NMS_IPSLA', 'NMS_COMPUTER', 'NMS_VM_HOST', 'NMS_APPLIANCE', 'NMS_OTHER', 'NMS_SERVER', 'NMS_PHONE', 'NMS_VIRTUAL_MACHINE', 'NMS_NETWORK_MANAGEMENT_AGENT', 'UNMANAGED_DEVICE', 'MANAGED_DEVICE')"
            )
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
        """Create an instance of Policy from a JSON string"""
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
        """Create an instance of Policy from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "id": obj.get("id"),
                "parentPolicyId": obj.get("parentPolicyId"),
                "name": obj.get("name"),
                "description": obj.get("description"),
                "nodeClass": obj.get("nodeClass"),
                "updated": obj.get("updated"),
                "nodeClassDefault": obj.get("nodeClassDefault"),
                "tags": obj.get("tags"),
                "fields": obj.get("fields"),
            }
        )
        return _obj
