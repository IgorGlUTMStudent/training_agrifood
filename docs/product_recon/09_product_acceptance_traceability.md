STATUS: PROPOSED PRODUCT SPEC — NOT CANON

# APR-02: Product Acceptance & Traceability Matrix

**Original workstream owner:** Alisa — Product Owner
**Execution takeover:** Vladimir — Integrator
**Reason:** final training timebox / Product Owner unavailable
**Workstream:** APR-02 Product MVP Scope & Acceptance
**Repository:** `Slave-of-Skynet/training_agrifood`
**Branch:** `alisa/apr-02-mvp-scope`
**APR02_BASE:** `6d0e4a50c36937f01b769a16a99bfa03af458c66`
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

| ID | Challenge / User Outcome | Source | Product behaviour | Status | Positive acceptance | Negative acceptance | Implementation evidence needed | Owner / dependency | Demo-safe claim |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PA-01** | **Outcome 1:** Which batches are most at risk? / Operational ramp prioritisation | ADR 0003 (D1, D3); VDR-04A; APR-01 Step 6 | Assessed batches of comparable engine version ordered strictly by `risk.score DESC, batch_id ASC`. | `ACCEPTED PRODUCT SEMANTICS` / `PROPOSED MVP SCOPE` | Все оценённые партии внутри одного операционного окна отгрузки, рассчитанные с использованием идентичной пары `engine_tier + engine_version`, отображаются в детерминированном порядке: `risk.score DESC, batch_id ASC`. Равенство скоров детерминированно разрешается алфавитным порядком идентификатора партии (`batch_id ASC`). | 1. `insufficient_data` **СТРОГО НЕ** получает `score = 0` или `0.0` и не сортируется как партия с наименьшим риском.<br>2. Различные тиры или версии движков (например, baseline vs learned ML) **СТРОГО НЕ** смешиваются автоматически в единую очередь ранжирования без доказательства сопоставимости скоров.<br>3. Фиксированное число $K=10$ **СТРОГО НЕ** является операционной квотой или лимитом проверки оператора. | Эндпоинт очереди Triage в бэкенде; модульный тест сортировки с проверкой тай-брейка `batch_id ASC`; UI-компонент таблицы с пагинацией/скроллом; тест изоляции партий с `insufficient_data`. | Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D2) | «Smart Harvest defines a deterministic ranking rule (score DESC, batch_id ASC) to prioritise batches assessed by the same engine version.» |
| **PA-02** | **Outcome 1:** Which batches are most at risk? / Risk assessment severity | ADR 0003 (D1, D2) | Monotonic loss severity score computed as $\text{score} = \text{clip}(\text{predicted\_loss\_fraction\_pct}, 0, 100) / 100$. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в схеме) | Поле `risk.score` является непрерывным числом с плавающей точкой в диапазоне $[0.0, 1.0]$, монотонно отражающим относительную тяжесть прогнозируемых потерь продукции. | 1. `risk.score` **СТРОГО НЕ** называется, не маркируется и не представляется оператору как «вероятность порчи» (probability of spoilage, e.g. «80% вероятность гниения»).<br>2. `risk.score` **СТРОГО НЕ** называется «уверенностью модели» (confidence) или «точностью».<br>3. `risk.score` **СТРОГО НЕ** конвертируется в бинарный вердикт pass/fail без валидированного операционного регламента. | Pydantic-валидатор `confloat(ge=0.0, le=1.0)` в `Risk`; UI-тест отсутствия символа `%` рядом со скором; проверка документации API и интерфейсных текстов. | Frontend (Denis) / Product Owner / Contract | «The risk score represents expected relative loss severity on a 0.0 to 1.0 scale, not probability of batch failure.» |
| **PA-03** | **Outcome 1:** Which batches are most at risk? / Risk categorisation | ADR 0003 (D2); PUX-08 | Normative policy: `risk.band = null`. No arbitrary traffic-light categorization. | `ACCEPTED PRODUCT SEMANTICS` / `DEFERRED / OUT OF MVP` | Поле `risk.band` в ответе API и контракте строго равно `null` (или отсутствует). Интерфейс отображает непрерывный числовой скор без цветовых категорий до появления утверждённого регламента. | 1. **СТРОГО ЗАПРЕЩЕНЫ** любые светофорные диапазоны риска (traffic-light bands: `red`, `yellow`, `green`, `high`, `moderate`, `low`) без отдельной валидированной политики порогов, утверждённой Human Gate.<br>2. Исследовательский порог бенчмарка ($\ge 15\%$ потерь из VDR-04A) **СТРОГО НЕ** хардкодится как операционный порог отсечения или аварийный алерт. | Тест схемы API, подтверждающий `risk.band is None`; UI-аудит компонентов, гарантирующий отсутствие цветовой классификации скора по ad-hoc порогам. | Backend (IGR) / Frontend (Denis) / Integrator Gate | «Risk bands (high/medium/low) are deferred; the system currently outputs the raw monotonic severity score without arbitrary color categories.» |
| **PA-04** | **Outcome 2:** When may quality begin to deteriorate? / Deterioration timing | ADR 0003 (D6); VDR-03; APR-01 Step 4 | Normative policy: `deterioration_horizon = null` with truthful unavailable message. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `DEFERRED / OUT OF MVP` (для расчета) | Поле `deterioration_horizon` равно `null`. Пользовательский интерфейс и API прозрачно и честно информируют оператора сообщением: *«not estimable from supplied observations»*. Допускается безопасный показ планового времени рейса (`planned_duration_hours`) как логистического контекста. | 1. **СТРОГО ЗАПРЕЩЕНЫ** любые таймеры обратного отсчета (countdown timers, e.g. «до порчи осталось 36 часов»).<br>2. **СТРОГО ЗАПРЕЩЕНЫ** сфабрикованные временные интервалы или синтетические даты/метки времени (поле `starts_at` **НЕ** заполняется фиктивными данными).<br>3. **СТРОГО ЗАПРЕЩЕНО** утверждать, что система вычисляет биологический срок годности. | Тест бэкенда на `deterioration_horizon is None`; UI-тест удаления неактивной ветки рендеринга `starts_at` в `AssessmentCard.tsx`; аудит текстов интерфейса. | Frontend (Denis) / Backend (IGR) | «Biological deterioration onset timing cannot be estimated from discrete checkpoint data; deterioration horizon is explicitly reported as null.» |
| **PA-05** | **Outcome 1–4:** Decision confidence / System reliability | ADR 0003 (D7); PUX-08 | Normative policy: `reliability.level = unavailable`, `confidence_score = null`. Factual limitation reporting. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `DEFERRED / OUT OF MVP` (для калибровки) | Контейнер `Reliability` возвращает `level: "unavailable"` и `confidence_score: None`. Ограничения качества и полноты данных транслируются исключительно через стандартизированные коды `reason_codes` и список `missing_requirements`. | 1. **СТРОГО ЗАПРЕЩЕНЫ** вымышленные проценты надежности/уверенности (invented confidence percentages, e.g. «95% надежность», «точность модели 88%»).<br>2. **СТРОГО ЗАПРЕЩЕНЫ** некалиброванные качественные плашки уверенности (`low`, `medium`, `high`).<br>3. Офлайн-метрики бенчмарка (VDR-04A Precision@10) **СТРОГО НЕ** переносятся в рантайм в качестве показателей надежности оценки. | Тест схемы ответа `reliability.confidence_score is None`; UI-тест отсутствия процентов уверенности на карточке партии. | Backend (IGR) / Frontend (Denis) | «Reliability confidence scores are unavailable pending statistical calibration; data limitations are communicated via factual reason codes.» |
| **PA-06** | **Outcome 3:** What factors contribute to the risk? / Explainability | ADR 0003 (D8); APR-01 Step 4 | Empty list `factors = []` accepted; factual context allowed strictly with `effect = "unknown"` and non-causal wording. | `ACCEPTED PRODUCT SEMANTICS` / `PROPOSED MVP SCOPE` (для контекста) / `DEFERRED / OUT OF MVP` (для XAI) | Список факторов может быть пустым (`factors = []`). При заполнении факторы отражают исключительно объективные наблюдаемые параметры партии, хранения и рейса (длительность хранения, культура, плановое время в пути) с обязательным значением `effect = "unknown"`. | 1. **СТРОГО ЗАПРЕЩЕНЫ** вымышленные причинно-следственные связи (fabricated causal drivers, e.g. «высокая температура вызвала 20% потерь»).<br>2. Направления влияния `increases_risk` / `decreases_risk` **СТРОГО ЗАПРЕЩЕНЫ** без валидированного математического алгоритма атрибуции признаков (SHAP/TreeSHAP).<br>3. **СТРОГО ЗАПРЕЩЕНЫ** агрономические утверждения, не подтверждённые литературой для конкретной культуры. | Тест генератора факторов в бэкенде (`effect == "unknown"`); UI-тест нейтрального отображения контекста без формулировок вины/причинности; аудит отсутствия некалиброванных SHAP-весов. | Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D4) | «Assessment factors present observed storage and shipment context with neutral effect; causal attribution requires a validated XAI engine.» |
| **PA-07** | **Outcome 4:** What action should be prioritised? / Action guidance | ADR 0003 (D9); APR-01 Step 5, Step 6 | Normative policy: `recommendation = null`. Standard dispatch clearance is operational SOP, not a model recommendation. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `DEFERRED / OUT OF MVP` (для действий) | Поле `recommendation` строго равно `null`. Пользовательский интерфейс отображает нейтральное информационное сообщение о том, что автоматические интервенции не сконфигурированы, а решение принимается оператором согласно регламенту склада (SOP). | 1. **СТРОГО ЗАПРЕЩЕНЫ** директивные предписания вмешательств (prescriptive interventions, e.g. «срочно доохладить», «перенаправить на местный рынок», «утилизировать»).<br>2. **СТРОГО ЗАПРЕЩЕНЫ** автоматические действия системы или автоматическое изменение маршрутов/заказов.<br>3. **СТРОГО ЗАПРЕЩЕНЫ** утверждения о предотвращенных убытках или финансовой экономии (predicted prevented-loss / savings, e.g. «действие сбережет €1 200»).<br>4. **СТРОГО ЗАПРЕЩЕНО** выставлять `requires_human_review = false`. | Тест схемы `recommendation is None`; UI-аудит отсутствия директивных кнопок действий и счетчиков предотвращенного ущерба; ревизия документации. | Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D5) | «Automated prescriptive recommendations are null; operational decisions remain entirely with the human operator following facility SOPs.» |
| **PA-08** | **Robustness & Data Integrity:** Handling incomplete data | ADR 0002; ADR 0003 (D7) | Incomplete inputs trigger `status = "insufficient_data"`, `risk = null`, `deterioration_horizon = null`, with factual `missing_requirements` and `reason_codes`. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `BLOCKED / UNKNOWN` (для операционного SOP) | Партии с отсутствующими обязательными полями или несоответствием схемы возвращают статус `insufficient_data`, пустой риск и пустой горизонт. Недостающие требования явно перечисляются в массиве `missing_requirements`. | 1. Статус `insufficient_data` **СТРОГО НЕ** превращается в `score = 0.0` и не интерпретируется системой как «безопасная партия».<br>2. `insufficient_data` **СТРОГО НЕ** вызывает автоматическое отклонение партии (auto-reject) или блокировку отгрузки без участия человека.<br>3. **СТРОГО ЗАПРЕЩЕНО** придумывать вымышленный обязательный процесс ручного контроля качества (invented mandatory QC workflow) или автоматически перенаправлять партию на лабораторный анализ. | Тесты валидатора входных данных в пайплайне инжестии; тесты фронтенда на раздельное отображение неоцененных партий; аудит текстов ошибок. | Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D3) | «Batches with incomplete data are explicitly flagged as insufficient_data without fabricating risk scores or forcing automated rejections.» |
| **PA-09** | **Predictive Validity:** Temporal leakage prevention | ADR 0002; VDR-01; VDR-02 | Strictly dispatch-safe inputs ($t \le T_{dispatch}$). Total exclusion of transit telemetry and destination outcomes. | `ACCEPTED PRODUCT SEMANTICS` / `IMPLEMENTATION REQUIRED` | Любой аналитический или предиктивный расчет использует строго данные, зафиксированные до или в момент $T_{dispatch} = \text{storage_sessions.dispatch_datetime}$. Разрешены только категории `PREDICTIVE_ELIGIBLE`, предрейсовый контроль `STAGE_CONDITIONAL` и телеметрия хранения `CONDITIONALLY_ELIGIBLE`. | 1. **СТРОГО ЗАПРЕЩЕНО** использование замеров контроля качества в пункте прибытия (`quality_checks` со стадией `arrival`).<br>2. **СТРОГО ЗАПРЕЩЕНО** использование фактических параметров транспортировки (`actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`, `cold_chain_incident`, `transit_temp_mean_c`).<br>3. **СТРОГО ЗАПРЕЩЕНО** использование исторических исходов (`historical_quality_outcomes.*`) при инференсе.<br>4. **СТРОГО ЗАПРЕЩЕНА** любая утечка информации из будущего (future leakage). | Автоматизированный тест в CI (VLD-CI), проверяющий отсутствие запрещенных колонок в датасете инференса; валидатор Pydantic `BatchAssessmentInput`. | Ingestion (IGR) / Integration (VLD) / CI | «The assessment is strictly temporal-safe, evaluating batches at dispatch time without peeking into transit incidents or arrival outcomes.» |
| **PA-10** | **Auditability & Provenance:** Truth in advertising & simulation marking | ADR 0001; ADR 0003 (D3); Canonical Schema | Synthetic fixtures and demo data explicitly marked with `simulation: true` and notice. Real engines declare exact tier and version. | `ACCEPTED PRODUCT SEMANTICS` / `CURRENT IMPLEMENTED CAPABILITY` (в фикстуре) / `IMPLEMENTATION REQUIRED` (в рантайме) | Каждый ответ системы содержит полный объект `Provenance`. Демонстрационные фикстуры содержат `simulation: true`, `engine_tier: "fixture"` и явный текст уведомления: *«SIMULATION / synthetic fixture / not challenge data»*. В UI отображается водяной знак или баннер симуляции. | 1. Синтетические фикстуры **СТРОГО НЕ** выдаются за реальные предсказания модели машинного обучения.<br>2. Результаты офлайн-исследований (VDR-04A) **СТРОГО НЕ** представляются как показатели работы живой системы.<br>3. Движки разных уровней (baseline vs learned) **СТРОГО НЕ** маскируются друг под друга. | Тест схемы API на наличие `provenance.simulation == True` для демо-выдачи; UI-тест баннера симуляции в `AssessmentCard.tsx`. | Backend (IGR) / Frontend (Denis) / Product Owner | «Demo fixtures are transparently marked as simulations with full engine provenance and version tracking.» |
| **PA-11** | **Data Integrity:** Telemetry channel omissions | ADR 0002; ADR 0003 (D10) | Structural telemetry channel omissions encoded as explicit `None` / `null`. | `ACCEPTED PRODUCT SEMANTICS` / `IMPLEMENTATION REQUIRED` | Физически отсутствующие каналы телеметрии (поверхностная температура плодов в ZONE-006, концентрации газов $CO_2/O_2$ в камерах без регулируемой газовой среды) передаются в схеме как `null`. | 1. Отсутствующие каналы телеметрии **СТРОГО НЕ** заполняются искусственными нулями (`0.0`, `-1.0`) или глобальными средними значениями выборки в сырых входных данных.<br>2. Отсутствие необязательных каналов **СТРОГО НЕ** является основанием для перевода партии в статус `insufficient_data`. | Тесты инжестии телеметрии с проверкой сохранения `null` для ZONE-006 и не-РГС камер; тесты валидации признаков. | Ingestion (IGR) / Data (Viktor) | «Missing sensor channels are preserved as explicit nulls without fabricating dummy zero values.» |
| **PA-12** | **Evaluation vs Production:** Separation of research metrics from operational guarantees | ADR 0003 (D1, D5); VDR-04A | Offline evaluation metrics remain strictly in model cards and research artifacts. | `ACCEPTED PRODUCT SEMANTICS` | Метрики бенчмарка (Precision@10, NDCG@10, F1-score на протоколе P1) документируются в исследовательских отчетах и паспорте модели как свидетельства исследовательской валидации. | 1. Исследовательские метрики бенчмарка **СТРОГО НЕ** хардкодятся в пользовательском интерфейсе в качестве операционных гарантий точности для конкретной смены.<br>2. Результаты протокола P3 (случайный сплит) **СТРОГО НЕ** используются как подтверждение качества модели. | Аудит интерфейса и текстов документации; проверка разделения аналитических артефактов и рантайм-кода. | Product Owner / Integrator (VLD) / Evaluation | «Offline benchmark metrics validate candidate architectures but are not runtime guarantees for individual operational shifts.» |
| **PA-13** | **Predictive Input Integrity:** Telemetry role & VDR-04B narrative boundary | ADR 0002; ADR 0003 (D10); VDR-04B; APR2-D6 | Telemetry preserved in canonical input (`BatchAssessmentInput`). Product narrative treats C+L baseline as candidate simplification path without overpromising predictive lift from chamber telemetry. | `ACCEPTED PRODUCT SEMANTICS` / `IMPLEMENTATION REQUIRED` (в контрактах) / `ACCEPTED NARRATIVE BOUNDARY` | Канонический контракт входных данных (`BatchAssessmentInput`) сохраняет поля телеметрии камер хранения (ADR 0002, ADR 0003 D10). Продуктовая документация и коммуникация честно отражают результаты VDR-04B: агрегированная телеметрия в протестированных моделях не дала стабильного маржинального прироста точности поверх плановой логистики; архитектура «культура + логистика» (C+L) зафиксирована как кандидатный путь упрощения. | 1. **СТРОГО ЗАПРЕЩЕНО** заявлять в продуктовых материалах, питчах или интерфейсе, что телеметрия камер доказанно повышает точность предсказания потерь в протестированных моделях.<br>2. **СТРОГО ЗАПРЕЩЕНО** заявлять, что «телеметрия бесполезна» и исключать её из канонической схемы инпута без формального решения об изменении схемы.<br>3. **СТРОГО ЗАПРЕЩЕНО** утверждать, что в исследовании VDR-04B окончательно выбраны продакшн-модели или зафиксирован финальный набор признаков. | Проверка схемы Pydantic `BatchAssessmentInput` (наличие полей телеметрии); аудит продуктовой документации, модельных карт и питч-материалов на отсутствие ложных заявлений о предиктивном вкладе телеметрии. | Data (Viktor) / Product Owner / Integrator (VLD) / APR2-D6 | «VDR-04B showed that tested aggregate chamber telemetry provided no stable marginal lift over planned logistics; C+L serves as a candidate simplification path while telemetry is preserved in canonical input.» |

