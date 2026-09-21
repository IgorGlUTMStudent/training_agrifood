STATUS: PROPOSED PRODUCT SPEC — NOT CANON

# APR-02: Product Acceptance & Traceability Matrix

**Original workstream owner:** Alisa — Product Owner
**Execution takeover:** Vladimir — Integrator
**Reason:** final training timebox / Product Owner unavailable
**Workstream:** APR-02 Product MVP Scope & Acceptance
**Repository:** `Slave-of-Skynet/training_agrifood`
**Original APR-02 branch:** `alisa/apr-02-mvp-scope`
**APR-02F reconciliation branch:** `vladimir/apr-02-human-gate-reconciliation`
**Original APR-02F contract base:** `204c3ac37fb2098bfe6c0908a66c54065cda23ae`
**Refreshed APR-02F base:** `cea6ece1d100434772b79b9eb42c8d7bd8488466` (Base Refresh Addendum; PR #22 / PR #28)
**Original APR02_BASE:** `6d0e4a50c36937f01b769a16a99bfa03af458c66`
**Target File:** `docs/product_recon/09_product_acceptance_traceability.md`
**Status:** PROPOSED PRODUCT SPEC — NOT CANON (APR-02 takeover synthesis / PROPOSED PRODUCT SPEC — requires Human Gate)

---

# ВХОДНОЙ КОНТЕКСТ

Полный контекст задачи (recon, решения ADR, snapshot реализации, gap map, 
proposed scope) см. в документах:
- `docs/product_recon/01_context_inventory.md` — `07_adversarial_review.md` (APR-01 recon)
- `docs/product_recon/08_mvp_scope_decision_packet.md` (APR-02 proposed scope)

Текущий документ содержит ТОЛЬКО acceptance & traceability матрицу (§10-§14).

---

# СТРУКТУРА СПЕЦИФИКАЦИИ ПРИЕМКИ (§10–§14 КОНТРАКТА APR-02)

## 10. MASTER TRACEABILITY MATRIX (§10)

Ниже представлена главная матрица сквозной трассируемости и критериев приёмки (Product Acceptance Traceability Matrix). Каждая строка строго связывает исходное требование спонсора или пользователя, принятые нормативные решения (ADR), фактическое состояние кода, предлагаемый функционал MVP и исчерпывающие **позитивные и негативные критерии приёмки**.

**Persona boundary (APR2-D1):** FACT: sponsor brief specifies only «farmer or storage operator». RECOMMENDATION: primary MVP design persona — **dispatch-side storage operator**; `Dispatch Supervisor` — SoS design label, не sponsor job title. Реальные hold/release полномочия, отмена отгрузки, смена перевозчика/ТС, mandatory QC, подписание CMR и inspection procedure / SOP — UNKNOWN. Advisory Decision Support; compound ramp title не канонизируется.

**Reading this matrix:** DECISION обозначает принятые ADR; OBSERVED RESULT — конкретные offline результаты; INFERENCE — ограниченный вывод; RECOMMENDATION — предложенный scope; UNKNOWN — открытые вопросы. Все APR2-D1–D6 остаются proposed / requires Human Gate. В колонке Implementation evidence needed различаются существующие ingestion code/tests и будущие analytics/UI проверки; наличие теста не означает его запуск в APR-02F. IGR-03 canonical ingestion реализован; assessment API по-прежнему возвращает synthetic fixture, без baseline engine или ranked queue.

| ID | Challenge / User Outcome | Source | Product behaviour | Status | Positive acceptance | Negative acceptance | Implementation evidence needed | Owner / dependency | Demo-safe claim |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PA-01** | **Outcome 1:** Which batches are most at risk? / Dataset-backed replay prioritisation | ADR 0002; ADR 0003 D1/D3; VDR-01/02; APR2-D2 | Proposed membership: `assessment_timestamp = storage_sessions.dispatch_datetime` in a configurable replay/view window. `facility_id` — UI/context filter only. | `ACCEPTED PRODUCT SEMANTICS` (clock/order) / `PROPOSED MVP SCOPE` (membership/UI) | Assessed batches одной пары `engine_tier + engine_version`: `risk.score DESC, batch_id ASC`. ID tie-break не означает разницу риска. `planned_dispatch_datetime` — plan/schedule context, условно допустимый по ADR 0002, не часы оценки. Duration/capacity UNKNOWN; pagination/scrolling — implementation detail. | Не ранжировать `insufficient_data`, не заменять null нулем, не смешивать движки, не вводить K=10 capacity. Не использовать вымышленные WMS statuses. QC offset в 2 часа — dataset observation, не warehouse operating window. Replay не доказывает live workflow. | Будущие проверки canonical-clock membership, context-only facility filter, same-engine sorting/ties, изоляции unscored batches и UI replay controls. | Backend / Frontend / Integrator Gate APR2-D2 | «The accepted rule ranks comparable assessed batches; the proposed demo selects recorded dispatch assessments in a configurable replay window. The queue is not implemented.» |
| **PA-02** | **Outcome 1:** Which batches are most at risk? / Risk assessment severity | ADR 0003 (D1, D2) | Monotonic loss severity score computed as $\text{score} = \text{clip}(\text{predicted\_loss\_fraction\_pct}, 0, 100) / 100$. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в схеме) | Поле `risk.score` является непрерывным числом с плавающей точкой в диапазоне $[0.0, 1.0]$, монотонно отражающим относительную тяжесть прогнозируемых потерь продукции. | 1. `risk.score` **СТРОГО НЕ** называется, не маркируется и не представляется оператору как «вероятность порчи» (probability of spoilage, e.g. «80% вероятность гниения»).<br>2. `risk.score` **СТРОГО НЕ** называется «уверенностью модели» (confidence) или «точностью».<br>3. `risk.score` **СТРОГО НЕ** конвертируется в бинарный вердикт pass/fail без валидированного операционного регламента. | Pydantic-валидатор `confloat(ge=0.0, le=1.0)` в `Risk`; UI-тест отсутствия символа `%` рядом со скором; проверка документации API и интерфейсных текстов. | Frontend (Denis) / Product Owner / Contract | «The accepted risk-score definition represents predicted relative loss severity on a 0.0 to 1.0 scale, not probability. The current fixture has no score.» |
| **PA-03** | **Outcome 1:** Which batches are most at risk? / Risk categorisation | ADR 0003 (D2); PUX-08 | Normative policy: `risk.band = null`. No arbitrary traffic-light categorization. | `ACCEPTED PRODUCT SEMANTICS` / `DEFERRED / OUT OF MVP` | Поле `risk.band` в ответе API и контракте строго равно `null` (или отсутствует). Интерфейс отображает непрерывный числовой скор без цветовых категорий до появления утверждённого регламента. | 1. **СТРОГО ЗАПРЕЩЕНЫ** любые светофорные диапазоны риска (traffic-light bands: `red`, `yellow`, `green`, `high`, `moderate`, `low`) без отдельной валидированной политики порогов, утверждённой Human Gate.<br>2. Исследовательский порог бенчмарка ($\ge 15\%$ потерь из VDR-04A) **СТРОГО НЕ** хардкодится как операционный порог отсечения или аварийный алерт. | Тест схемы API, подтверждающий `risk.band is None`; UI-аудит компонентов, гарантирующий отсутствие цветовой классификации скора по ad-hoc порогам. | Backend (IGR) / Frontend (Denis) / Integrator Gate | «Risk bands are deferred. The accepted policy uses an unbanded severity score for assessed batches; the current fixture has risk = null.» |
| **PA-04** | **Outcome 2:** When may quality begin to deteriorate? / Deterioration timing | ADR 0003 (D6); VDR-03; APR-01 Step 4 | Normative policy: `deterioration_horizon = null` with truthful unavailable message. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `DEFERRED / OUT OF MVP` (для расчета) | Поле `deterioration_horizon` равно `null`. Пользовательский интерфейс и API прозрачно и честно информируют оператора сообщением: *«not estimable from supplied observations»*. Допускается безопасный показ планового времени рейса (`planned_duration_hours`) как логистического контекста. | 1. **СТРОГО ЗАПРЕЩЕНЫ** любые таймеры обратного отсчета (countdown timers, e.g. «до порчи осталось 36 часов»).<br>2. **СТРОГО ЗАПРЕЩЕНЫ** сфабрикованные временные интервалы или синтетические даты/метки времени (поле `starts_at` **НЕ** заполняется фиктивными данными).<br>3. **СТРОГО ЗАПРЕЩЕНО** утверждать, что система вычисляет биологический срок годности. | Тест бэкенда на `deterioration_horizon is None`; UI-тест удаления неактивной ветки рендеринга `starts_at` в `AssessmentCard.tsx`; аудит текстов интерфейса. | Frontend (Denis) / Backend (IGR) | «Biological deterioration onset timing cannot be estimated from discrete checkpoint data; deterioration horizon is explicitly reported as null.» |
| **PA-05** | **Outcome 1–4:** Decision confidence / System reliability | ADR 0003 (D7); PUX-08 | Normative policy: `reliability.level = unavailable`, `confidence_score = null`. Factual limitation reporting. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `DEFERRED / OUT OF MVP` (для калибровки) | Контейнер `Reliability` возвращает `level: "unavailable"` и `confidence_score: None`. Ограничения качества и полноты данных транслируются исключительно через стандартизированные коды `reason_codes` и список `missing_requirements`. | 1. **СТРОГО ЗАПРЕЩЕНЫ** вымышленные проценты надежности/уверенности (invented confidence percentages, e.g. «95% надежность», «точность модели 88%»).<br>2. **СТРОГО ЗАПРЕЩЕНЫ** некалиброванные качественные плашки уверенности (`low`, `medium`, `high`).<br>3. Офлайн-метрики бенчмарка (VDR-04A Precision@10) **СТРОГО НЕ** переносятся в рантайм в качестве показателей надежности оценки. | Тест схемы ответа `reliability.confidence_score is None`; UI-тест отсутствия процентов уверенности на карточке партии. | Backend (IGR) / Frontend (Denis) | «Reliability confidence scores are unavailable pending statistical calibration; data limitations are communicated via factual reason codes.» |
| **PA-06** | **Outcome 3:** What factors contribute to the risk? / Partial support only | ADR 0003 D5/D8; APR2-D4 | Proposed baseline `factors = []`; separate «How this score is computed» and «Batch Context»; model attribution deferred. | `ACCEPTED PRODUCT SEMANTICS` (baseline/D8 allowance) / `PROPOSED MVP SCOPE` (separation) / attribution `NOT SUPPORTED` | Объяснить training median loss по crop, global training-median fallback для unseen crop и clipping / 100 без probability. Batch Context отдельно: crop, variety, storage duration, planned logistics, observed conditions; метка «Context only; contribution to this score has not been established.» | Не представлять context как causes/drivers/contributing risk factors/model contributions, даже с `effect = unknown`. `increases_risk` / `decreases_risk` запрещены до отдельно валидированного attribution mechanism; SHAP сам по себе не достаточен. Не объявлять Outcome 3 полностью выполненным. | Будущие проверки baseline `factors == []`, корректного объяснения расчета и визуального отделения контекста. Сейчас fixture содержит только synthetic `data_quality` factor, не baseline attribution. | Backend / Frontend / Integrator Gate APR2-D4 | «The proposed baseline has an explainable score mechanism and separate Batch Context; feature/model attribution remains unsupported.» |
| **PA-07** | **Outcome 4:** What action should be prioritised? / Action guidance | Sponsor brief; ADR 0003 D9; APR2-D5 | `recommendation = null`; proposed neutral unavailable block without operational instruction. | Outcome 4: **NOT SUPPORTED BY CURRENT EVIDENCE** / null implemented in fixture / UI copy proposed | Сохранять null. Proposed copy: «Action recommendations are unavailable. Current evidence does not validate intervention effectiveness. Smart Harvest prioritizes batches for review but does not prescribe an operational action.» Ranking в этой фразе — предложенная возможность, не текущий runtime. | Не закрывать Outcome 4 через null или ranking. Не ссылаться на якобы известный SOP, не назначать и не перечислять примерные действия, не обещать economic savings; не выставлять `requires_human_review = false`. | Будущие проверки `recommendation is None`, нейтрального текста и отсутствия action controls / claims. Action catalogue и intervention effectiveness требуют отдельного evidence gate. | Backend / Frontend / Integrator Gate APR2-D5 | «Action recommendations are unavailable; Outcome 4 is not supported by current evidence. Ranking is not an intervention recommendation.» |
| **PA-08** | **Robustness & Data Integrity:** Handling incomplete data | ADR 0002; ADR 0003 (D7) | `status = "insufficient_data"` when the selected engine cannot satisfy its declared minimum assessment inputs; `risk = null`, `deterioration_horizon = null`. Factual `missing_requirements` and `reason_codes` are reported; exact engine minimums and mapping-error handling in a future assessment service remain implementation-contract questions. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `PROPOSED MVP SCOPE` (нейтральная секция) / `BLOCKED / UNKNOWN` (операционная обработка) | Статус `status = "insufficient_data"` возникает, когда выбранный движок не может удовлетворить свои заявленные минимальные входные требования для оценки; `risk` и `deterioration_horizon` остаются `null`. Недостающие требования и причины фиксируются фактологически в `missing_requirements` и `reason_codes`. Предлагается отдельная нейтральная секция «Not assessed / Incomplete data», вне numeric ranking; статус не означает низкий или высокий риск и не определяет operational disposition. IGR-03 mapper уже отклоняет malformed input / schema-invalid data через ошибки валидации; это не `RiskAssessment` со статусом `insufficient_data`. Точные engine minimums и их обработка в будущем assessment service остаются вопросом контракта реализации. | 1. Статус `insufficient_data` **СТРОГО НЕ** превращается в `score = 0` или `0.0` и не интерпретируется системой как «безопасная партия».<br>2. `insufficient_data` **СТРОГО НЕ** назначает QC, автоматический пропуск или блокировку; система не определяет следующее операционное действие.<br>3. **СТРОГО ЗАПРЕЩЕНО** придумывать вымышленный обязательный процесс ручного контроля качества (invented mandatory QC workflow) или автоматически перенаправлять партию на лабораторный анализ. | Тесты бэкенда на возврат `insufficient_data` при невозможности движка удовлетворить минимальные требования оценки; тесты фронтенда на раздельное отображение неоцененных партий; аудит текстов ошибок. | Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D3) | «No predictive score is available for this batch because required inputs were not satisfied. This does not mean low or high risk. Smart Harvest does not determine the operational disposition of this batch.» |
| **PA-09** | **Predictive Validity:** Temporal input integrity | ADR 0002; VDR-01/02; IGR-03 / PR #28 | Implemented raw-snapshot → typed `BatchAssessmentInput`; `assessment_timestamp == storage_sessions.dispatch_datetime`. | `ACCEPTED INPUT SEMANTICS` / **CURRENT IMPLEMENTED INGESTION CAPABILITY**; analytics/runtime assessment не реализован | Mapper выполняет batch/session/zone/facility joins и typed parsing; допускает harvest/pre-dispatch QC, telemetry только `entry_datetime <= timestamp <= dispatch_datetime`, planned logistics из плановых полей без actual transit realizations. | Arrival QC, historical outcomes, actual transit и post-dispatch telemetry не входят в canonical input. Не выдавать implemented ingestion за end-to-end production assessment или scoring. | Existing code: `backend/app/domain/batch.py`, `backend/app/ingestion/canonical_mapper.py`; existing tests: `backend/tests/test_ingestion_canonical.py` — clock, joins, stage/interval bounds, forbidden-field absence, leakage invariance. APR-02F не заявляет их запуск; будущая analytics integration потребует своих проверок. | Ingestion / Integration; analytics — future bounded work | «IGR-03 implements dispatch-safe canonical input mapping. Production scoring and assessment output remain unimplemented.» |
| **PA-10** | **Auditability & Provenance:** Truth in advertising & simulation marking | ADR 0001; ADR 0003 (D3); Canonical Schema | Synthetic fixtures and demo data explicitly marked with `simulation: true` and notice. Real engines declare exact tier and version. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `IMPLEMENTATION REQUIRED` (в рантайме) | Каждый ответ системы содержит полный объект `Provenance`. Демонстрационные фикстуры содержат `simulation: true`, `engine_tier: "fixture"` и явный текст уведомления: *«SIMULATION / synthetic fixture / not challenge data»*. В UI отображается водяной знак или баннер симуляции. | 1. Синтетические фикстуры **СТРОГО НЕ** выдаются за реальные предсказания модели машинного обучения.<br>2. Результаты офлайн-исследований (VDR-04A) **СТРОГО НЕ** представляются как показатели работы живой системы.<br>3. Движки разных уровней (baseline vs learned) **СТРОГО НЕ** маскируются друг под друга. | Тест схемы API на наличие `provenance.simulation == True` для демо-выдачи; UI-тест баннера симуляции в `AssessmentCard.tsx`. | Backend (IGR) / Frontend (Denis) / Product Owner | «Demo fixtures are transparently marked as simulations with full engine provenance and version tracking.» |
| **PA-11** | **Data Integrity:** Telemetry channel omissions | ADR 0002; ADR 0003 D10; IGR-03 / PR #28 | Canonical mapper preserves structural missing telemetry as `None` / serialized `null`. | `ACCEPTED INPUT SEMANTICS` / **CURRENT IMPLEMENTED INGESTION CAPABILITY** | Non-CA `co2_ppm` / `o2_pct` и ZONE-006 `produce_surface_temperature_c` сохраняются как `None`, без искусственных нулей или средних. | Не фабриковать значения. Наличие ingestion missingness policy не доказывает engine-specific sufficiency; необязательный отсутствующий канал сам по себе не означает `insufficient_data`. | Existing `canonical_mapper.py` и `backend/tests/test_ingestion_canonical.py`: `test_telemetry_structural_missingness_preserved`, `test_no_silent_imputation_of_empty_channels`. APR-02F инспектирует их, не заявляет запуск; engine sufficiency tests остаются будущей работой. | Ingestion / Data; engine minimums — future contract | «IGR-03 preserves structural sensor gaps as None in canonical inputs; this does not establish analytics or engine sufficiency.» |
| **PA-12** | **Evaluation vs Production:** Separation of research metrics from operational guarantees | ADR 0003 (D1, D5); VDR-04A | Offline evaluation metrics remain strictly in model cards and research artifacts. | `ACCEPTED PRODUCT SEMANTICS` | Метрики документируются только с точным протоколом, model/feature family и offline benchmark context. VDR-04A P1 HGB F3 (Context + Telemetry + Planned logistics) не является runtime или crop-median baseline; acceptance модели остается отдельным решением. | 1. Исследовательские метрики бенчмарка **СТРОГО НЕ** хардкодятся в пользовательском интерфейсе в качестве операционных гарантий точности для конкретной смены.<br>2. Результаты протокола P3 (случайный сплит) **СТРОГО НЕ** используются как подтверждение качества модели. | Аудит интерфейса и текстов документации; проверка разделения аналитических артефактов и рантайм-кода. | Product Owner / Integrator (VLD) / Evaluation | «Offline benchmark results describe tested candidates under named protocols; they neither select an engine nor establish runtime performance of the MVP baseline.» |
| **PA-13** | **Predictive Input Integrity:** Telemetry role & VDR-04B boundary | ADR 0002; ADR 0003 D5/D10; VDR-04B report/results JSON; APR2-D6 | Telemetry remains canonical input, now typed and mapped by IGR-03; this does not validate predictive utility. C+L is a candidate feature-family simplification for a future learned-engine decision. | `DECISION` (input/baseline) / `OBSERVED RESULT` (research) / `RECOMMENDATION` (narrative, requires Human Gate) | C = pre-dispatch context, T = aggregate telemetry, L = planned logistics. Для tested Ridge/HGB telemetry не дает стабильного marginal lift; некоторые P1 ranking metrics лучше с C+T+L, P2 robustness обычно за C+L. Принятое MVP engine direction — deterministic crop-median baseline, еще не runtime. VDR-04B — committed research evidence used by this proposed Human Gate package; **DRAFT FOR REVIEW — EVIDENCE ONLY**, acceptance остается Human Integrator decision. | Не выбирать C+L как current MVP architecture, production model, approved learned engine или final feature set. Не объявлять telemetry бесполезной или удалять ее; не заявлять stable/general predictive superiority. Monitoring/audit/diagnostics/equipment-health utility UNKNOWN, не валидирована VDR-04B и не реализована. Не повышать research до canon. | Проверка сохранения canonical telemetry schema; аудит narrative, точных protocol/model labels и отделения research evidence от runtime, canon и будущего learned-engine gate. | Data / Product / Integrator Gate APR2-D6 | «Tested telemetry aggregates showed no stable marginal improvement over planned-logistics-enabled features; P1/P2 differ. C+L is only a future learned-engine candidate, while telemetry remains canonical.» |

