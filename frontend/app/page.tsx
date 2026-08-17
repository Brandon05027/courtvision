"use client";

import { useState } from "react";


type PossessionSummary = {
  summary: string;
  positive: string;
  improvement: string;
  evidence_keys: string[];
};


export default function Home() {
  const [analysis, setAnalysis] =
    useState<PossessionSummary | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function analyzePossession() {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/possessions/summary",
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