---

## 11. RIGOROUS NEGATIVE ACCEPTANCE CRITERIA (§11)

В соответствии с требованиями контракта APR-02 (§11), формулируются 12 критических негативных критериев приёмки. Нарушение любого из них является **блокирующим дефектом** приемочного тестирования:

1. **NEG-01 (Score Fabrication on Incomplete Data):**  
   Партия со статусом `insufficient_data` ни при каких обстоятельствах не должна получать числовой скор (`score = 0`, `score = 0.0` или любое иное значение). В интерфейсе и API поля `risk` и `deterioration_horizon` обязаны быть строго `null`.
2. **NEG-02 (Unvalidated Engine Mixing):**  
   Партии, оценённые разными движками (например, `engine_tier = "baseline"` и `engine_tier = "learned"`), либо разными версиями одного движка, ни при каких обстоятельствах не должны автоматически объединяться в единую ранжированную очередь без валидированного доказательства сопоставимости шкал.
3. **NEG-03 (Arbitrary Operational Quota):**  
   Число $K=10$ ни при каких обстоятельствах не должно интерпретироваться как операционная пропускная способность смены, обязательная квота физического досмотра или лимит отображения партий в системе.
4. **NEG-04 (Misleading Score Semantics):**  
   Скор риска (`risk.score`) ни при каких обстоятельствах не должен называться, подписываться или описываться как «вероятность порчи» (probability), «процент риска», «точность модели» или «уверенность» (confidence).
