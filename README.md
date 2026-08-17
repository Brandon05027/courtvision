# CourtVision AI

CourtVision AI is a basketball video analytics platform that converts short game clips into structured player-tracking data, court-coordinate analytics, visualizations, and evidence-grounded possession summaries.

The project combines computer vision, deterministic analytics, human-in-the-loop correction, FastAPI services, a Next.js frontend, evaluation utilities, and an optional LLM explanation layer.

## Demo Flow

CourtVision processes a basketball clip through this pipeline:

```text
Basketball Video
        ↓
Video Preprocessing
        ↓
Player Detection
        ↓
Player Tracking
        ↓
Manual Court Calibration
        ↓
Court Coordinate Mapping
        ↓
Team Classification
        ↓
Human Corrections
        ↓
Movement / Shot / Possession Analytics
        ↓
Evidence-Grounded AI Summary
        ↓
FastAPI
        ↓
Next.js Dashboard
```

The current portfolio version is designed for short, fixed or mostly fixed-camera basketball clips rather than full broadcast games.

---

## Problem

Raw basketball video contains useful information about player movement, spacing, shot locations, and possessions, but extracting that information manually is slow.

CourtVision explores how a computer-vision pipeline can transform video into structured basketball analytics while keeping uncertain model outputs reviewable by a human.

The system is designed around three principles:

1. Computer vision extracts observations.
2. Deterministic Python code calculates analytics.
3. Generative AI explains structured facts rather than inventing basketball events.

---

## Key Features

### Player Detection

CourtVision uses a YOLO-based detector to identify people in basketball frames.

Each detection contains:

* Bounding-box coordinates
* Detection confidence
* An approximate court-contact point based on the bottom-center of the bounding box

The contact point is later transformed into basketball-court coordinates.

### Player Tracking

ByteTrack connects detections across frames and assigns persistent track IDs.

Tracking output includes:

* Frame number
* Timestamp
* Track ID
* Detection confidence
* Bounding box
* Approximate court-contact point

This allows CourtVision to analyze player movement over time rather than treating every frame independently.

### Manual Court Calibration

CourtVision uses a four-point homography transformation to map video pixels onto a standardized half-court coordinate system.

The current half-court convention is:

```text
Width: 50 feet
Length: 47 feet
```

A user selects four corresponding image points, and OpenCV calculates the perspective transformation matrix.

This converts coordinates such as:

```text
Video:
x = 842 px
y = 391 px
```

into physical court coordinates such as:

```text
Court:
x = 18.4 ft
y = 11.2 ft
```

### Court Mapping

Tracked player positions are transformed through the homography matrix.

CourtVision records whether each mapped position is inside the configured court boundary and can group valid positions by player track.

### Movement Analytics

CourtVision calculates deterministic player metrics including:

* Distance traveled
* Average speed
* Maximum speed
* Tracking duration
* Number of tracked positions
* Tracking coverage

Large unrealistic position jumps can be filtered to reduce the effect of tracking errors.

### Movement Paths and Heatmaps

CourtVision can generate:

* Top-down player movement paths
* Player heatmaps
* Half-court visualizations

Matplotlib uses a non-GUI backend so visualization tests can run in headless environments.

### Team Classification

CourtVision samples jersey colors across multiple frames instead of relying on a single image.

The current pipeline:

```text
Tracked player
    ↓
Torso crop
    ↓
LAB color conversion
    ↓
Median jersey color per frame
    ↓
Median track-level color profile
    ↓
Distance to team reference colors
    ↓
Team A / Team B / Unknown
```

An unknown-distance threshold prevents referees or visually dissimilar people from being forced into one of the two teams.

### Human-in-the-Loop Corrections

Automatic classification is not treated as ground truth.

CourtVision supports manual team corrections and can mark detections as:

```text
team_a
team_b
unknown
ignore
```

Ignored tracks can be excluded from downstream analytics.

This allows uncertain computer-vision predictions to be corrected before they contaminate later calculations.

### Shot Workflow

CourtVision supports manually confirmed shot records with:

* Shooter track ID
* Timestamp
* Court coordinates
* Team
* Made or missed result
* Approximate shot type

Shot types are currently categorized using deterministic court-distance rules such as:

* Paint
* Mid-range
* Three-pointer

Confirmed shots can be rendered onto a shot chart.

### Possession and Spacing Analytics

CourtVision supports manually segmented possessions.

Each possession can store:

* Team
* Start time
* End time
* Duration
* Result
* Pass count

CourtVision also calculates offensive spacing using average pairwise distance between tracked teammates.

Possession-level spacing can include:

* Average spacing
* Minimum spacing
* Maximum spacing
* Number of spacing samples

### Evidence-Grounded AI Summaries

CourtVision includes an optional LLM layer that explains structured possession analytics.

The model does not calculate movement, spacing, or possession statistics.

Instead, deterministic CourtVision code first produces facts such as:

