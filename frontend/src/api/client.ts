import type { HealthResponse, RiskAssessment } from "./contracts";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { Accept: "application/json" },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Backend returned HTTP ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return getJson<HealthResponse>("/api/v1/health", signal);
}

export function getDemoAssessment(signal?: AbortSignal): Promise<RiskAssessment> {
  return getJson<RiskAssessment>("/api/v1/demo/assessment", signal);
}
