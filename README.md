# Sovereign AI Workbench

> **A self-hosted, offline-first Agentic AI Workbench for confidential industrial workflows.**

This repository contains our **Smart India Hackathon (SIH) 2026** solution for building a sovereign, locally deployed AI workbench capable of executing complex industrial tasks using open-weight multimodal models.

## ✨ Features

* 🧠 **Local Model Registry** — Automatically discovers and routes tasks to locally available Ollama models.
* 🤖 **Agentic Execution** — Plans and executes multi-step tasks using bounded tool-calling.
* 🔧 **Local Tool System** — File operations, document processing, code execution and other local capabilities.
* 📚 **Local RAG** — Semantic document search using SQLite + `sqlite-vec` with local embeddings.
* 🧠 **Conversational Memory** — Consolidates long conversations into persistent local memory.
* 👁️ **Multimodal / Vision Support** — Handles image-based tasks through local vision-capable models.
* 📄 **Document Generation** — Generates structured DOCX reports and other artifacts locally.
* ⚡ **Resource-Aware Inference** — Considers available CPU/RAM/GPU resources when configuring local models.
* 🔒 **Local-First Architecture** — Designed so sensitive data and inference remain on the organization's infrastructure.
* 🧾 **Execution Tracing** — Tracks agent steps, model calls and tool execution for transparency and debugging.

---

# 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      Streamlit UI    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Orchestrator      │
                         │ Task Classification  │
                         │   Model Routing      │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    ▼               ▼                ▼
             ┌───────────┐   ┌────────────┐   ┌─────────────┐
             │   Agent   │   │Model       │   │ Knowledge   │
             │  Engine   │   │Registry    │   │    / RAG    │
             └─────┬─────┘   └──────┬─────┘   └──────┬──────┘
                   │                │                │
                   ▼                ▼                ▼
             ┌───────────┐   ┌────────────┐   ┌─────────────┐
             │   Tools   │   │  Ollama    │   │ SQLite +    │
             │ Execution │   │Local Models│   │ sqlite-vec  │
             └───────────┘   └────────────┘   └─────────────┘
```

---

# 🧠 Local Model Registry

The workbench discovers models available through **Ollama** and determines their capabilities.

Example model configuration:

```text
llama3.2:3b
qwen2.5-coder:1.5b
qwen3-vl:4b
nomic-embed-text
```

Models can be selected according to the requirements of a task, such as:

* General reasoning
* Coding
* Vision
* Embeddings
* Context requirements
* Available system resources

This avoids tying the system to a single model.

---

# 🤖 Agentic Execution

The agent operates through a bounded execution loop:

```text
User Task
   │
   ▼
Task Classification
   │
   ▼
Model Selection
   │
   ▼
Planning / Decision
   │
   ▼
Tool Execution
   │
   ▼
Observation
   │
   ├──────► Continue
   │
   ▼
Validation / Final Response
```

The agent maintains an execution trace containing:

* Task steps
* Model decisions
* Tool calls
* Tool results
* Errors
* Final output

Execution is bounded to prevent uncontrolled agent loops.

---

# 📚 Local Knowledge & RAG

The system provides a completely local document retrieval pipeline.

```text
Documents
    │
    ▼
Chunking
    │
    ▼
Local Embeddings
    │
    ▼
SQLite + sqlite-vec
    │
    ▼
Semantic Search
    │
    ▼
Relevant Context
    │
    ▼
Local LLM
```

The system uses local embeddings and does not require an external vector database.

Supported knowledge can include:

* Manuals
* SOPs
* Technical documentation
* Reports
* Correspondence
* Reference documents

---

# 🧠 Conversational Memory

Long conversations can be consolidated into persistent local memory.

Instead of keeping an unlimited raw conversation:

```text
Long Conversation
       │
       ▼
Memory Consolidation
       │
       ▼
Local Summary + Embedding
       │
       ▼
Persistent Memory
```

This helps control context size while retaining useful information.

---

# 👁️ Multimodal Processing

The system supports vision-capable local models for image-based tasks.

Potential inputs include:

* Scanned documents
* Photographs
* Handwritten notes
* Engineering drawings
* Other visual references

Vision processing is performed through locally available models.

---

# 📄 Artifact Generation

The workbench can generate structured documents from agent workflows.

Example:

```text
Documents / Data
       │
       ▼
Agent Analysis
       │
       ▼
Validation
       │
       ▼
Generated Artifact
       │
       ▼