5. **NEG-05 (Uncalibrated Risk Bands):**  
   Ни при каких обстоятельствах в интерфейс не должны выводиться светофорные цветовые плашки (`red`, `yellow`, `green`) или категории (`high`, `moderate`, `low`), пока не будет утверждена калиброванная операционная политика порогов, согласованная с регламентом бизнеса.
6. **NEG-06 (Fabricated Deterioration Countdown):**  
   Ни при каких обстоятельствах в интерфейсе не должен отображаться таймер обратного отсчета до порчи (countdown), синтетическая дата наступления некондиции или расчетный интервал часов/дней до деградации.
7. **NEG-07 (Invented Confidence Percentages):**  
   Ни при каких обстоятельствах система не должна генерировать или отображать вымышленные проценты надежности (например, «надежность оценки 95%») или некалиброванные уровни low/med/high.
8. **NEG-08 (Unsubstantiated Causal Drivers):**  
   Ни при каких обстоятельствах в факторах риска (`factors`) не должны выводиться утверждения о причинно-следственной связи или направления влияния (`increases_risk` / `decreases_risk`) без валидированного математического алгоритма атрибуции (XAI).
9. **NEG-09 (Prescriptive Interventions & Savings Claims):**  
   Ни при каких обстоятельствах система не должна выдавать директивные команды на физические действия («доохладить», «утилизировать»), совершать автоматические действия без участия человека (`requires_human_review = false`) или заявлять о суммах предотвращенного ущерба («спасет €1 200»).
