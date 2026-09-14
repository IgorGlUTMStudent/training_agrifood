import type { RiskAssessment } from "../api/contracts";

interface AssessmentCardProps {
  assessment: RiskAssessment;
}

export function AssessmentCard({ assessment }: AssessmentCardProps) {
  const isInsufficient = assessment.status === "insufficient_data";

  return (
    <section className="panel assessment-panel" aria-labelledby="assessment-heading">
      <div className="fixture-banner">{assessment.provenance.notice}</div>
      <p className="eyebrow">Contract proof</p>
      <h2 id="assessment-heading">Synthetic assessment</h2>
      <p className="batch-id">Batch: {assessment.batch_id}</p>

      {isInsufficient ? (
        <div className="insufficient-state">
          <strong>Insufficient data</strong>
          <p>
            No risk percentage or deterioration horizon is shown because validated
            challenge inputs are not available.
          </p>
        </div>
      ) : (
        <div className="assessment-values">
          <p>Risk score: {assessment.risk?.score}</p>
          <p>
            Deterioration window starts: {assessment.deterioration_horizon?.starts_at}
          </p>
        </div>
      )}

      <div className="factor-list">
        <h3>Structured factors</h3>
        {assessment.factors.map((factor) => (
          <article key={factor.code}>
            <span>{factor.category.replace("_", " ")}</span>
            <p>{factor.summary}</p>
          </article>
        ))}
      </div>

      <div className="reliability">
        Reliability: <strong>{assessment.reliability.level}</strong>
      </div>
    </section>
  );
}
