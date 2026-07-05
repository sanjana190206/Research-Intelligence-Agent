import os
from typing import Any

import requests

from rag.agents import (
    CitationGapDetectionAgent,
    FutureTrendPredictionAgent,
    HypothesisGenerationAgent,
    LiteratureReviewAgent,
    NoveltyAnalysisAgent,
    ResearchQAAgent,
    ResearchSummarizationAgent,
    SectionDraftingAgent,
)


AGENT_REGISTRY = {
    "summary": ResearchSummarizationAgent,
    "literature_review": LiteratureReviewAgent,
    "citation_gaps": CitationGapDetectionAgent,
    "novelty": NoveltyAnalysisAgent,
    "future_trends": FutureTrendPredictionAgent,
    "hypotheses": HypothesisGenerationAgent,
    "section_drafting": SectionDraftingAgent,
    "qa": ResearchQAAgent,
}


class BobPlanner:
    """IBM Bob planner adapter with a local fallback for offline demos."""

    def plan(self, task: str):
        bob_plan = self._plan_with_bob(task)
        if bob_plan:
            return bob_plan
        return self._local_plan(task)

    def _plan_with_bob(self, task: str):
        endpoint = os.getenv("IBM_BOB_ENDPOINT")
        api_key = os.getenv("IBM_BOB_API_KEY")
        if not endpoint or not api_key:
            return None

        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "task": task,
                    "available_agents": list(AGENT_REGISTRY.keys()),
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            steps = payload.get("agents") or payload.get("steps")
            if isinstance(steps, list):
                return [step for step in steps if step in AGENT_REGISTRY]
        except Exception as exc:
            print(f"IBM Bob planning fallback used: {exc}")
        return None

    def _local_plan(self, task: str):
        normalized = task.lower()
        if "full" in normalized or "dashboard" in normalized or "upload" in normalized:
            return [
                "summary",
                "literature_review",
                "novelty",
                "citation_gaps",
                "future_trends",
                "hypotheses",
            ]
        if "novel" in normalized:
            return ["novelty"]
        if "citation" in normalized or "reference" in normalized:
            return ["citation_gaps"]
        if "trend" in normalized or "future" in normalized:
            return ["future_trends"]
        if "review" in normalized:
            return ["literature_review"]
        if "hypothesis" in normalized:
            return ["hypotheses"]
        if "section" in normalized or "draft" in normalized:
            return ["section_drafting"]
        if "question" in normalized or "ask" in normalized or "qa" in normalized:
            return ["qa"]
        if "summary" in normalized or "summarize" in normalized:
            return ["summary"]
        return ["summary", "novelty"]


class BobOrchestrator:
    def __init__(self):
        self.planner = BobPlanner()

    def run(self, task: str, **kwargs):
        activity = [
            self._activity("IBM Bob Planning", "complete", "Bob selected the required research agents."),
        ]
        plan = self.planner.plan(task)
        outputs: dict[str, Any] = {}
        evidence = []
        confidence_scores = []

        for agent_key in plan:
            agent = AGENT_REGISTRY[agent_key]()
            activity.append(self._activity(agent.name, "running", "Agent execution started."))
            result = self._run_agent(agent_key, agent, kwargs)
            outputs[agent_key] = result.output
            evidence.extend(result.evidence)
            confidence_scores.append(result.confidence_score)
            activity[-1] = self._activity(agent.name, "complete", "Agent execution completed.")

        confidence = round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else 0.0
        activity.append(self._activity("Granite Response Generated", "complete", "IBM Granite generated agent outputs."))

        return {
            "task": task,
            "plan": plan,
            "outputs": outputs,
            "activity": activity,
            "evidence": self._dedupe_evidence(evidence),
            "confidence_score": confidence,
        }

    def _run_agent(self, agent_key, agent, kwargs):
        if agent_key == "qa":
            return agent.run(kwargs.get("question", ""), kwargs.get("history", []))
        if agent_key == "section_drafting":
            return agent.run(kwargs.get("section", "Introduction"))
        return agent.run()

    def _activity(self, label, status, detail):
        return {
            "label": label,
            "status": status,
            "detail": detail,
        }

    def _dedupe_evidence(self, evidence):
        seen = set()
        unique = []
        for item in evidence:
            key = (item.get("source"), item.get("chunk_index"))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique[:10]

