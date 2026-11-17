from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

class EvidenceLoc(BaseModel):
    artifact_id: str
    version: str
    location: str
    quote: str | None = None

class ArtifactMeta(BaseModel):
    artifact_id: str
    kind: str
    version: str
    content_hash: str

class ApprovalTarget(BaseModel):
    doc: str
    version: str
    anchor: str
    field: str

class Approval(BaseModel):
    id: str
    target: ApprovalTarget
    from_: Any = Field(alias="from")
    to: Any
    status: Literal["approved", "rejected", "pending", "revoked"]
    approved_by: str | None = None
    seq: int = 0
    supersedes: list[str] = []
    model_config = ConfigDict(populate_by_name=True)

class Requirement(BaseModel):
    anchor: str
    text: str
    line_span: str
    parse_status: Literal["PARSED", "UNSUPPORTED", "AMBIGUOUS"]
    parse_reason: str | None = None
    rule: Any | None = None

class Finding(BaseModel):
    id: str
    severity: Literal["BLOCKER", "MAJOR", "MINOR", "INFO"]
    category: str
    rule_ref: str | None = None
    artifact: str | None = None
    version: str | None = None
    location: str | None = None
    evidence: list[EvidenceLoc] = []
    counterexample: dict[str, Any] | None = None
    correction: str | None = None
    source: Literal["deterministic", "model"] = "deterministic"
    verification: Literal["exhaustive", "sampled", "static", "unverified"] = "exhaustive"

class Coverage(BaseModel):
    requirements_total: int = 0
    requirements_reviewed: int = 0
    unsupported: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    approval_conflicts: list[dict[str, Any]] = []
    unreviewed: list[dict[str, Any]] = []
    artifacts_reviewed: list[dict[str, Any]] = []
    verification_mode: Literal["exhaustive", "sampled"] = "exhaustive"

class Check(BaseModel):
    name: str
    required: bool = True
    outcome: Literal["passed", "failed", "skipped", "error"]
    mode: str = "exhaustive"
    details: str = ""

class ReviewReport(BaseModel):
    report_version: str = "1.0"
    bundle_id: str
    reviewer_version: str = "0.1.0"
    status: Literal["PASS", "CHANGES_REQUIRED", "INCOMPLETE"]
    summary: str
    findings: list[Finding] = []
    coverage: Coverage = Coverage()
    checks: list[Check] = []
    provenance: dict[str, Any] = {}
    resources: dict[str, Any] = {}
    cache: dict[str, Any] = {}
