# 🎬 AI Video Assistance

<div align="center">

### **Turn Videos Into Insights. Instantly.**

<br>

## 🚀 [Try AI Video Assistance Live →](YOUR_LIVE_LINK_HERE)

<br>

**Upload a video or paste a YouTube link. Get the insights that matter.**

</div>

---

## ✨ What is AI Video Assistance?

**AI Video Assistance** is an AI-powered tool designed to help you understand video content without spending hours watching it.

Whether it's a long **YouTube video, podcast, lecture, or meeting recording**, simply provide your content and let AI do the heavy lifting.

It doesn't just generate a transcript—it helps you understand what actually matters.

> **Watch less. Understand more.**

---

## 🔥 Why AI Video Assistance?

Today, understanding video content often means switching between multiple tools.

You might use YouTube for a transcript, search Google for additional context, and use an AI chatbot to ask questions.

**AI Video Assistance brings everything together in one powerful workflow.**

```text
🎥 Video
   ↓
🎙️ Transcription
   ↓
🧠 AI Analysis
   ↓
📄 Summary • ✓ Action Items • ◆ Key Decisions • ❓ Open Questions
   ↓
💬 Chat with Your Video
```

---

# ✨ Features

### 📤 Upload or Paste a Link

* Upload video and audio files directly.
* Paste a YouTube link to analyze online content.

### 📄 Smart Summaries

Turn long-form content into a clear and concise summary.

### ✓ Action Items

Automatically identify actionable tasks and important next steps from meetings and discussions.

### ◆ Key Decisions

Quickly discover important decisions and conclusions made throughout the content.

### ❓ Open Questions

Identify unanswered questions and topics that may need further discussion.

### 💬 Chat with AI

Ask questions about your video and get answers based on its actual content using a **RAG-powered chat system**.

---

# 🖼️ Preview

<div align="center">

### Upload & Analyze

![AI Video Assistance Upload Page](assets/upload.png)

<br>

### AI-Powered Insights

![AI Video Assistance Insights](assets/insights.png)

</div>

---

# ⚙️ How It Works

```text
                    ┌─────────────────────┐
                    │   VIDEO / YOUTUBE   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  AUDIO PROCESSING   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   TRANSCRIPTION     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    AI ANALYSIS      │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
           📄 Summary     ✓ Actions      ◆ Decisions
                               │
                               ▼
                         ❓ Questions
                               │
                               ▼
                         💬 AI Chat
```

---

# 🛠️ Tech Stack

| Technology       | Purpose                    |
| ---------------- | -------------------------- |
| **Python**       | Core application           |
| **Streamlit**    | Interactive web interface  |
| **FFmpeg**       | Audio and video processing |
| **Whisper**      | Audio transcription        |
| **LangChain**    | AI workflow orchestration  |
| **ChromaDB**     | Vector database            |
| **Hugging Face** | Embeddings                 |
| **RAG**          | Context-aware video chat   |

---

# 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Add your environment variables

Create a `.env` file in the root directory:

```env
YOUR_API_KEY=your_api_key_here
```

### 6. Run the application

```bash
streamlit run app.py
```

---

# 📁 Project Structure

```text
AI-Video-Assistance/
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   ├── audio_processor.py
│   └── wallpaper.jpg
│
├── downloads/
├── vector_db/
│
├── app.py
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

<div align="center">

## 🎬 AI Video Assistance

### **Understand more. Watch less.**

Built with ❤️ and AI

</div>
