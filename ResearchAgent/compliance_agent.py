from google.adk.agents import LlmAgent

from ResearchAgent.compliance_instructions import COMPLIANCE_AGENT_INSTRUCTION
from ResearchAgent.config import MODEL_NAME


compliance_agent = LlmAgent(
    name="ComplianceAgent",
    model=MODEL_NAME,
    instruction=COMPLIANCE_AGENT_INSTRUCTION,
    output_key="compliance_verdict",
)
