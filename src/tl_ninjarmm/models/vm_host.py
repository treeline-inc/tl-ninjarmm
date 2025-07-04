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

from pydantic import ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from tl_ninjarmm.models.device import Device
from tl_ninjarmm.models.maintenance import Maintenance
from tl_ninjarmm.models.node_references import NodeReferences
from tl_ninjarmm.models.note import Note
from typing import Set
from typing_extensions import Self


class VMHost(Device):
    """
    VMHost
    """  # noqa: E501

    cpu_mhz: Optional[StrictInt] = Field(
        default=None, description="CPU Frequency", alias="cpuMhz"
    )
    cpu_model: Optional[StrictStr] = Field(
        default=None, description="CPU Model", alias="cpuModel"
    )
    ht_active: Optional[StrictBool] = Field(
        default=None, description="Is Hyper-Threading active?", alias="htActive"
    )
    ht_available: Optional[StrictBool] = Field(
        default=None, description="Is Hyper-Threading available?", alias="htAvailable"
    )
    last_boot_time: Optional[Union[StrictFloat, StrictInt]] = Field(
        default=None, description="Last toot time", alias="lastBootTime"
    )
    memory_size: Optional[StrictInt] = Field(
        default=None, description="Total memory size (bytes)", alias="memorySize"
    )
    model: Optional[StrictStr] = Field(default=None, description="Model")
    name: Optional[StrictStr] = Field(default=None, description="Name")
    cpu_cores: Optional[StrictInt] = Field(
        default=None, description="Number of CPU Cores", alias="cpuCores"
    )
    cpu_packages: Optional[StrictInt] = Field(
        default=None, description="Number of CPUs", alias="cpuPackages"
    )
    cpu_threads: Optional[StrictInt] = Field(
        default=None,
        description="Total number of logical CPU cores",
        alias="cpuThreads",
    )
    service_tag: Optional[StrictStr] = Field(
        default=None, description="Service Tag", alias="serviceTag"
    )
    vendor: Optional[StrictStr] = Field(default=None, description="Vendor")
    release_name: Optional[StrictStr] = Field(
        default=None, description="Release Name", alias="releaseName"
    )
    version: Optional[StrictStr] = Field(default=None, description="Version")
    build_number: Optional[StrictStr] = Field(
        default=None, description="Build number", alias="buildNumber"
    )
    __properties: ClassVar[List[str]] = [
        "id",
        "parentDeviceId",
        "organizationId",
        "locationId",
        "nodeClass",
        "nodeRoleId",
        "rolePolicyId",
        "policyId",
        "approvalStatus",
        "offline",
        "displayName",
        "systemName",
        "dnsName",
        "netbiosName",
        "created",
        "lastContact",
        "lastUpdate",
        "userData",
        "tags",
        "fields",
        "maintenance",
        "references",
        "ipAddresses",
        "macAddresses",
        "publicIP",
        "notes",
        "deviceType",
        "cpuMhz",
        "cpuModel",
        "htActive",
        "htAvailable",
        "lastBootTime",
        "memorySize",
        "model",
        "name",
        "cpuCores",
        "cpuPackages",
        "cpuThreads",
        "serviceTag",
        "vendor",
        "releaseName",
        "version",
        "buildNumber",
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
        """Create an instance of VMHost from a JSON string"""
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
        # override the default output from pydantic by calling `to_dict()` of maintenance
        if self.maintenance:
            _dict["maintenance"] = self.maintenance.to_dict()
        # override the default output from pydantic by calling `to_dict()` of references
        if self.references:
            _dict["references"] = self.references.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in notes (list)
        _items = []
        if self.notes:
            for _item_notes in self.notes:
                if _item_notes:
                    _items.append(_item_notes.to_dict())
            _dict["notes"] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of VMHost from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate(
            {
                "id": obj.get("id"),
                "parentDeviceId": obj.get("parentDeviceId"),
                "organizationId": obj.get("organizationId"),
                "locationId": obj.get("locationId"),
                "nodeClass": obj.get("nodeClass"),
                "nodeRoleId": obj.get("nodeRoleId"),
                "rolePolicyId": obj.get("rolePolicyId"),
                "policyId": obj.get("policyId"),
                "approvalStatus": obj.get("approvalStatus"),
                "offline": obj.get("offline"),
                "displayName": obj.get("displayName"),
                "systemName": obj.get("systemName"),
                "dnsName": obj.get("dnsName"),
                "netbiosName": obj.get("netbiosName"),
                "created": obj.get("created"),
                "lastContact": obj.get("lastContact"),
                "lastUpdate": obj.get("lastUpdate"),
                "userData": obj.get("userData"),
                "tags": obj.get("tags"),
                "fields": obj.get("fields"),
                "maintenance": Maintenance.from_dict(obj["maintenance"])
                if obj.get("maintenance") is not None
                else None,
                "references": NodeReferences.from_dict(obj["references"])
                if obj.get("references") is not None
                else None,
                "ipAddresses": obj.get("ipAddresses"),
                "macAddresses": obj.get("macAddresses"),
                "publicIP": obj.get("publicIP"),
                "notes": [Note.from_dict(_item) for _item in obj["notes"]]
                if obj.get("notes") is not None
                else None,
                "deviceType": obj.get("deviceType"),
                "cpuMhz": obj.get("cpuMhz"),
                "cpuModel": obj.get("cpuModel"),
                "htActive": obj.get("htActive"),
                "htAvailable": obj.get("htAvailable"),
                "lastBootTime": obj.get("lastBootTime"),
                "memorySize": obj.get("memorySize"),
                "model": obj.get("model"),
                "name": obj.get("name"),
                "cpuCores": obj.get("cpuCores"),
                "cpuPackages": obj.get("cpuPackages"),
                "cpuThreads": obj.get("cpuThreads"),
                "serviceTag": obj.get("serviceTag"),
                "vendor": obj.get("vendor"),
                "releaseName": obj.get("releaseName"),
                "version": obj.get("version"),
                "buildNumber": obj.get("buildNumber"),
            }
        )
        return _obj
