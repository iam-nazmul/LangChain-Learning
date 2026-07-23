# spec.md — AI-Generated Art Platform

**Working title:** ArtForge (placeholder)
**Stack:** Python · FastAPI · LangChain · ChatOllama — `qwen3:8b` (text) + `qwen3-vl:8b` (vision/curation) · Stable Diffusion (diffusers)
**Status:** Draft v1
**Last updated:** 2026-07-22

---

## 0. Read this first — the core architectural decision

A common misconception: **ChatOllama does not generate images.** Ollama serves *text* (and some *vision-understanding*) LLMs — it cannot produce pixels. Text-to-image generation needs a diffusion model (Stable Diffusion / SDXL / FLUX) or an external image API (DALL·E, etc.).

So this system is built as **two cooperating layers**:

| Layer | Job | Powered by |
|-------|-----|-----------|
| **Brain (text)** | Understands user intent, engineers/enhances prompts, picks styles, writes titles/metadata, personalizes per user | **ChatOllama `qwen3:8b` + LangChain** |
| **Eyes (vision)** | Looks at rendered candidates to rank/select the best (curation) | **ChatOllama `qwen3-vl:8b`** (text-only `qwen3:8b` can't see images) |
| **Hands (pixels)** | Turns the engineered prompt into an actual image | **Stable Diffusion (local, via `diffusers`)** or a pluggable image-gen provider |

FastAPI is the glue and the public API. This split is the single most important thing to get right — the LLM makes the art *smart*, the diffusion model makes it *exist*.

---

## 1. Problem Statement

Creating high-quality, on-brand, personalized digital art at scale is slow and skill-gated. Non-artists struggle to write good image prompts, and existing tools (MidJourney, DALL·E) are closed, hard to automate/self-host, and don't remember a user's taste. This project delivers a **self-hostable, automated art pipeline** where an LLM does the "creative direction" (prompt craft, curation, personalization) and an open diffusion model does the rendering — cheaply, privately, and API-first.

## 2. Goals

1. **One-line to art:** a user submits a plain-language idea and receives finished, well-composed images without writing a "good" prompt themselves.
2. **Automated pipeline end to end:** creation → curation (auto-rank/select best of N) → personalization, with no manual step required.
3. **Self-hosted & private:** runs fully locally (Ollama + local diffusion) with no third-party image API required.
4. **Personalization that improves over time:** the system learns each user's stylistic preferences and biases new outputs toward them.
5. **API-first:** every capability is a documented FastAPI endpoint others can build on.

## 3. Non-Goals (v1)

1. **Training/fine-tuning custom diffusion models** — v1 uses off-the-shelf checkpoints + LoRAs; custom model training is a separate initiative.
2. **A polished consumer web/mobile UI** — v1 ships the API + a minimal demo page only.
3. **Marketplace / payments / NFT minting** — monetization is out of scope until the core pipeline is proven.
4. **Video / 3D / audio generation** — still images only for v1.
5. **Multi-tenant billing & quota enforcement** — auth stubs only; hardening is v2.

## 4. Target Users

- **Indie creators / small businesses** who need on-brand assets (thumbnails, social posts, mockups) fast.
- **Developers** who want a self-hosted image-gen API with an LLM prompt layer they can embed.
- **Hobbyists** who want good art without learning prompt engineering.

---

## 5. System Architecture

```
                     ┌──────────────────────────────────────────┐
   HTTP / JSON       │                FastAPI                    │
  ───────────────►   │  /generate  /curate  /personalize  /jobs │
                     └───────────────┬──────────────────────────┘
                                     │
                 ┌───────────────────┴───────────────────┐
                 │            LangChain Orchestrator       │
                 │  ┌──────────────┐   ┌────────────────┐  │
                 │  │ Prompt-Craft │   │  Curation      │  │
                 │  │ chain        │   │  chain (judge) │  │
                 │  └──────┬───────┘   └───────┬────────┘  │
                 │         │  ChatOllama LLM   │           │
                 │  ┌──────┴───────┐   ┌───────┴────────┐  │
                 │  │ Personalize  │   │ Metadata/Title │  │
                 │  │ chain (RAG)  │   │ chain          │  │
                 │  └──────────────┘   └────────────────┘  │
                 └───────────┬─────────────────┬───────────┘
                             │                 │
                   engineered prompt      user taste vectors
                             │                 │
                 ┌───────────▼──────┐   ┌──────▼──────────┐
                 │ Image Gen Backend│   │ Vector Store    │
                 │ (Stable Diffusion│   │ (Chroma/pgvector)│
                 │  via diffusers)  │   │ + Postgres      │
                 └───────────┬──────┘   └─────────────────┘
                             │
                 ┌───────────▼──────┐
                 │ Object Storage   │
                 │ (local FS / S3)  │
                 └──────────────────┘
```

**Request lifecycle (happy path for `/generate`):**
1. User sends an idea + optional constraints (aspect ratio, style hint, count).
2. **Prompt-Craft chain** (ChatOllama) expands the idea into a rich, model-ready prompt + negative prompt, injecting the user's learned style (RAG from vector store).
3. Image backend renders **N candidates** from that prompt.
4. **Curation chain** (a vision-capable Ollama model, e.g. LLaVA/llama3.2-vision, or an aesthetic scorer) ranks candidates and selects the best.
5. **Metadata chain** writes a title, description, and tags.
6. Results persisted; user preference signals recorded for future personalization.
7. Response returns image URLs + metadata (async job pattern for long renders).

---

## 6. Tech Stack

| Concern | Choice | Notes |
|---------|--------|-------|
| API framework | **FastAPI** + Uvicorn | async, auto OpenAPI docs |
| LLM serving | **Ollama** | `qwen3:8b` (text: prompt-craft, personalize, metadata), `qwen3-vl:8b` (vision: curation). ~6 GB VRAM each; alt vision model `llama3.2-vision:11b` for 8–16 GB VRAM |
| LLM framework | **LangChain** | `langchain-ollama` `ChatOllama`, LCEL chains, output parsers |
| Image generation | **`diffusers`** (SD 1.5 / SDXL / FLUX.1) | pluggable `ImageBackend` interface |
| Vector store | **Chroma** (dev) / **pgvector** (prod) | stores user taste + prompt history embeddings |
| Relational DB | **PostgreSQL** + SQLAlchemy | users, jobs, artworks, feedback |
| Job queue | **Celery + Redis** (or FastAPI `BackgroundTasks` in v0) | renders are slow; must be async |
| Object storage | Local FS (dev) / **S3-compatible** (prod) | generated images |
| Validation | **Pydantic v2** | request/response schemas |
| Packaging | **uv** or Poetry; Docker Compose | reproducible local stack |

---

## 7. User Stories

- As a **creator**, I want to type a plain idea and get finished images, so that I don't have to learn prompt engineering.
- As a **creator**, I want the system to auto-pick the best of several attempts, so that I'm not sifting through junk.
- As a **returning user**, I want new art to match my past likes, so that outputs feel personalized to my taste.
- As a **developer**, I want a `/generate` REST endpoint with async jobs, so that I can integrate art generation into my own app.
- As a **user**, I want each artwork to come with a title and tags, so that I can organize and reuse them.
- As a **user**, I want to thumbs-up/down results, so that the system learns what I like.
- *(Edge)* As a **user**, if a render fails or the prompt is rejected as unsafe, I want a clear error and no silent hang.

---

## 8. API Design (FastAPI)

All endpoints under `/api/v1`. Long-running generation uses an **async job** pattern.

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/generate` | Submit an art request → returns `job_id` |
| `GET`  | `/jobs/{job_id}` | Poll job status + results |
| `POST` | `/curate` | Given N image IDs, rank/select best (standalone) |
| `POST` | `/enhance-prompt` | Return the engineered prompt only (no render) |
| `POST` | `/feedback` | Record like/dislike/rating on an artwork |
| `GET`  | `/users/{id}/taste` | Inspect the learned style profile |
| `GET`  | `/artworks/{id}` | Fetch artwork + metadata |
| `GET`  | `/healthz` | Liveness (Ollama + DB + backend reachable) |

**`POST /generate` request:**
```json
{
  "user_id": "u_123",
  "idea": "a cozy mountain village at sunset",
  "count": 4,
  "aspect_ratio": "16:9",
  "style_hint": "watercolor",
  "personalize": true
}
```

**`GET /jobs/{job_id}` response (done):**
```json
{
  "job_id": "job_abc",
  "status": "succeeded",
  "engineered_prompt": "...",
  "results": [
    {
      "artwork_id": "art_1",
      "url": "https://.../art_1.png",
      "title": "Amber Hollow",
      "tags": ["landscape", "sunset", "watercolor"],
      "curation_score": 0.92,
      "selected": true
    }
  ]
}
```

---

## 9. LangChain + ChatOllama design

Four LCEL chains, each a small single-responsibility unit:

1. **Prompt-Craft chain** — `ChatOllama(model="qwen3:8b")` + a system prompt that turns a casual idea into a detailed positive prompt, a negative prompt, and suggested generation params. Output parsed via a Pydantic `StructuredOutputParser`. (Qwen3 has a "thinking" mode — disable it for this chain to keep latency/output clean, or parse it out.)
2. **Personalization (RAG) chain** — `qwen3:8b` retrieves the user's top-liked prompts/styles from the vector store and injects them as context so the Prompt-Craft chain biases toward learned taste.
3. **Curation chain** — the **vision** model `qwen3-vl:8b` scores each candidate on prompt-adherence + aesthetics and returns a ranking. This step *must* use a vision model — `qwen3:8b` is text-only and cannot see the rendered images. (Optionally combine with a lightweight aesthetic-scorer for speed.)
4. **Metadata chain** — `qwen3-vl:8b` writes title, description, tags from the final image + prompt (vision helps it describe what's actually in the picture; `qwen3:8b` works too if you feed it only the prompt).

Design rules:
- Every chain returns **validated structured output** (Pydantic), never free text the API has to regex.
- Chains are **composable and independently testable**; the orchestrator wires them.
- Keep an `ImageBackend` **Protocol** (`generate(prompt, params) -> list[Image]`) so Stable Diffusion vs. an external API is swappable without touching chains.

---

## 10. Data Model (core tables)

- **users**(id, created_at, settings)
- **artworks**(id, user_id, job_id, url, prompt, engineered_prompt, params_json, title, tags, curation_score, created_at)
- **jobs**(id, user_id, status, request_json, error, created_at, finished_at)
- **feedback**(id, user_id, artwork_id, signal[like|dislike|rating], value, created_at)
- **taste_vectors** (in vector store): per-user embeddings of liked prompts/styles for RAG personalization

---

## 11. Requirements

### Must-Have (P0) — v1 cannot ship without these
- [ ] `POST /generate` runs the full pipeline: prompt-craft → render N → curate → metadata.
- [ ] `qwen3:8b`-backed Prompt-Craft chain producing structured positive/negative prompts.
- [ ] Working local Stable Diffusion backend behind the `ImageBackend` interface.
- [ ] Async job pattern (`/jobs/{id}`) — no request blocks on a full render.
- [ ] Curation that auto-selects a "best" image from N candidates.
- [ ] Persistence of artworks + jobs; images saved to storage and served by URL.
- [ ] `/healthz` verifying Ollama, DB, and image backend are reachable.
- [ ] Basic safety filter on prompts (block disallowed content) with a clear error.

### Nice-to-Have (P1)
- [ ] Personalization RAG chain wired to real feedback signals.
- [ ] `/enhance-prompt` (prompt-only) and `/feedback` endpoints.
- [ ] Style presets / LoRA selection.
- [ ] Minimal demo web page.

### Future Considerations (P2)
- [ ] Custom model / LoRA training.
- [ ] Marketplace, licensing, payments.
- [ ] Multi-provider image backends (DALL·E, Replicate) with cost routing.
- [ ] Batch/scheduled generation jobs.

---

## 12. Suggested project structure

```
artforge/
├── app/
│   ├── main.py                # FastAPI app + routers
│   ├── api/v1/                # generate, jobs, curate, feedback routes
│   ├── chains/                # prompt_craft, curate, personalize, metadata
│   ├── backends/              # image_backend.py (Protocol) + sd_diffusers.py
│   ├── services/              # orchestrator, curation, personalization
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic request/response
│   ├── workers/               # Celery tasks
│   └── core/                  # config, ollama client, storage, safety
├── tests/
├── docker-compose.yml         # api + ollama + postgres + redis
├── pyproject.toml
└── spec.md
```

---

## 13. Phased Roadmap

- **Phase 0 — Walking skeleton:** FastAPI up, ChatOllama Prompt-Craft chain returns an engineered prompt, one SD render saved to disk. Sync, single image. *(Proves the brain↔hands split works.)*
- **Phase 1 — Pipeline (P0):** N candidates + curation + metadata + async jobs + persistence + health/safety. This is the shippable v1.
- **Phase 2 — Personalization (P1):** feedback capture + RAG taste profiles biasing new prompts.
- **Phase 3 — Hardening (v2):** Celery/Redis at scale, S3, auth/quotas, provider-pluggable backends.

---

## 14. Success Metrics

**Leading (days–weeks):**
- Generation success rate ≥ 95% (jobs finishing without error).
- Median end-to-end latency for a 4-image job under target hardware budget (define once GPU is chosen).
- "Best pick accepted" rate ≥ 60% (user keeps the auto-curated selection).

**Lagging (weeks–months):**
- Personalization lift: liked-rate on personalized outputs vs. non-personalized (target +20%).
- Repeat usage: % of users returning within 7 days.

Define exact targets after the first benchmark on real hardware.

---

## 15. Open Questions

- **[Eng]** Target hardware / GPU VRAM budget? Determines SDXL vs. SD1.5 vs. FLUX and batch size.
- **[Eng]** Curation approach: vision-LLM judge vs. a dedicated aesthetic scorer vs. both? Trade latency for quality.
- **[Eng/Product]** BackgroundTasks (simpler) vs. Celery+Redis (scalable) for v1 job handling?
- **[Legal/Safety]** What content policy and prompt-filter rules apply, and who owns them?
- **[Product]** Is an external image-API fallback (DALL·E/Replicate) in scope, or strictly self-hosted for v1?
- **[Data]** How many feedback signals before personalization meaningfully kicks in (cold-start handling)?

---

### Appendix — quick start (dev)
```bash
# 1. models
ollama pull qwen3:8b         # text brain: prompt-craft, personalize, metadata
ollama pull qwen3-vl:8b      # vision: curation (ranking rendered images)

# 2. stack
docker compose up -d          # api + ollama + postgres + redis

# 3. smoke test
curl -X POST localhost:8000/api/v1/generate \
  -H 'content-type: application/json' \
  -d '{"user_id":"u_1","idea":"cozy mountain village at sunset","count":4}'
```
