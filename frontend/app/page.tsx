"use client";

import {
  MouseEvent,
  useEffect,
  useRef,
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


type CalibrationPoint = {
  x: number;
  y: number;
};


type AnalyticsData = {
  unique_track_count: number;
  mapped_record_count: number;
  inside_court_record_count: number;
  player_distances_feet: Record<
    string,
    number
  >;
};


export default function Home() {
  // =========================
  // General
  // =========================

  const [error, setError] =
    useState<string | null>(null);


  // =========================
  // Video upload
  // =========================

  const videoInputRef =
    useRef<HTMLInputElement | null>(
      null
    );

  const [videoFile, setVideoFile] =
    useState<File | null>(null);

  const [uploading, setUploading] =
    useState(false);

  const [
    uploadedVideoId,
    setUploadedVideoId,
  ] = useState<string | null>(
    null
  );


  // =========================
  // Processing
  // =========================

  const [
    processingJobId,
    setProcessingJobId,
  ] = useState<string | null>(
    null
  );

  const [
    processingStatus,
    setProcessingStatus,
  ] = useState<string | null>(
    null
  );

  const [
    processingStage,
    setProcessingStage,
  ] = useState<string | null>(
    null
  );

  const [
    processingProgress,
    setProcessingProgress,
  ] = useState(0);

  const [
    processingMessage,
    setProcessingMessage,
  ] = useState<string | null>(
    null
  );

  const [
    trackRecordCount,
    setTrackRecordCount,
  ] = useState<number | null>(
    null
  );

  const [
    uniqueTrackCount,
    setUniqueTrackCount,
  ] = useState<number | null>(
    null
  );


  // =========================
  // Calibration
  // =========================

  const calibrationImageRef =
    useRef<HTMLImageElement | null>(
      null
    );

  const [
    calibrationPoints,
    setCalibrationPoints,
  ] = useState<CalibrationPoint[]>(
    []
  );

  const [
    calibrating,
    setCalibrating,
  ] = useState(false);

  const [
    calibrationComplete,
    setCalibrationComplete,
  ] = useState(false);

  const [
    mappedTrackCount,
    setMappedTrackCount,
  ] = useState<number | null>(
    null
  );

  const [
    insideCourtCount,
    setInsideCourtCount,
  ] = useState<number | null>(
    null
  );


  // =========================
  // Analytics
  // =========================

  const [
    analyticsLoading,
    setAnalyticsLoading,
  ] = useState(false);

  const [
    analyticsData,
    setAnalyticsData,
  ] = useState<AnalyticsData | null>(
    null
  );


  // =========================
  // Temporary possession demo
  // =========================

  const [
    analysis,
    setAnalysis,
  ] =
    useState<PossessionSummary | null>(
      null
    );

  const [loading, setLoading] =
    useState(false);


  // =========================
  // Poll processing status
  // =========================

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

            setTrackRecordCount(
              data.track_record_count ??
                null
            );

            setUniqueTrackCount(
              data.unique_track_count ??
                null
            );

            if (
              data.status ===
                "review_required" ||
              data.status ===
                "completed" ||
              data.status ===
                "failed"
            ) {
              window.clearInterval(
                interval
              );
            }
          } catch {
            // Try again next poll.
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


  // =========================
  // Upload video
  // =========================

  async function uploadVideo() {
    if (!videoFile) {
      setError(
        "Please choose a video first."
      );

      return;
    }

    setUploading(true);
    setError(null);

    setUploadedVideoId(null);
    setProcessingJobId(null);
    setProcessingStatus(null);
    setProcessingStage(null);
    setProcessingProgress(0);
    setProcessingMessage(null);

    setTrackRecordCount(null);
    setUniqueTrackCount(null);

    setCalibrationPoints([]);
    setCalibrationComplete(false);
    setMappedTrackCount(null);
    setInsideCourtCount(null);

    setAnalyticsData(null);
    setAnalysis(null);

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

      // Upload is complete here.
      setUploading(false);

      await startProcessing(
        data.video_id
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(
          err.message
        );
      }
    } finally {
      setUploading(false);
    }
  }


  // =========================
  // Start processing
  // =========================

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
    } catch (err) {
      if (err instanceof Error) {
        setError(
          err.message
        );
      }
    }
  }


  // =========================
  // Calibration click
  // =========================

  function handleCalibrationClick(
    event: MouseEvent<HTMLImageElement>
  ) {
    if (
      calibrationPoints.length >= 4
    ) {
      return;
    }

    const image =
      calibrationImageRef.current;

    if (!image) {
      return;
    }

    const rectangle =
      image.getBoundingClientRect();

    const displayedX =
      event.clientX -
      rectangle.left;

    const displayedY =
      event.clientY -
      rectangle.top;

    const scaleX =
      image.naturalWidth /
      rectangle.width;

    const scaleY =
      image.naturalHeight /
      rectangle.height;

    const x =
      displayedX *
      scaleX;

    const y =
      displayedY *
      scaleY;

    setCalibrationPoints(
      (current) => [
        ...current,
        {
          x: Math.round(x),
          y: Math.round(y),
        },
      ]
    );
  }


  // =========================
  // Reset calibration
  // =========================

  async function resetCalibration() {
    if (!processingJobId) {
      return;
    }

    setError(null);

    try {
      const response =
        await fetch(
          `${API_URL}/api/v1/videos/jobs/${processingJobId}/reset-calibration`,
          {
            method: "POST",
          }
        );

      if (!response.ok) {
        const body =
          await response.json();

        throw new Error(
          body.detail ??
            "Could not reset calibration."
        );
      }

      const data =
        await response.json();

      setCalibrationPoints([]);
      setCalibrationComplete(false);

      setMappedTrackCount(null);
      setInsideCourtCount(null);

      setAnalyticsData(null);

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
    } catch (err) {
      if (err instanceof Error) {
        setError(
          err.message
        );
      }
    }
  }


  // =========================
  // Submit calibration
  // =========================

  async function submitCalibration() {
    if (
      !processingJobId ||
      calibrationPoints.length !== 4
    ) {
      setError(
        "Select exactly four court points first."
      );

      return;
    }

    setCalibrating(true);
    setError(null);

    try {
      const response =
        await fetch(
          `${API_URL}/api/v1/videos/jobs/${processingJobId}/calibrate`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              image_points:
                calibrationPoints,
            }),
          }
        );

      if (!response.ok) {
        let message =
          `Calibration failed: ${response.status}`;

        try {
          const body =
            await response.json();

          if (body.detail) {
            message =
              body.detail;
          }
        } catch {
          // Keep fallback error.
        }

        throw new Error(
          message
        );
      }

      const data =
        await response.json();

      setCalibrationComplete(
        true
      );

      setMappedTrackCount(
        data.mapped_track_count
      );

      setInsideCourtCount(
        data.inside_court_count
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
    } catch (err) {
      if (err instanceof Error) {
        setError(
          err.message
        );
      }
    } finally {
      setCalibrating(false);
    }
  }


  // =========================
  // Analytics
  // =========================

  async function generateAnalytics() {
    if (!processingJobId) {
      setError(
        "Processing job is missing."
      );

      return;
    }

    setAnalyticsLoading(true);
    setError(null);

    try {
      const response =
        await fetch(
          `${API_URL}/api/v1/videos/jobs/${processingJobId}/analytics`,
          {
            method: "POST",
          }
        );

      if (!response.ok) {
        const body =
          await response.json();

        throw new Error(
          body.detail ??
            `Analytics failed: ${response.status}`
        );
      }

      const data =
        await response.json();

      setAnalyticsData(
        data
      );

      setProcessingStatus(
        "processing"
      );

      setProcessingStage(
        "analytics"
      );

      setProcessingProgress(
        90
      );

      setProcessingMessage(
        "Movement analytics generated successfully."
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(
          err.message
        );
      }
    } finally {
      setAnalyticsLoading(false);
    }
  }


  // =========================
  // Temporary possession demo
  // =========================

  async function analyzePossession() {
    setLoading(true);
    setError(null);

    try {
      const response =
        await fetch(
          `${API_URL}/api/v1/possessions/summary`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
            },
            body: JSON.stringify({
              possession_id:
                "poss_001",
              team:
                "team_a",
              start_time:
                5.0,
              end_time:
                15.0,
              duration_seconds:
                10.0,
              result:
                "missed_shot",
              pass_count:
                3,
              manually_segmented:
                true,
              spacing: {
                average_spacing_feet:
                  14.8,
                minimum_spacing_feet:
                  11.2,
                maximum_spacing_feet:
                  18.4,
                spacing_sample_count:
                  20,
              },
            }),
          }
        );

      if (!response.ok) {
        throw new Error(
          `Request failed: ${response.status}`
        );
      }

      const data:
        PossessionSummary =
          await response.json();

      setAnalysis(
        data
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(
          err.message
        );
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
        fontFamily:
          "Arial, sans-serif",
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
          color: "#888",
        }}
      >
        Basketball video analytics
        and evidence-grounded
        possession insights.
      </p>


      {/* ========================= */}
      {/* 1. VIDEO UPLOAD */}
      {/* ========================= */}

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
          video for CourtVision
          analysis.
        </p>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "14px",
            marginTop: "18px",
          }}
        >
          <input
            ref={videoInputRef}
            type="file"
            accept=".mp4,.mov,.avi,.mkv,video/*"
            style={{
              display: "none",
            }}
            onChange={(event) => {
              const selectedFile =
                event.currentTarget
                  .files?.[0];

              if (!selectedFile) {
                return;
              }

              setVideoFile(
                selectedFile
              );

              setUploadedVideoId(
                null
              );

              setError(null);
            }}
          />

          <button
            type="button"
            onClick={() =>
              videoInputRef
                .current
                ?.click()
            }
            style={{
              width: "fit-content",
              padding: "12px 18px",
              borderRadius: "8px",
              border:
                "1px solid #aaa",
              cursor: "pointer",
              fontWeight: "bold",
              fontSize: "16px",
            }}
          >
            Choose Basketball Video
          </button>

          {videoFile ? (
            <div>
              <strong>
                Selected video:
              </strong>

              <p>
                {videoFile.name}
              </p>
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
              cursor:
                uploading
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
              marginTop: "20px",
            }}
          >
            <strong>
              Upload successful
            </strong>

            <p>
              Video ID:{" "}
              {uploadedVideoId}
            </p>

            {processingJobId && (
              <p>
                Job ID:{" "}
                {processingJobId}
              </p>
            )}
          </div>
        )}


        {processingJobId && (
          <div
            style={{
              marginTop: "24px",
              padding: "18px",
              border:
                "1px solid #ddd",
              borderRadius: "10px",
            }}
          >
            <h3>
              Processing Status
            </h3>

            <p>
              <strong>
                Status:
              </strong>{" "}
              {processingStatus}
            </p>

            <p>
              <strong>
                Stage:
              </strong>{" "}
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

            <p>
              {processingProgress}%
            </p>

            {processingStage ===
              "tracking" && (
              <p
                style={{
                  color: "#888",
                }}
              >
                Player tracking can
                take a few minutes
                for longer clips.
              </p>
            )}

            {uniqueTrackCount !==
              null && (
              <div>
                <strong>
                  Tracking Results
                </strong>

                <p>
                  Raw track IDs:{" "}
                  {uniqueTrackCount}
                </p>

                <p>
                  Tracking records:{" "}
                  {trackRecordCount}
                </p>
              </div>
            )}

            {processingStatus ===
              "review_required" && (
              <div
                style={{
                  marginTop: "18px",
                  padding: "14px",
                  border:
                    "1px solid #ccc",
                  borderRadius: "8px",
                }}
              >
                <strong>
                  Player tracking
                  complete
                </strong>

                <p>
                  Next step:
                  calibrate the
                  basketball court.
                </p>
              </div>
            )}
          </div>
        )}
      </section>


      {/* ========================= */}
      {/* 2. CALIBRATION */}
      {/* ========================= */}

      {processingJobId &&
        (
          processingStatus ===
            "review_required" ||
          calibrationComplete
        ) && (
          <section
            style={{
              border:
                "1px solid #ddd",
              borderRadius: "12px",
              padding: "24px",
              marginBottom: "24px",
            }}
          >
            <h2>
              Calibrate Basketball
              Court
            </h2>

            <p>
              Click four court points
              in this exact order:
            </p>

            <ol>
              <li>
                Top-left
              </li>

              <li>
                Top-right
              </li>

              <li>
                Bottom-left
              </li>

              <li>
                Bottom-right
              </li>
            </ol>

            <img
              ref={
                calibrationImageRef
              }
              src={`${API_URL}/api/v1/videos/jobs/${processingJobId}/calibration-frame`}
              alt="Basketball court calibration"
              onClick={
                handleCalibrationClick
              }
              style={{
                width: "100%",
                maxWidth: "800px",
                cursor: "crosshair",
                borderRadius: "8px",
                marginTop: "20px",
                display: "block",
              }}
            />

            <div
              style={{
                marginTop: "18px",
              }}
            >
              <strong>
                Points selected:{" "}
                {
                  calibrationPoints.length
                }
                /4
              </strong>

              {calibrationPoints.map(
                (
                  point,
                  index
                ) => (
                  <p
                    key={
                      index
                    }
                  >
                    Point{" "}
                    {index + 1}: (
                    {point.x},{" "}
                    {point.y})
                  </p>
                )
              )}
            </div>

            <div
              style={{
                display: "flex",
                gap: "12px",
                marginTop: "18px",
              }}
            >
              <button
                onClick={
                  resetCalibration
                }
                style={{
                  padding:
                    "10px 18px",
                  cursor:
                    "pointer",
                }}
              >
                Reset Points
              </button>

              <button
                onClick={
                  submitCalibration
                }
                disabled={
                  calibrating ||
                  calibrationPoints.length !==
                    4
                }
                style={{
                  padding:
                    "10px 18px",
                  cursor:
                    calibrationPoints.length ===
                      4 &&
                    !calibrating
                      ? "pointer"
                      : "not-allowed",
                  fontWeight:
                    "bold",
                }}
              >
                {calibrating
                  ? "Calibrating..."
                  : "Confirm Court"}
              </button>
            </div>


            {calibrationComplete && (
              <div
                style={{
                  marginTop: "20px",
                  padding: "16px",
                  border:
                    "1px solid #ccc",
                  borderRadius: "8px",
                }}
              >
                <strong>
                  Court calibration
                  complete
                </strong>

                <p>
                  Tracking positions
                  were mapped into
                  basketball-court
                  coordinates.
                </p>

                <p>
                  Mapped tracking
                  records:{" "}
                  {mappedTrackCount}
                </p>

                <p>
                  Records inside
                  court:{" "}
                  {insideCourtCount}
                </p>

                <button
                  onClick={
                    generateAnalytics
                  }
                  disabled={
                    analyticsLoading
                  }
                  style={{
                    marginTop: "16px",
                    padding:
                      "10px 18px",
                    fontWeight: "bold",
                    cursor:
                      analyticsLoading
                        ? "not-allowed"
                        : "pointer",
                  }}
                >
                  {analyticsLoading
                    ? "Generating Analytics..."
                    : "Continue to Analytics"}
                </button>
              </div>
            )}
          </section>
        )}


      {/* ========================= */}
      {/* 3. COURTVISION RESULTS */}
      {/* ========================= */}

      {analyticsData && (
        <section
          style={{
            border:
              "1px solid #ddd",
            borderRadius: "12px",
            padding: "24px",
            marginBottom: "24px",
          }}
        >
          <h2>
            CourtVision Results
          </h2>


          {/* Summary */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(160px, 1fr))",
              gap: "16px",
              marginTop: "20px",
            }}
          >
            <div>
              <strong>
                Stable Tracking
                Segments
              </strong>

              <p>
                {
                  analyticsData
                    .unique_track_count
                }
              </p>
            </div>

            <div>
              <strong>
                Mapped Records
              </strong>

              <p>
                {
                  analyticsData
                    .mapped_record_count
                }
              </p>
            </div>

            <div>
              <strong>
                Inside Court
              </strong>

              <p>
                {
                  analyticsData
                    .inside_court_record_count
                }
              </p>
            </div>
          </div>


          {/* Movement Heatmap */}

          <div
            style={{
              marginTop: "32px",
            }}
          >
            <h3>
              Movement Heatmap
            </h3>

            <p
              style={{
                color: "#888",
              }}
            >
              Tracking observations
              mapped into
              basketball-court
              coordinates.
            </p>

            {processingJobId && (
              <img
                src={`${API_URL}/api/v1/videos/jobs/${processingJobId}/movement-heatmap`}
                alt="CourtVision movement heatmap"
                style={{
                  width: "100%",
                  maxWidth: "800px",
                  marginTop: "14px",
                  borderRadius: "10px",
                  border:
                    "1px solid #ddd",
                  display: "block",
                }}
              />
            )}
          </div>


          {/* Tracked Video */}

          <div
            style={{
              marginTop: "32px",
            }}
          >
            <h3>
              Tracked Video
            </h3>

            <p
              style={{
                color: "#888",
              }}
            >
              Computer-vision
              tracking overlay for
              the uploaded clip.
            </p>

            {processingJobId && (
              <video
                controls
                src={`${API_URL}/api/v1/videos/jobs/${processingJobId}/tracked-video`}
                style={{
                  width: "100%",
                  maxWidth: "800px",
                  borderRadius: "10px",
                  marginTop: "14px",
                }}
              >
                Your browser does not
                support video playback.
              </video>
            )}
          </div>


          {/* Top movement */}

          <div
            style={{
              marginTop: "32px",
            }}
          >
            <h3>
              Top Movement Segments
            </h3>

            <p
              style={{
                color: "#888",
              }}
            >
              Longest mapped movement
              distances from stable
              tracking segments.
            </p>

            <div
              style={{
                display: "grid",
                gap: "10px",
                marginTop: "14px",
              }}
            >
              {Object.entries(
                analyticsData
                  .player_distances_feet
              )
                .sort(
                  (
                    [, distanceA],
                    [, distanceB]
                  ) =>
                    distanceB -
                    distanceA
                )
                .slice(0, 10)
                .map(
                  (
                    [
                      trackId,
                      distance,
                    ]
                  ) => (
                    <div
                      key={
                        trackId
                      }
                      style={{
                        padding:
                          "12px",
                        border:
                          "1px solid #ddd",
                        borderRadius:
                          "8px",
                      }}
                    >
                      <strong>
                        Track{" "}
                        {trackId}
                      </strong>

                      <p>
                        Distance
                        traveled:{" "}
                        {distance.toFixed(
                          1
                        )}{" "}
                        ft
                      </p>
                    </div>
                  )
                )}
            </div>
          </div>


          <div
            style={{
              marginTop: "28px",
              padding: "14px",
              border:
                "1px solid #ddd",
              borderRadius: "8px",
            }}
          >
            <strong>
              Experimental Feature
            </strong>

            <p
              style={{
                marginBottom: 0,
              }}
            >
              Jersey-color team
              classification is
              available in the
              backend but is not
              required for the
              primary analytics
              workflow.
            </p>
          </div>
        </section>
      )}


      {/* ========================= */}
      {/* 4. TEMPORARY POSSESSION */}
      {/* ========================= */}

      <section
        style={{
          border:
            "1px solid #ddd",
          borderRadius: "12px",
          padding: "24px",
          marginBottom: "24px",
        }}
      >
        <h2>
          Demo Possession
        </h2>

        <p
          style={{
            color: "#888",
          }}
        >
          Temporary demo data. This
          will be replaced by the
          real possession workflow
          in Session 24.
        </p>

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
            <strong>
              Result
            </strong>

            <p>
              Missed Shot
            </p>
          </div>

          <div>
            <strong>
              Duration
            </strong>

            <p>
              10.0 sec
            </p>
          </div>

          <div>
            <strong>
              Passes
            </strong>

            <p>
              3
            </p>
          </div>

          <div>
            <strong>
              Avg. Spacing
            </strong>

            <p>
              14.8 ft
            </p>
          </div>
        </div>

        <button
          onClick={
            analyzePossession
          }
          disabled={
            loading
          }
          style={{
            marginTop: "20px",
            padding:
              "10px 18px",
            cursor:
              loading
                ? "not-allowed"
                : "pointer",
          }}
        >
          {loading
            ? "Analyzing..."
            : "Generate Demo AI Analysis"}
        </button>
      </section>


      {/* ========================= */}
      {/* ERROR */}
      {/* ========================= */}

      {error && (
        <section
          style={{
            border:
              "1px solid #ccc",
            borderRadius: "12px",
            padding: "20px",
            marginBottom: "24px",
          }}
        >
          <strong>
            Error
          </strong>

          <p>
            {error}
          </p>
        </section>
      )}


      {/* ========================= */}
      {/* AI RESPONSE */}
      {/* ========================= */}

      {analysis && (
        <section
          style={{
            border:
              "1px solid #ddd",
            borderRadius: "12px",
            padding: "24px",
          }}
        >
          <h2>
            AI Possession Analysis
          </h2>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>
              Summary
            </strong>

            <p>
              {analysis.summary}
            </p>
          </div>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>
              Positive
            </strong>

            <p>
              {analysis.positive}
            </p>
          </div>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>
              Improvement
            </strong>

            <p>
              {
                analysis.improvement
              }
            </p>
          </div>

          <div
            style={{
              marginTop: "20px",
            }}
          >
            <strong>
              Evidence Used
            </strong>

            <ul>
              {analysis
                .evidence_keys
                .map(
                  (key) => (
                    <li
                      key={
                        key
                      }
                    >
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