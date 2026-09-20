STATUS: RESEARCH NOTE — NOT CANON

# APR-01: Proposed Operator Product Workflow (Step 7 Synthesis)

**Owner:** Alisa — Product Owner  
**Workstream:** APR-01 Product & Requirements Recon  
**Status:** Step 7 Research Note (NOT CANON)  
**Base SHA:** `aa5d40bee8368342e7a6b540278c26416cc89457`  
**Target File:** `docs/product_recon/06_proposed_product_workflow.md`  

---

## 0. Назначение и границы документа

Настоящий документ формулирует **предлагаемый продуктовый сценарий работы оператора (Proposed Operator Product Workflow)** для системы **Smart Harvest** в рамках воркстрима **APR-01 (Шаг 7)**.

Документ объединяет в единый сквозной пользовательский путь:
1. Кандидатную целевую персону (*Dispatch Supervisor / Ramp Quality Inspector* `[RECOMMENDATION — requires TEAM DECISION]`) и модель решений из [05_user_decision_model.md](05_user_decision_model.md);
2. Четыре обязательных вопроса-исхода спонсорского пакета челленджа `[CHALLENGE FACT]`;
3. Нормативные границы допустимости входных данных и оценку strictly at $T_{assess} \equiv T_{dispatch}$ ([ADR 0002](0002-predictive-input-semantics.md));
4. Эмпирические факты данных по дискретности качества и отсутствию наблюдаемого онсета порчи ([VDR-03](../data_recon/03_target_horizon_feasibility.md));
5. Разделение между доказанной реализуемостью ранжирования на бенчмарке ([VDR-04A](../data_recon/04_dispatch_predictability.md)) и предлагаемым, но ещё не принятым продуктовым сценарием приоритизации;
6. Безусловное сохранение схемы и семантики существующего контракта `RiskAssessment` ([backend/app/domain/assessment.py](../../backend/app/domain/assessment.py), [docs/data_contract.md](../data_contract.md)).

> [!IMPORTANT]
> **Границы проектирования (Product Workflow vs. UI Design):**
> Настоящий документ описывает **логику и этапы принятия решений оператором**, состав необходимой информации, зависимости от данных и защитные барьеры. Документ **НЕ проектирует конкретные экранные формы, кнопки, цветовую палитру или визуальную разметку интерфейса**. Разработка макетов UI/UX относится к компетенции дизайнера/фронтенд-инженера (prscr) и будет выполнена на основе настоящей продуктовой модели.

---

## 1. Сквозной путь оператора (Operator Decision Path)

Путь оператора охватывает 8 последовательных логических фаз:

```
[1. Вход оператора]
       |
       v
[2. Обнаружение приоритетной проблемы] (Ранжированная очередь отгрузки — кандидатный фрейминг)
       |
       v
[3. Выбор партии (Triage)] (Фокус на партии с повышенным риском в пределах рабочей очереди)
       |
       v
[4. Понимание уровня риска] (Оценка статуса assessed/insufficient_data, скора и risk.band)
       |
       v
[5. Понимание физических причин] (Анализ факторов с категориями storage, environmental, transport)
       |
       v
[6. Понимание срочности и горизонта] (Сопоставление с planned_duration_hours; horizon=null)
       |
       v
[7. Оценка возможного действия] (Анализ кандидатного класса действия; recommendation nullable)
       |
       v
[8. Решение оператора] (Утверждение действия человеком; requires_human_review = true)
```

---

## 2. Пошаговая спецификация этапов рабочего процесса

### Этап 1: Вход оператора и ориентация в смене (User Entry & Shift Orientation)
* **Цель этапа:** Инициализация рабочего контекста диспетчера рампы на начало операционного окна погрузки.
* **Действие оператора:** Оператор входит в систему Smart Harvest, выбирает своё предприятие (`facility_id`) и рабочую дату.
* **Закрываемый вопрос пользователя:** *«Какие партии назначены на отгрузку в текущее операционное окно?»*
* **Необходимая информация на $T_{dispatch}$ `[PREDICTIVE_ELIGIBLE / CONTEXT_ONLY]`:**
  * `facilities.facility_id`, `facilities.facility_name`;
  * Список партий, у которых `storage_sessions.dispatch_datetime` попадает в текущий рабочий интервал;
  * Связанные метаданные партий: `batches.crop_type`, `batches.variety`, `storage_sessions.zone_id`, `storage_sessions.storage_session_id`.
