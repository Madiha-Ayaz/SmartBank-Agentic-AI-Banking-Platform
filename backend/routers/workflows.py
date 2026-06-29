from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter

from backend.config import settings
from backend.schemas import WorkflowListResponse

logger = logging.getLogger("smartbank.routers.workflows")
router = APIRouter(prefix="/api/workflows", tags=["Workflows"])


@router.get("", response_model=WorkflowListResponse)
def list_workflows() -> WorkflowListResponse:
    wf_dir = settings.ROOT_DIR / "workflows"
    workflows = []
    if wf_dir.exists():
        for f in sorted(wf_dir.glob("*.bpmn")):
            content = f.read_text()
            workflows.append(
                {
                    "name": f.stem,
                    "file": f.name,
                    "size": f.stat().st_size,
                    "process_id": _extract_process_id(content),
                }
            )
    return WorkflowListResponse(workflows=workflows)


def _extract_process_id(xml_content: str) -> str:
    import re
    m = re.search(r"process\s+id=\"([^\"]+)\"", xml_content)
    return m.group(1) if m else "unknown"