---

## 11. RIGOROUS NEGATIVE ACCEPTANCE CRITERIA (§11)

В соответствии с требованиями контракта APR-02 (§11), формулируются 12 критических негативных критериев приёмки. Нарушение любого из них является **блокирующим дефектом** приемочного тестирования:

1. **NEG-01 (Score Fabrication on Incomplete Data):**  
   Партия со статусом `insufficient_data` ни при каких обстоятельствах не должна получать числовой скор (`score = 0`, `score = 0.0` или любое иное значение). В интерфейсе и API поля `risk` и `deterioration_horizon` обязаны быть строго `null`. Не трактовать отсутствие оценки как высокий/низкий риск; показывать отдельно «Not assessed / Incomplete data» с причинами, без SOP или operational disposition.
2. **NEG-02 (Unvalidated Engine Mixing):**  
   Партии, оценённые разными движками (например, `engine_tier = "baseline"` и `engine_tier = "learned"`), либо разными версиями одного движка, ни при каких обстоятельствах не должны автоматически объединяться в единую ранжированную очередь без валидированного доказательства сопоставимости шкал.
3. **NEG-03 (Arbitrary Operational Quota):**  
   Число $K=10$ ни при каких обстоятельствах не должно интерпретироваться как операционная пропускная способность смены, обязательная квота физического досмотра или лимит отображения партий в системе. Нельзя выводить warehouse window из QC offset в 2 часа, использовать отсутствующие readiness statuses или заменять `storage_sessions.dispatch_datetime` на плановую дату; live membership остается UNKNOWN.