* **Допустимость по ADR 0002:** Полностью допустимо (контекстная и статическая информация объекта).
* **Эпистемический статус:** `[DOMAIN FACT]` (стандартное начало операционной смены).

---

### Этап 2: Обнаружение приоритетной проблемы (Priority Problem Detection)
* **Цель этапа:** Выявление партий, требующих первоочередного внимания, среди назначенных к отправке.
* **Действие оператора:** Оператор просматривает сводную очередь отгрузки, упорядоченную по уровню риска.
* **Закрываемый вопрос челленджа:** **Outcome 1: «Which batches are most at risk?»** `[CHALLENGE FACT]`.
* **Разделение статусов валидации и продукта:**
  * **`ranking feasibility: SUPPORTED BY BENCHMARK`** (исследование VDR-04A показало, что при использовании доступных на $T_{dispatch}$ плановых параметров логистики модели демонстрируют высокую точность ранжирования верхнего среза на ретроспективном тесте: Precision@10 = 100.0%, NDCG@10 = 0.88);
  * **`production risk prioritisation workflow: PROPOSED / NOT YET ADOPTED`** (интерфейсный фрейминг очереди носит статус `RECOMMENDATION / candidate product framing — requires VLD-02B / human integration decision`; точный операционный порог отсечки и размер рабочей квоты не зафиксированы и не приравниваются жёстко к K=10).
* **Отображаемые поверхности существующего контракта `RiskAssessment`:**
  * `RiskAssessment.status`: `assessed` против `insufficient_data`;
  * `RiskAssessment.risk.score`: числовое значение $\in [0, 1]$ (ключ сортировки очереди);
  * `RiskAssessment.risk.band`: буквальные значения перечисления `low`, `moderate`, `high` (значение `medium` отсутствует в контракте);
  * `RiskAssessment.reliability.level`: уровень надёжности сформированной оценки (`high`, `medium`, `low`, `unavailable`).
* **Эпистемический статус:** `[CHALLENGE FACT]` + `[DATA FACT — VDR-04A]` (бенчмарк ранжирования) + `[RECOMMENDATION]` (продуктовый сценарий очереди).

---

### Этап 3: Выбор партии для детального контроля (Batch Selection & Triage)
* **Цель этапа:** Фиксация рабочей единицы и переход к анализу партии перед погрузкой.
* **Действие оператора:** Диспетчер выбирает партию из верхней части списка риска (или партию, транспорт под которую уже подан к рампе) для детального анализа.
* **Закрываемый вопрос пользователя:** *«Каковы паспортные, качественные и логистические параметры выбранной партии?»*
* **Необходимая информация на $T_{dispatch}$ `[PREDICTIVE_ELIGIBLE / CONDITIONALLY_ELIGIBLE]`:**
  * `batches.batch_id`, `batches.harvest_datetime`, `batches.harvest_weight_kg`;
  * `storage_sessions.storage_duration_days`, `storage_sessions.bin_stack_tier`, `storage_sessions.storage_session_id`;
  * `shipments.destination_market`, `shipments.vehicle_type`, `shipments.planned_duration_hours`.
* **Допустимость по ADR 0002:** Полностью допустимо.
* **Эпистемический статус:** `[DOMAIN FACT]` (выбор партии по графику подачи автотранспорта).

---

### Этап 4: Понимание уровня риска и статуса данных (Risk Understanding)
* **Цель этапа:** Оценка надёжности предиктивного предупреждения и полноты данных.
* **Действие оператора:** Оператор проверяет статус оценки партии:
  * **Случай А (`status == AssessmentStatus.ASSESSED`):** Партия имеет достаточную доказательную базу; оператор считывает величину `risk.score`, диапазон `risk.band` (`low`, `moderate`, `high`) и уровень достоверности `reliability.level`.
  * **Случай Б (`status == AssessmentStatus.INSUFFICIENT_DATA`):** Данные телеметрии или контроля признаны недостаточными согласно политике валидации. Поля `risk` и `deterioration_horizon` возвращаются как `None` (согласно валидатору схемы Pydantic для `insufficient_data`). Система информирует оператора кодами причин `reliability.reason_codes` (например, `telemetry_truncated_pre_dispatch`) и переводит процесс в режим **ручной обязательной инспекции QC**.
