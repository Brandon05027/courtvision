# CourtVision AI

CourtVision AI is a basketball video analysis platform that combines computer vision, spatial analytics, and AI-generated coaching feedback.

Users can upload a short basketball clip, process player movement, manually calibrate the court, review movement analytics, define a possession, and generate an evidence-grounded coaching report from the measured data.

## Live Demo

Frontend:

https://courtvision-ochre.vercel.app

Backend API:

https://courtvision-backend.onrender.com

API documentation:

https://courtvision-backend.onrender.com/docs

> Note: The public backend runs on a free cloud instance. Computer-vision inference is CPU-intensive, so full uploaded-video processing may be significantly slower than local execution. The complete pipeline is designed and tested locally.

---

## Features

### Video Upload and Processing

- Upload short basketball clips through the web interface
- Validate video type and upload size
- Create persistent processing jobs
- Poll job status and processing progress
- Store intermediate analysis results by job ID

### Player Detection and Tracking

- Detect people using Ultralytics YOLO
- Track detections across frames using ByteTrack
- Extract:
  - bounding boxes
  - confidence scores
  - track IDs
  - timestamps
  - player court-contact points
- Generate an annotated tracking video

Because broadcast basketball footage can contain referees, spectators, occlusions, and ID switches, CourtVision describes tracking output as **stable tracking segments** rather than claiming perfect player identity.

### Court Calibration and Homography

CourtVision converts image coordinates into basketball-court coordinates using a manually defined four-point homography.

The browser allows the user to select court reference points directly from a calibration frame.

Mapped positions use a:

- 50-foot court width
- 47-foot half-court length

This allows pixel-based computer-vision output to become interpretable spatial basketball data.

### Movement Analytics

CourtVision analyzes mapped tracking observations to calculate metrics such as:

- distance traveled
- average speed
- maximum speed
- tracking coverage
- court positioning

The application also generates:

- movement paths
- player heatmaps
- overall movement heatmaps

### Possession Review

Users can manually define a possession by entering:

- possession start time
- possession end time
- result
- pass count

CourtVision then extracts tracking observations from that time window and calculates spatial evidence including:

- possession duration
- average spacing
- minimum spacing
- maximum spacing

Manual review is intentionally used for possession boundaries and outcomes rather than claiming unreliable automatic event recognition.

### Evidence-Grounded AI Coaching

CourtVision connects structured basketball analytics to an LLM to generate possession-level coaching feedback.

The AI receives only approved evidence fields such as:

- possession duration
- result
- pass count
- average spacing
- minimum spacing
- maximum spacing

The response includes:

- summary
- positive observation
- improvement recommendation
- evidence fields used

This architecture reduces unsupported AI claims by grounding coaching feedback in measured possession data.

---

## System Workflow

```text
Basketball Video
       |
       v
Video Upload
       |
       v
YOLO Person Detection
       |
       v
ByteTrack Tracking
       |
       v
Manual Court Calibration
       |
       v
Homography Mapping
       |
       v
Movement Analytics
       |
       +--------------------+
       |                    |
       v                    v
Movement Heatmap      Tracked Video
       |
       v
Manual Possession Review
       |
       v
Spacing Analysis
       |
       v
Evidence-Grounded AI Coaching