4. **NEG-04 (Misleading Score Semantics):**  
   Скор риска (`risk.score`) ни при каких обстоятельствах не должен называться, подписываться или описываться как «вероятность порчи» (probability), «процент риска», «точность модели» или «уверенность» (confidence).
5. **NEG-05 (Uncalibrated Risk Bands):**  
   Ни при каких обстоятельствах в интерфейс не должны выводиться светофорные цветовые плашки (`red`, `yellow`, `green`) или категории (`high`, `moderate`, `low`), пока не будет утверждена калиброванная операционная политика порогов, согласованная с регламентом бизнеса.
6. **NEG-06 (Fabricated Deterioration Countdown):**  
   Ни при каких обстоятельствах в интерфейсе не должен отображаться таймер обратного отсчета до порчи (countdown), синтетическая дата наступления некондиции или расчетный интервал часов/дней до деградации.
7. **NEG-07 (Invented Confidence Percentages):**  
   Ни при каких обстоятельствах система не должна генерировать или отображать вымышленные проценты надежности (например, «надежность оценки 95%») или некалиброванные уровни low/med/high.
8. **NEG-08 (Unsubstantiated Causal Drivers):**  
   Ни при каких обстоятельствах в факторах риска (`factors`) не должны выводиться утверждения о причинно-следственной связи или направления влияния (`increases_risk` / `decreases_risk`) без отдельно валидированного алгоритма атрибуции (XAI). Для предложенного baseline `factors = []`; механизм расчета и Batch Context разделены, контекст не является вкладом в скор. SHAP сам по себе не достаточен; Outcome 3 не закрыт полностью.