* **Закрываемый вопрос челленджа:** **Outcome 1: «Which batches are most at risk?»** `[CHALLENGE FACT]`.
* **Защитный контракт:** `risk.score` не интерпретируется как калиброванная вероятность брака, а служит относительной мерой риска `[DATA FACT — VDR-04A / docs/data_contract.md]`.
* **Эпистемический статус:** `[CHALLENGE FACT]` + `[TEAM DECISION]` (обработка `insufficient_data` по канону контракта).

---

### Этап 5: Понимание физических причин риска (Cause / Factor Understanding)
* **Цель этапа:** Получение оператором прозрачного физического объяснения риска для исключения недоверия к алгоритму (Grant et al. 2026).
* **Действие оператора:** Оператор раскрывает структурированный блок причин риска `factors`.
* **Закрываемый вопрос челленджа:** **Outcome 3: «What factors contribute to the risk?»** `[CHALLENGE FACT]`.
* **Отображаемые поверхности контракта `RiskAssessment.factors`:**
  * Список структурированных объектов `AssessmentFactor` со строгим соблюдением перечислений `backend/app/domain/assessment.py`:
    * `code: str` (машиночитаемый код фактора);
    * `category: FactorCategory`: строго из набора `data_quality`, `environmental`, `storage`, `transport`, `inventory`, `historical`;
    * `effect: FactorEffect`: `increases_risk`, `decreases_risk`, `unknown`;
    * `summary: str` (пояснение на естественном языке с физическими величинами и описанием условий);
    * `evidence_references: list[str]` (ссылки на источники данных).
* **Пример наполнения с учётом ограничений семантики `[INFERENCE / RECOMMENDATION]`:**
  1. *storage:* «elevated temperature exposure (накопление температурного стресса выше целевой уставки хранения в камере)» `[DATA FACT — VDR-01]`;
  2. *environmental:* «циклы оттайки испарителя с флагом `condensation_flag = True` (составная семантика: цикл оттайки испарителя либо расчётная точка росы)» `[DATA FACT — VDR-01]`;
  3. *inventory:* «measured firmness decline (зафиксированное снижение твёрдости мякоти плодов между сбором и предотгрузочным контролем)» `[DATA FACT — VDR-01]`;
  4. *transport:* «longer planned transit (длительная плановая транспортировка в обычном тентованном транспорте `Ambient Truck` для чувствительной культуры)» `[DATA FACT — VDR-04A]`.
* **Эпистемический статус:** `[CHALLENGE FACT]` (требование выявления факторов) + `[DOMAIN FACT]` (XAI в агрономии).

---

### Этап 6: Понимание срочности и горизонта риска (Urgency & Horizon Context)
* **Цель этапа:** Оценка запаса стойкости партии относительно сложности предстоящего маршрута.
* **Действие оператора:** Оператор сопоставляет состояние партии с параметрами планового рейса.
* **Закрываемый вопрос челленджа:** **Outcome 2: «When may quality begin to deteriorate?»** `[CHALLENGE FACT]`.
* **Позиция по контракту и данным (VDR-03 Anchor) `[DATA FACT — VDR-03]`:**
  * CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping deterioration_horizon null until later evidence + integration decision support population;
  * **Запрет ложной точности:** Система **НЕ отображает** фиктивный обратный отсчёт до порчи;
  * **Запрет спекуляций о моменте порчи:** Система **не имеет права утверждать точку времени, когда деградация фактически начнётся** (включая утверждения «порча начнётся во время рейса»);
  * **Реализация контекста Outcome 2:** Поле `shipments.planned_duration_hours` используется оператором исключительно как **контекстный предиктор риска некондиции к моменту прибытия (Arrival-Condition Risk)** `[DATA FACT — VDR-03 / RECOMMENDATION]`.
* **Эпистемический статус:** `[CHALLENGE FACT]` + `[DATA FACT — VDR-03]` (отсутствие непрерывного горизонта порчи).

