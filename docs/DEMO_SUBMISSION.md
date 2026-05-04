# Canvas Demo Submission — go/demos Form Fill

Copy-paste these values into the demo submission form at go/demos.

---

## General Info

### Demo Type *
**AI/ML Solution** *(or "Generative AI" / "Vertex AI Demo" depending on available options)*

### Title *
**Canvas — Multimodal AI Orchestrator**

### Thumbnail Summary *
Visual node-based workflow engine that chains Gemini, Veo, Lyria, and Cloud TTS to generate end-to-end multimedia content (images, audio, video) without code.

---

## Attribution

### Current Owner / Point of Contact *
gauravz

### Team Owner
*(Fill in your Moma team name, e.g., "AI Solutions Engineering")*

### Contributors
*(Add anyone who contributed; can leave blank)*

### Channel
*(Choose appropriate channel from your Moma list, e.g., "AI/ML Demos", "Vertex AI Showcase")*

---

## Demo Media

Upload screenshots from `docs/images/` in the repo:
- `01-main-canvas.png` — main canvas view (use as thumbnail)
- `02-workflow-tabs.png` — multiple workflow tabs
- `03-saved-canvas.png` — saved workflows panel
- `04-asset-library.png` — asset library
- `05-toolbar-actions.png` — toolbar with visibility controls
- `06-sidebar-signin.png` — sidebar with Firebase auth

---

## Click-To-Deploy

### Click-To-Deploy Path
*(Skip this section unless you set up automation in go/demos GOB repo)*

---

## Assets

### Demo Guide Link *
https://github.com/gauravz7/canvas/blob/main/docs/USER_GUIDE.md

### Live Application
- **Live Application Link Name:** Canvas Studio
- **Live Application URL:** https://vibe-studio-refactor-440790012685.us-central1.run.app

### Other Assets to Add
- **GitHub Repository:** https://github.com/gauravz7/canvas
- **Product Deck (PPTX):** https://github.com/gauravz7/canvas/blob/main/docs/Canvas_Product_Deck.pptx
- **Architecture Doc:** https://github.com/gauravz7/canvas/blob/main/docs/USER_GUIDE.md#architecture

### Key Asset
**Live Application** (Canvas Studio) — featured as the top button

### Featured Video
*(Optional: record a 2-min walkthrough and upload to YouTube/Drive)*

---

## Purpose

### Purpose *

Canvas lets users **build complex AI media generation pipelines visually** by connecting nodes — no code required. Drop a Gemini Image node, connect it to a Veo Standard node for animation, pipe through TTS for narration, combine with Lyria background music in the Video Editor, and export a finished video.

The platform abstracts the complexity of orchestrating Vertex AI services (Gemini 3.1, Veo 3.1, Lyria 3, Cloud TTS, Imagen) behind a drag-and-drop interface, with built-in support for:

- Multi-modal inputs (text, image, video, audio)
- Real-time streaming execution via Server-Sent Events
- Team collaboration with workflow sharing (private / team / public)
- Asset library with auto-saved generation history
- Multiple workflow tabs for parallel projects

### Business Value *

**Unlocks AI media production for non-engineers.** Marketing, design, and content teams can now self-serve cinematic ad creation, virtual try-on workflows, character-driven video sequences, and lookbook generation — work that previously required engineers to write code against multiple Vertex AI APIs.

**Concrete use cases:**
- **Product ads at scale:** product photo + brand brief → 4K hero image + animated video ad with voiceover and music in <5 minutes
- **Cinematic content:** character + scene description → 3 cinematic shots (wide/medium/close-up) with consistent character → assembled cinema sequence with Lyria Pro score
- **Virtual try-on:** person + garment + background → photorealistic VTO image → animated fashion reel with music

**Customer-facing impact:**
- Reduces time-to-create from days to minutes
- No engineering dependency for content production
- Reusable workflows shared across teams
- Auto-saved assets with full prompt provenance for compliance/audit

### Technical Value *

**Showcases the full Vertex AI generative stack in a single application:**

- **Gemini 3.1 family:** flash-lite (text), flash-image-preview (image), flash-tts-preview (TTS with 23 languages, 7 voices, system instructions)
- **Veo 3.1 family:** lite/fast/generate-001 video generation, video extension, image-to-video, subject reference, 4K upscale via predictLongRunning
- **Lyria 3 Pro & Clip:** image-conditioned music generation with auto-generated lyrics
- **Imagen 4.0 Upscale:** image super-resolution
- **GCS-backed asset persistence** with automatic Cloud Run instance recovery

**Engineering patterns demonstrated:**
- Node-based DAG execution engine with topological sort
- SSE streaming for real-time UX during long-running model calls
- Firebase Auth + token verification on FastAPI backend
- Auto-migration for deprecated model names
- Smart error propagation (failed node → downstream skipped automatically)
- Automatic GCS upload for video inputs that downstream nodes (extend/upscale) require

**Architecture:** React + Vite + ReactFlow frontend, FastAPI + SQLAlchemy backend, deployed on Cloud Run with GCS for asset persistence.

---

## Metadata

### Industries
- Media & Entertainment
- Retail & E-commerce (for VTO use case)
- Marketing/Advertising

### Solutions
- Generative AI
- Multimodal AI
- Content Creation Automation

### Hero Products * (select up to 4)
1. **Vertex AI** (Gemini 3.1)
2. **Vertex AI** (Veo 3.1)
3. **Vertex AI** (Lyria 3)
4. **Cloud Run**

*(Alternative if Lyria isn't listed: Cloud Text-to-Speech)*

### Content Labels
- Demo
- Internal
- Customer-facing
- Tutorial
*(Pick what applies in your Moma options)*

---

## Quick Reference Block (for chat/email)

```
Demo: Canvas — Multimodal AI Orchestrator
Owner: gauravz
URL: https://vibe-studio-refactor-440790012685.us-central1.run.app
Repo: https://github.com/gauravz7/canvas
Guide: https://github.com/gauravz7/canvas/blob/main/docs/USER_GUIDE.md
Hero products: Vertex AI (Gemini, Veo, Lyria), Cloud Run

Pitch: Visual workflow builder for chaining Gemini, Veo, Lyria, and TTS
to generate end-to-end multimedia content (images, audio, video) without
code. Drag-drop UI, real-time SSE execution, team workflow sharing,
auto-saved asset library.
```
