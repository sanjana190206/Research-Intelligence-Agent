import re

from rag.agents.base import AgentResult, BaseResearchAgent
from rag.granite_client import generate_text


class NoveltyAnalysisAgent(BaseResearchAgent):
    name = "Novelty Analysis Agent"
    query = (
        "novel contribution proposed method innovation "
        "comparison baseline results research gap"
    )

    def run(self):
        context, evidence = self.get_context(n_results=8)
        score = self._estimate_novelty_score(context, evidence)

        prompt = f"""
You are an expert research novelty evaluator.

Using ONLY the research context below, evaluate the novelty of the uploaded paper.

Return EXACTLY in this format.

Novel Contributions:
- Contribution 1
- Contribution 2
- Contribution 3

Why The Work Is Unique:
- Point 1
- Point 2

Novelty Score:
{score}/100

Suggested Improvements:
- Improvement 1
- Improvement 2
- Improvement 3

Rules:
- Use ONLY the provided context.
- Do not invent information.
- Do not change the headings.
- Complete every section.

Research Context:
{context}

Novelty Analysis:
"""

        output = generate_text(prompt, max_new_tokens=800)

        contributions = self._extract_section(
            output,
            "Novel Contributions:",
            [
                "Why The Work Is Unique:",
                "Novelty Score:",
                "Suggested Improvements:",
            ],
        )

        suggestions = self._extract_section(
            output,
            "Suggested Improvements:",
            [],
        )

        return AgentResult(
            self.name,
            {
                "novelty_score": score,
                "analysis": output,
                "contributions": contributions,
                "suggestions": suggestions,
            },
            evidence,
            self.confidence_from_evidence(evidence),
        )

    def _extract_section(self, text, start_heading, end_headings):
        start = text.find(start_heading)

        if start == -1:
            return []

        start += len(start_heading)

        end = len(text)

        for heading in end_headings:
            position = text.find(heading, start)
            if position != -1:
                end = min(end, position)

        section = text[start:end].strip()

        items = []

        for line in section.splitlines():
            line = line.strip()

            if not line:
                continue

            line = re.sub(r"^[-•*]\s*", "", line)

            if line:
                items.append(line)

        return items

    def _estimate_novelty_score(self, context, evidence):
        context = context.lower()

        novelty_patterns = [
            r"\bnovel\b",
            r"\bnovel approach\b",
            r"\bnovel method\b",
            r"\bnovel framework\b",
            r"\bwe propose\b",
            r"\bwe present\b",
            r"\bwe introduce\b",
            r"\bfirst\b",
            r"\boutperform\b",
            r"\bsurpass\b",
            r"\bnew architecture\b",
            r"\bsignificantly improve\b",
        ]

        limitation_patterns = [
            r"\blimitation\b",
            r"\bfuture work\b",
            r"\bsurvey\b",
            r"\breplication\b",
            r"\bbaseline only\b",
        ]

        novelty_hits = sum(
            len(re.findall(pattern, context))
            for pattern in novelty_patterns
        )

        limitation_hits = sum(
            len(re.findall(pattern, context))
            for pattern in limitation_patterns
        )

        confidence = self.confidence_from_evidence(evidence)

        score = novelty_hits * 6 - limitation_hits * 4 + confidence * 15

        return max(20, min(95, round(score)))