9. **NEG-09 (Prescriptive Interventions & Savings Claims):**  
   Ни при каких обстоятельствах система не должна выдавать директивные команды на физические действия («доохладить», «утилизировать»), совершать автоматические действия без участия человека (`requires_human_review = false`) или заявлять о суммах предотвращенного ущерба («спасет €1 200»). Outcome 4 остается NOT SUPPORTED BY CURRENT EVIDENCE; null, unavailable copy и ranking не выполняют требование рекомендаций.
10. **NEG-10 (Future Information Leakage):**  
    Ни при каких обстоятельствах в модель оценки на инференсе не должны проникать замеры качества при прибытии (`stage = "arrival"`), фактические параметры транспортировки (задержки, аварии, температура рейса) или исторические метки списания.
11. **NEG-11 (Masked Synthetic Data):**  
    Ни при каких обстоятельствах синтетическая фикстура или демонстрационные данные не должны выдаваться за результаты работы реальной прогнозной модели машинного обучения.
12. **NEG-12 (Unsubstantiated Telemetry Utility & Arbitrary Omission):**
    Запрещено заявлять стабильное или общее превосходство telemetry по tested benchmarks, ее общую бесполезность, разрешение удалить canonical telemetry или доказанность monitoring/audit/diagnostics. Нельзя называть C+L текущей MVP architecture или approved engine. Некоторые P1 ranking metrics лучше с C+T+L, P2 robustness обычно за C+L; честное указание этой разницы допустимо. VDR-04B остается DRAFT FOR REVIEW — EVIDENCE ONLY, не canon.

