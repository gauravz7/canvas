# Canvas — Demo Hosting Request (go/demo-hosting-request)

Copy-paste these values into the demo hosting request form.

---

## IAM Permissions / Roles Required by the Demo Development Team

The team needs the following **least-privilege roles** scoped to the demo project:

### Vertex AI (GenAI models)
- `roles/aiplatform.user` — Invoke Vertex AI APIs (Gemini, Veo, Lyria, Imagen)
- `roles/aiplatform.serviceAgent` — Background operations (predictLongRunning ops for Veo)

### Cloud Storage (GCS — for video/asset persistence + Veo input/output)
- `roles/storage.objectAdmin` (scoped to specific buckets: `genmedia-canvas`, `gs://<assets-bucket>`)
- `roles/storage.bucketViewer` — List buckets in console

### Cloud Run (deployment + serving)
- `roles/run.developer` — Deploy and update Cloud Run services
- `roles/run.invoker` (for `allUsers` on the service) — Public endpoint
- `roles/iam.serviceAccountUser` — Deploy with attached service account

### Cloud Build (build container images)
- `roles/cloudbuild.builds.editor` — Submit builds, push to Artifact Registry
- `roles/artifactregistry.writer` — Push container images
- `roles/storage.objectAdmin` on `gcr.io/<project>` bucket — Push to GCR

### Firebase / Identity Platform (Google sign-in)
- `roles/firebase.admin` (or finer: `roles/identityplatform.admin`) — Manage auth providers, authorized domains
- `roles/firebase.viewer` — Console access

### Cloud Logging & Monitoring (debug + observability)
- `roles/logging.viewer` — Read Cloud Run logs
- `roles/monitoring.viewer` — View metrics

### Service Usage (enable APIs)
- `roles/serviceusage.serviceUsageAdmin` — Enable required APIs (one-time setup)

### APIs to Enable
| API | Purpose |
|-----|---------|
| `aiplatform.googleapis.com` | Vertex AI (Gemini, Veo, Lyria, Imagen) |
| `texttospeech.googleapis.com` | Cloud Text-to-Speech (legacy fallback) |
| `run.googleapis.com` | Cloud Run service |
| `cloudbuild.googleapis.com` | Cloud Build for container images |
| `artifactregistry.googleapis.com` | Container Registry |
| `storage.googleapis.com` | Cloud Storage |
| `identitytoolkit.googleapis.com` | Firebase Auth / Identity Platform |
| `firebase.googleapis.com` | Firebase project management |
| `iap.googleapis.com` | Identity-Aware Proxy (if using IAP) |

---

## Organization Policy Mutations

The following org policies need to be **relaxed** for the demo to deploy successfully:

### 1. Allow Unauthenticated Cloud Run Invocations
- **Policy:** `iam.allowedPolicyMemberDomains`
- **Required mutation:** Allow `allUsers` as a member (currently restricted to organization domain).
- **Why:** Cloud Run service must be publicly accessible (`--allow-unauthenticated`) so the React frontend (and external demo viewers) can hit `/api/*` without org-level auth. Auth is enforced via Firebase tokens at the application layer.
- **Alternative:** Keep IAP-only access, but the OAuth client needs `localhost` and Cloud Run domain in authorized origins.

### 2. Public IP for Cloud Run Service
- **Policy:** `compute.vmExternalIpAccess` / Cloud Run ingress restrictions
- **Required mutation:** Allow ingress = `all` (default-internal-only blocks public access)
- **Why:** Same as above — the demo needs public reachability.

### 3. Domain-Restricted Sharing
- **Policy:** `iam.allowedPolicyMemberDomains` (for sharing GCS-backed media)
- **Required mutation:** Allow sharing with `alphabet@google.com`, `alphabet-extendedworkforce@google.com`, `googlers-intern@google.com` for the GCS asset bucket.
- **Why:** Per the demo guide, viewer access for these identities is required.

### 4. Skip Default Network Constraints (if Argolis)
- **Policy:** `compute.skipDefaultNetworkCreation`
- **Required mutation:** Allow Cloud Run to use default networking
- **Why:** Cloud Run uses Google-managed networking; restrictive policies block deployment.

### 5. Service Account Key Creation (if needed)
- **Policy:** `iam.disableServiceAccountKeyCreation`
- **Required mutation:** Relax for the demo's CI/CD service account (only if not using Workload Identity).
- **Why:** Local development sometimes needs a service account JSON key. Workload Identity is preferred but requires extra setup.

### 6. Vertex AI Region Restriction
- **Policy:** `gcp.resourceLocations` 
- **Required mutation:** Allow `us-central1` and `global` (Veo 3.1 uses `global` location for some endpoints)
- **Why:** Veo 3.1 generate models are served via the `global` location; region restrictions to e.g. EU-only break video generation.

### 7. Allowed AI Platform Models
- **Policy:** `aiplatform.allowedModels` (if set)
- **Required mutation:** Allow access to:
  - `gemini-3.1-*` (pro/flash-lite/flash-image/flash-tts) preview models
  - `veo-3.1-*-001` GA models
  - `lyria-3-pro-preview`, `lyria-3-clip-preview`
  - `imagen-4.0-upscale-preview`
- **Why:** These are the models the demo actively uses.

### 8. Firebase Auth Provider Allowlist
- **Policy:** Firebase / Identity Platform OAuth providers
- **Required mutation:** Enable Google as a sign-in provider; add `localhost` and the Cloud Run domain to authorized domains.
- **Why:** Firebase Auth blocks sign-in from non-authorized domains (`auth/unauthorized-domain` error).

---

## Quick-Reference Block

```
PROJECT: vital-octagon-19612
SERVICE NAME: vibe-studio-refactor
REGION: us-central1
PUBLIC URL: https://vibe-studio-refactor-440790012685.us-central1.run.app
GCS BUCKETS: genmedia-canvas (videos), <project>.appspot.com (assets)

ROLES (least-privilege):
- aiplatform.user
- storage.objectAdmin (scoped buckets)
- run.developer + run.invoker (allUsers)
- cloudbuild.builds.editor + artifactregistry.writer
- firebase.admin (auth provider config)
- logging.viewer (debugging)

ORG POLICIES TO RELAX:
- iam.allowedPolicyMemberDomains → allow allUsers on Cloud Run
- Cloud Run ingress → allow all
- gcp.resourceLocations → allow us-central1 + global
- aiplatform.allowedModels → allow Gemini/Veo/Lyria preview models
- Firebase authorized domains → add localhost + Cloud Run URL
```
