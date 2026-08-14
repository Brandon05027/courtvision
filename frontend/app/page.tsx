"use client";

import { useState } from "react";

type HealthResponse = {
  status: string;
  service: string;
};

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");

  async function checkBackend() {
    setError("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/health`
      );

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data: HealthResponse = await response.json();
      setHealth(data);
    } catch {
      setError("Could not connect to the CourtVision backend.");
    }
  }

  return (
    <main className="min-h-screen p-10">
      <h1 className="text-4xl font-bold">
        CourtVision AI
      </h1>

      <p className="mt-4">
        Basketball computer vision and analytics platform.
      </p>

      <button
        onClick={checkBackend}
        className="mt-8 rounded bg-black px-4 py-2 text-white"
      >
        Check Backend
      </button>

      {health && (
        <p className="mt-4">
          Backend status: {health.status}
        </p>
      )}

      {error && (
        <p className="mt-4">
          {error}
        </p>
      )}
    </main>
  );
}