10. **NEG-10 (Future Information Leakage):**  
    Ни при каких обстоятельствах в модель оценки на инференсе не должны проникать замеры качества при прибытии (`stage = "arrival"`), фактические параметры транспортировки (задержки, аварии, температура рейса) или исторические метки списания.
11. **NEG-11 (Masked Synthetic Data):**  
    Ни при каких обстоятельствах синтетическая фикстура или демонстрационные данные не должны выдаваться за результаты работы реальной прогнозной модели машинного обучения.
12. **NEG-12 (Unsubstantiated Telemetry Utility & Arbitrary Omission):**
    Ни при каких обстоятельствах в продуктовых материалах, интерфейсе или документации не должно заявляться, что телеметрия камер хранения доказанно повышает точность моделей оценки в протестированных архитектурах, либо что телеметрия «бесполезна» и может быть произвольно удалена из канонической схемы инпута без формального архитектурного согласования.

---

## 12. FOUR CHALLENGE OUTCOMES TRACEABILITY MATRIX (§12)

Компактная матрица адресации четырех исходных требований спонсора (Challenge Outcomes) в продуктовой архитектуре:

| Challenge outcome | Accepted semantic support | Current implementation | Proposed MVP support | Current limitation | Demo-safe wording |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Outcome 1 — Which batches are most at risk?** | `ACCEPTED PRODUCT SEMANTICS`<br>(ADR 0003 D1, D2, D3: монотонный скор тяжести потерь, сортировка `score DESC, batch_id ASC` внутри одного движка). | `CURRENT IMPLEMENTED CAPABILITY`<br>(Только синтаксический сетевой контракт: эндпоинт `/demo/assessment` возвращает одиночную фикстуру; `/health` сообщает `analytics: not_configured`; аналитика и очередь отсутствуют). | `PROPOSED MVP SCOPE`<br>(Интерактивная таблица очереди Triage партий текущего операционного окна; бэкенд-расчет скора бейслайн-движком `baseline-crop-median-v1`). | В коде отсутствует аналитический эндпоинт ранжирования; отсутствует многопакетный UI; продакшн-модель ML не выбрана и не обучена. | «Smart Harvest establishes a deterministic ranking rule to prioritise batches by predicted loss severity; the current demo proves contract readiness, with the operational queue proposed for MVP.» |
| **Outcome 2 — When may quality begin to deteriorate?** | `ACCEPTED PRODUCT SEMANTICS`<br>(ADR 0003 D6: `deterioration_horizon = null` с честным дисклеймером *«not estimable from supplied observations»*). | `CURRENT IMPLEMENTED CAPABILITY`<br>(Поле `null` в фикстуре; в `AssessmentCard.tsx` есть неактивная ветка даты, подлежащая удалению). | `PROPOSED MVP SCOPE`<br>(Явное текстовое информирование о невозможности оценки времени онсета; отображение `planned_duration_hours` как отдельного логистического контекста рейса). | Биологический момент наступления деградации математически невозможно восстановить по трем дискретным чекпоинтам качества; биодеградационная модель отсутствует. | «Biological deterioration onset is not estimable from supplied observation data; the system reports deterioration horizon as null while displaying planned transit duration as logistical context.» |
| **Outcome 3 — What factors contribute to the risk?** | `ACCEPTED PRODUCT SEMANTICS`<br>(ADR 0003 D8: допустим пустой список `factors = []` либо объективный контекст с `effect = "unknown"`; каузальные формулировки запрещены). | `CURRENT IMPLEMENTED CAPABILITY`<br>(Одиночный статичный фактор качества данных `data_quality` с `effect: unknown` в фикстуре). | `PROPOSED MVP SCOPE`<br>(Вывод 3–4 объективных контекстных параметров партии и рейса: сорт, длительность хранения, плановый рейс, статус предрейсового осмотра с `effect = "unknown"`). | Алгоритм объяснимости (XAI / TreeSHAP) не реализован и не валидирован; направленные эффекты признаков (`increases_risk`/`decreases_risk`) не рассчитываются; причинность отсутствует. | «The system displays observed storage and shipment conditions as factual context; statistical factor attribution will be enabled once an explainability engine is validated.» |
| **Outcome 4 — What action should be prioritised?** | `ACCEPTED PRODUCT SEMANTICS`<br>(ADR 0003 D9: `recommendation = null` до прохождения evidence-гейта; стандартный выпуск партии — процесс склада, а не рекомендация; `requires_human_review = true`). | `CURRENT IMPLEMENTED CAPABILITY`<br>(Поле `recommendation: None` в фикстуре). | `PROPOSED MVP SCOPE`<br>(Нейтральное системное сообщение в UI о том, что автоматические интервенции не сконфигурированы, а решение о досмотре принимается диспетчером по регламенту склада). | В датасете отсутствуют контрфактические наблюдения об исходах вмешательств; каталог действий не утвержден челленджем; директивные подсказки аналитически несостоятельны. | «Automated prescriptive recommendations are null; the system prioritises batches for human attention, leaving operational decisions to qualified personnel following facility SOPs.» |

