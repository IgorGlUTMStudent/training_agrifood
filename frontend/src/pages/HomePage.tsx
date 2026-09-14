import { useCallback, useEffect, useState } from "react";

import { getDemoAssessment, getHealth } from "../api/client";
import type { HealthResponse, RiskAssessment } from "../api/contracts";
import { AssessmentCard } from "../components/AssessmentCard";
import { BackendStatus } from "../components/BackendStatus";

type ConnectionState =
  | { kind: "loading" }
  | { kind: "available"; health: HealthResponse; assessment: RiskAssessment }
  | { kind: "unavailable"; message: string };

export function HomePage() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "loading" });
  const [reloadKey, setReloadKey] = useState(0);

  const retry = useCallback(() => {
    setConnection({ kind: "loading" });
    setReloadKey((current) => current + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    Promise.all([
      getHealth(controller.signal),
      getDemoAssessment(controller.signal),
    ])
      .then(([health, assessment]) => {
        setConnection({ kind: "available", health, assessment });
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        const message = error instanceof Error ? error.message : "Unknown connection error";
        setConnection({ kind: "unavailable", message });
      });

    return () => controller.abort();
  }, [reloadKey]);

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Operator decision-support prototype</p>
        <h1>Smart Harvest</h1>
        <p>
          A minimal foundation for transparent post-harvest risk assessment.
          Analytics and dataset integration are not configured yet.
        </p>
      </header>

      {connection.kind === "loading" && (
        <section className="panel connection-state" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          <div>
            <p className="eyebrow">Backend status</p>
            <h2>Connecting…</h2>
          </div>
        </section>
      )}

      {connection.kind === "unavailable" && (
        <section className="panel connection-state connection-state--error" aria-live="polite">
          <div>
            <p className="eyebrow">Backend status</p>
            <h2>Unavailable</h2>
            <p>The application could not reach the Smart Harvest API: {connection.message}</p>
          </div>
          <button type="button" onClick={retry}>
            Try again
          </button>
        </section>
      )}

      {connection.kind === "available" && (
        <div className="content-grid">
          <BackendStatus health={connection.health} />
          <AssessmentCard assessment={connection.assessment} />
        </div>
      )}
    </main>
  );
}
