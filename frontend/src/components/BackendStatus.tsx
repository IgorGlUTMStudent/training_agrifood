import type { HealthResponse } from "../api/contracts";

interface BackendStatusProps {
  health: HealthResponse;
}

export function BackendStatus({ health }: BackendStatusProps) {
  return (
    <section className="panel status-panel" aria-labelledby="backend-status-heading">
      <div>
        <p className="eyebrow">Backend status</p>
        <h2 id="backend-status-heading">Available</h2>
      </div>
      <span className="status-chip status-chip--available">Connected</span>
      <dl className="metadata">
        <div>
          <dt>Service</dt>
          <dd>{health.service}</dd>
        </div>
        <div>
          <dt>Analytics</dt>
          <dd>{health.analytics.replace("_", " ")}</dd>
        </div>
      </dl>
    </section>
  );
}