---

## 13. CURRENT IMPLEMENTATION GAP MAP (§13)

Карта текущих разрывов между нормативными решениями и работающим кодом фиксирует зависимости для будущих воркстримов.  
*Примечание:* Данная карта **НЕ назначает задачи исполнителям**, а исключительно документирует архитектурные и технические зависимости (Dependencies).

```
[ACCEPTED PRODUCT SEMANTIC] ───► [CURRENT CODE] ───► [GAP] ───► [REQUIRED FUTURE OWNER]
```

1. **Operational Ranking Queue:**
   - *Accepted Product Semantic:* ADR 0003 (D1, D3) — приоритизация партий операционного окна по правилу `risk.score DESC, batch_id ASC` строго внутри одного `engine_tier + engine_version`.
   - *Current Code:* В `backend/app/api/routes.py` есть только эндпоинт одиночной фикстуры `GET /demo/assessment`. Во фронтенде `HomePage.tsx` и `AssessmentCard.tsx` рендерят одну карточку.
   - *Gap:* Отсутствует бэкенд-эндпоинт для запроса списка партий с параметрами сортировки и фильтрации по окну/объекту; во фронтенде отсутствует компонент таблицы очереди (Triage Queue).
   - *Required Future Owner:* Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D2).

2. **Deterministic Baseline Engine:**
   - *Accepted Product Semantic:* ADR 0003 (D5) — расчет скора по обучающей медиане потерь для культуры (с глобальным фоллбэком) как эксплуатационный бейслайн `baseline-crop-median-v1`.
   - *Current Code:* Директория `backend/app/analytics/` содержит только пустой `__init__.py`. Эндпоинт `/health` возвращает `"analytics": "not_configured"`.
   - *Gap:* Логика загрузки исторических медиан и вычисления бейслайн-скора не реализована в сервисах бэкенда.
   - *Required Future Owner:* Backend (IGR) / Analytics / Integration (VLD).

