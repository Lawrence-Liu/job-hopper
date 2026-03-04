from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, TypedDict
from uuid import uuid4

import google.auth
from google.auth.transport.requests import Request
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

class ExtractedInfo(BaseModel):
    skills: list[str] = Field(default_factory=list)
    qualifications: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


class EnhancedResumeOutput(BaseModel):
    enhanced_resume: str


class ResumeVerificationOutput(BaseModel):
    has_fabrication: bool = False
    suspicious_items: list[str] = Field(default_factory=list)
    summary: str = ""


class ResumeGraphState(TypedDict, total=False):
    job_desc: str
    original_resume: str
    extracted_info: Dict[str, Any]
    enhanced_resume: str
    verification_report: Dict[str, Any]
    verification_round: int
    styled_resume: str


@dataclass
class ResumeLangGraphRunner:
    model: str = "gemini-2.5-flash"
    temperature: float = 0.1
    max_verification_rounds: int = 3
    adc_scopes: tuple[str, ...] = (
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/generative-language",
    )

    def _adc_credentials(self):
        credentials, _ = google.auth.default(scopes=list(self.adc_scopes))
        if getattr(credentials, "requires_scopes", False):
            credentials = credentials.with_scopes(list(self.adc_scopes))
        credentials.refresh(Request())
        return credentials

    def _llm(self) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=self.model,
            temperature=self.temperature,
            credentials=self._adc_credentials(),
        )

    def _extractor_model(self):
        return self._llm().with_structured_output(ExtractedInfo, method="function_calling")

    def _enhancer_model(self):
        return self._llm().with_structured_output(EnhancedResumeOutput, method="function_calling")

    def _verifier_model(self):
        return self._llm().with_structured_output(ResumeVerificationOutput, method="function_calling")

    def _invoke_config(self) -> Dict[str, Any]:
        return {"configurable": {"thread_id": f"resume-agent-{uuid4()}"}}

    def _extract_info_node(self, state: ResumeGraphState) -> Dict[str, Any]:
        extractor = self._extractor_model()
        result = extractor.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a senior job description analyst. "
                        "Extract required skills, qualifications, and responsibilities."
                    )
                ),
                HumanMessage(
                    content=(
                        "Review the job description and extract required details.\n"
                        "Return fields: skills, qualifications, responsibilities.\n\n"
                        f"Job description:\n{state['job_desc']}"
                    )
                ),
            ]
        )
        return {"extracted_info": result.model_dump()}

    def _enhance_resume_node(self, state: ResumeGraphState) -> Dict[str, Any]:
        enhancer = self._enhancer_model()

        verification_report = state.get("verification_report", {})
        retry_feedback = ""
        if verification_report.get("has_fabrication"):
            suspicious_items = verification_report.get("suspicious_items", [])
            summary = verification_report.get("summary", "")
            retry_feedback = (
                "\n\nVerifier feedback from previous draft (must fix all items):\n"
                f"Summary: {summary}\n"
                f"Suspicious items: {json.dumps(suspicious_items, ensure_ascii=False)}\n"
                "Rewrite the enhanced resume to remove unsupported claims while preserving relevance."
            )

        result = enhancer.invoke(
            [
                SystemMessage(
                    content=(
                        "You are an expert resume enhancement writer. "
                        "Preserve the original JSON structure while improving relevance."
                    )
                ),
                HumanMessage(
                    content=(
                        "Update the original resume JSON to align with extracted job requirements.\n"
                        "Do NOT invent experiences, skills, or qualifications not supported by the original resume.\n"
                        "Add a section listing missing skills/qualifications required by the JD.\n\n"
                        "Return output in a single top-level field named `enhanced_resume` containing the full resume JSON.\n\n"
                        f"Original resume:\n{state['original_resume']}\n\n"
                        f"Extracted job info:\n{json.dumps(state['extracted_info'], ensure_ascii=False)}"
                        f"{retry_feedback}"
                    )
                ),
            ]
        )
        if not result.enhanced_resume:
            raise ValueError(
                "LLM returned empty `enhanced_resume`. "
                "Retry with a smaller prompt or verify model/tool-calling response format."
            )
        return {"enhanced_resume": result.enhanced_resume}

    def _verify_resume_node(self, state: ResumeGraphState) -> Dict[str, Any]:
        verifier = self._verifier_model()
        current_round = state.get("verification_round", 0) + 1
        result = verifier.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a strict resume fact-checking auditor. "
                        "Compare an enhanced resume against the original resume and flag only unsupported claims."
                    )
                ),
                HumanMessage(
                    content=(
                        "Check whether the enhanced resume contains fabricated or unsupported information compared to the original resume.\n"
                        "Return:\n"
                        "- has_fabrication: true if any unsupported claim exists\n"
                        "- suspicious_items: concise bullet-style strings for each suspicious claim\n"
                        "- summary: brief overall conclusion\n\n"
                        f"Original resume JSON:\n{state['original_resume']}\n\n"
                        f"Enhanced resume JSON:\n{state['enhanced_resume']}"
                    )
                ),
            ]
        )
        verification_report = result.model_dump()

        if verification_report.get("has_fabrication") and current_round >= self.max_verification_rounds:
            raise ValueError(
                "Enhanced resume still has unsupported claims after maximum verification rounds. "
                f"Summary: {verification_report.get('summary', '')}. "
                f"Items: {verification_report.get('suspicious_items', [])}"
            )

        return {
            "verification_report": verification_report,
            "verification_round": current_round,
        }

    def _route_after_verify(self, state: ResumeGraphState) -> str:
        report = state.get("verification_report", {})
        if report.get("has_fabrication"):
            return "enhance_resume_agent"
        return "style_resume_agent"

    def _style_resume_node(self, state: ResumeGraphState) -> Dict[str, Any]:
        styled = self._llm().invoke(
            [
                SystemMessage(
                    content=(
                        "You are a professional resume stylist. "
                        "Convert enhanced JSON resumes to business-ready Markdown."
                    )
                ),
                HumanMessage(
                    content=(
                        "Convert the enhanced JSON resume to Markdown.\n"
                        "Do NOT add new sections or skills not present in the JSON.\n"
                        "Return Markdown only.\n\n"
                        f"Enhanced resume JSON:\n{json.dumps(state['enhanced_resume'], ensure_ascii=False, indent=2)}"
                    )
                ),
            ]
        )
        return {"styled_resume": str(styled.content).strip()}

    def _build_graph(self):
        graph = StateGraph(ResumeGraphState)
        graph.add_node("extract_info_agent", self._extract_info_node)
        graph.add_node("enhance_resume_agent", self._enhance_resume_node)
        graph.add_node("verify_resume_agent", self._verify_resume_node)
        graph.add_node("style_resume_agent", self._style_resume_node)

        graph.add_edge(START, "extract_info_agent")
        graph.add_edge("extract_info_agent", "enhance_resume_agent")
        graph.add_edge("enhance_resume_agent", "verify_resume_agent")
        graph.add_conditional_edges(
            "verify_resume_agent",
            self._route_after_verify,
            {
                "enhance_resume_agent": "enhance_resume_agent",
                "style_resume_agent": "style_resume_agent",
            },
        )
        graph.add_edge("style_resume_agent", END)

        return graph.compile(checkpointer=InMemorySaver())

    def run(
        self,
        *,
        job_desc: str,
        original_resume: str,
        enhanced_resume_path: str | None = None,
        styled_resume_path: str | None = None,
    ) -> Dict[str, Any]:
        app = self._build_graph()
        result = app.invoke(
            {
                "job_desc": job_desc,
                "original_resume": original_resume,
            },
            config=self._invoke_config(),
        )

        extracted_info = result["extracted_info"]
        enhanced_resume = result["enhanced_resume"]
        verification_report = result["verification_report"]
        styled_resume = result["styled_resume"]

        enhanced_path_str = None
        styled_path_str = None
        if enhanced_resume_path and styled_resume_path:
            enhanced_path = Path(enhanced_resume_path)
            styled_path = Path(styled_resume_path)
            enhanced_path.parent.mkdir(parents=True, exist_ok=True)
            styled_path.parent.mkdir(parents=True, exist_ok=True)

            enhanced_path.write_text(
                json.dumps(json.loads(enhanced_resume), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            styled_path.write_text(styled_resume, encoding="utf-8")
            enhanced_path_str = str(enhanced_path)
            styled_path_str = str(styled_path)

        return {
            "extracted_info": extracted_info,
            "enhanced_resume": enhanced_resume,
            "verification_report": verification_report,
            "styled_resume": styled_resume,
            "enhanced_resume_path": enhanced_path_str,
            "styled_resume_path": styled_path_str,
        }
