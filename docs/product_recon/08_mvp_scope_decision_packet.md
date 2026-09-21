STATUS: PROPOSED PRODUCT SPEC — NOT CANON

# APR-02: MVP Scope Decision Packet & Product Specification

**Original workstream owner:** Alisa — Product Owner
**Execution takeover:** Vladimir — Integrator
**Reason:** final training timebox / Product Owner unavailable
**Workstream:** APR-02 Product MVP Scope
**Repository:** `Slave-of-Skynet/training_agrifood`
**Original APR-02 branch:** `alisa/apr-02-mvp-scope`
**APR-02F reconciliation branch:** `vladimir/apr-02-human-gate-reconciliation`
**Original APR-02F contract base:** `204c3ac37fb2098bfe6c0908a66c54065cda23ae`
**Refreshed APR-02F base:** `cea6ece1d100434772b79b9eb42c8d7bd8488466` (Base Refresh Addendum; PR #22 / PR #28)
**Original APR02_BASE:** `6d0e4a50c36937f01b769a16a99bfa03af458c66`
**Target File:** `docs/product_recon/08_mvp_scope_decision_packet.md`
**Status:** PROPOSED PRODUCT SPEC — NOT CANON (APR-02 takeover synthesis / PROPOSED PRODUCT SPEC — requires Human Gate)

---

# ВХОДНОЙ КОНТЕКСТ (RECON ЭТАП 1)

## 1. CHALLENGE OUTCOMES
Исходный контекст тренировочного задания **Smart Harvest — Reduce Post-Harvest Losses** (Sponsor Brief: Training Challenge #3 — AgriFood; `sponsor_pack/README.md`) формулирует четыре обязательных операционных вопроса, на которые должна отвечать система поддержки принятия решений оператора на этапе отгрузки:
1. **Outcome 1 — «Which batches are most at risk?»**: выявление и приоритизация партий плодоовощной продукции с наивысшим риском потерь/деградации перед погрузкой в транспортное средство.
2. **Outcome 2 — «When may quality begin to deteriorate?»**: оценка временного горизонта наступления деградации или момента выхода качества за пределы допустимых кондиций.
3. **Outcome 3 — «What factors contribute to the risk?»**: прозрачное информирование оператора об агрономических, климатических, складских и логистических факторах, определяющих оценку риска.
4. **Outcome 4 — «What action should be prioritised?»**: предоставление приоритизированных рекомендаций по действиям для предотвращения или снижения потерь урожая.

*Граница обязательств:* Добавление любых новых требований к челленджу категорически запрещено. Продуктовая спецификация обязана прямо адресовать данные четыре исхода, сохраняя абсолютную честность относительно того, что из них поддержано данными и кодом, а что остаётся нереализованным или аналитически необоснованным.

---

## 2. ACCEPTED SEMANTICS (ADR 0002 / ADR 0003)

### ADR 0002: Predictive Input Semantics and Temporal Leakage Boundary (Accepted 2026-09-19)
- **Момент оценки:** Строго $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$ (завершение нахождения партии в холодильной камере, момент принятия решения об отгрузке). Единственные канонические часы: `assessment_context.assessment_timestamp`.
- **Классификация 73 полей сырых данных:**
  1. `PREDICTIVE_ELIGIBLE` (25 полей): наблюдаемы и зафиксированы до $T_{dispatch}$ (паспорт партии, сбор, базовые атрибуты склада/камеры).
  2. `STAGE_CONDITIONAL` (4 поля): замеры качества (`quality_checks`); стадии `harvest` и `pre_dispatch` разрешены; стадия `arrival` — строго **FORBIDDEN_FUTURE**.
  3. `CONDITIONALLY_ELIGIBLE` (16 полей): телеметрия за период хранения ($T_{entry} \le t \le T_{dispatch}$) и плановая логистика (`shipments.planned_*`).
  4. `CONTEXT_ONLY` (10 полей): идентификаторы (`batch_id`, `storage_session_id`, `facility_id`, `zone_id`) и наименования.
  5. `LABEL_OR_EVALUATION_ONLY` (4 поля): исторические исходы (`historical_quality_outcomes.*`); категорически запрещены на инференсе.
  6. `FORBIDDEN_FUTURE` (5 полей): фактические события транспортировки (`actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`, `cold_chain_incident`, `transit_temp_mean_c`).
  7. `RAW_ONLY / NOT NEEDED` (9 полей): суррогатные ключи и дублирующие внешние ключи.
- **Строгая негативная граница (Strict Negative Boundary):** Приёмка в пункте назначения, дорожные инциденты, фактические задержки, телеметрия после $T_{dispatch}$ и исторические исходы никогда не должны проникать в модель оценки.
- **Явные пропуски:** Пропуски каналов (поверхностная температура в ZONE-006, газы в не-РГС) кодируются как `None` / `null`. Запрещена фабрикация нулей (`0.0`, `-1.0`) или средних.

### ADR 0003: Assessment, Ranking and Evaluation Semantics (Accepted 2026-09-20)
- **D1 (Задача и таргет):** Первичная операционная задача — приоритизация/ранжирование партий на отгрузке. Первичный офлайн таргет — `loss_fraction_pct` (доля списания в пункте назначения). Метки `quality_status`, `quality_score` и `economic_loss_eur` не являются таргетами продакшна. Порог $\ge 15\%$ — исключительно аналитическая релевантность для бенчмарка, но НЕ операционный порог риска или алерт.
- **D2 (Скор и диапазон риска):** Скор риска вычисляется детерминированно как монотонная мера тяжести потерь:
  $$\text{score} = \frac{\text{clip}(\text{predicted\_loss\_fraction\_pct}, 0, 100)}{100}$$
  Скор не является вероятностью, калиброванной уверенностью или гарантией убытка. Текущая нормативная политика: `risk.band = null`. Никаких произвольных порогов или цветовых категорий.
- **D3 (Ранжирование и сопоставимость):** Ранжирование строго по `risk.score DESC, batch_id ASC` (стабильность сортировки). Единая очередь ранжирования допустима **СТРОГО для результатов одной пары `engine_tier + engine_version`**. Объединение разных тиров или версий без валидации запрещено. `insufficient_data` не имеет скора и не может трактоваться как нулевой риск. Ранжирование — это приоритизация, а не исчерпывающий скрининг. OBSERVED RESULT: Recall@10 = 0.0333 относится к исследовательскому HGB F3 (Context + Telemetry + Planned logistics), VDR-04A P1 (2024 train / 2025 test), а не к runtime или медианному бейслайну.
- **D4 (Плановая логистика):** Признаки плановой логистики опциональны / условно допустимы. В VDR-04A они показали наибольшую ассоциацию с потерями, однако это не каузальный эффект. Ранжирование без логистики возможно.
- **D5 (Протокол оценки и бейслайн):** Первичный протокол — P1 Forward Inter-Season Holdout (обучение на сезоне 2024, тест на сезоне 2025). Вторичный — P2 Chamber-Time Grouped OOF. P3 (случайный сплит) признан невалидным диагностическим тестом. Эксплуатационный бейслайн — медиана `loss_fraction_pct` обучающей выборки по культуре (с глобальной медианой для новых культур).
- **D6 (Горизонт деградации):** Текущее решение: `deterioration_horizon = null` для всех аналитических движков с честным сообщением *«not estimable from supplied observations»*. Запрещены таймеры обратного отсчёта и произвольные интервалы.
- **D7 (Надёжность и достаточность):** Текущее решение: `reliability.level = unavailable`, `confidence_score = null`. Фактические ограничения транслируются через `reason_codes` и `missing_requirements`. Статус `assessed` означает способность движка рассчитать скор; `insufficient_data` — невозможность выполнить минимальные требования (при этом `risk = null`, `horizon = null`). Усечение телеметрии (204 батча 2026 г.) и структурные пропуски не являются поводом для авто-отклонения. Произвольные пороги устаревания данных не приняты.
- **D8 (Факторы и объяснимость):** `AssessmentFactor` отражает либо фактические условия контекста (`effect = unknown`), либо валидированный вклад в выход модели. Направления `increases_risk` / `decreases_risk` означают вклад в скор модели, а не биологическую причину. До появления объясняющего движка список факторов может оставаться пустым (`factors = []`). Вымышленные факторы запрещены.
- **D9 (Рекомендации и действия):** Текущий предиктивный вывод: `recommendation = null` до прохождения отдельного evidence-гейта. Реальный операционный процесс и полномочия пользователя — UNKNOWN. Запрещено вводить `requires_human_review = false`. Запрещены любые утверждения об эффективности вмешательств или предотвращённых финансовых потерях.
- **D10 (Телеметрия в инпуте):** Телеметрия сохраняется в каноническом инпуте. Слабый прирост F1 $\to$ F2 не даёт права исключать её из будущих моделей без прямого абляционного теста моделей с логистикой.

---

## 3. EVIDENCE MAP SUMMARY (APR-01 01–07)
Воркстрим APR-01 (Product & Requirements Recon, шаги 0–8) выполнил детальное исследование продуктового контекста. Его кандидатные роли, процессы и классы действий — исследовательские предложения, не sponsor FACT и не принятый каталог действий; APR-02F применяет границы §9:
- **01 Context Inventory:** Систематизировал 6 категорий знания, зафиксировал границу $T_{dispatch}$, отделил факты спонсора от предположений команды.
- **02 Research Questions:** Сформировал 11 исследовательских направлений и выделил 10–15 приоритетных вопросов (P0) для продуктового контура.
- **03 Source Map:** Определил 4-уровневую иерархию источников (Tier 1: FAO/USDA/министерства; Tier 2: рецензируемые публикации; Tier 3: отраслевые регламенты; Tier 4: вторичные материалы).
- **04 Evidence Map:** Сопоставил 15 рецензированных академических и отраслевых источников (Kader, Gross, Watkins, Thompson, FAO, UC Davis) с продуктовыми вопросами. Установил строгие агрономические ограничения: культуроспецифичность, непереносимость порогов томатов на яблоки, отсутствие контрфактических данных об эффекте вмешательств в наблюдательных датасетах.
- **05 User Decision Model:** Определил кандидатные персоны оператора, решения на рампе (D1: физический осмотр, D2: стандартный выпуск, D3: удержание/доохлаждение, D4: коммерческая эскалация), 5 исследовательских классов действий и жесткую границу доступности данных на $T_{dispatch}$.
- **06 Proposed Product Workflow:** Спроектировал 7-этапный сценарий работы оператора (вход $\to$ обнаружение проблемы $\to$ выбор партии $\to$ понимание риска $\to$ понимание причин $\to$ понимание срочности $\to$ решение человека). Разделил минимально полезную информацию и категорически запрещённые обещания.
- **07 Adversarial Review:** Провел сквозной стресс-тест по 10 калибровочным направлениям и 13 категориям уязвимостей. Устранил жесткую квоту K=10, вымышленные пороги и псевдокоды действий, отвязал стандартный выпуск от контракта рекомендаций, верифицировал составную семантику флага конденсации и устранил выдуманную автоматическую маршрутизацию партий `insufficient_data` на QC.

---

## 4. CURRENT IMPLEMENTATION SNAPSHOT
FACT: implementation snapshot сверён на refreshed APR-02F base `cea6ece1d100434772b79b9eb42c8d7bd8488466`. Исходные базы сохранены в provenance выше; PR #22 интегрировал PUX-08, PR #28 — IGR-03 canonical input mapping.
- **Backend API (`backend/app/api/routes.py`):**
  - Эндпоинт `GET /health` возвращает:
    ```json
    {
      "status": "ok",
      "service": "smart-harvest",
      "analytics": "not_configured"
    }
    ```
    Статус `analytics = not_configured` подтверждён в коде.
  - Эндпоинт `GET /demo/assessment` возвращает одиночную синтетическую фикстуру из `backend/app/services/demo_assessment.py`:
    ```python
    RiskAssessment(
        batch_id="synthetic-batch-001",
        status=AssessmentStatus.INSUFFICIENT_DATA,
        risk=None,
        deterioration_horizon=None,
        factors=[
            AssessmentFactor(
                code="validated_inputs_unavailable",
                category=FactorCategory.DATA_QUALITY,
                effect=FactorEffect.UNKNOWN,
                summary="Validated assessment inputs are not configured for this fixture.",
            )
        ],
        recommendation=None,
        reliability=Reliability(
            level=ReliabilityLevel.UNAVAILABLE,
            confidence_score=None,
            reason_codes=["INSUFFICIENT_VALIDATED_INPUTS"],
            missing_requirements=["Validated challenge dataset schema"],
        ),
        provenance=Provenance(
            contract_version="1.0.0",
            engine_tier="fixture",
            engine_version="foundation-fixture-v1",
            simulation=True,
            notice="SIMULATION / synthetic fixture / not challenge data",
        ),
    )
    ```
- **Backend Analytics & Ingestion:**
  - `backend/app/analytics/` содержит только пустой `__init__.py`. Аналитический движок, расчет скоров, детерминированный бейслайн, логика очереди ранжирования — **ОТСУТСТВУЮТ**.
  - **CURRENT IMPLEMENTED INGESTION CAPABILITY (IGR-03 / PR #28):** `backend/app/domain/batch.py` определяет typed `BatchAssessmentInput`; `backend/app/ingestion/canonical_mapper.py` детерминированно преобразует raw snapshot в canonical input. Реализованы batch/session/zone/facility joins, typed parsing, `assessment_timestamp == storage_sessions.dispatch_datetime`, только harvest/pre-dispatch QC и telemetry в `entry_datetime <= timestamp <= dispatch_datetime`. Структурные пропуски сохраняются как `None`; planned logistics не использует actual transit realizations; arrival QC, historical outcomes и post-dispatch telemetry исключены.
  - **Evidence boundary:** В `backend/tests/test_ingestion_canonical.py` существуют проверки joins/clock, structural missingness и leakage invariance. Это implemented ingestion, не production `RiskAssessment` service, scoring или ranking endpoint; они отсутствуют. APR-02F инспектирует committed code/tests, но не заявляет запуск тестов.
- **Frontend Client (`frontend/src/**`):**
  - `HomePage.tsx` опрашивает `/health` и `/demo/assessment`. Отображает `BackendStatus` и компонент `AssessmentCard`.
  - `AssessmentCard.tsx` отображает **ОДНУ статическую карточку** для единственного синтетического батча `synthetic-batch-001` с баннером недостатка данных (*«No risk percentage or deterioration horizon is shown because validated challenge inputs are not available»*).
  - В интерфейсе **НЕТ таблицы партий, НЕТ очереди приоритизации, НЕТ переключения между батчами, НЕТ фильтрации по операционным окнам**.
  - В коде присутствуют неактивные ветки отображения сырого скора и даты начала деградации (`assessment.risk?.score`, `assessment.deterioration_horizon?.starts_at`), недостижимые в текущем статусе фикстуры.
- **Принцип честности:** `IMPLEMENTED ≠ ANALYTICALLY VALIDATED`. Foundation fixture доказывает сетевой контракт; IGR-03 отдельно реализует canonical ingestion. Ни одна из этих возможностей **НЕ является работающим аналитическим или предиктивным MVP**.

---

## 5. PUX-08 STATUS
Воркстрим UX (Денис, PR #22, файл `docs/recon/PUX-08-data-ux-reconciliation.md`):
- **FACT:** PUX-08 интегрирован в репозиторий через PR #22; сам документ сохраняет **DRAFT FOR REVIEW**.
- Документ сверяет UX с ADR 0002/0003, VDR-01–04A/04B и APR-01/02, отдельно маркируя принятые решения и предложения.
- **DECISION BOUNDARY:** Repository integration не делает рекомендации PUX-08 принятым product canon. Они **NOT CANON / not authoritative by themselves**, требуют Integrator/Human Gate там, где необходимо.
- В текущей матрице PUX-08 принятая ranking semantics имеет `KEEP`, конкретный operator triage workflow — `BLOCKED` до продуктовых решений; risk bands и actions — `BLOCKED`, reliability display — `CHANGE` без числовой confidence; countdown, financial savings и streaming — `REMOVE`.
- **PENDING UX DEPENDENCIES** ниже означают ожидающие продуктовых решений/реализации элементы, не ожидание merge PUX-08. APR2-D1–D6 сохраняют подготовленные APR-02F границы; PUX-08 не изменяется этим fix-up.

---

## 6. IDENTIFIED GAPS
1. **Разрыв между canonical input и аналитикой:** IGR-03 canonical point-of-dispatch mapping и typed `BatchAssessmentInput` реализованы. Ранжирование и crop-median baseline приняты нормативно, но analytics scoring, production assessment service и multi-batch ranking endpoint остаются нереализованными.
2. **Разрыв между очередью ранжирования и UI:** Сортировка `score DESC, batch_id ASC` утверждена в ADR 0003 D3, но фронтенд отображает только одну статическую карточку. Интерфейс очереди партий (Triage Queue) не существует в коде.
3. **Операционный регламент для `insufficient_data`:** Семантика схемы определена (`risk = null`, `horizon = null`), но физические действия оператора при получении такого статуса остаются открытыми. Автоматическая маршрутизация на ручной контроль качества (QC) отвергнута как неподтверждённая.
4. **Минимальные требования движков:** Не специфицирован точный состав обязательных полей для детерминированного бейслайна и будущего предиктивного движка.
5. **Отсутствие механизма объяснений:** XAI-алгоритм не выбран и не валидирован. RECOMMENDATION для будущего baseline: `factors = []`, отдельные «How this score is computed» и «Batch Context»; контекст не является вкладом в скор (APR2-D4).
6. **Полное отсутствие валидации действий:** Outcome 4 — **NOT SUPPORTED BY CURRENT EVIDENCE**. `recommendation = null` и сообщение о недоступности не выполняют требование о приоритизированном действии (APR2-D5).

---

## 7. UNKNOWN / MISSING
В соответствии с глобальным реестром `docs/assumptions_unknowns.md` и ADR 0003, следующие 10 областей остаются строгими **UNKNOWN**:
1. Семейство production learned-модели, гиперпараметры, финальный сабсет признаков и процедура её приёмки.
2. Точные минимальные требования движков, правила маршрутизации fallback, кросс-тирная сопоставимость скоров.
3. Калибровка доверительных интервалов, операционные пороги диапазонов риска (`risk.band`), пороги устаревания телеметрии.
4. Момент начала биологической деградации, агрономические пороги культур, интервальные оценки времени порчи.
5. Алгоритм объяснимости (XAI), референтный базис атрибуции, валидация понятности оператору.
6. Подтверждение design persona человеком; реальные полномочия и SOP, длительность окна и емкость проверки, будущая live queue membership. APR2-D1/D2 предлагают только design persona и dataset-backed replay/view policy.
7. Реальная эффективность корректирующих действий, их стоимость, логистические задержки, предотвращённый ущерб.
8. Происхождение исторической метки `quality_score`, границы статусов качества, валидность расчётных цен культур.
9. Обобщающая способность моделей на новые культуры и хозяйства, устойчивость к сдвигу распределений.
10. Инфраструктура хостинга, персистентность, время отклика; полезность телеметрии для monitoring / audit / diagnostics и equipment-health detection не валидирована и не реализована.

---

# ОБЯЗАТЕЛЬНЫЕ ЭПИСТЕМИЧЕСКИЕ ГРАНИЦЫ (§5)

Метки доказательности: **FACT** — прямой факт источника/кода; **DECISION** — принятое ADR-решение; **OBSERVED RESULT** — результат конкретного исследования; **INFERENCE** — ограниченный вывод; **RECOMMENDATION** — предложение; **UNKNOWN** — открытый вопрос. Коммит исследования не делает его каноном. APR2-D1–D6 ниже — RECOMMENDATION до Human Gate.

Отдельно используются пять статусов области/реализации:

- **A. CURRENT IMPLEMENTED CAPABILITY (Текущие реализованные возможности):**  
  Только то, что физически присутствует в committed коде репозитория (`backend/app/**`, `frontend/src/**`). Не путать с аналитически валидированными возможностями.

- **B. ACCEPTED PRODUCT SEMANTICS (Принятая продуктовая семантика):**  
  Формально утверждённые нормативные решения команды и интегратора (ADR 0001, ADR 0002, ADR 0003). Являются обязательными рамками для проектирования; степень реализации указана отдельно (IGR-03 input mapping реализован, analytics/output runtime отсутствует).

- **C. PROPOSED MVP SCOPE (Предлагаемый объём MVP):**  
  Рекомендации синтеза APR-02 (takeover synthesis) по целевому функционалу MVP, выносимые на утверждение интегратору. **НЕ являются командным решением до прохождения Human Gate.**

- **D. DEFERRED / OUT OF MVP (Отложено / За рамками MVP):**  
  Функционал и концепции, исключённые из ближайшего релиза ввиду отсутствия данных, калибровки, объясняющих движков или контрфактических доказательств.

- **E. BLOCKED / UNKNOWN (Заблокировано / Неизвестно):**  
  Элементы, реализация которых невозможна без внешних решений (выбор персоны, определение емкости оператора, подтверждение каталога действий челленджем).

---

# 7. СТРУКТУРА ПРОДУКТОВОГО ОБЪЁМА (§7)

## 7.1 Product objective
**Smart Harvest** — предлагаемый advisory Decision Support для dispatch-side storage operator в момент отгрузки ($T_{dispatch}$). RECOMMENDATION: помочь приоритизировать партии по скору тяжести потерь; снижение реальных потерь остается целью, а не подтвержденным эффектом продукта.

### Привязка к 4 challenge outcomes:
- **Outcome 1 («Which batches are most at risk?»):** Предлагается ранжирование оценённых партий configurable replay/view window по `assessment_timestamp = storage_sessions.dispatch_datetime`, строго внутри одной пары `engine_tier + engine_version`, по `risk.score DESC, batch_id ASC`. Равные скоры не означают разный риск из-за порядка ID; runtime-очередь и baseline отсутствуют.
- **Outcome 2 («When may quality begin to deteriorate?»):** Не поддержан расчет времени онсета: `deterioration_horizon = null`, «not estimable from supplied observations». `planned_duration_hours` можно показывать только как плановый логистический контекст, не как установленный горизонт риска или порчи.
- **Outcome 3 («What factors contribute to the risk?»):** Частичная поддержка: механизм baseline объясним, наблюдаемый Batch Context может быть показан отдельно. Для baseline `factors = []`; атрибуция признаков к скору не поддержана. Контекст не закрывает Outcome 3 полностью.
- **Outcome 4 («What action should be prioritised?»):** **NOT SUPPORTED BY CURRENT EVIDENCE**; `recommendation = null`. Нейтральное сообщение о недоступности не выполняет Outcome 4. Ранжирование партий не является рекомендацией вмешательства; каталог действий и их эффективность не валидированы.

*Запрет:* Никаких новых требований, выходящих за рамки исходного задания спонсора, в спецификацию не вводится.

---

## 7.2 Current capability snapshot
FACT: snapshot сверён на refreshed APR-02F base `cea6ece1d100434772b79b9eb42c8d7bd8488466`:

1. **Разделение статусов:**  
   `IMPLEMENTED ≠ ANALYTICALLY VALIDATED`. Наличие Pydantic-схем и HTTP-эндпоинтов в бэкенде доказывает лишь корректность синтаксического контракта, но не наличие аналитического продукта.
2. **Отсутствие предиктивного MVP:**  
   В репозитории **НЕТ работающего предиктивного MVP**. IGR-03 реализует raw-snapshot → typed `BatchAssessmentInput` mapping и temporal leakage boundaries; committed ingestion tests существуют. В `backend/app/analytics/` только `__init__.py`; нет scoring runtime, crop-median engine, production assessment service, ranking endpoint, learned model или генератора рекомендаций.
3. **Подтверждение `analytics = not_configured`:**  
   Эндпоинт `/health` прямо декларирует: `"analytics": "not_configured"`.
4. **Синтетическая фикстура:**  
   Единственной доступной формой assessment API output остается статическая синтетическая фикстура `synthetic-batch-001` (`status: "insufficient_data"`).
5. **Фронтенд:**  
   Клиентское приложение отображает **ОДНУ статическую карточку** с сообщением о недоступности валидированных входных данных. Очередь партий, списки, фильтры и таблицы в интерфейсе отсутствуют.

---

## 7.3 Candidate target MVP scope

Ниже раздельно указаны принятая семантика, состояние реализации и предлагаемый объём; предложения не являются каноном:

### 1. Batch prioritisation (Приоритизация партий)
- **Статус семантики ранжирования:** `ACCEPTED SEMANTIC — IMPLEMENTATION REQUIRED`  
  - *Обоснование:* ADR 0003 (D1, D3) утверждает ранжирование по `risk.score DESC, batch_id ASC` как первичную операционную задачу. Требуется программная реализация в бэкенде и фронтенде.
- **Статус состава очереди и емкости оператора:** `PROPOSED MVP — REQUIRES INTEGRATOR DECISION`  
  - *Обоснование:* RECOMMENDATION: выбирать записанные события `assessment_timestamp = storage_sessions.dispatch_datetime` в configurable replay/view window; `facility_id` — UI/context filter only. `planned_dispatch_datetime` — условно допустимый по ADR 0002 плановый контекст, не часы оценки. Длительность окна, реальная емкость и live membership — UNKNOWN (APR2-D2).
- **Ограничение сопоставимости:** В одной очереди могут находиться строго партии, оценённые одной и той же парой `engine_tier + engine_version` (ADR 0003 D3).

### 2. Batch detail (Детальный экран партии)
- **Статус:** `PROPOSED MVP — REQUIRES INTEGRATOR DECISION`  
  - *Кандидатный состав экрана:* Идентификация партии (`batch_id`, `crop_type`, `variety`), контекст сбора и хранения (`facility_id`, `zone_id`, `storage_duration_days`), плановая логистика (`destination_market`, `planned_duration_hours`), скор тяжести потерь (`risk.score`), метаданные расчета (`engine_tier`, `engine_version`, `generated_at`), фактические ограничения (`reason_codes`, `missing_requirements`).
  - *Строгие запреты:* **НЕ ТРЕБОВАТЬ** и не отображать: категориальные диапазоны (`risk.band`), вероятности порчи (%), калиброванные проценты уверенности (`confidence_score %`).

### 3. Insufficient-data state (Состояние нехватки данных)
- **Статус семантики и контракта:** `ACCEPTED SEMANTIC — IMPLEMENTATION REQUIRED`  
  - *Обоснование:* ADR 0003 (D7) фиксирует: `status = "insufficient_data"`, `risk = null`, `deterioration_horizon = null`, информирование через `reason_codes` и `missing_requirements`.
- **Статус представления:** `PROPOSED MVP — REQUIRES INTEGRATOR DECISION`: отдельная нейтральная секция «Not assessed / Incomplete data», вне числового ранжирования, без вывода о низком/высоком риске (APR2-D3).
- **Статус операционного процесса обработки:** `BLOCKED / UNKNOWN`; APR2-D3 не определяет физические действия.
  - *Обоснование:* В каноне нет правил, что физически должен делать оператор с партией без скора. **Категорически запрещено выдумывать автоматическую маршрутизацию на обязательный контроль качества (QC).**

### 4. Deterioration timing (Время начала деградации)
- **Статус текущего представления:** `CURRENTLY IMPLEMENTED` (в контракте/фикстуре) / `ACCEPTED SEMANTIC — IMPLEMENTATION REQUIRED` (в рантайме)  
  - *Обоснование:* ADR 0003 (D6) предписывает: `deterioration_horizon = null` с честным текстом *«not estimable from supplied observations»*. Поле сохраняется в схеме для прямой совместимости.
- **Статус таймеров и интервалов:** `DEFERRED` / `BLOCKED / UNKNOWN`  
  - *Обоснование:* В данных нет биосенсоров и непрерывных замеров качества (VDR-03). Превращение Outcome 2 в таймер обратного отсчета (countdown) категорически запрещено.

### 5. Explainability (Механизм, контекст и атрибуция)
- **DECISION:** ADR 0003 D8 допускает контекст с `effect = unknown` либо `factors = []`; это разрешение схемы, не доказательство вклада контекста в baseline.
- **RECOMMENDATION — PROPOSED MVP:** Для `baseline-crop-median-v1` использовать `factors = []`; отдельно «How this score is computed» (обучающая медиана по культуре, global training-median fallback для unseen crop, clipping / 100) и «Batch Context» с текстом «Context only; contribution to this score has not been established.»
- **UNKNOWN / DEFERRED:** Метод и валидация model attribution. `increases_risk` / `decreases_risk` запрещены до отдельной валидации; добавление SHAP само по себе ее не заменяет. Outcome 3 не выполнен полностью.

### 6. Recommendations (Рекомендации действий)
- **Статус текущего представления:** `CURRENTLY IMPLEMENTED` (в контракте/фикстуре) / `ACCEPTED SEMANTIC — IMPLEMENTATION REQUIRED` (в рантайме)  
  - *Обоснование:* ADR 0003 (D9) утверждает `recommendation = null`. Outcome 4 — **NOT SUPPORTED BY CURRENT EVIDENCE**; информационный блок не является рекомендацией действия.
- **Статус каталога действий и автоматических рекомендаций:** `DEFERRED` / `BLOCKED / UNKNOWN`  
  - *Обоснование:* В данных отсутствуют контрфактические наблюдения об эффекте вмешательств. Исследовательские классы действий из APR-01 (шаг 6) запрещено превращать в функции продакшна без утверждения каталога действий челленджем.

### 7. Reliability (Оценка надёжности)
- **Статус текущего представления:** `CURRENTLY IMPLEMENTED` (в контракте/фикстуре) / `ACCEPTED SEMANTIC — IMPLEMENTATION REQUIRED` (в рантайме)  
  - *Обоснование:* ADR 0003 (D7) предписывает: `reliability.level = unavailable`, `confidence_score = null`.
- **Статус калиброванной уверенности и уровней low/med/high:** `DEFERRED` / `BLOCKED / UNKNOWN`  
  - *Обоснование:* Калибровка вероятностей и доверительных интервалов не проводилась. Проектирование плашек уверенности («95% надежно») запрещено.

---

# 8. MVP SCOPE CLASSIFICATION (§8)

В таблице ниже представлена детальная классификация всех продуктовых возможностей Smart Harvest.  
*Статус области:* `CURRENT`, `PROPOSED MVP`, `DEFER`, `BLOCKED`.  
**ВАЖНО:** Статус `PROPOSED MVP` отражает предложение APR-02 takeover synthesis и **НЕ является решением команды** до утверждения на соответствующем гейте (Human Gate).

| Capability | Accepted semantic | Current implementation | Product recommendation | Dependency / owner | Scope status | Rationale |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **Operational Triage Queue** | ADR 0003 D1/D3: `risk.score DESC, batch_id ASC` внутри одной пары `engine_tier + engine_version`. | Очередь отсутствует; одна fixture-карточка. | Configurable replay/view window по `assessment_timestamp = storage_sessions.dispatch_datetime`; `facility_id` — UI/context filter only; planned schedule не заменяет часы оценки. | Backend / Frontend / APR2-D2 | **PROPOSED MVP** | Длительность, capacity и live workflow UNKNOWN; tie-break ID не различает риск. |
| **Deterministic Baseline Engine** | ADR 0003 (D5): расчет скора по обучающей медиане `loss_fraction_pct` для культуры (с глобальным фоллбэком). | Отсутствует. В `backend/app/analytics/` только `__init__.py`. | Реализовать минимальный расчет медианного скора в бэкенде как бейслайн-движок `baseline-crop-median-v1`. | Backend (IGR) / Integrator (VLD) | **PROPOSED MVP** | APR-02 takeover recommendation: дает реальный недеградированный скор для очередей без ожидания сложного ML. |
| **Batch Detail View** | ADR 0002 / ADR 0003: паспорт партии, условия хранения, плановая логистика, скор потерь, метаданные расчета. | Карточка синтетического батча с неактивными ветками скора и даты. | Реализовать панель детального просмотра выбранной партии с отображением контекста и ограничений. | Frontend (Denis) / Product Owner | **PROPOSED MVP** | APR-02 takeover recommendation: позволяет оператору понять контекст партии перед принятием решения. |
| **Insufficient-data Contract** | ADR 0003 (D7): `status = insufficient_data`, `risk = null`, `horizon = null`, текстовые причины и недостающие поля. | Реализовано в схеме и фикстуре `demo_assessment.py`. | Сохранить контракт в неизменном виде при переходе на реальные данные. | Backend (IGR) / Contract | **CURRENT** | Полностью соответствует принятой канонической схеме. |
| **Insufficient-data Operator Workflow** | ADR 0003 D3/D7: без скора и выдуманной маршрутизации. | Только fixture-карточка. | Отдельная «Not assessed / Incomplete data» с причинами; не нулевой, низкий или высокий риск. | Integrator Gate APR2-D3 | **PROPOSED MVP** (UI) / **BLOCKED** (операции) | Система не определяет дальнейшую операционную обработку; реальные полномочия и SOP UNKNOWN. |
| **Deterioration Horizon Display** | ADR 0003 (D6): `deterioration_horizon = null`, текст *«not estimable from supplied observations»*. | Поле `null` в фикстуре. В UI есть неактивная ветка `starts_at`. | Выводить явное честное сообщение о невозможности расчета времени деградации; убрать `starts_at` из UI. | Frontend (Denis) | **CURRENT** | Текущая контрактная политика — `null`. Требуется лишь очистка UI от неактивного отображения даты. |
| **Deterioration Countdown / Intervals** | ADR 0003 (D6): таймеры обратного отсчета и интервалы запрещены текущей доказательной базой (VDR-03). | Не реализовано. | Полностью исключить из скоупа MVP любые таймеры порчи и интервалы часов/дней. | Data (Viktor) / Domain | **DEFER** | Биологический онсет не может быть рассчитан на имеющихся 3 дискретных чекпоинтах качества. |
| **Score Method & Batch Context** | ADR 0003 D5/D8: baseline и допустимость пустого списка. | В fixture один `data_quality`, `effect: unknown`; это не baseline attribution. | Baseline `factors = []`; отдельно метод расчета и Batch Context с явным отсутствием установленного вклада. | Frontend / APR2-D4 | **PROPOSED MVP** | Контекст не является причиной/driver/contribution; Outcome 3 частично поддержан, атрибуция не поддержана. |
| **Model-Attribution XAI Factors** | ADR 0003 (D8): направления `increases_risk` / `decreases_risk` разрешены только при наличии валидированного алгоритма. | Не реализовано. | Отложить до появления отдельного XAI-модуля и согласования алгоритма объяснимости. | Analytics / Integrator | **DEFER** | Метод атрибуции не выбран и не валидирован; SHAP сам по себе не решает задачу. |
| **Recommendation Display** | ADR 0003 D9: `recommendation = null`. | `recommendation: None` в fixture. | Нейтральный блок недоступности без операционной инструкции. | Frontend / APR2-D5 | **CURRENT** (null) / **PROPOSED MVP** (copy) | Outcome 4 — **NOT SUPPORTED BY CURRENT EVIDENCE**, не выполнен через null. |
| **Prescriptive Action Catalogue** | ADR 0003 (D9): запрет рекомендаций вмешательств без валидированного каталога и контрфактических данных. | Не реализовано. | Исключить из MVP кнопки директивных вмешательств («доохладить», «сменить ТС», «утилизировать»). | Domain / Sponsor / Challenge | **DEFER** | В датасете нет контрфактов; каталог действий не утвержден организаторами челленджа. |
| **Reliability Level & Score** | ADR 0003 (D7): `reliability.level = unavailable`, `confidence_score = null`. | Реализовано в фикстуре (`level: "unavailable"`, `confidence_score: None`). | Сохранить контракт; в UI показывать статус «Unavailable» без выдумывания процентов. | Frontend (Denis) | **CURRENT** | Соответствует текущему каноническому контракту. |
| **Calibrated Confidence UI** | ADR 0003 (D7): запрет выдумывания процентов надежности и уровней low/med/high без калибровки. | Не реализовано. | Отложить до проведения статистической калибровки вероятностей и интервалов ошибок. | Data (Viktor) / Evaluation | **DEFER** | Метрики надежности требуют валидированной калибровочной кривой на отложенной выборке. |
| **Risk Categorization (Bands)** | ADR 0003 (D2): `risk.band = null`. Запрет волюнтаристских порогов high/mod/low. | Поле `band` опционально в схеме, отсутствует в выдаче. | Отложить цветовую классификацию рисков (светофоры) до появления операционных нормативов бизнеса. | Integrator / Business Gate | **DEFER** | Порог $\ge 15\%$ в VDR-04A был исследовательским; операционные пороги списаний неизвестны. |
| **Telemetry Narrative Boundary** | ADR 0002 / ADR 0003 D10: telemetry остается canonical input. | Typed canonical input и telemetry mapping реализованы в IGR-03; аналитика не сконфигурирована. | C+L — candidate feature-family simplification для будущего learned-engine decision; текущее принятое направление — crop-median baseline. | Data / Integrator / APR2-D6 | **PROPOSED NARRATIVE** / learned engine **DEFERRED** | VDR-04B — committed research, DRAFT FOR REVIEW — EVIDENCE ONLY. Некоторые P1 ranking metrics лучше у C+T+L; P2 robustness обычно за C+L. Monitoring/audit/diagnostics — UNKNOWN, не реализованы и не валидированы. |

---

# 9. PRODUCT DECISIONS REQUIRING HUMAN GATE (§9)

Ниже сформулированы 6 обязательных продуктовых развилок, требующих утверждения Интегратором (Human Gate). APR-02 takeover synthesis формулирует проблему, ограничения, варианты, компромиссы и дает рекомендации, но **НЕ принимает решение самостоятельно** (требуется Human Gate).

---

### DECISION APR2-D1: Primary User Persona for Smart Harvest MVP

- **FACT — sponsor brief:** Sponsor specifies only «farmer or storage operator», без конкретного job title, полномочий или SOP.
- **RECOMMENDATION — proposed amended decision:** Primary MVP design persona: **dispatch-side storage operator**. Рабочее имя `Dispatch Supervisor` — только **SoS design persona**, не sponsor FACT. Составная должность Dispatch Supervisor / Ramp Quality Inspector не канонизируется.
- **Why / trade-off:** Фокус на пользователе, принимающем или поддерживающем решения в момент отгрузки, помогает проектировать advisory Decision Support; он не устанавливает реальные обязанности сотрудника.
- **UNKNOWN:** Hold/release authority, отмена отгрузки, смена перевозчика/ТС, обязательный QC, подписание CMR/транспортных документов, требуемая процедура инспекции и реальный SOP.
- **Evidence / boundary:** Sponsor brief; ADR 0002 (момент оценки), ADR 0003 D1. APR-01 05–07 — исследовательские предложения, не доказательство полномочий.
- **Owner / decision gate:** Vladimir (Human Integrator). **PROPOSED — requires Human Gate; not approved.** При отсрочке design persona остается предложением.

---

### DECISION APR2-D2: Exact Operational Queue UX & Membership Policy

- **FACT:** Данные содержат `facility_id`, `dispatch_datetime` и `planned_dispatch_datetime`; авторитетные WMS readiness statuses отсутствуют.
- **OBSERVED RESULT:** VDR-02: `pre_dispatch` QC ровно за 2 часа до `dispatch_datetime` в supplied dataset. Этот synthetic dataset pattern не доказывает реальное warehouse operating window или SOP.
- **DECISION — ADR 0002 / ADR 0003 D3:** `assessment_timestamp = storage_sessions.dispatch_datetime`; сортировка `risk.score DESC, batch_id ASC` только внутри одной пары `engine_tier + engine_version`. Cross-engine comparability не валидирована. Порядок ID при равных скорах детерминированный и не означает различий риска.
- **RECOMMENDATION — proposed amended decision:** Для dataset-backed MVP/demo выбирать canonical recorded assessment events в **configurable replay/view window**. `facility_id` — только UI/context filter. `planned_dispatch_datetime` можно показывать как plan/schedule context, условно допустимый по ADR 0002; он не заменяет canonical assessment clock.
- **UNKNOWN / trade-off:** Точная длительность окна и реальная review capacity неизвестны; фиксированная квота K=10 запрещена. Pagination/scrolling — детали реализации. Replay из snapshot не устанавливает будущую live queue membership или реальный рабочий процесс.
- **Evidence / boundary:** Sponsor README; ADR 0002; ADR 0003 D3; VDR-01/02. Dataset observation не превращается в operational FACT.
- **Owner / decision gate:** Vladimir (Human Integrator). **PROPOSED — requires Human Gate; not approved.** До гейта membership остается предложением.

---

### DECISION APR2-D3: Operator Treatment of `insufficient_data` State

- **DECISION — ADR 0003 D3/D7:** `insufficient_data` имеет `risk = null`, `deterioration_horizon = null`, без числового скора; это не нулевой риск и не участник numeric ranking. Доступные `reason_codes` / `missing_requirements` объясняют ограничения.
- **RECOMMENDATION — proposed amended decision:** Отдельная нейтральная секция **Not assessed / Incomplete data**, визуально отличная от scored batches, без вывода о низком или высоком риске.
- **Proposed UI copy:** “No predictive score is available for this batch because required inputs were not satisfied. This does not mean low or high risk. Smart Harvest does not determine the operational disposition of this batch.”
- **UNKNOWN / boundary:** Операционная обработка и SOP неизвестны. Не назначать QC, автоматический пропуск или блокировку; система не знает обязательного следующего действия. Раздельное представление требует отдельной секции, но предотвращает смешение отсутствия оценки с величиной риска.
- **FACT — implementation:** Сейчас существует только synthetic insufficient-data fixture; proposed section не реализована. Точные engine minimums и fallback routing остаются открытыми.
- **Owner / decision gate:** Vladimir (Human Integrator). **PROPOSED — requires Human Gate; not approved.** При отсрочке действует null-contract, без изобретения workflow.

---

### DECISION APR2-D4: Minimum Truthful Explainability Baseline

- **DECISION — ADR 0003 D5/D8:** Принятое направление MVP — `baseline-crop-median-v1`: медиана `loss_fraction_pct` обучающей выборки по культуре, global training-median fallback для unseen crop. D8 разрешает factual context с `effect = unknown` либо пустой список; это не доказательство вклада контекста в baseline score.
- **RECOMMENDATION — proposed amended decision:** Для baseline **`factors = []`**. Отделить три понятия: механизм расчета, Batch Context и отложенную model attribution. Это продуктовый выбор в рамках D8, без изменения схемы или ADR.
- **How this score is computed:** “The score is derived from the historical median loss fraction for this crop in the training data.” Указать global training-median fallback для unseen crop и `risk.score = clip(predicted_loss_fraction_pct, 0, 100) / 100`; никаких вероятностей или confidence.
- **Batch Context:** Можно отдельно показывать crop, variety, storage duration, planned logistics и observed storage conditions с меткой “Context only; contribution to this score has not been established.” Не называть эти поля causes, drivers, contributing risk factors или model contributions; длительность рейса, тип ТС и pre-dispatch check не являются установленными вкладами в baseline score.
- **UNKNOWN / DEFERRED:** Метод model attribution, его референтный базис и валидация. `increases_risk` / `decreases_risk` запрещены до отдельного валидированного механизма; добавление SHAP само по себе не решает explainability.
- **Outcome 3 / trade-off:** Механизм скора объясним, контекст полезен отдельно, но атрибуция «what contributes to this risk» для текущего baseline не поддержана. Outcome 3 не выполнен полностью.
- **FACT — implementation:** В текущей synthetic fixture один `data_quality` factor с `effect = unknown`; baseline и предложенные UI-блоки не реализованы. Его не выдавать за baseline attribution.
- **Owner / decision gate:** Vladimir (Human Integrator). **PROPOSED — requires Human Gate; not approved.** При отсрочке не фабриковать factors.

---

### DECISION APR2-D5: Honest Representation of Challenge Outcome 4 (Recommendations)

- **DECISION — ADR 0003 D9:** Сохраняется **`recommendation = null`**; действие требует отдельного evidence-гейта.
- **FACT / evidence boundary:** Sponsor Outcome 4 требует приоритизированного действия; текущие данные не устанавливают intervention effects или validated action catalogue (VDR-03; APR-01 evidence map).
- **RECOMMENDATION — proposed amended decision:** Outcome 4 — **NOT SUPPORTED BY CURRENT EVIDENCE**. Показать нейтральный блок недоступности; он не закрывает Outcome 4. Ранжирование партий по assessment score не является рекомендацией вмешательства.
- **Proposed UI copy:** “Action recommendations are unavailable. Current evidence does not validate intervention effectiveness. Smart Harvest prioritizes batches for review but does not prescribe an operational action.” Последняя фраза описывает proposed ranking capability; текущий runtime остается fixture без очереди.
- **UNKNOWN / boundary:** Каталог действий, эффективность вмешательств и реальные операционные процедуры неизвестны. Блок не должен ссылаться на warehouse SOP, назначать действия, перечислять примерные рекомендации или обещать экономию.
- **Trade-off:** Явное сообщение объясняет недоступность, но сохраняет незакрытое требование спонсора. FACT: в fixture `recommendation = null`; предлагаемый текст не реализован.
- **Owner / decision gate:** Vladimir (Human Integrator). **PROPOSED — requires Human Gate; not approved.** При отсрочке null сохраняется, Outcome 4 остается неподдержанным.

---

### DECISION APR2-D6: Telemetry Evidence / MVP Narrative Boundary (VDR-04B Product Implication)

- **DECISION — ADR 0002 / ADR 0003 D5/D10:** Telemetry остается canonical input. Принятое направление MVP остается deterministic crop-median baseline; он еще не реализован в приложении. Learned engine и final feature subset не выбраны.
- **OBSERVED RESULT — VDR-04B:** Для tested Ridge/HGB representations агрегированная telemetry не дала стабильного marginal improvement поверх planned-logistics-enabled features. C = pre-dispatch context (не только crop), T = aggregate telemetry, L = planned logistics. P1 и P2 не дают одинаковых выводов: некоторые P1 ranking metrics лучше у C+T+L; P2 robustness в целом за C+L.
- **Benchmark context:** HGB, P1 forward inter-season (2024 train / 2025 test): NDCG@10 C+L = 0.8695, C+T+L = 0.8831; P2 chamber-time grouped OOF: 0.9150 и 0.8888 соответственно. Это offline learned-model results, не качество runtime или crop-median baseline (VDR-04B report и results JSON).
- **INFERENCE / RECOMMENDATION — proposed amended decision:** C+L — **candidate feature-family simplification for a future learned-engine decision**. Он не является выбранной production model, текущей MVP analytics architecture или approved learned engine. Результат не разрешает удалить telemetry и не устанавливает ее общую бесполезность.
- **UNKNOWN:** Monitoring, storage-condition audit, diagnostics и equipment-health detection — возможные будущие гипотезы; VDR-04B их не валидировал, текущая реализация их не предоставляет.
- **Research status / boundary:** VDR-04B — **committed research evidence used by this proposed Human Gate package**, со статусом **DRAFT FOR REVIEW — EVIDENCE ONLY**. Приемка как project evidence остается решением Human Integrator; коммит и этот пакет не делают отчет каноном.
- **Trade-off:** Кандидат упрощения уменьшает число feature families, но не доказывает универсального превосходства и требует отдельного learned-engine решения.
- **Owner / decision gate:** Vladimir (Human Integrator). **PROPOSED — requires Human Gate; not approved.** При отсрочке telemetry остается canonical, baseline direction сохраняется, learned-engine выбор не производится.

---

# 10. PENDING UX DEPENDENCIES (PUX-08 BOUNDARY §15)

В соответствии с контрактом APR-02 фиксируются строгие границы взаимодействия с воркстримом UX (Денис):

1. **Статус PUX-08:**  
   **FACT:** `docs/recon/PUX-08-data-ux-reconciliation.md` интегрирован через PR #22, но сохраняет **DRAFT FOR REVIEW**. **DECISION BOUNDARY:** integration не означает принятия рекомендаций; они **NOT CANON**, не авторитетны сами по себе и требуют соответствующего Integrator/Human Gate.
2. **Предложения vs Решения:**  
   Все предложения Дениса по структуре экранов, бейджам, карточкам и фильтрам являются профессиональными рекомендациями, но **не имеют статуса командных решений** до утверждения Интегратором.
3. **Отсутствие необходимости реконсиляции:**  
   В рамках APR-02 не требуется проводить принудительное согласование текста с черновиком PUX-08.
4. **Реестр ожидающих UX-зависимостей (Pending Items):**
   - *UX-DEP-1:* Верстка интерактивной таблицы очереди приоритизации партий (`Triage Queue`) с поддержкой сортировки `risk.score DESC, batch_id ASC` (зависит от решения APR2-D2).
   - *UX-DEP-2:* Реализация раздельного отображения партий со статусом `insufficient_data` (зависит от решения APR2-D3).
   - *UX-DEP-3:* Очистка компонента `AssessmentCard.tsx` от неактивных полей `risk.band`, `confidence_score` и `deterioration_horizon.starts_at`.
   - *UX-DEP-4:* Отдельные «How this score is computed» и «Batch Context» при baseline `factors = []`; нейтральный блок `recommendation = null`, не закрывающий Outcome 4 (зависит от APR2-D4/D5).

---

# 11. ПЕРЕЧЕНЬ ЗАПРЕЩЁННЫХ УТВЕРЖДЕНИЙ И ДЕЙСТВИЙ (§18)

В соответствии с требованиями контракта APR-02 подтверждается строгое соблюдение запретов:
- [x] **ЗАПРЕЩЕНО** называть текущую синтетическую фикстуру работающим аналитическим или предиктивным MVP.
- [x] **ЗАПРЕЩЕНО** выдавать offline VDR-04A P1 HGB F3 (Context + Telemetry + Planned logistics) NDCG@10 = 0.8831, Precision@10 = 1.0 за runtime performance MVP baseline или production accuracy.
- [x] **ЗАПРЕЩЕНО** Product Owner'у самостоятельно выбирать или утверждать архитектуру learned ML-модели.
- [x] **ЗАПРЕЩЕНО** вводить любые новые пороги риска или категориальные диапазоны (`risk.band = low/mod/high`).
- [x] **ЗАПРЕЩЕНО** создавать каталог действий или перечень автоматических рекомендаций.
- [x] **ЗАПРЕЩЕНО** устанавливать значение `recommendation ≠ null` без прохождения формального action-гейта.
- [x] **ЗАПРЕЩЕНО** проектировать или обещать таймеры обратного отсчета до порчи (deterioration countdown).
- [x] **ЗАПРЕЩЕНО** использовать градации надежности low/medium/high или числовые проценты уверенности без валидированной статистической калибровки.
- [x] **ЗАПРЕЩЕНО** придумывать операционную пропускную способность (capacity) оператора (квоту K=10 и т.п.).
- [x] **ЗАПРЕЩЕНО** придумывать обязательную автоматическую маршрутизацию партий `insufficient_data` на ручной QC.
- [x] **ЗАПРЕЩЕНО** превращать черновик PUX-08 в нормативное командное решение (DECISION).
- [x] **Граница APR-02F:** Разрешены только этот файл, `09_product_acceptance_traceability.md` и status-only repair в `docs/decisions/0003-assessment-evaluation-semantics.md`; принятые ADR-решения и provenance не меняются. Остальной канон, VDR-04B, PUX-08 и application code вне write scope.

---
*Документ подготовлен в рамках APR-02 takeover synthesis (Vladimir — Integrator) из-за таймбокса финала тренировки для передачи на рассмотрение Human Gate.*
*Конец спецификации.*