3. **Point-of-Dispatch Ingestion Pipeline:**
   - *Accepted Product Semantic:* ADR 0002 — канонический инпут `BatchAssessmentInput` на момент $T_{dispatch}$, строгое отсечение прибытия и транзитных данных, трансляция структурных пропусков как `null`.
   - *Current Code:* `backend/app/ingestion/` содержит `raw_reader.py` и `diagnostics.py`, но нет маппера в каноническую схему `BatchAssessmentInput`.
   - *Gap:* Отсутствует конвейер преобразования сырых CSV-файлов в строго валидированные Pydantic-модели инпута с проверкой временных границ.
   - *Required Future Owner:* Ingestion (IGR) / Integration (VLD).

4. **Handling of `insufficient_data` in UI:**
   - *Accepted Product Semantic:* ADR 0003 (D7) — статус `insufficient_data`, отсутствие скора и горизонта, информирование через `reason_codes` и `missing_requirements`.
   - *Current Code:* Статичная плашка в единственной демо-карточке `AssessmentCard.tsx`.
   - *Gap:* В интерфейсе нет механизма разделения очереди на оценённые партии и партии с неполными данными (вкладка/секция); нет динамического рендеринга списка недостающих требований.
   - *Required Future Owner:* Frontend (Denis) / Integrator Gate (APR2-D3).