---

## 12. FOUR CHALLENGE OUTCOMES TRACEABILITY MATRIX (§12)

Компактная матрица адресации четырех исходных требований спонсора (Challenge Outcomes) в продуктовой архитектуре:

| Challenge outcome | Accepted semantic support | Current implementation | Proposed MVP support | Current limitation | Demo-safe wording |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Outcome 1 — Which batches are most at risk?** | DECISION: ADR 0003 D1/D2/D3; score и same-engine order. | Только synthetic fixture; `analytics: not_configured`; baseline и queue отсутствуют. | RECOMMENDATION: baseline-crop-median-v1 и configurable replay/view window по `assessment_timestamp = storage_sessions.dispatch_datetime`, `facility_id` context filter. | Duration/capacity/live membership UNKNOWN; cross-engine comparability не валидирована. | «Comparable assessed batches are proposed to be ranked by the accepted rule; the current demo only demonstrates the contract.» |
| **Outcome 2 — When may quality begin to deteriorate?** | `ACCEPTED PRODUCT SEMANTICS`<br>(ADR 0003 D6: `deterioration_horizon = null` с честным дисклеймером *«not estimable from supplied observations»*). | `CURRENT IMPLEMENTED CAPABILITY`<br>(Поле `null` в фикстуре; в `AssessmentCard.tsx` есть неактивная ветка даты, подлежащая удалению). | `PROPOSED MVP SCOPE`<br>(Явное текстовое информирование о невозможности оценки времени онсета; отображение `planned_duration_hours` как отдельного логистического контекста рейса). | Биологический момент наступления деградации математически невозможно восстановить по трем дискретным чекпоинтам качества; биодеградационная модель отсутствует. | «Biological deterioration onset is not estimable from supplied observation data; the fixture reports a null horizon; displaying planned transit duration separately as logistical context remains proposed.» |
| **Outcome 3 — What factors contribute to the risk?** | DECISION: ADR 0003 D5/D8; empty factors допустимы; D8 allowance context не доказывает contribution. | Только synthetic `data_quality` factor с `effect: unknown`; baseline отсутствует. | RECOMMENDATION: baseline `factors = []`; «How this score is computed» и отдельный «Batch Context». | Механизм объясним, контекст можно показать; feature/model attribution для baseline unsupported. Outcome 3 не выполнен полностью. | «The proposed baseline score mechanism is explainable; Batch Context is not evidence of contribution to that score.» |
| **Outcome 4 — What action should be prioritised?** | DECISION: ADR 0003 D9, `recommendation = null`. | `recommendation: None` в fixture. | RECOMMENDATION: нейтральное unavailable message без инструкции. **NOT SUPPORTED BY CURRENT EVIDENCE**. | Нет validated action catalogue и intervention effectiveness; ranking не является рекомендацией действия. | «Action recommendations are unavailable. The null policy does not fulfil Outcome 4.» |

