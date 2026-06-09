"""Agents console read model + editable threshold/mode (Phase 0)."""
from fastapi import APIRouter, Depends, HTTPException

from .. import auth

from ..agents_data import store
from ..models import Agent, AgentListResp, AgentPatch, AgentSummary

router = APIRouter(prefix="/api", tags=["agents"])


@router.get("/agents", response_model=AgentListResp)
def list_agents() -> AgentListResp:
    return AgentListResp(**store.list())


@router.get("/agents/{agent_id}", response_model=Agent)
def get_agent(agent_id: str) -> Agent:
    a = store.get(agent_id)
    if a is None:
        raise HTTPException(status_code=404, detail=f"agent {agent_id} not found")
    return Agent(**a)


@router.patch("/agents/{agent_id}", response_model=AgentSummary)
def patch_agent(agent_id: str, patch: AgentPatch, _: dict = Depends(auth.require_controller)) -> AgentSummary:
    """SIDE-EFFECTFUL: updates threshold/mode and writes an audit entry."""
    updated = store.patch(agent_id, patch.threshold, patch.mode)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"agent {agent_id} not found")
    return AgentSummary(**updated)
