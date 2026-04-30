# Canvas - Multimodal Orchestrator
## Product Overview & Feature Deck

---

### Slide 1: Title

# Canvas
## Multimodal AI Orchestrator

*Build visual AI workflows connecting text, image, audio, and video generation*

**Powered by:** Google Gemini, Veo, Lyria, and Cloud TTS

---

### Slide 2: What is Canvas?

Canvas is a **visual node-based workflow engine** that lets you chain multiple AI models together to create complex media generation pipelines — without writing code.

**Key Value Props:**
- **Visual workflow builder** — drag, drop, and connect AI nodes
- **Multi-model orchestration** — chain Gemini, Veo, Lyria, TTS in one pipeline
- **Real-time execution** — watch results stream node-by-node via SSE
- **Team collaboration** — share workflows with teams or make them public
- **Asset management** — every generated asset is saved with its prompt history

![Main Canvas](images/01-main-canvas.png)

---

### Slide 3: Architecture

```
                    ┌──────────────┐
                    │   Frontend   │
                    │  React/Vite  │
                    │  ReactFlow   │
                    └──────┬───────┘
                           │ SSE / REST
                    ┌──────┴───────┐
                    │   Backend    │
                    │   FastAPI    │
                    │  Workflow    │
                    │   Engine     │
                    └──────┬───────┘
                           │
        ┌──────────┬───────┼───────┬──────────┐
        │          │       │       │          │
   ┌────┴────┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌────┴────┐
   │ Gemini  │ │ Veo │ │Lyria│ │ TTS │ │ Imagen  │
   │3.1 Pro  │ │ 3.1 │ │  3  │ │ 3.1 │ │   4.0   │
   │Flash/Lite│ │Lite │ │Pro/ │ │Flash│ │Upscale  │
   └─────────┘ │Fast │ │Clip │ └─────┘ └─────────┘
               └─────┘ └─────┘
```

**Stack:** React + Vite | FastAPI + SQLAlchemy | Firebase Auth | Google Cloud Run

---

### Slide 4: Node Types

| Category | Nodes | What it does |
|----------|-------|-------------|
| **Inputs** | Text, Image, Video, Audio | Upload or type content to feed into the pipeline |
| **Gemini** | Text, Image | Generate text responses or images from multimodal prompts |
| **Voice & Music** | Speech Gen, Lyria Clip, Lyria Pro | Text-to-speech (23 languages, 7 voices) and AI music generation |
| **Video** | Veo Standard, Extend, Reference | Generate, extend, or style-match videos |
| **Upscale** | Image Upscaler, Video Upscaler | Enhance resolution up to 4K |
| **Editor** | Video Editor | Combine videos, audio, and backgrounds with ffmpeg |
| **Outputs** | Text, Image, Audio, Video | Display and download results |

![Toolbar](images/02-toolbar-nodes.png)

---

### Slide 5: Workflow Execution

**How it works:**

1. **Build** — Drag nodes onto the canvas, connect them with edges
2. **Configure** — Set model, voice, language, aspect ratio per node
3. **Run** — Click Run, watch nodes execute in topological order
4. **Stream** — Results appear in real-time via Server-Sent Events
5. **Save** — Generated media is auto-saved to the Asset Library

**Smart error handling:**
- Failed nodes show red status
- Downstream nodes are **automatically skipped** (not executed with empty data)
- Clear error messages at the point of failure

---

### Slide 6: Workflow Tabs

![Workflow Tabs](images/03-workflow-tabs.png)

Work on **multiple workflows simultaneously**:

- **"+ New"** — Create a new blank workflow
- **Click tabs** — Switch between workflows instantly
- **Double-click** — Rename a tab
- **"x"** — Close a tab
- **State preserved** — Switching between Canvas/History/Studio doesn't lose your work

---

### Slide 7: Team Collaboration

**Create a team:**
1. Click "+" next to Teams in the sidebar
2. Name your team → get a **join code**

**Share the join code** — teammates enter it to join

**Workflow visibility:**

| Level | Who sees it |
|-------|------------|
| **Private** | Only you (default) |
| **Team** | All members of a selected team |
| **Public** | Everyone on the platform |

Set visibility from the dropdown in the toolbar before saving.