---

## 13. CURRENT IMPLEMENTATION GAP MAP (§13)

Карта текущих разрывов между нормативными решениями и работающим кодом фиксирует зависимости для будущих воркстримов.  
*Примечание:* Данная карта **НЕ назначает задачи исполнителям**, а исключительно документирует архитектурные и технические зависимости (Dependencies).

```
[ACCEPTED PRODUCT SEMANTIC] ───► [CURRENT CODE] ───► [GAP] ───► [REQUIRED FUTURE OWNER]
```

1. **Operational Ranking Queue:**
   - *Accepted Product Semantic:* ADR 0003 (D1, D3) — приоритизация оценённых партий по правилу `risk.score DESC, batch_id ASC` строго внутри одного `engine_tier + engine_version`.
   - *Current Code:* В `backend/app/api/routes.py` есть только эндпоинт одиночной фикстуры `GET /demo/assessment`. Во фронтенде `HomePage.tsx` и `AssessmentCard.tsx` рендерят одну карточку.
   - *Gap:* Отсутствует бэкенд-эндпоинт для запроса списка партий с параметрами сортировки и фильтрации по окну/объекту; во фронтенде отсутствует компонент таблицы очереди (Triage Queue). Membership по canonical recorded assessment timestamp и configurable replay/view window — RECOMMENDATION APR2-D2, не принятое live workflow.
   - *Required Future Owner:* Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D2).

2. **Deterministic Baseline Engine:**
   - *Accepted Product Semantic:* ADR 0003 (D5) — расчет скора по обучающей медиане потерь для культуры (с глобальным фоллбэком) как эксплуатационный бейслайн `baseline-crop-median-v1`.
   - *Current Code:* Директория `backend/app/analytics/` содержит только пустой `__init__.py`. Эндпоинт `/health` возвращает `"analytics": "not_configured"`.
   - *Gap:* Логика загрузки исторических медиан и вычисления бейслайн-скора не реализована в сервисах бэкенда.
   - *Required Future Owner:* Backend (IGR) / Analytics / Integration (VLD).

3. **Point-of-Dispatch Ingestion Pipeline:**
   - *Accepted Product Semantic:* ADR 0002 — канонический инпут `BatchAssessmentInput` на момент $T_{dispatch}$, строгое отсечение прибытия и транзитных данных, трансляция структурных пропусков как `null`.
   - *Current Code:* IGR-03 / PR #28 реализует typed `BatchAssessmentInput` в `backend/app/domain/batch.py` и deterministic raw-snapshot mapper в `backend/app/ingestion/canonical_mapper.py`, включая joins, typed parsing, dispatch clock, QC/telemetry boundaries, planned logistics и сохранение structural `None`.
   - *Implemented Evidence:* `backend/tests/test_ingestion_canonical.py` содержит temporal/leakage-invariance и structural-missingness проверки; их наличие не является заявлением о запуске тестов APR-02F.
   - *Remaining Gap:* Canonical ingestion реализован; подключение к будущему scoring runtime и production `RiskAssessment` service отсутствует. Mapper не выполняет analytics, ranking или recommendation generation.
   - *Required Future Owner:* Ingestion (IGR) / Integration (VLD).

4. **Handling of `insufficient_data` in UI:**
   - *Accepted Product Semantic:* ADR 0003 (D7) — статус `insufficient_data`, отсутствие скора и горизонта, информирование через `reason_codes` и `missing_requirements`.
   - *Current Code:* Статичная плашка в единственной демо-карточке `AssessmentCard.tsx`.
   - *Gap:* В интерфейсе нет механизма разделения очереди на оценённые партии и партии с неполными данными (вкладка/секция); нет динамического рендеринга списка недостающих требований. Предлагается «Not assessed / Incomplete data»; операционная обработка UNKNOWN, не определяется APR2-D3.
   - *Required Future Owner:* Frontend (Denis) / Integrator Gate (APR2-D3).

5. **Score Method & Separate Batch Context:**
   - *Accepted Product Semantic:* ADR 0003 D5/D8 — crop-median baseline; `factors = []` разрешены. Разрешение factual context с `effect = unknown` не доказывает contribution к baseline score.
   - *Current Code:* Единственный synthetic data-quality factor в fixture; baseline не реализован.
   - *Proposed Gap:* Baseline `factors = []`; отдельно объяснение training crop median / unseen-crop global training median / clipping и Batch Context с меткой об отсутствии установленного вклада. Не упаковывать context как baseline risk factors.
   - *Required Future Owner:* Backend / Frontend / Integrator Gate APR2-D4; Outcome 3 остается частично поддержанным.

6. **Model Attribution Explainability (XAI):**
   - *Accepted Product Semantic:* ADR 0003 (D8) — направления `increases_risk` / `decreases_risk` допустимы строго при наличии валидированного алгоритма атрибуции.
   - *Current Code:* Полностью отсутствует.
   - *Gap:* Метод XAI и референтный базис не выбраны и не валидированы; добавление SHAP само по себе не решает explainability.
   - *Required Future Owner:* Data / Analytics (Viktor) / Integration (VLD) — *DEFERRED*.

7. **Action Catalogue & Recommendation System:**
   - *Accepted Product Semantic:* ADR 0003 (D9) — сохранение `recommendation = null` до появления контрфактических доказательств и утверждения каталога действий.
   - *Current Code:* Поле `recommendation: None` в фикстуре.
   - *Gap:* В предметной области и датасете отсутствуют данные о результатах вмешательств; каталог действий не утвержден спонсором. Outcome 4 — NOT SUPPORTED BY CURRENT EVIDENCE.
   - *Required Future Owner:* Challenge Sponsor / Domain / Integrator Gate (APR2-D5) — *DEFERRED*.