---

### Этап 7: Оценка возможного действия (Candidate Action Evaluation)
* **Цель этапа:** Анализ предложенного варианта вмешательства с учётом доступности ресурсов.
* **Действие оператора:** Оператор просматривает блок рекомендации `recommendation`.
* **Закрываемый вопрос челленджа:** **Outcome 4: «What action should be prioritised?»** `[CHALLENGE FACT]`.
* **Отображаемые поверхности контракта `RiskAssessment.recommendation`:**
  * Если алгоритм формирования рекомендаций ещё не валидирован, поле **`recommendation` остаётся `null`** (`Optional[Recommendation] = None`);
  * Если рекомендация сформирована:
    * `action_code: str` (код кандидата, не являющийся утверждённым production-контрактом);
    * `label: str` (понятное операционное наименование);
    * `priority: RecommendationPriority`: строго из набора `informational`, `low`, `medium`, `high` (значение `critical` отсутствует в контракте);
    * `rationale_codes: list[str]` (коды связанных факторов риска);
    * `requires_human_review: bool` (APR-01 candidate corrective actions require human review; the existing field defaults to true, while any broader production invariant would require a shared-contract/product decision).
* **Кандидатные классы действий (не production-контракты):**
  * Класс 1: Стандартный допуск к погрузке (Standard Clearance);
  * Класс 2: Технологическая задержка на рампе для контроля QC (Operational Hold & Re-inspection);
  * Класс 3: Предрейсовое доохлаждение партии (Pre-cooling Treatment);
  * Класс 4: Рекомендация назначения рефрижератора (Refrigerated Transport Reassignment);
  * Класс 5: Сокращение маршрута или переработка (Route Shortening / Processing Diversion).
* **Эпистемический статус:** `[CHALLENGE FACT]` + `[DOMAIN FACT]` (процедуры склада) + `[TEAM DECISION]` (APR-01 candidate corrective actions require human review; existing field defaults to true). Никакое действие не объявляется «оптимальным», и каузальный выигрыш не утверждается.

---

### Этап 8: Принятие решения человеком (Human Decision & Execution)
* **Цель этапа:** Окончательное утверждение или отклонение рекомендации человеком и оформление статуса партии.
* **Действие оператора:** Оператор принимает ответственное производственное решение:
  1. **Подтвердить рекомендацию (Accept):**
     * При стандартном допуске $\to$ подписание разрешения на погрузку;
     * При необходимости контроля/охлаждения $\to$ передача заявки службе качества или технологу камер;
  2. **Отклонить / Переопределить рекомендацию (Override):**
     * При наличии внешних коммерческих условий оператор подтверждает выпуск партии с фиксацией причины в журнале.
* **Полномочия сотрудника `[UNKNOWN / CONTRACT-DEPENDENT]`:** Объем полномочий оператора рампы по задержке груза, замене перевозчика или отмене рейса определяется внутренними регламентами предприятия и контрактами с грузовладельцами.
* **Эпистемический статус:** `[DOMAIN FACT]` (человек несёт окончательную ответственность за выпуск продукции).

---

## 3. Матрица верификации этапов Workflow против вопросов челленджа