5. **Contextual Explainability (Factual Baseline):**
   - *Accepted Product Semantic:* ADR 0003 (D8) — заполнение `AssessmentFactor` объективными параметрами контекста с `effect = "unknown"`.
   - *Current Code:* Захардкоженный единственный фактор качества данных в фикстуре.
   - *Gap:* Отсутствует сервис извлечения контекстных признаков партии (сорт, длительность хранения, плановый рейс) и упаковки их в контейнер факторов.
   - *Required Future Owner:* Backend (IGR) / Frontend (Denis) / Integrator Gate (APR2-D4).

6. **Model Attribution Explainability (XAI):**
   - *Accepted Product Semantic:* ADR 0003 (D8) — направления `increases_risk` / `decreases_risk` допустимы строго при наличии валидированного алгоритма атрибуции.
   - *Current Code:* Полностью отсутствует.
   - *Gap:* Отсутствует выбор, реализация и валидация XAI-модуля (SHAP/TreeSHAP) и референтного набора данных.
   - *Required Future Owner:* Data / Analytics (Viktor) / Integration (VLD) — *DEFERRED*.

7. **Action Catalogue & Recommendation System:**
   - *Accepted Product Semantic:* ADR 0003 (D9) — сохранение `recommendation = null` до появления контрфактических доказательств и утверждения каталога действий.
   - *Current Code:* Поле `recommendation: None` в фикстуре.
   - *Gap:* В предметной области и датасете отсутствуют данные о результатах вмешательств; каталог действий не утвержден спонсором.
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
| 1. «Smart Harvest — это система поддержки принятия решений (Decision Support), помогающая оператору на отгрузке (кандидатная персона pending утверждения APR2-D1) приоритизировать партии по относительной тяжести прогнозируемых потерь.» | 1. «Система рассчитывает точный час, день или время, когда партия продукции начнет портиться.» *(Биологический онсет не рассчитывается)* |
| 2. «Ранжирование партий выполняется детерминированно по правилу: скор по убыванию, идентификатор партии по возрастанию, строго внутри одной версии движка.» | 2. «Скор риска 0.82 означает 82%-ю вероятность того, что эта партия сгниет в пути.» *(Скор — монотонная мера потерь, а не вероятность)* |
| 3. «Оценка строится строго на данных, доступных в момент отгрузки ($T_{dispatch}$), полностью исключая заглядывание в будущее (утечку данных о рейсе или приёмке).» | 3. «Внедрение нашей системы гарантированно снизит потери на 15% или сбережет распределительному центру €50 000 в сезон.» *(Эффект вмешательств не доказан)* |
| 4. «В исследовательском бенчмарке на отложенных сезонах (VDR-04A, протокол P1) модели ранжирования продемонстрировали высокую способность приоритизировать топ-10 партий с высоким риском (NDCG@10 = 0.88, Precision@10 = 1.0 при Recall@10 ≈ 0.0333). Это свидетельство эффективности верхнего ранжирования (top-K evidence), а не исчерпывающий скрининг всех потерь и не эксплуатационная гарантия точности в рантайме.» | 4. «Наш продакшн-алгоритм работает с точностью 100% в реальном времени или гарантирует выявление всех деградирующих партий.» *(Не путать офлайн-бенчмарк верхнего ранжирования с исчерпывающим скринингом и эксплуатационной гарантией)* |
| 5. «При нехватке ключевых входных данных контракт бэкенда фиксирует статус `insufficient_data` со списком `missing_requirements` (в текущем UI отображается только статус, динамический рендеринг списка требований предложен в MVP).» | 5. «Система предписывает оператору доохладить партию или отменить отправку.» *(Рекомендации строго null, решения принимает только человек)* |
| 6. «Горизонт деградации честно возвращается как `null`, так как имеющиеся контрольные замеры качества не позволяют восстановить момент начала биологической порчи.» | 6. «Продукт успешно внедрен и протестирован на реальных холодильных складах Молдовы.» *(Мы работаем с учебным датасетом)* |
| 7. «В текущей рантайм-фикстуре представлен только синтетический фактор качества данных (`data_quality`); извлечение контекстных факторов с `effect = "unknown"` является предложением MVP (APR2-D4); до внедрения валидированного XAI приписывание причинно-следственной связи запрещено.» | 7. «Зеленый статус означает абсолютную безопасность партии, а красный — гарантированный брак.» *(Цветовые диапазоны риска не валидированы и запрещены)* |
| 8. «Текущая демонстрация бэкенда и интерфейса использует валидированную синтетическую фикстуру со статусом симуляции для подтверждения надежности сетевого контракта.» | 8. «Партии с неполными данными автоматически отбраковываются и направляются на обязательную лабораторную экспертизу.» *(Вымышленный регламент)* |
| 9. «Исследование VDR-04B показало, что агрегированная телеметрия камер хранения не дает стабильного маржинального прироста точности поверх признаков плановой логистики; модель на базе культуры и логистики (C+L) рассматривается как кандидатный путь упрощения, при этом телеметрия сохраняется в каноническом инпуте.» | 9. «Телеметрия камер хранения бесполезна и может быть удалена из системы» ИЛИ «В исследовании VDR-04B окончательно выбраны продакшн-модели и зафиксирован финальный набор признаков.» |