8. **Calibrated Reliability & Operational Bands:**
   - *Accepted Product Semantic:* ADR 0003 (D2, D7) — `risk.band = null`, `confidence_score = null`, `reliability.level = unavailable`.
   - *Current Code:* Соответствует принятому решению (поля пусты/отсутствуют).
   - *Gap:* Отсутствует статистическая калибровка доверительных интервалов и бизнес-обоснование порогов потерь.
   - *Required Future Owner:* Data (Viktor) / Evaluation / Integrator Gate — *DEFERRED*.

---

## 14. DEMO AND PITCH CLAIM SAFETY (§14)

Для обеспечения строгой академической честности и предотвращения репутационных рисков при публичных демонстрациях и защите проекта (Pitch / Demo) устанавливаются обязательные правила допустимых и категорически запрещённых формулировок.

| SAFE TO SAY (Допустимо заявлять) | MUST NOT SAY (Категорически запрещено заявлять) |
| :--- | :--- |
| 1. «RECOMMENDATION APR2-D1: primary MVP design persona — dispatch-side storage operator; Dispatch Supervisor — SoS design label. Sponsor specifies only farmer or storage operator. Advisory decision support, без установленных реальных полномочий.» | 1. «Система рассчитывает точный час, день или время, когда партия продукции начнет портиться.» *(Биологический онсет не рассчитывается)* |
| 2. «DECISION: `risk.score DESC, batch_id ASC` внутри одной пары `engine_tier + engine_version`; ID tie-break не различает риск. Runtime queue отсутствует; APR2-D2 предлагает canonical dispatch-event replay window.» | 2. «Скор риска 0.82 означает 82%-ю вероятность того, что эта партия сгниет в пути.» *(Скор — монотонная мера потерь, а не вероятность)* |
| 3. «DECISION ADR 0002: оценка ограничена данными на `assessment_timestamp = storage_sessions.dispatch_datetime`, без transit/arrival leakage. FACT: IGR-03 реализует canonical ingestion mapper; scoring, ranking endpoint и production assessment service отсутствуют.» | 3. «Внедрение нашей системы гарантированно снизит потери на 15% или сбережет распределительному центру €50 000 в сезон.» *(Эффект вмешательств не доказан)* |
| 4. «OBSERVED RESULT: offline VDR-04A, P1 forward inter-season (2024 train / 2025 test), HGB F3 (Context + Telemetry + Planned logistics): NDCG@10 = 0.8831, Precision@10 = 1.0, Recall@10 = 0.0333. Это learned benchmark, не runtime performance crop-median baseline, не исчерпывающий скрининг и не гарантия.» | 4. «Наш продакшн-алгоритм работает с точностью 100% в реальном времени или гарантирует выявление всех деградирующих партий.» *(Не путать офлайн-бенчмарк верхнего ранжирования с исчерпывающим скринингом и эксплуатационной гарантией)* |
| 5. «При нехватке ключевых входных данных контракт бэкенда фиксирует статус `insufficient_data` со списком `missing_requirements` (в текущем UI отображается только статус, динамический рендеринг списка требований предложен в MVP).» | 5. «Система предписывает оператору доохладить партию или отменить отправку.» *(Рекомендации строго null, решения принимает только человек)* |
| 6. «Горизонт деградации честно возвращается как `null`, так как имеющиеся контрольные замеры качества не позволяют восстановить момент начала биологической порчи.» | 6. «Продукт успешно внедрен и протестирован на реальных холодильных складах Молдовы.» *(Мы работаем с учебным датасетом)* |
| 7. «FACT: fixture содержит synthetic data_quality factor с effect = unknown. RECOMMENDATION APR2-D4: baseline factors = [], отдельные How this score is computed и Batch Context; attribution unsupported, Outcome 3 не выполнен полностью.» | 7. «Зеленый статус означает абсолютную безопасность партии, а красный — гарантированный брак.» *(Цветовые диапазоны риска не валидированы и запрещены)* |
| 8. «Текущая демонстрация бэкенда и интерфейса использует валидированную синтетическую фикстуру со статусом симуляции для подтверждения надежности сетевого контракта.» | 8. «Партии с неполными данными автоматически отбраковываются и направляются на обязательную лабораторную экспертизу.» *(Вымышленный регламент)* |
| 9. «OBSERVED RESULT VDR-04B: tested telemetry aggregates не дали stable marginal lift; некоторые P1 ranking metrics лучше с C+T+L, P2 robustness обычно за C+L. C+L (context + planned logistics) — candidate feature-family simplification для future learned-engine decision; текущее принятое направление — crop-median baseline. Telemetry canonical. Отчет committed, DRAFT FOR REVIEW — EVIDENCE ONLY; acceptance требует Human Integrator.» | 9. «Телеметрия камер хранения бесполезна и может быть удалена из системы» ИЛИ «В исследовании VDR-04B окончательно выбраны продакшн-модели и зафиксирован финальный набор признаков» ИЛИ «Полезность телеметрии для мониторинга/диагностики доказана VDR-04B или реализована в системе.» |

---

## 15. PUX-08 BOUNDARY & PENDING UX DEPENDENCIES (§15)

