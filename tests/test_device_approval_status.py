"""
The published spec lists only PENDING and APPROVED for approvalStatus, but the
API returns STAGED and DECOMMISSIONED as well (see TRE-4036). The spec fixer
adds the missing values before generation; these tests pin that behaviour.
"""

import pytest
from pydantic import ValidationError

from tl_ninjarmm.models.device import Device
from tl_ninjarmm.models.device_search_match import DeviceSearchMatch
from tl_ninjarmm.models.node_with_detailed_references import (
    NodeWithDetailedReferences,
)

DOCUMENTED_APPROVAL_STATUSES = ["PENDING", "STAGED", "APPROVED", "DECOMMISSIONED"]
MODELS_WITH_APPROVAL_STATUS = [Device, DeviceSearchMatch, NodeWithDetailedReferences]


@pytest.mark.parametrize("model", MODELS_WITH_APPROVAL_STATUS)
@pytest.mark.parametrize("status", DOCUMENTED_APPROVAL_STATUSES)
def test_accepts_every_documented_approval_status(model, status):
    assert model(approvalStatus=status).approval_status == status


@pytest.mark.parametrize("model", MODELS_WITH_APPROVAL_STATUS)
def test_rejects_unknown_approval_status(model):
    with pytest.raises(ValidationError, match="must be one of enum values"):
        model(approvalStatus="RETIRED")
