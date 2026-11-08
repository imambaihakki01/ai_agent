import asyncio
from nexus_agent.agents import delegate

def test_unknown_subagent_role_is_rejected_without_provider_call():
    result=asyncio.run(delegate({}, "root", "do work"))
    assert "Unknown sub-agent role" in result