---

## 15. PUX-08 BOUNDARY & PENDING UX DEPENDENCIES (§15)

В соответствии с контрактом APR-02 подтверждается статус взаимодействия с воркстримом UX:
1. **Статус PUX-08:** Документ `docs/recon/PUX-08-data-ux-reconciliation.md` (Денис, PR #22) имеет статус `DRAFT FOR REVIEW` и **НЕ ЯВЛЯЕТСЯ АВТОРИТЕТНЫМ РЕШЕНИЕМ (NOT CANON)**.
2. **Граница полномочий:** Рекомендации PUX-08 не могут использоваться как принятые продуктовые решения до прохождения гейта Интегратора.
3. **Реестр ожидающих UX-зависимостей:**
   - `UX-DEP-1 (Triage Queue UI):` Разработка таблицы ранжирования с поддержкой правила `risk.score DESC, batch_id ASC` (заблокирована до утверждения `APR2-D2`).
   - `UX-DEP-2 (Insufficient Data Panel):` Проектирование изолированного представления для партий со статусом `insufficient_data` (заблокировано до утверждения `APR2-D3`).
   - `UX-DEP-3 (Card Cleanup):` Очистка `AssessmentCard.tsx` от неактивных полей `risk.band`, `confidence_score` и `starts_at`.
   - `UX-DEP-4 (Context & Disclaimer Containers):` Создание нейтральных контейнеров для фактов контекста (`effect = unknown`) и дисклеймера об отсутствии рекомендаций (`recommendation = null`) (заблокировано до утверждения `APR2-D4` и `APR2-D5`).

---

## 16. EPISTEMIC CLASSIFICATION SUMMARY (§5)

Каждый аспект продуктовой спецификации строго соотнесен с одной из пяти эпистемических категорий:

- **A. CURRENT IMPLEMENTED CAPABILITY:**  
  Pydantic-схемы контракта `RiskAssessment`; эндпоинты `/health` (`analytics: not_configured`) и `/demo/assessment`; синтетическая фикстура `synthetic-batch-001` со статусом `insufficient_data`; одиночная карточка `AssessmentCard.tsx`.
- **B. ACCEPTED PRODUCT SEMANTICS:**  
  ADR 0001 (контрактная архитектура); ADR 0002 (граница $T_{dispatch}$, классификация 73 полей, запрет утечек); ADR 0003 (D1: таргет `loss_fraction_pct`, D2: скор тяжести потерь, `band = null`, D3: ранжирование `score DESC, batch_id ASC` внутри одного движка, D5: медианный бейслайн, D6: `horizon = null`, D7: `reliability = unavailable`, D8: факты с `effect = unknown`, D9: `recommendation = null`, D10: сохранение телеметрии).
- **C. PROPOSED MVP SCOPE:**  
  Предложения APR-02 takeover synthesis: интерактивная таблица очереди приоритизации (Triage Queue); реализация сервиса бейслайн-скора `baseline-crop-median-v1`; панель детального просмотра контекста партии; отображение 3–4 объективных контекстных параметров партии; нейтральный системный блок отсутствия рекомендаций; модель C+L как кандидатный путь упрощения при сохранении телеметрии в каноническом инпуте.
- **D. DEFERRED / OUT OF MVP:**  
  Светофорные диапазоны риска (`risk.band`); таймеры деградации и интервалы часов/дней; калиброванные проценты уверенности; направленные факторы XAI (`increases_risk`/`decreases_risk`); каталог корректирующих действий и оценка финансовой экономии; learned ML-модели до проведения приемочного тестирования.
- **E. BLOCKED / UNKNOWN:**  
  Операционный регламент обработки партий с `insufficient_data` (APR2-D3); точный состав сменной очереди и предельная емкость оператора (APR2-D2); целевая персона пользователя (APR2-D1); алгоритм сопоставимости скоров между разными движками.

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
- [x] **ЗАПРЕЩЕНО** изменять любые файлы репозитория, кроме целевых файлов воркстрима APR-02: `docs/product_recon/08_mvp_scope_decision_packet.md` и `docs/product_recon/09_product_acceptance_traceability.md`.

---
*Документ подготовлен в рамках APR-02 takeover synthesis (Vladimir — Integrator) из-за таймбокса финала тренировки для передачи на рассмотрение Human Gate.*
*Конец спецификации.*