| Этап Workflow | Вопрос оператора / челленджа | Необходимая информация к $T_{dispatch}$ | Соответствие ADR 0002 | Зависимость от Data Recon (VDR) | Эпистемический статус |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Этап 1 (Вход)** | Каков план отгрузки на смену? | `facilities.*`, расписание отгрузок, `storage_session_id` | Контекст | VDR-01 (10 предприятий, 25 камер) | `[DOMAIN FACT]` |
| **Этап 2 (Очередь)** | **Outcome 1: Which batches are most at risk?** | `RiskAssessment.status`, `risk.score`, `risk.band` (`low`, `moderate`, `high`) | Safe output | VDR-04A (Ранжирование: Precision@10 = 100%, NDCG@10 = 0.88) | `[CHALLENGE FACT]` / `[DATA FACT]` / `[RECOMMENDATION]` |
| **Этап 3 (Выбор)** | Каковы параметры выбранной партии? | `batches.*`, `storage_sessions.*`, `shipments.planned_*` | PREDICTIVE / CONDITIONAL | VDR-01 (Связь 1:1:1:1 между батчем, сессией и рейсом) | `[DATA FACT — VDR-01]` |
| **Этап 4 (Риск)** | Насколько надёжна оценка партии? | `status`, `risk.score`, `reliability.level`, `reason_codes` | Safe output | VDR-01/02 (Обработка пропусков в ZONE-006 и обрыва 2026 года) | `[TEAM DECISION]` |
| **Этап 5 (Причины)**| **Outcome 3: What factors contribute to the risk?** | `factors[]` (категории `storage`, `environmental`, `transport`, `inventory`) | Safe output | VDR-01 (Телеметрия 30 мин), VDR-02 (Строгий срез по $T_{dispatch}$) | `[CHALLENGE FACT]` / `[DOMAIN FACT]` |
| **Этап 6 (Срочность)**| **Outcome 2: When may quality begin to deteriorate?** | `planned_duration_hours`, `deterioration_horizon` (строго `null`) | Safe output | VDR-03 (Запрет continuous countdown; context predictor only) | `[CHALLENGE FACT]` / `[DATA FACT]` |
| **Этап 7 (Действие)**| **Outcome 4: What action should be prioritised?** | `recommendation` (nullable; priority `low`, `medium`, `high`, `informational`) | Safe output | VDR-04A (Логистика как фактор риска; action space unvalidated) | `[CHALLENGE FACT]` / `[DOMAIN FACT]` |
| **Этап 8 (Решение)**| Выпускать ли партию на рампе? | Экспертная оценка оператора, физический осмотр паллет | Вне модели | Полномочия зависят от контракта объекта (APR-01 Step 6) | `[DOMAIN FACT / UNKNOWN]` |

---

## 4. Градация информационной насыщенности (Information Tiers)

Для предотвращения когнитивной перегрузки диспетчера рампы информация разделяется на два эшелона `[RECOMMENDATION]`:

### Эшелон А: Минимально полезная информация (First Screen Glance)
Состав данных, доступный в строке рабочей очереди отгрузки:
1. **Идентификатор и биология:** `batch_id`, `crop_type`, `variety`;
2. **Маршрутный контекст:** `destination_market`, `vehicle_type`, `planned_duration_hours`;
3. **Статус оценки данных:** `status` (`assessed` или `insufficient_data`);
4. **Приоритет риска:** визуальный индикатор относительного ранга (на основе `risk.score` и `risk.band`);
5. **Ключевой фактор:** краткое описание доминирующего фактора риска;
6. **Рекомендуемое действие:** краткий ярлык действия или статус отсутствия рекомендации (`null`).

### Эшелон Б: Вторичная детальная информация (Deep Inspection Drawer)
Раскрывается при детальном анализе партии:
1. **История хранения:** Номер камеры (`zone_id`), ярус штабелирования (`bin_stack_tier`), срок хранения `storage_duration_days`, идентификатор `storage_session_id`;
2. **Динамика микроклимата:** График и интегральные показатели температуры камеры, среднее отклонение от уставки, факты циклов оттайки с флагом конденсации;
3. **Инструментальный тренд качества:** Сравнительная таблица замеров при сборе (`harvest`) и перед отгрузкой (`pre_dispatch`): падение твёрдости мякоти ($\Delta Firmness$), сахаристость ($\Delta Brix$), дефекты ($\Delta Defect$);
4. **Полный массив факторов:** Развёрнутый список `factors[]` со строгими категориями `FactorCategory` и текстовыми пояснениями;
5. **Обоснование рекомендации:** Коды причин (`rationale_codes`), статус обязательности ручной проверки (APR-01 candidate corrective actions require human review; existing field defaults to true), приоритет `priority`;
6. **Метаданные достоверности:** Уровень надёжности (`reliability.level`), причины снижения качества данных (`reason_codes`), версия предиктивного движка (`provenance`).

---

## 5. Запрещённые продуктовые обещания (Claims We Must NOT Make Yet)

Для защиты профессиональной репутации команды SoS перед жюри устанавливаются **строгие негативные границы продуктовых обещаний** `[RECOMMENDATION / TEAM DECISION]`:

