"use client";

import {
  useEffect,
  useState,
} from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

type PossessionSummary = {
  summary: string;
  positive: string;
  improvement: string;
  evidence_keys: string[];
};


export default function Home() {
  const [analysis, setAnalysis] =
    useState<PossessionSummary | null>(null);

  const [videoFile, setVideoFile] =
    useState<File | null>(null);

  const [uploading, setUploading] =
    useState(false);

  const [uploadedVideoId, setUploadedVideoId] =
    useState<string | null>(null);
  const [processingJobId, setProcessingJobId] =
    useState<string | null>(null);

  const [processingStatus, setProcessingStatus] =
    useState<string | null>(null);

  const [processingStage, setProcessingStage] =
    useState<string | null>(null);

  const [processingProgress, setProcessingProgress] =
    useState(0);

  const [processingMessage, setProcessingMessage] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
  if (!processingJobId) {
    return;
  }

  const interval =
    window.setInterval(
      async () => {
        try {
          const response =
            await fetch(
              `${API_URL}/api/v1/videos/jobs/${processingJobId}`
            );

          if (!response.ok) {
            return;
          }

          const data =
            await response.json();

          setProcessingStatus(
            data.status
          );

          setProcessingStage(
            data.stage
          );

          setProcessingProgress(
            data.progress
          );

          setProcessingMessage(
            data.message
          );

          if (
            data.status === "ready" ||
            data.status === "completed" ||
            data.status === "failed"
          ) {
            window.clearInterval(
              interval
            );
          }

        } catch {
          // Polling can retry on
          // the next interval.
        }
      },
      1000
    );

  return () => {
    window.clearInterval(
      interval
    );
  };

}, [processingJobId]);

  async function uploadVideo() {
  if (!videoFile) {
    setError(
      "Please choose a video first."
    );

    return;
  }

  setUploading(true);
  setError(null);

  try {
    const formData =
      new FormData();

    formData.append(
      "video",
      videoFile
    );

    const response =
      await fetch(
        `${API_URL}/api/v1/videos/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

    if (!response.ok) {
      throw new Error(
        `Upload failed: ${response.status}`
      );
    }

    const data =
      await response.json();

    setUploadedVideoId(
      data.video_id
    );
    await startProcessing(
      data.video_id
    );
  } catch (err) {
    if (
      err instanceof Error
    ) {
      setError(
        err.message
      );
    }
  } finally {
    setUploading(false);
  }
}

async function startProcessing(
  videoId: string
) {
  try {
    const response =
      await fetch(
        `${API_URL}/api/v1/videos/${videoId}/process`,
        {
          method: "POST",
        }
      );

    if (!response.ok) {
      throw new Error(
        `Could not start processing: ${response.status}`
      );
    }

    const data =
      await response.json();

    setProcessingJobId(
      data.job_id
    );

    setProcessingStatus(
      data.status
    );

    setProcessingStage(
      data.stage
    );

    setProcessingProgress(
      data.progress
    );

    setProcessingMessage(
      data.message
    );

    return data.job_id;

  } catch (err) {
    if (err instanceof Error) {
      setError(
        err.message
      );
    }

    return null;
  }
}

  async function analyzePossession() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_URL}/api/v1/possessions/summary`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            possession_id: "poss_001",
            team: "team_a",
            start_time: 5.0,
            end_time: 15.0,
            duration_seconds: 10.0,
            result: "missed_shot",
            pass_count: 3,
            manually_segmented: true,
            spacing: {
              average_spacing_feet: 14.8,
              minimum_spacing_feet: 11.2,
              maximum_spacing_feet: 18.4,
              spacing_sample_count: 20,
            },
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          `Request failed: ${response.status}`
        );
      }

      const data: PossessionSummary =
        await response.json();

      setAnalysis(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "An unknown error occurred."
        );
      }
    } finally {
      setLoading(false);
    }
  }


  return (
    <main
      style={{
        maxWidth: "900px",
        margin: "0 auto",
        padding: "48px 24px",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <h1
        style={{
          fontSize: "36px",
          marginBottom: "8px",
        }}
      >
        CourtVision AI
      </h1>

      <p
        style={{
          marginBottom: "32px",
          color: "#555",
        }}
      >
        Basketball video analytics and
        evidence-grounded possession insights.
      </p>

      <section
        style={{
          border: "1px solid #ddd",
          borderRadius: "12px",
          padding: "24px",
          marginBottom: "24px",
        }}
      >
        <h2>Possession 1</h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(140px, 1fr))",
            gap: "16px",
            marginTop: "20px",
          }}
        >
          <div>
            <strong>Result</strong>
            <p>Missed Shot</p>
          </div>

          <div>
            <strong>Duration</strong>
            <p>10.0 sec</p>
          </div>

          <div>
            <strong>Passes</strong>
            <p>3</p>
          </div>

          <div>
            <strong>Avg. Spacing</strong>
            <p>14.8 ft</p>
          </div>
        </div>

        <button
          onClick={analyzePossession}
          disabled={loading}
          style={{
            marginTop: "20px",
            padding: "10px 18px",
            cursor: loading
              ? "not-allowed"
              : "pointer",
          }}
        >
          {loading
            ? "Analyzing..."
            : "Generate AI Analysis"}
        </button>
      </section>
        <section
          style={{
            border: "1px solid #ddd",
            borderRadius: "12px",
            padding: "24px",
            marginBottom: "24px",
          }}
        >
          <h2>
            Upload Basketball Clip
          </h2>

          <p>
            Upload a short basketball
            video for CourtVision analysis.
          </p>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "14px",
                marginTop: "18px",
              }}
            >
              <label
                htmlFor="video-upload"
                style={{
                  display: "inline-block",
                  width: "fit-content",
                  padding: "12px 18px",
                  borderRadius: "8px",
                  border: "1px solid #aaa",
                  cursor: "pointer",
                  fontWeight: "bold",
                  background: "#111",
                }}
              >
                Choose Basketball Video
              </label>

              <input
                id="video-upload"
                type="file"
                accept=".mp4,.mov,.avi,.mkv"
                onChange={(event) => {
                  const file =
                    event.target.files?.[0] ?? null;

                  setVideoFile(file);
                  setUploadedVideoId(null);
                  setError(null);
                }}
                style={{
                  display: "none",
                }}
              />

              {videoFile ? (
                <div>
                  <strong>Selected video:</strong>
                  <p>{videoFile.name}</p>
                </div>
              ) : (
                <p
                  style={{
                    color: "#888",
                    margin: 0,
                  }}
                >
                  No video selected
                </p>
              )}

              <button
                onClick={uploadVideo}
                disabled={uploading}
                style={{
                  width: "fit-content",
                  padding: "12px 20px",
                  borderRadius: "8px",
                  border: "none",
                  cursor: uploading
                    ? "not-allowed"
                    : "pointer",
                  fontWeight: "bold",
                  fontSize: "16px",
                }}
              >
                {uploading
                  ? "Uploading..."
                  : "Upload & Continue"}
              </button>
            </div>

          {uploadedVideoId && (
            <div
              style={{
                marginTop: "16px",
              }}
            >
              <strong>
                Upload successful
              </strong>

              <p>
                Video ID:{" "}
                {uploadedVideoId}
              </p>
            </div>
          )}
          {processingJobId && (
            <div
              style={{
                marginTop: "24px",
                padding: "18px",
                border: "1px solid #ddd",
                borderRadius: "10px",
              }}
            >
              <h3>
                Processing Status
              </h3>

              <p>
                <strong>Status:</strong>
                {" "}
                {processingStatus}
              </p>

              <p>
                <strong>Stage:</strong>
                {" "}
                {processingStage}
              </p>

              <p>
                {processingMessage}
              </p>

              <div
                style={{
                  width: "100%",
                  height: "14px",
                  background: "#ddd",
                  borderRadius: "8px",
                  overflow: "hidden",
                  marginTop: "12px",
                }}
              >
                <div
                  style={{
                    width:
                      `${processingProgress}%`,
                    height: "100%",
                    background: "#444",
                    transition:
                      "width 0.3s ease",
                  }}
                />
              </div>

              <p
                style={{
                  marginTop: "8px",
                }}
              >
                {processingProgress}%
              </p>
            </div>
          )}
        </section>
      {error && (
        <section
          style={{
            border: "1px solid #ccc",
            borderRadius: "12px",
            padding: "20px",
          }}
        >
          <strong>Error</strong>
          <p>{error}</p>
        </section>
      )}

      {analysis && (
        <section
          style={{
            border: "1px solid #ddd",
            borderRadius: "12px",
            padding: "24px",
          }}
        >
          <h2>AI Possession Analysis</h2>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>Summary</strong>
            <p>{analysis.summary}</p>
          </div>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>Positive</strong>
            <p>{analysis.positive}</p>
          </div>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>Improvement</strong>
            <p>{analysis.improvement}</p>
          </div>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>Evidence Used</strong>

            <ul>
              {analysis.evidence_keys.map(
                (key) => (
                  <li key={key}>
                    {key}
                  </li>
                )
              )}
            </ul>
          </div>
        </section>
      )}
    </main>
  );
}