---

### Slide 8: Saved Canvas

![Saved Canvas](images/04-saved-canvas.png)

**Three views:**
- **Mine** — Your private and shared workflows
- **Team** — Workflows shared by teammates
- **Public** — Community workflows

**Built-in templates:**
- Product Ad Workflow
- Influencer Video
- Fashion Virtual Tryon
- Look Book Creation

Click any workflow to preview, run, or open in the editor.

---

### Slide 9: Asset Library

![Asset Library](images/05-asset-library.png)

Every generated media asset is **automatically saved** with:
- Full prompt text
- Model used
- Timestamp
- File type

**Features:**
- Filter by type: Images / Videos / Audio
- Search by prompt text
- Grid or list view
- Download any asset
- Expandable prompt display

---

### Slide 10: AI Models

| Capability | Models | Default |
|-----------|--------|---------|
| **Text** | gemini-3.1-pro-preview, gemini-3.1-flash-lite-preview | flash-lite |
| **Image** | gemini-3.1-flash-image-preview, gemini-2.5-flash-image | flash-image |
| **Video** | veo-3.1-generate-001, veo-3.1-fast-generate-001, veo-3.1-lite-generate-001 | lite |
| **Music** | lyria-3-pro-preview (full songs), lyria-3-clip-preview (30s clips) | clip |
| **TTS** | gemini-3.1-flash-tts-preview (23 languages, 7 voices) | flash-tts |
| **Upscale** | imagen-4.0-upscale-preview (images), veo-3.1-generate-001 (video 4K) | — |

All defaults are set to **lite/flash** variants for speed and cost efficiency.

---

### Slide 11: TTS Features

**23 supported languages** including:
English, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Hindi, Arabic, Russian, and more

**7 voices:** Kore, Leda, Puck, Charon, Fenrir, Aoede, Enceladus

**System Instructions** — customize speaking style:
- *"Speak cheerfully and with enthusiasm"*
- *"Use a calm, professional news anchor tone"*
- *"Whisper softly as if telling a secret"*

---

### Slide 12: Security

| Feature | Implementation |
|---------|---------------|
| **Authentication** | Firebase Google Sign-In with JWT tokens |
| **Authorization** | Per-route auth dependencies, team-based access control |
| **Path Traversal** | realpath validation on all file-serving endpoints |
| **XSS Prevention** | React state rendering (no innerHTML/insertAdjacentHTML) |
| **CORS** | Configurable origins, no wildcard with credentials |
| **Media Serving** | Dedicated /api/media endpoint with sanitized paths |
| **Cache** | LRU with 100-entry limit and 30-minute TTL |

---

### Slide 13: Deployment

**Cloud Run** — Single container deployment

```bash
export GOOGLE_CLOUD_PROJECT=your-project
./deploy.sh
```

**Requirements:**
- GCP project with Vertex AI enabled
- Firebase project with Google auth
- ~2GB memory, 1 CPU

**Environment variables:**
- `GOOGLE_CLOUD_PROJECT` — GCP project ID
- `FIREBASE_PROJECT_ID` — Firebase project ID
- `CORS_ORIGINS` — Allowed frontend origins

---

### Slide 14: Demo Workflow

**"Product Ad Workflow"**

```
[Text Input: "Luxury watch"] 
    → [Gemini Image: Generate product photo]
        → [Image Upscaler: 4K enhancement]
            → [Output: Download high-res image]
    → [Gemini Text: Write ad copy]
        → [Speech Gen: Narrate in French]
            → [Output: Download audio]
    → [Veo Standard: Generate video ad]
        → [Video Upscaler: 4K]
            → [Output: Download video]
```

Three parallel pipelines from a single text input — image, audio, and video — all orchestrated visually.

---

### Slide 15: What's Next

- **Workflow versioning** — Git-like history for workflow changes
- **Scheduled execution** — Run workflows on a timer
- **API endpoints** — Expose workflows as REST APIs
- **Custom nodes** — Plugin system for user-defined node types
- **Real-time collaboration** — Multiple users editing the same workflow
- **Cost tracking** — Per-workflow API cost estimation

---

*Built with Gemini, Veo, Lyria, and Cloud TTS on Google Cloud*