1. **МЫ НЕ ОБЕЩАЕМ точный таймер порчи:** В данных нет непрерывного биологического датчика деградации. CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping deterioration_horizon null until later evidence + integration decision support population. Мы также не утверждаем, что порча «начнётся в ходе рейса» `[DATA FACT — VDR-03]`;
2. **МЫ НЕ УТВЕРЖДАЕМ, что `risk.score` — это строгая калиброванная вероятность брака:** Числовой скор риска отражает относительный ранг уязвимости партии в текущей выборке и используется для приоритизации очереди, но не откалиброван как статистическая вероятность финансового убытка `[DATA FACT — VDR-04A / docs/data_contract.md]`;
3. **МЫ НЕ ПРЕДЛАГАЕМ полностью автоматическое вмешательство без человека:** Система является советчиком (Decision Support System). Любое кандидатное корректирующее действие требует подтверждения уполномоченным персоналом (requires_human_review в схеме имеет значение по умолчанию true; кандидаты APR-01 требуют человеческой верификации) `[DOMAIN FACT / Greer et al. 1994]`;
4. **МЫ НЕ ЗАЯВЛЯЕМ каузального снижения потерь:** Мы не обещаем спасение X% продукции, так как в наблюдательном датасете отсутствуют контрфактические исходы `[DATA FACT — VDR-04A]`;
5. **МЫ НЕ ЗАЯВЛЯЕМ способность предсказывать дорожные аварии рефрижераторов:** Внезапный механический отказ компрессора в пути (`cold_chain_incident`) является стохастическим пост-отгрузочным шоком, который физически невозможно спрогнозировать из данных склада `[DATA FACT — VDR-02 / ADR 0002]`.

---

## 6. Сводка обязательных открытых неизвестных рабочего процесса (Workflow UNKNOWNs Register)

В соответствии с каноническими правилами проекта и границами этапа APR-01 предложенный операторский сценарий оставляет строго открытыми следующие 14 критических неизвестных:

| № | Открытый вопрос (UNKNOWN) | Гейт / Орган принятия решения | Влияние на продуктовый рабочий процесс (Workflow) |
| :-: | :--- | :---: | :--- |
| **1** | **Primary Smart Harvest persona** | `[TEAM DECISION / UNKNOWN]` | Сценарий сфокусирован на диспетчере рампы (*Dispatch Supervisor*), однако окончательный выбор целевой роли требует междисциплинарного утверждения командой SoS. |
| **2** | **Точные полномочия выбранной persona** | `[UNKNOWN / CONTRACT-DEPENDENT]` | Влияет на этапы 7–8: имеет ли линейный оператор право единолично отменить рейс или заказать рефрижератор, либо эти действия требуют эскалации на коммерческую службу. |
| **3** | **Фактический operational dispatch workflow конкретных объектов** | `[CANDIDATE PROPOSAL / UNKNOWN]` | 8-этапный сценарий является аналитическим синтезом отраслевых регламентов и требует эмпирической валидации на реальных регламентах складов Молдовы. |
| **4** | **Permitted action space challenge** | `[CHALLENGE CLARIFICATION / UNKNOWN]` | Рекомендации этапа 7 носят статус кандидатных классов действий до прояснения критериев оценки исхода 4 организаторами челленджа. |
| **5** | **Deterioration-onset semantics** | `[DATA/EVALUATION DECISION / UNKNOWN]` | На этапе 6: CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping deterioration_horizon null until later evidence + integration decision support population. Семантика деградации моделируется через риск некондиции по прибытии (`planned_duration_hours`), а не через непрерывный обратный отсчёт. |
| **6** | **Production target** | `[DATA/EVALUATION DECISION (VLD-02B) / UNKNOWN]` | Влияет на математический смысл `risk.score` на этапах 2 и 4; окончательный выбор таргета передан на гейт VLD-02B. |
| **7** | **Risk threshold / band semantics** | `[DATA/EVALUATION DECISION / TEAM DECISION / UNKNOWN]` | В интерфейсе очереди отгрузки (этап 2) не вводятся волюнтаристские пороги; диапазоны `risk.band` (`low`, `moderate`, `high`) требуют калибровки совместно с Data & Evaluation. |
| **8** | **Telemetry sufficiency / staleness policy** | `[DATA/EVALUATION DECISION / UNKNOWN]` | Определяет условие срабатывания аварийного сценария этапа 4Б (`status: 'insufficient_data'`) при нехватке временных рядов телеметрии. |
| **9** | **Treatment 204 truncated batches** | `[DATA/EVALUATION DECISION / UNKNOWN]` | Порядок отображения 204 партий 2026 года с усечённой предотгрузочной телеметрией зависит от утверждённой политики минимальной достаточности данных. |
| **10** | **Actual costs / capacity corrective actions** | `[UNKNOWN]` | Влияет на расчёт приоритета действий на этапе 7: какова реальная стоимость простоя ТС на рампе и доступность свободных мощностей охлаждения в регионах Молдовы. |
| **11** | **Validated intervention effects** | `[UNKNOWN — NO COUNTERFACTUAL DATA IN DATASET]` | Сценарий не моделирует гарантированный процент спасения продукции от вмешательств, так как в наблюдательном датасете отсутствуют контрфактические исходы. |
| **12** | **Accepted agronomic thresholds / rules** | `[UNKNOWN — PENDING DOMAIN RULE ADMISSION]` | Физические пороги факторов (этап 5) взяты из литературы и ожидают официального внесения в канонический свод `docs/domain_rules.md`. |
| **13** | **Evaluation split / metric / baseline** | `[DATA/EVALUATION DECISION (Viktor VDR-04 / VLD-02B)]` | Метрики ранжирования очереди исследованы в VDR-04A и подлежат утверждению в VLD-02B. |
| **14** | **Quantitative loss-reduction claims** | `[UNKNOWN / PROHIBITED CLAIM WITHOUT DEPLOYMENT]` | Категорический запрет любых числовых обещаний эффекта («сохранение X тонн ягод») на всех этапах пользовательского интерфейса и документации. |

