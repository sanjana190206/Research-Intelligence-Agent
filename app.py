from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rag.agents.citation_gap_agent import CitationGapDetectionAgent
from rag.agents.future_trend_agent import FutureTrendPredictionAgent
from rag.agents.novelty_agent import NoveltyAnalysisAgent
from rag.bob_orchestrator import BobOrchestrator
from rag.chunker import chunk_text
from rag.gap_detector import detect_research_gaps
from rag.literature_review import generate_literature_review
from rag.pdf_loader import extract_page_count, extract_text, extract_top_keywords
from rag.rag_pipeline import ask_question_with_evidence
from rag.report_exporter import build_docx_report, build_markdown_report, build_pdf_report
from rag.summarizer import summarize_paper
from rag.vector_store import store_chunks
import os

os.makedirs("uploads", exist_ok=True)
os.makedirs("chroma_db", exist_ok=True)


app = FastAPI(title="Research Intelligence Agent")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")
chat_history = []
orchestrator = BobOrchestrator()
active_paper = {
    "filename": None,
    "chunks": 0,
}
latest_report = {}


def answer_question(question: str):
    result = ask_question_with_evidence(question, chat_history)
    answer = result.output
    chat_history.append({
        "question": question,
        "answer": answer,
    })
    return result


def workflow_step(label, status="complete", detail=""):
    return {
        "label": label,
        "status": status,
        "detail": detail,
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request},
    )


@app.get("/ask", response_class=HTMLResponse)
def ask(request: Request, q: str):
    result = answer_question(q)
    return templates.TemplateResponse(
        request,
        "results.html",
        {
            "request": request,
            "question": q,
            "answer": result.output,
            "history": chat_history,
        },
    )


@app.get("/api/ask")
def ask_api(q: str):
    result = answer_question(q)
    return {
        "question": q,
        "answer": result.output,
        "history": chat_history,
        "evidence": result.evidence,
        "confidence_score": result.confidence_score,
    }


@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as uploaded_file:
        uploaded_file.write(await file.read())

    text = extract_text(file_path)

    # ===== DEBUG =====
    print("=" * 60)
    print("Uploaded PDF:", file.filename)
    print("Characters extracted:", len(text))
    print("First 500 characters:")
    print(text[:500])
    print("=" * 60)
    # =================

    chunks = chunk_text(text)
    store_chunks(chunks, source=file.filename)
    pages = extract_page_count(file_path)
    keywords = extract_top_keywords(text, n=5)
    active_paper["filename"] = file.filename
    active_paper["chunks"] = len(chunks)
    active_paper["pages"] = pages
    active_paper["keywords"] = keywords

    upload_activity = [
        workflow_step("PDF Uploaded", detail=file.filename),
        workflow_step("Text Extracted", detail=f"{len(text)} characters extracted."),
        workflow_step("Chunks Created", detail=f"{len(chunks)} chunks created."),
        workflow_step("Embeddings Generated", detail="ChromaDB generated vector embeddings."),
        workflow_step("ChromaDB Search Ready", detail="Vector store is ready for retrieval."),
    ]

    return {
        "message": f"{file.filename} uploaded successfully",
        "chunks": len(chunks),
        "pages": pages,
        "keywords": keywords,
        "active_paper": active_paper,
        "activity": upload_activity,
    }


@app.get("/summary")
def summary():
    report = orchestrator.run("summary")
    return {"summary": report["outputs"].get("summary"), **report}


@app.get("/review")
def review():
    report = orchestrator.run("literature review")
    return {"review": report["outputs"].get("literature_review"), **report}


@app.get("/gaps")
def gaps():
    return {"gaps": detect_research_gaps()}


@app.get("/section")
def section(section: str):
    report = orchestrator.run("section drafting", section=section)
    return {"section": section, "content": report["outputs"].get("section_drafting"), **report}


@app.get("/novelty")
def novelty():
    result = NoveltyAnalysisAgent().run()

    return {
        "novelty": result.output,
        "evidence": result.evidence,
        "confidence_score": result.confidence_score,
        "activity": [
            workflow_step("IBM Bob Planning", detail="Bob selected the Novelty Analysis Agent."),
            workflow_step("Novelty Agent", detail="Novelty analysis completed."),
            workflow_step("LLM Response Generated", detail="Novelty analysis generated successfully."),
        ],
    }


@app.get("/citation-gaps")
def citation_gaps():
    result = CitationGapDetectionAgent().run()
    return {
        "citation_gaps": result.output,
        "evidence": result.evidence,
        "confidence_score": result.confidence_score,
        "activity": [
            workflow_step("IBM Bob Planning", detail="Bob selected the Citation Gap Detection Agent."),
            workflow_step("Citation Agent", detail="Citation gap detection completed."),
            workflow_step("Granite Response Generated", detail="IBM Granite generated citation recommendations."),
        ],
    }


@app.get("/future-trends")
def future_trends():
    result = FutureTrendPredictionAgent().run()
    return {
        "future_trends": result.output,
        "evidence": result.evidence,
        "confidence_score": result.confidence_score,
        "activity": [
            workflow_step("IBM Bob Planning", detail="Bob selected the Future Trend Prediction Agent."),
            workflow_step("Future Trend Agent", detail="Future trend prediction completed."),
            workflow_step("Granite Response Generated", detail="IBM Granite generated trend output."),
        ],
    }



@app.get("/export/{format_name}")
def export_report(format_name: str):
    report = latest_report or orchestrator.run("full dashboard analysis export")
    normalized = format_name.lower()

    if normalized == "md":
        content = build_markdown_report(report)
        return Response(
            content,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=research_report.md"},
        )
    if normalized == "docx":
        content = build_docx_report(report)
        return Response(
            content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=research_report.docx"},
        )
    if normalized == "pdf":
        content = build_pdf_report(report)
        return Response(
            content,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=research_report.pdf"},
        )

    return {"error": "Unsupported export format. Use md, pdf, or docx."}
@app.get("/chunks")
def chunks():
    from rag.vector_store import get_all_chunks
    return {"chunks": get_all_chunks()}
