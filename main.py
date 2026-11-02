from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question
from rich import print


load_dotenv()

def run_pipeline(source: str, language: str = "english", progress_callback=None) -> dict:
    """
    Runs the full pipeline.

    progress_callback(stage, detail=None) is optional. The Streamlit UI passes it
    to show live steps. Stage keys used by app.py:
    download, transcribe, summary, actions, decisions, questions, index
    """

    def report(stage, detail=None):
        if progress_callback:
            try:
                progress_callback(stage, detail)
            except Exception:
                # A UI problem must never break the actual analysis
                pass

    print("starting AI Video Assistant")

    # 1. Download / extract / split audio
    report("download")
    chunks = process_input(source)

    # 2. Speech -> text
    engine = "Sarvam AI" if language == "hinglish" else "Whisper"
    try:
        total_chunks = len(chunks)
        transcribe_detail = f"{engine} is transcribing {total_chunks} audio chunk(s)"
    except TypeError:
        transcribe_detail = f"{engine} is transcribing your audio"

    report("transcribe", transcribe_detail)
    transcript = transcribe_all(chunks, language)
    print(f"raw transcription (first 300 characters ) {transcript[:300]}")

    # 3. Title + summary
    report("summary")
    title = generate_title(transcript)
    summary = summarize(transcript)

    # 4. Action items
    report("actions")
    action_item = extract_action_items(transcript)

    # 5. Key decisions
    report("decisions")
    decisions = extract_key_decisions(transcript)

    # 6. Open questions
    report("questions")
    questions = extract_questions(transcript)

    # 7. Vector DB for chat
    report("index")
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_item,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }

if __name__ == "__main__":
    # CLI entry point
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    result = run_pipeline(source, language)

    print("\n" + "=" * 60)
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)

    # Phase 2 — Chat with your meeting via RAG
    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue
        answer = ask_question(rag_chain, question)
        print(f"\n🤖 Assistant: {answer}\n")