---

## 7. Междисциплинарные связи и зависимости продуктового процесса

* **Implementation dependencies (Backend / Shared Contract):**
  * Продуктовый сценарий опирается на контракт `RiskAssessment` из `backend/app/domain/assessment.py` и `docs/data_contract.md`;
  * Для партий с неполными данными возвращается `status: AssessmentStatus.INSUFFICIENT_DATA`, при этом `risk = None` и `deterioration_horizon = None`;
  * CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping `deterioration_horizon` null until later evidence + integration decision support population;
  * Массив `factors` наполняется объектами со строгими категориями `FactorCategory` (`storage`, `environmental`, `transport`, `inventory`, `historical`, `data_quality`);
  * Первичный ключ сессии: `storage_sessions.storage_session_id`;
  * До утверждения логики рекомендаций поле `recommendation` возвращается как `None`;
  * APR-01 candidate corrective actions require human review; the existing field defaults to true, while any broader production invariant would require a shared-contract/product decision; приоритет выбирается из `informational`, `low`, `medium`, `high`.
* **Questions for Data & Evaluation / Proposed VLD-02B decision:**
  * Результаты VDR-04A подтверждают реализуемость ранжирования на бенчмарке (`ranking feasibility: SUPPORTED BY BENCHMARK`), но продуктовый сценарий очереди остаётся проектным предложением (`PROPOSED / NOT YET ADOPTED`);
  * Выбор итогового таргета и калибровка порогов `risk.band` (`low`, `moderate`, `high`) осуществляются на гейте VLD-02B;
  * Правила обработки 204 партий 2026 года и определение политики достаточности телеметрии подлежат утверждению в рамках VLD-02B.
* **UX candidate — pending TEAM/INTEGRATOR decision:**
  * Сценарий пользовательского интерфейса моделирует работу диспетчера рампы (`RECOMMENDATION — requires TEAM DECISION`);
  * Очередь отгрузки по уровню риска предлагается как режим приоритизации (Triage Queue), не навязывая фиксированной квоты «топ-10»;
  * Кандидатный интерфейс не отображает таймеров обратного отсчёта до порчи плодов;
  * Карточка партии формирует факторы риска с учётом составной природы `condensation_flag = (surface <= dew) OR defrost_on`.