```json
{
  "duration_seconds": 10.0,
  "result": "missed_shot",
  "pass_count": 3,
  "average_spacing_feet": 14.8,
  "minimum_spacing_feet": 11.2,
  "maximum_spacing_feet": 18.4
}
```

The language model then returns structured fields:

```json
{
  "summary": "...",
  "positive": "...",
  "improvement": "...",
  "evidence_keys": []
}
```

The output is validated with Pydantic, and evidence keys are restricted to approved factual fields.

CourtVision also instructs the model not to infer unsupported causes from outcomes. For example, a missed shot alone does not prove poor shot selection or poor execution.

If the external AI provider fails, CourtVision can return a deterministic fallback summary so the core analytics remain available.

---

## System Architecture

```text
                         ┌─────────────────────┐
                         │   Next.js Frontend  │
                         └─────────┬───────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         └─────────┬───────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ Analytics Layer  │          │  AI Summary      │
          │                  │          │  Layer           │
          │ Movement         │          │                  │
          │ Spacing          │          │ Structured facts │
          │ Shots            │          │ Pydantic         │
          │ Possessions      │          │ validation       │
          └────────┬─────────┘          │ Evidence checks  │
                   │                    └──────────────────┘
                   ▼
          ┌──────────────────┐
          │ Court Mapping    │
          │ + Homography     │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Team Assignment  │
          │ + Corrections    │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ ByteTrack        │
          │ Player Tracking  │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ YOLO Detection   │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Basketball Video │
          └──────────────────┘
```

---

## Pipeline Caching and Failure Recovery

CourtVision tracks processing stages separately:

```text
preprocessing
detection
tracking
calibration
mapping
analytics
summary
```

Each stage can be:

```text
pending
running
completed
failed
```

This allows successful work to be reused.

For example, if court calibration changes:

```text
Preprocessing     completed → reused
Detection         completed → reused
Tracking          completed → reused
Calibration       pending   → rerun
Mapping           pending   → rerun
Analytics         pending   → rerun
Summary           pending   → rerun
```

This avoids unnecessarily rerunning expensive computer-vision stages.

Failures are isolated as well.

If the AI summary fails, successfully completed tracking and analytics are preserved.

---

## Evaluation

CourtVision includes evaluation utilities for measuring system quality rather than relying only on visual inspection.

Supported metrics include:

* Detection precision
* Detection recall
* Labeled tracking coverage
* Identity-switch rate
* Average court-position error
* Processing throughput in frames per second

Example metric definitions:

```text
Precision
Of the detections CourtVision considered valid players,
how many were actually players?

Recall
Of the real players present,
how many were detected?

Identity-switch rate
How frequently tracking IDs incorrectly change.

Court-position error
Euclidean distance between mapped coordinates and
manually labeled court positions.

Processing FPS
Frames processed per second of computation.
```

Real performance values should be reported only after evaluating manually labeled clips.

---

## API

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Generate Possession Summary

```http
POST /api/v1/possessions/summary
```

Example request:

```json
{
  "possession_id": "poss_001",
  "team": "team_a",
  "start_time": 5.0,
  "end_time": 15.0,
  "duration_seconds": 10.0,
  "result": "missed_shot",
  "pass_count": 3,
  "manually_segmented": true,
  "spacing": {
    "average_spacing_feet": 14.8,
    "minimum_spacing_feet": 11.2,
    "maximum_spacing_feet": 18.4,
    "spacing_sample_count": 20
  }
}
```

Example response structure:

```json
{
  "summary": "...",
  "positive": "...",
  "improvement": "...",
  "evidence_keys": [
    "duration_seconds",
    "result",
    "pass_count",
    "average_spacing_feet"
  ]
}
```

FastAPI provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend

The Next.js dashboard connects directly to the FastAPI possession-analysis endpoint.

The current interface displays:

* Possession result
* Duration
* Pass count
* Average spacing
* AI-generated summary
* Positive observation
* Improvement opportunity
* Evidence fields used by the AI

The complete request flow is:

```text
User
  ↓
Next.js
  ↓
fetch()
  ↓
FastAPI
  ↓
Pydantic request validation
  ↓
CourtVision analytics / AI service
  ↓
Structured response validation
  ↓
React state
  ↓
Dashboard update
```

---

## Technology Stack

### Computer Vision and Analytics

* Python
* OpenCV
* Ultralytics YOLO
* ByteTrack
* NumPy
* Matplotlib

### Backend

* FastAPI
* Pydantic
* Uvicorn
* Python dotenv
* OpenAI-compatible Python SDK

### Frontend

* Next.js
* React
* TypeScript

### Engineering

* pytest
* Docker
* Git
* GitHub

---

## Project Structure

