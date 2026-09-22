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
  const isBaseline =
    assessment.status === "assessed" &&
    assessment.provenance.engine_tier === "deterministic_baseline";
  const { reliability, recommendation, factors } = assessment;

  return (
    <section className="panel assessment-panel" aria-labelledby="assessment-heading">
      {assessment.provenance.simulation && (
        <div className="fixture-banner" role="note">
          {assessment.provenance.notice}
        </div>
      )}

      <p className="eyebrow">Batch Review</p>
      <h2 id="assessment-heading">
        {isInsufficient ? "Not assessed / Incomplete data" : "Batch Assessment"}
      </h2>
      <p className="batch-id">Batch: {assessment.batch_id}</p>

      {isInsufficient ? (
        <div className="insufficient-state" role="status">
          <p className="insufficient-notice">
            No predictive score is available for this batch because required inputs were
            not satisfied. This does not mean low or high risk. Smart Harvest does not
            determine the operational disposition of this batch.
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
            <span className="metric-label">Predicted loss severity score</span>
            <span className="metric-value">{assessment.risk?.score}</span>
            <p className="metric-caption">
              Prioritisation score (0.00–1.00). Not a probability or guarantee of loss.
            </p>
          </div>
        </div>
      )}

      {isBaseline && (
        <div className="assessment-section score-computation-section">
          <h3>How this score is computed</h3>
          <p>
            The score is derived from the historical median loss_fraction_pct for this crop in
            the training partition.
          </p>
          <p>For an unseen crop, the global training-partition median is used.</p>
          <p>
            That predicted loss fraction is clipped to [0, 100] and divided by 100.
          </p>
          <p>
            The resulting risk.score is a [0, 1] relative loss-severity score, not a probability,
            confidence score, or guaranteed future loss.
          </p>
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
          <p className="status-note">
            Action recommendations are unavailable. Current evidence does not validate
            intervention effectiveness. Smart Harvest prioritizes batches for review but
            does not prescribe an operational action.
          </p>
        )}
      </div>

      {factors.length > 0 && (
        <div className="assessment-section factor-list">
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

      <div className="assessment-section metadata-section">
        <div className="reliability">
          Reliability: <strong>{reliability.level}</strong>
        </div>
        <dl className="provenance-meta">
          <div>
            <dt>Engine tier</dt>
            <dd>{assessment.provenance.engine_tier.replace("_", " ")}</dd>
          </div>
          <div>
            <dt>Engine version</dt>
            <dd>{assessment.provenance.engine_version}</dd>
          </div>
          <div>
            <dt>Contract version</dt>
            <dd>{assessment.provenance.contract_version}</dd>
          </div>
        </dl>
      </div>
    </section>
  );
}
