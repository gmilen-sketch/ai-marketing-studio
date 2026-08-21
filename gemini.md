# Gemini Workspace Configuration & Memory Guide

This document preserves critical session parameters, authenticated scopes, and model guidelines for the SiteGround AI Video Production and Ad Repurposing workflow. Keep this file in memory across all agent sessions.

---

## 1. System Credentials & Active Billing Verification

* **Authentication Strategy**: This project uses Google Application Default Credentials (ADC) bound to your active GCP developer user.
* **Active Account**: `admin@mgenchev.altostrat.com`
* **Active GCP Project ID**: `firsttestproject-343414`
* **Billing & API Access**: **Fully Activated**. The environment has direct programmatic access to live Google GenAI model suites, Vertex AI, and connected BigQuery analytics backends. 
* **Rule**: **NEVER assume the environment is mocked or sandbox-blocked.** Always execute physical integration tests on live models during TDD cycles when requested.

---

## 2. Model Directory & Selection Guidelines (2026/2027)

Do not use legacy or deprecated versions (like `gemini-1.5-flash` or `gemini-2.5-flash`). Always target our latest production-grade frontier models:

| Task / Capability | Model Identifier | Tier / Release Class |
| :--- | :--- | :--- |
| **High-Speed Creative & Scripting** | `gemini-3.5-flash` | Production (Latest Frontier Model) |
| **Complex Logic, Outpainting Reasoning** | `gemini-3.5-pro` | Production (Highest Reasoning Cap) |
| **Multimodal Editing & Directing** | `gemini-omni-flash-preview` | Experimental (Interactions API) |
| **Cinematic B-Roll Synthesis** | `models/veo-3.2-creative-generate-002` | Production (Veo Video Tier) |
| **Static Canvas Backdrop Rendering** | `models/nano-banana-2` | Production (High-Density Studio UI) |

---

## 3. Core Architectural Rules for Future Sessions

1. **Zero-Distortion Principle**: Always preserve pixel-perfect interface text by using the hybrid compositing strategy. Let `Veo 3.2` synthesize beautiful, abstract moving backdrops, and overlay high-density SiteGround screenshots programmatically using our custom, verified `FFmpegCompositor`.
2. **PPC Telemetry Integration**: Programmatically enrich prompt payloads by querying `siteground_analytics.pmax_creative_telemetry` on BigQuery before drafting variants.
3. **HITL Interruption Hook**: The ADK node must cleanly yield standard `hitl_consent_request` objects to the A2UI and raise `NodeInterruptedError` to await manual storyboard sign-offs.