```text
courtvision/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   └── possessions.py
│   │   ├── schemas/
│   │   │   └── possession.py
│   │   └── services/
│   │       ├── ai_summary.py
│   │       ├── analytics.py
│   │       ├── calibration.py
│   │       ├── corrections.py
│   │       ├── detection.py
│   │       ├── evaluation.py
│   │       ├── mapping.py
│   │       ├── pipeline.py
│   │       ├── possessions.py
│   │       ├── shots.py
│   │       ├── team_classification.py
│   │       ├── tracking.py
│   │       ├── video.py
│   │       └── visualization.py
│   │
│   ├── test/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/
│   └── app/
│       └── page.tsx
│
├── sample_videos/
├── output/
├── .gitignore
└── README.md
```

Generated videos, model weights, environment secrets, and local outputs are excluded from source control.

---

## Local Setup

### Backend

From the backend directory:

```powershell
cd C:\Project\courtvision\backend
```

Create and activate a virtual environment if needed:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create:

```text
backend/.env
```

using:

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=
```

The AI service is optional. Core analytics can operate independently of the external LLM provider.

Start FastAPI:

```powershell
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

In another terminal:

```powershell
cd C:\Project\courtvision\frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

---

## Tests

Run the complete backend test suite from:

```text
C:\Project\courtvision\backend
```

with:

```powershell
python -m pytest
```

Tests cover functionality including:

* Video metadata and frame extraction
* Player analytics
* Court calibration
* Mapping
* Team classification
* Human corrections
* Visualization generation
* Shot records
* Possession and spacing analytics
* Evidence-grounded AI fallback behavior
* FastAPI endpoints
* Pipeline state management
* Evaluation metrics

External LLM calls should not be required for normal unit-test execution.

---

## Docker

Build the backend image:

```powershell
cd C:\Project\courtvision\backend
docker build -t courtvision-backend .
```

Run without external AI credentials:

```powershell
docker run --rm -p 8000:8000 courtvision-backend
```

If the application configuration requires an API key, pass the local environment file at runtime:

```powershell
docker run --rm -p 8000:8000 --env-file .env courtvision-backend
```

Verify:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Secrets are not copied into the Docker image.

---

## Engineering Decisions

### Why YOLO and ByteTrack are separate

Detection answers:

> Where are people in this frame?

Tracking answers:

> Which detections belong to the same person over time?

Separating the two allows each part of the pipeline to be evaluated and replaced independently.

### Why manual court calibration

Reliable automatic court detection would significantly increase the scope of the MVP.

Manual four-point calibration preserves the important computer-vision and linear-algebra problem while keeping the system feasible for short clips.

### Why use track-level jersey profiles

Single-frame color classification is fragile because lighting, skin, background pixels, referees, and partial occlusion can distort color measurements.

CourtVision samples torso regions across multiple frames and uses a median track-level LAB color profile.

### Why support human correction

Computer-vision predictions are probabilistic.

Allowing users to correct uncertain team or event assignments prevents bad predictions from silently propagating into downstream analytics.

### Why the LLM does not calculate analytics

Statistics such as distance, speed, spacing, and possession duration have deterministic definitions.

CourtVision calculates these in Python and gives the resulting facts to the language model only for explanation.

This reduces hallucination risk and makes AI-generated claims traceable to structured evidence.

### Why stage-level caching matters

Detection and tracking are relatively expensive.

Changing calibration should not require recomputing detections that are still valid.

Stage invalidation allows CourtVision to rerun only the portions of the pipeline affected by a change.

---

## Current Limitations

The current portfolio version intentionally limits scope.

* Optimized for short clips rather than full games
* Best suited for fixed or mostly fixed cameras
* Static homography does not automatically compensate for major camera pans or zooms
* Pretrained person detection can include referees or other people
* Tracking IDs can switch during heavy occlusion
* Team classification depends on visually distinguishable jersey colors
* Possession boundaries are manually segmented
* Shot outcomes are manually confirmed
* Reliable automatic ball tracking is not currently part of the core MVP
* No multi-camera synchronization
* No live analysis
* No automatic foul, assist, rebound, or defensive-scheme recognition

These limitations are intentional scope decisions rather than hidden assumptions.

---

## Future Improvements

Potential extensions include:

* Persisting analysis results in a database
* Background worker queue for long-running video jobs
* Direct-to-object-storage video uploads
* More advanced tracking and appearance embeddings
* Automated calibration assistance
* Ball detection and trajectory modeling
* Shot-attempt suggestions
* Larger manually labeled evaluation dataset
* Confidence-driven review interface
* Player naming
* Processing observability and profiling
* Deployment of frontend and backend
* Automatic generation of possession clips

---

## What CourtVision Demonstrates

CourtVision was built to demonstrate more than model inference.

The project includes:

```text
Computer vision
Object detection
Multi-object tracking
Homography
Coordinate transformations
Deterministic analytics
Visualization
Human-in-the-loop AI
Structured LLM integration
Hallucination controls
Pydantic validation
REST API design
React / Next.js integration
Failure recovery
Pipeline caching
Evaluation metrics
Automated testing
Docker
```

The central engineering idea is:

> **Computer vision produces observations, deterministic software produces analytics, and generative AI explains only the evidence that the system can support.**