В соответствии с контрактом APR-02 подтверждается статус взаимодействия с воркстримом UX:
1. **Статус PUX-08:** FACT: `docs/recon/PUX-08-data-ux-reconciliation.md` интегрирован через PR #22 и сохраняет `DRAFT FOR REVIEW`. DECISION BOUNDARY: repository integration не делает рекомендации accepted product canon; они **NOT CANON / not authoritative by themselves**, требуют Integrator/Human Gate там, где необходимо.
2. **Граница полномочий:** Рекомендации PUX-08 не могут использоваться как принятые продуктовые решения до прохождения гейта Интегратора.
3. **Реестр ожидающих UX-зависимостей:**
   - `UX-DEP-1 (Triage Queue UI):` Разработка таблицы ранжирования с поддержкой правила `risk.score DESC, batch_id ASC` (заблокирована до утверждения `APR2-D2`).
   - `UX-DEP-2 (Insufficient Data Panel):` Проектирование изолированного представления для партий со статусом `insufficient_data` (заблокировано до утверждения `APR2-D3`).
   - `UX-DEP-3 (Card Cleanup):` Очистка `AssessmentCard.tsx` от неактивных полей `risk.band`, `confidence_score` и `starts_at`.
   - `UX-DEP-4 (Score Method, Context & Unavailable Message):` Отдельные «How this score is computed» и «Batch Context», baseline `factors = []`; нейтральный блок `recommendation = null`, не закрывающий Outcome 4 (requires APR2-D4/D5 Human Gate).

---

## 16. EPISTEMIC CLASSIFICATION SUMMARY (§5)

Метки FACT / DECISION / OBSERVED RESULT / INFERENCE / RECOMMENDATION / UNKNOWN отделяют доказательность (см. §10). Ниже — отдельная классификация области и реализации:

- **A. CURRENT IMPLEMENTED CAPABILITY:**  
  IGR-03 typed `BatchAssessmentInput`, deterministic canonical mapper и committed ingestion tests (temporal boundaries / structural missingness / leakage invariance); Pydantic-схемы контракта `RiskAssessment`; эндпоинты `/health` (`analytics: not_configured`) и `/demo/assessment`; синтетическая фикстура `synthetic-batch-001` со статусом `insufficient_data`; одиночная карточка `AssessmentCard.tsx`.
- **B. ACCEPTED PRODUCT SEMANTICS:**  
  ADR 0001 (контрактная архитектура); ADR 0002 (граница $T_{dispatch}$, классификация 73 полей, запрет утечек); ADR 0003 (D1: таргет `loss_fraction_pct`, D2: скор тяжести потерь, `band = null`, D3: ранжирование `score DESC, batch_id ASC` внутри одного движка, D5: медианный бейслайн, D6: `horizon = null`, D7: `reliability = unavailable`, D8: допустимы факты с `effect = unknown` либо пустой список, без доказательства attribution, D9: `recommendation = null`, D10: сохранение телеметрии).
- **C. PROPOSED MVP SCOPE:**  
  RECOMMENDATION: dispatch-side storage operator как SoS design persona; configurable canonical dispatch-event replay queue; реализация `baseline-crop-median-v1`; нейтральная секция unassessed; baseline `factors = []` с отдельными score method и Batch Context; блок недоступности рекомендаций, не закрывающий Outcome 4. APR2-D1–D6 требуют Human Gate. C+L обсуждается только как feature-family candidate для будущего learned-engine decision, не MVP architecture.
- **D. DEFERRED / OUT OF MVP:**  
  Светофорные диапазоны риска (`risk.band`); таймеры деградации и интервалы часов/дней; калиброванные проценты уверенности; направленные факторы XAI (`increases_risk`/`decreases_risk`); каталог корректирующих действий и оценка финансовой экономии; learned ML-модели до проведения приемочного тестирования.
- **E. BLOCKED / UNKNOWN:**  
  Реальные полномочия и SOP; длительность окна/review capacity; будущая live queue membership; приемка design persona; attribution/XAI; action catalogue и intervention effectiveness; production learned engine и final feature subset; cross-engine comparability; telemetry monitoring/audit/diagnostics utility. VDR-04B acceptance как project evidence остается отдельным Human Integrator decision.

---

## 17. FAILURE ACCEPTANCE CHECKLIST & PROHIBITED ACTIONS (§18)

В соответствии с требованиями контракта APR-02 (§18), подтверждается неукоснительное соблюдение всех ограничений:
- [x] **ЗАПРЕЩЕНО** называть foundation fixture работающим аналитическим или предиктивным MVP.
- [x] **ЗАПРЕЩЕНО** называть метрики офлайн-бенчмарка VDR-04A показателями производительности в рантайме.
- [x] **ЗАПРЕЩЕНО** Product Owner'у самостоятельно выбирать или утверждать архитектуру learned-модели.
- [x] **ЗАПРЕЩЕНО** вводить любые новые пороги риска или категориальные диапазоны (`risk.band`).
- [x] **ЗАПРЕЩЕНО** создавать каталог действий или перечень автоматических рекомендаций.
- [x] **ЗАПРЕЩЕНО** устанавливать `recommendation ≠ null` без отдельного гейта валидации действий.
- [x] **ЗАПРЕЩЕНО** проектировать или обещать таймеры обратного отсчета до порчи (countdown).
- [x] **ЗАПРЕЩЕНО** использовать градации надежности low/medium/high или вымышленные проценты уверенности без статистической калибровки.
- [x] **ЗАПРЕЩЕНО** придумывать операционную емкость оператора (квоту K=10 и т.п.).
- [x] **ЗАПРЕЩЕНО** придумывать обязательную автоматическую маршрутизацию партий `insufficient_data` на контроль качества (QC).
- [x] **ЗАПРЕЩЕНО** превращать черновик PUX-08 в нормативное командное решение (DECISION).
- [x] **Граница APR-02F:** Разрешены только этот файл, `08_mvp_scope_decision_packet.md` и status-only repair в `docs/decisions/0003-assessment-evaluation-semantics.md`; принятые ADR-решения и provenance не меняются. Остальной канон, VDR-04B, PUX-08 и application code вне write scope.

---
*Документ подготовлен в рамках APR-02 takeover synthesis (Vladimir — Integrator) из-за таймбокса финала тренировки для передачи на рассмотрение Human Gate.*
*Конец спецификации.*
