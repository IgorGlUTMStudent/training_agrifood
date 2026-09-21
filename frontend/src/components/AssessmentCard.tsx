import type { RiskAssessment } from "../api/contracts";

interface AssessmentCardProps {
  assessment: RiskAssessment;
}

function humanizeReasonCode(code: string): string {
  return code
    .toLowerCase()
    .split("_")
    .map((word, idx) => (idx === 0 ? word.charAt(0).toUpperCase() + word.slice(1) : word))
    .join(" ");
}

export function AssessmentCard({ assessment }: AssessmentCardProps) {
  const isInsufficient = assessment.status === "insufficient_data";
  const { reliability, recommendation, factors } = assessment;

  return (
    <section className="panel assessment-panel" aria-labelledby="assessment-heading">
      <div className="fixture-banner">{assessment.provenance.notice}</div>
      <p className="eyebrow">Contract proof</p>
      <h2 id="assessment-heading">Synthetic assessment</h2>
      <p className="batch-id">Batch: {assessment.batch_id}</p>

      {isInsufficient ? (
        <div className="insufficient-state" role="status">
          <strong>Insufficient data</strong>
          <p>
            No risk score is available because required inputs could not be satisfied.
            This batch cannot be scored and must not be treated as zero risk.
          </p>

          {reliability.reason_codes.length > 0 && (
            <div className="limitation-block">
              <span className="limitation-label">Reason codes:</span>
              <ul className="chip-list" aria-label="Reason codes">
                {reliability.reason_codes.map((code) => (
                  <li key={code} className="chip chip--reason">
                    {humanizeReasonCode(code)}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {reliability.missing_requirements.length > 0 && (
            <div className="limitation-block">
              <span className="limitation-label">Missing requirements:</span>
              <ul className="chip-list" aria-label="Missing requirements">
                {reliability.missing_requirements.map((req) => (
                  <li key={req} className="chip chip--requirement">
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="assessment-values">
          <div className="assessment-metric">
            <span className="metric-label">Predicted loss severity score:</span>
            <span className="metric-value">{assessment.risk?.score}</span>
            <p className="metric-caption">
              Prioritisation score (0.00–1.00). Not a probability or guarantee of loss.
            </p>
          </div>
        </div>
      )}

      <div className="assessment-section">
        <h3>Deterioration timing</h3>
        <p className="status-note">Not estimable from supplied observations</p>
      </div>

      <div className="assessment-section">
        <h3>Recommendation</h3>
        {recommendation ? (
          <div className="recommendation-content">
            <p className="recommendation-label">{recommendation.label}</p>
            {recommendation.requires_human_review && (
              <span className="review-flag">Human review required</span>
            )}
          </div>
        ) : (
          <p className="status-note">No validated recommendation available</p>
        )}
      </div>

      {factors.length > 0 && (
        <div className="factor-list">
          <h3>Structured factors</h3>
          {factors.map((factor) => (
            <article key={factor.code}>
              <div className="factor-header">
                <span className="factor-category">{factor.category.replace("_", " ")}</span>
                <span className="factor-effect">Effect: {factor.effect.replace("_", " ")}</span>
              </div>
              <p>{factor.summary}</p>
            </article>
          ))}
        </div>
      )}

      <div className="reliability">
        Reliability: <strong>{reliability.level}</strong>
      </div>
    </section>
  );
}