DOCX Report
```

Generated artifacts can be associated with the task that produced them.

---

# ⚡ Resource-Aware Inference

The system monitors available system resources and uses them when configuring local inference.

Resources considered include:

* CPU
* RAM
* GPU / VRAM
* Context size
* Model memory requirements
* RAG budgets
* Thread configuration

This is particularly important for on-premise deployments where hardware configurations can vary.

---

# 🔒 Sovereign / Local-First Design

The core principle is:

> **Sensitive data should remain inside the organization's infrastructure.**

The system is designed around:

```text
                    ORGANIZATION
                         │
          ┌──────────────┴──────────────┐
          │                             │
       Documents                    AI Models
          │                             │
          └──────────────┬──────────────┘
                         │
                  Sovereign AI
                    Workbench
                         │
                 Local Processing
```

No external AI API is required for the core inference pipeline.

> **Important:** Docker connectivity currently uses Ollama networking configuration for container communication. A production air-gapped deployment should additionally enforce OS/container-level network isolation and provide network telemetry.

---

# 📁 Project Structure

```text
.
├── app.py
├── agent.py
├── orchestrator.py
├── model_registry.py
├── rag.py
├── memory_manager.py
├── doc_gen.py
├── config.py
├── start.py
├── start_docker.py
├── debug.py
│
├── tools/
├── data/
├── artifacts/
├── models/
└── ...
```

---

# 🛠️ Requirements

* Python 3.10+
* Ollama
* Pandoc
* Git
* Optional: Docker / Docker Compose
* Local GPU recommended for larger models

---

# 🚀 Installation

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY>
```

Install dependencies using the project's environment setup.

Ensure Ollama is running:

```bash
ollama serve
```

Then start the application:

```bash
python start.py
```

The startup script handles environment checks and local model setup.

---

# 🐳 Docker Deployment

Docker deployment is also supported through:

```bash
python start_docker.py
```

The Docker startup process checks the required services and configures Ollama connectivity for the containerized application.

For production deployment, network isolation should be enforced at the infrastructure level rather than relying solely on application configuration.

---

# 🧪 Testing

The repository includes an integration/debug test suite.

Run:

```bash
python debug.py
```

The test suite covers areas including:

* Resource configuration
* Local model discovery
* Model routing
* Task classification
* RAG indexing
* Dynamic ingestion
* Semantic search
* DOCX generation
* Agent tool execution
* Vision workflow
* Memory consolidation

Temporary test data is created and cleaned up during testing.

---

# 💡 Example Workflow

A representative industrial workflow:

```text
Upload Inspection Report
          │
          ▼
     Local Processing
          │
          ▼
     Vision / OCR
          │
          ▼
      Local RAG
          │
          ▼
     SOP Retrieval
          │
          ▼
    Agent Reasoning
          │
          ▼
       Validation
          │
          ▼
    Generate Report
          │
          ▼
     Local Artifact
```

The complete workflow can be executed without sending the confidential documents to an external AI service.

---

# 🧬 Provenance & Traceability

A major design direction is to treat AI outputs as traceable objects rather than isolated chatbot responses.

Conceptually:

```text
Document
   │
   ├── contains ──► Finding
   │                  │
   │                  ├── supported_by ──► Evidence
   │                  │
   │                  └── checked_against ──► SOP
   │
   ▼
Task
   │
   └── generated ──► Artifact
                         │
                         └── derived_from ──► Document
```

This creates a foundation for **provenance, auditability and explainability** in industrial AI workflows.

---

# 🎯 Design Philosophy

### Local First

Keep sensitive processing within the organization's infrastructure.

### Model Agnostic

Do not make the entire system dependent on one AI model.

### Agentic but Bounded

Allow multi-step execution while maintaining limits and traceability.

### Observable

Every important execution step should be inspectable.

### Resource Aware

Adapt inference to the available hardware.

### Reproducible

Tasks, artifacts and execution traces should be recoverable and inspectable.

---

# 🏆 SIH 2026

This project is being developed for **Smart India Hackathon 2026**.

The goal is to demonstrate a practical sovereign AI workbench capable of performing confidential industrial knowledge work using locally hosted open-weight multimodal AI.

---

# 🤝 Meet the Team

| Name        | GitHub Profile                                       |
| :---------- | :--------------------------------------------------- |
| **Het**     | [@Hetk28](https://github.com/Hetk28)                 |
| **Arijeet** | [@ArijeetKurse](https://github.com/ArijeetKurse)     |
| **Yug**     | [@YugShah17](https://github.com/YugShah17)           |
| **Mahek**   | [@mahekpatel2112](https://github.com/mahekpatel2112) |
| **Murli**   | [@MurliT](https://github.com/MurliT)                 |
| **Vikas**   | [@Vicky404-git](https://github.com/Vicky404-git)     |

---

# 📌 Status

**Active Development — SIH 2026**

The current implementation provides the core local model, agent, RAG, memory, multimodal and document-generation foundations. Additional production-hardening, security controls, network enforcement and observability can be added as the project evolves.

