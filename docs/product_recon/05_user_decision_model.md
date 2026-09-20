STATUS: RESEARCH NOTE — NOT CANON

# APR-01: Evidence-Backed User Decision Model (Step 6 Synthesis)

**Owner:** Alisa — Product Owner  
**Workstream:** APR-01 Product & Requirements Recon  
**Status:** Step 6 Research Note (NOT CANON)  
**Base SHA:** `aa5d40bee8368342e7a6b540278c26416cc89457`  
**Target File:** `docs/product_recon/05_user_decision_model.md`  

---

## 0. Назначение, цель и методологические рамки документа

Настоящий документ формирует **доказательно обоснованную модель принятия операционных решений (Evidence-Backed User Decision Model)** для системы поддержки решений **Smart Harvest** в рамках воркстрима **APR-01 (Шаг 6)**.

### Целевая формула модели:
Документ структурирован вокруг канонической цепочки принятия решений:
$$\text{Кто принимает решение} \longrightarrow \text{В какой момент} \longrightarrow \text{Какой вопрос решает} \longrightarrow \text{Какую информацию имеет} \longrightarrow \text{Какое действие может рассматривать} \longrightarrow \text{Что остаётся неизвестным}$$

### Границы применимости (Чего документ НЕ делает):
1. **НЕ проектирует пользовательский интерфейс (UI/UX design):** документ не содержит макетов экранов, кнопок или визуальных спецификаций (задача воркстрима UX/Front-End под управлением prscr);
2. **НЕ утверждает новых обязательных требований к продукту:** все элементы носят статус аналитических гипотез, рекомендаций и кандидатных моделей;
3. **НЕ выбирает финальный целевой показатель (production target):** выбор между процентом потерь (`loss_fraction_pct`), категориями (`quality_status`) или баллами (`quality_score`) закреплён за интегратором на гейте VLD-02B;
4. **НЕ определяет волюнтаристских численных порогов риска или операционных квот:** численные отсечки не хардкодятся и требуют валидации;
5. **НЕ моделирует непрерывный таймер ухудшения качества:** в соответствии с вердиктом VDR-03 exact horizon остаётся неподтверждённым, continuous countdown запрещён; CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping deterioration_horizon null until later evidence + integration decision support population;
6. **НЕ внедряет закрытых production `action_code`:** рекомендации описываются через кандидатные классы действий, а поле `recommendation` обязано допускать значение `null`;
7. **НЕ изменяет канонические контракты:** write-scope строго ограничен `docs/product_recon/`.

### Система эпистемической маркировки:
* **`[CHALLENGE FACT]`** — прямое требование спонсорского пакета или канона челленджа;
* **`[DATA FACT — VDR-XX]`** — эмпирически подтверждённое и воспроизводимое свойство датасета;
* **`[DOMAIN FACT]`** — факт из отрецензированных внешних нормативных источников (FAO, USDA, UNECE, научная литература);
* **`[INFERENCE]`** — обоснованный аналитический вывод или рабочая гипотеза продуктового анализа;
* **`[RECOMMENDATION]`** — предложение продуктового владельца для проектных решений команды;
* **`[TEAM DECISION]`** — зафиксированное внутреннее решение команды Slave of Skynet (SoS);
* **`[UNKNOWN]`** — неразрешённый пробел в данных или требованиях, требующий прояснения на отдельном гейте.

---

## 1. Сквозная архитектура модели операционных решений

| Звено цепочки | Ключевое содержание | Эпистемический статус | Обоснование в evidence / каноне |
| :--- | :--- | :---: | :--- |
| **1. Кто принимает решение** | **Dispatch Supervisor / Ramp Quality Inspector** *(Диспетчер рампы / инспектор отгрузки)* | `[RECOMMENDATION — requires TEAM DECISION]` | Находится непосредственно на рампе в момент $T_{dispatch}$; физически контролирует процесс погрузки партий в кузов ТС. |
| **2. В какой момент** | **$T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$** *(Окончание хранения / выгрузка на рампу)* | `[CHALLENGE FACT / ADR 0002]` | Канонический временной срез ADR 0002. Хранение в камере завершено, рейс ещё не начался. |
| **3. Какой вопрос решает** | **D1: Допуск (Release/Hold); D2: Доохлаждение; D3: Верификация ТС; D4: Соответствие маршруту.** Ответ на 4 исхода челленджа. | `[INFERENCE / Candidate Decision Model]` | Синтез регламентов FAO (1989, 2004), UNECE (2017) и 4 аналитических вопросов спонсорского брифа. |
| **4. Какую информацию имеет** | **Предотгрузочные данные:** паспорт партии, паспорт зоны, ряды телеметрии до $T_{dispatch}$, QC при сборе и за 2 ч до отгрузки, плановый рейс. | `[CHALLENGE FACT / ADR 0002]` | Строгий входной контракт ADR 0002. Все пост-отгрузочные поля строго изолированы (Strict Negative Boundary). |
| **5. Какое действие рассматривает** | **Кандидатные классы действий 1–5:** Clearance, Operational Hold, Pre-cooling, Reassignment, Route Shortening. | `[CANDIDATE ACTION CLASS / RECOMMENDATION — NOT PRODUCTION CONTRACT]` | Отрецензированная литература по агрологистике. `recommendation.action_code` не зафиксирован; допускается `recommendation = null`. |
| **6. Что остаётся неизвестным** | **Реестр 14 обязательных UNKNOWNs:** персона, полномочия, workflow, action space, horizon, target, sufficiency и др. | `[UNKNOWN]` | Зафиксированные точки неопределённости, сохраняемые открытыми до формальных гейтов. |

---

## 2. Звено 1: Кто принимает решение (Decision Maker / Persona Candidates)

### Контекст коммерческой инфраструктуры Молдовы:
Спонсорский бриф формулирует целевого пользователя обобщённо: *«farmer or storage operator»* `[CHALLENGE FACT]`. Однако исследуемый датасет охватывает 10 региональных коммерческих хабов и распределительных центров Молдовы ёмкостью от 2,500 до 6,000 тонн с 25 специализированными камерами `[DATA FACT — VDR-01]`. В условиях таких предприятий операционное управление распределено между несколькими штатными ролями `[DOMAIN FACT]`:

```
+----------------------------------------------------------------------------------------------------+
|                                    ШТАТНАЯ СТРУКТУРА ХАБА                                          |
|                                                                                                    |
|  [Facility / Commercial Director]      -- Коммерческие контракты, выбор рынков сбыта, споры        |
|              |                                                                                     |
|  [Cold Store / QC Manager]             -- Технологические карты камер, приёмка с поля, мониторинг  |
|              |                                                                                     |
|  [Dispatch Supervisor / Ramp Inspector]-- Допуск партий на рампе, осмотр кузова ТС, CMR (T_dispatch)|
+----------------------------------------------------------------------------------------------------+
```

### Сравнительный анализ ролей-кандидатов (Reconciliation с 04_evidence_map.md):

| Роль в литературе | Документированные процедуры `[DOMAIN FACT]` | Степень релевантности моменту $T_{dispatch}$ | Фактические полномочия сотрудника `[UNKNOWN / CONTRACT-DEPENDENT]` |
| :--- | :--- | :---: | :--- |
| **1. Dispatch Supervisor / Ramp Inspector** *(Диспетчер рампы / инспектор)* | Контроль погрузки; экспресс-осмотр тары и плодов; проверка чистоты и охлаждения кузова ТС; подписание товаросопроводительных документов (CMR). | **ВЫСОКАЯ** (находится непосредственно у ворот рампы в момент $T_{dispatch}$) | В процедурах описано право зафиксировать дефект и приостановить погрузку. Право отменить рейс, заказать другой транспорт или изменить распределение партий зависит от регламентов хаба и договоров с владельцами груза (`UNKNOWN / CONTRACT-DEPENDENT`). |
| **2. Cold Store / QC Manager** *(Технолог хранения / начальник ОТК)* | Управление режимами холодильных камер; контроль созревания плодов в период хранения; лабораторные анализы качества; оформление актов несоответствия. | **СРЕДНЯЯ** (работает с партией в период хранения; на рампе присутствует эпизодически) | Документировано право наложить технологический карантин на партию/камеру и назначить переборку или охлаждение. Право вмешиваться в графики перевозок зависит от контракта (`UNKNOWN / CONTRACT-DEPENDENT`). |
| **3. Facility / Commercial Director** *(Директор хаба / коммерческий директор)* | Заключение контрактов с торговыми сетями и экспортерами; согласование логистических операторов; финансовое урегулирование убытков и рекламаций. | **НИЗКАЯ** (стратегическое управление, удалённое от физического досмотра паллет) | Обладает юридическими полномочиями по перенаправлению партий и расторжению договоров, но не работает с линейным диспетчерским интерфейсом в реальном времени. |

### Выбор целевой роли для Smart Harvest:
* **PRIMARY USER (Кандидат в основную персону):** **Dispatch Supervisor / Ramp Quality Inspector** *(Диспетчер рампы / контролёр отгрузки)* `[RECOMMENDATION — requires TEAM DECISION]`.
  * *Обоснование:* Момент оценки системы зафиксирован как $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$ (ADR 0002). Это момент физической выгрузки паллет на погрузочную платформу перед отправкой. Именно специалист на рампе непосредственно взаимодействует с поданным транспортом. Закрепление данной роли остаётся открытым командным решением `[TEAM DECISION / UNKNOWN]`.
* **SECONDARY USER (Вторичная персона):** **Cold Store QC Manager** *(Технолог хранения / менеджер по качеству)* `[RECOMMENDATION]`.
  * *Обоснование:* Адресат технологической эскалации при необходимости дополнительного экспертного контроля или выявлении аномалий микроклимата камеры (`requires_human_review` по умолчанию `true`).

---

## 3. Звено 2: В какой момент принимается решение (Decision Moment)

### Якорное время оценки (Temporal Anchor):
В соответствии с каноническим решением **ADR 0002 (VLD-02A)**:
$$T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$$

```
ХРАНЕНИЕ В КАМЕРЕ (Завершено)                  ТРАНСПОРТИРОВКА В РЕЙСЕ (Предстоит)
======================================|===========================================> Время (t)
  T_harvest         T_pre_dispatch    |                   T_actual_departure     T_actual_arrival
  (Сбор)            (QC за 2.0 ч)     |                   (Выезд со стоянки)     (Прибытие в сеть)
                                      |
                           МОМЕНТ ОЦЕНКИ T_dispatch
                         (Выгрузка партии на рампу)
```

### Физическая и технологическая специфика момента:
1. **Точка разделения фаз:** До момента $T_{dispatch}$ партия находится под контролем стационарных систем климата склада. После погрузки и выезда ТС партия переходит в зону внешних температур и дорожных условий `[DOMAIN FACT]`;
2. **Окно операционной реакции:** $T_{dispatch}$ — момент, когда складской персонал может провести контрольный осмотр, зафиксировать несоответствие кузова ТС или передать партию на технологическую перепроверку `[DOMAIN FACT / INFERENCE]`;
3. **Строгая граница данных:** Вся информация, возникающая после $T_{dispatch}$ (фактический выезд со стоянки, задержки в пути, показания дорожного регистратора температуры, контроль в пункте назначения, финансовые рекламации), физически не существует в момент оценки и строго исключена из входного пространства модели `[CHALLENGE FACT / ADR 0002]`.

---

## 4. Звено 3: Какой вопрос решает оператор (Decision Problem)

Линейный персонал склада стремится предотвратить отправку партий со скрытой деградацией, которые могут быть забракованы покупателем, соблюдая при этом регламентные технологические процедуры `[DOMAIN FACT / INFERENCE]`.

### Кандидатный цикл операционных решений на этапе отгрузки:
На этапе предрейсовой подготовки рассматривается четырёхзвенный цикл операционных решений `[INFERENCE / Candidate Decision Model]`:

```
                           МОМЕНТ ОЦЕНКИ T_dispatch
                                      |
                                      v
         +----------------------------------------------------------+
         |  D1. Допуск партии к погрузке (Release vs. Hold)         |
         +----------------------------------------------------------+
                    |                                  |
               [ДОПУЩЕНА]                          [ЗАДЕРЖАНА]
                    |                                  |
                    v                                  v
         +----------------------+             +---------------------+
         | D2. Проверка         |             | Назначение углуб-   |
         | доохлаждения         |             | ленного контроля QC |
         | (Pre-cool Check)     |             +---------------------+
         +----------------------+
                    |
                    v
         +----------------------------------------------------------+
         | D3. Верификация поданного ТС (Vehicle / Carrier Check)   |
         +----------------------------------------------------------+
                    |
                    v
         +----------------------------------------------------------+
         | D4. Соответствие транспорта маршруту (Route-Matching)    |
         +----------------------------------------------------------+
```

| Код | Наименование решения | Операционный вопрос оператора | Допустимые альтернативы | Границы полномочий `[UNKNOWN / CONTRACT-DEPENDENT]` |
| :--- : | :--- | :--- | :--- | :--- |
| **D1** | **Release vs. Hold** *(Допуск к погрузке)* | Готова ли партия к погрузке в транспорт по текущему качественному состоянию? | **1. Release** (выпуск без ограничений);<br>**2. Hold** (задержка на рампе для инструментального контроля QC). | Процедуры QC фиксируют право временной задержки партии при подозрении на дефект; право окончательной блокировки отгрузки зависит от регламентов предприятия. |
| **D2** | **Pre-cool Verification** *(Контроль охлаждения)* | Соответствует ли температура плодов нормативу погрузки в рефрижератор? | **1. Confirm Pre-cooled** (температура в норме);<br>**2. Re-cool Required** (требуется доохлаждение в камере). | Отраслевой стандарт рекомендует проверять температуру перед погрузкой; возможность назначения доохлаждения ограничена наличием свободных камер хаба. |
| **D3** | **Carrier Verification** *(Верификация ТС)* | Соответствует ли поданное транспортное средство классу перевозимого груза? | **1. Accept Carrier** (подан надлежащий рефрижератор);<br>**2. Flag Incompatible** (подан тент или изотерм для нестойкой культуры). | Оператор уполномочен зафиксировать несоответствие кузова ТС заявке; заказ другого ТС требует санкции службы логистики. |
| **D4** | **Transport-Route Matching** *(Соответствие плечу)* | Выдержит ли партия транспортировку назначенной длительности в заданном ТС? | **1. Proceed Route** (маршрут согласован);<br>**2. Reroute Recommendation** (рекомендация сократить плечо доставки). | Перенаправление партии или отмена экспортного рейса выходит за рамки полномочий рампы и требует коммерческого решения руководства. |

### Сопряжение с 4 обязательными исходами челленджа `[CHALLENGE FACT]`:

1. **Outcome 1: «Which batches are most at risk?»**
   * *Статус валидации:* **`ranking feasibility: SUPPORTED BY BENCHMARK`** (VDR-04A доказал способность моделей ранжировать партии по риску при наличии плановой логистики: Precision@10 = 100.0%, NDCG@10 = 0.88).  
   * *Статус в продукте:* **`production risk prioritisation workflow: PROPOSED / NOT YET ADOPTED`** (алгоритм вычисления и калибровки рабочего `risk.score` ожидает решения на гейте VLD-02B; фиксированная операционная квота «топ-10» не вводится, речь идёт об общем ранжировании очереди по риску).
2. **Outcome 2: «When may quality begin to deteriorate?»**
   * *Статус валидации:* **`NOT YET SUPPORTED`** (для точного момента онсета деградации);  
   * *Конфликт данных и требований:* Бриф челленджа запрашивает временной ответ, однако исследование VDR-03 установило, что датасет не содержит метки времени начала биологической порчи плодов. CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping deterioration_horizon null until later evidence + integration decision support population.  
   * *Допустимый продуктовый контекст:* Поле `shipments.planned_duration_hours` выступает исключительно **контекстным предиктором для оценки риска некондиции к моменту прибытия**. Система **не имеет права утверждать точку времени, когда деградация начнётся** (включая утверждения о том, что она начнётся «в ходе рейса»).
3. **Outcome 3: «What factors contribute to the risk?»**
   * *Статус валидации:* **`PARTIALLY SUPPORTED`**;  
   * Физические величины телеметрии и замеров доступны до $T_{dispatch}$, однако формальный алгоритм атрибуции важности признаков и канонизация агрономических порогов в `docs/domain_rules.md` ожидают утверждения на этапе ML/Evaluation (Viktor).  
   * *Семантика конденсации (VDR-01):* Признак `condensation_flag` подчиняется составной логике: `condensation_flag = (surface <= dew) OR defrost_on`. В объяснениях факторов флаг не должен трактоваться исключительно как прямое измерение жидкой влаги на плодах, а должен отражать составную семантику (цикл оттайки испарителя либо расчетное достижение точки росы).
4. **Outcome 4: «What action should be prioritized?»**
   * *Статус валидации:* **`PARTIALLY SUPPORTED`** (для наличия классов действий в литературе) / **`NOT YET SUPPORTED`** (для алгоритмического выбора системой приоритетного production-действия);  
   * В спонсорском пакете отсутствует закрытый перечень действий челленджа (`[CHALLENGE CLARIFICATION / UNKNOWN]`).  
   * Датасет не содержит контрфактических данных о результатах вмешательств (`[UNKNOWN — NO COUNTERFACTUAL DATA IN DATASET]`). Утверждения о каузальном снижении потерь строго исключены.

---

## 5. Звено 4: Какую информацию имеет оператор (Available Information)

Вся информация строго разделена на разрешённую на $T_{dispatch}$ и запрещённую (ADR 0002):

### Матрица доступных данных на момент оценки ($T_{dispatch}$):

| Группа информации | Поля схемы данных | Исходная таблица | Допустимость по ADR 0002 |
| :--- | :--- | :--- | :---: |
| **Паспорт партии** | `batch_id`, `crop_type`, `variety`, `origin_region`, `harvest_weight_kg` | `batches.csv` | `PREDICTIVE_ELIGIBLE` |
| **Параметры сбора** | `harvest_datetime`, `harvest_temperature_c`, `field_precooled` | `batches.csv` | `PREDICTIVE_ELIGIBLE` |
| **Контекст хранения** | `zone_id`, `zone_type`, `target_temperature_c`, `bin_stack_tier`, `storage_duration_days`, `storage_session_id` | `storage_zones.csv`, `storage_sessions.csv` | `PREDICTIVE_ELIGIBLE` / `CONTEXT_ONLY` |
| **Инструментальный QC** | `firmness_kg_cm2`, `sugar_brix`, `defect_pct` на этапах `harvest` и `pre_dispatch` | `quality_checks.csv` | `STAGE_CONDITIONAL` (H и PD) |
| **Микроклимат камеры** | Ряды `air_temperature_c`, `produce_surface_temperature_c`, `defrost_on`, `condensation_flag`, `co2_ppm` от $T_{entry}$ до $T_{dispatch}$ | `sensor_readings.csv` | `CONDITIONALLY_ELIGIBLE` |
| **Плановая логистика** | `destination_market`, `destination_region`, `vehicle_type`, `planned_duration_hours` | `shipments.csv` | `CONDITIONALLY_ELIGIBLE` |

### Запрещённая информация (Strict Negative Boundary) `[CHALLENGE FACT / ADR 0002]`:
Ни одно из следующих полей **не может являться входом предиктивной модели или фактором объяснения на $T_{dispatch}$**:
* `quality_checks.*` при `stage == 'arrival'` — измерения на рампе покупателя спустя длительное время после отгрузки;
* `shipments.actual_departure_datetime` — фактический выезд машины со стоянки;
* `shipments.actual_arrival_datetime`, `shipments.actual_delay_minutes` — дорожные задержки и время в пути;
* `shipments.cold_chain_incident`, `shipments.transit_temp_mean_c` — отказ холодильной установки в пути и показания дорожного логгера (будущие стохастические события);
* `historical_quality_outcomes.*` (`loss_fraction_pct`, `quality_status`, `quality_score`, `economic_loss_eur`) — итоговые коммерческие исходы приёмки.

---

## 6. Звено 5: Какое действие может рассматривать оператор (Candidate Action Space)

Никакое действие из литературы не может считаться утверждённым требованием Smart Harvest до согласования интегратором `[CHALLENGE FACT / INFERENCE]`. Все классы действий рассматриваются как:  
**`[CANDIDATE ACTION CLASS / RECOMMENDATION — NOT PRODUCTION CONTRACT]`**.

Код `recommendation.action_code` считается неразрешённым (`UNRESOLVED`) до утверждения на проектном гейте. При отсутствии валидированной логики формирования рекомендаций контракт **обязан допускать `recommendation = None`**. Никакое действие не объявляется «оптимальным».

### Спецификация кандидатных классов действий:

#### Класс 1: Стандартный допуск к отгрузке (Standard Dispatch Clearance)
* **Evidence / Source `[DOMAIN FACT]`:** FAO (1989) Section 4; UNECE (2017); GCCA (2018).
* **Operational Feasibility Status:** Высокая (штатная процедура приемо-сдаточного контроля).
* **Authority Dependency `[UNKNOWN / CONTRACT-DEPENDENT]`:** Линейный диспетчер рампы подписывает разрешение в рамках стандартного регламента.
* **Data Dependency:** Доступные на $T_{dispatch}$ параметры качества и плановой логистики.
* **Validation Status:** Candidate Proposal. Каузальный эффект на сохранность груза в пути не валидирован (нет контрфактов).
* **Whether Human Review is Required:** Не требуется при отсутствии зарегистрированных сигналов риска.

#### Класс 2: Технологическая задержка на рампе для контроля QC (Operational Hold & Re-inspection)
* **Evidence / Source `[DOMAIN FACT]`:** GCCA (2018) Cold Storage SOPs; USDA AMS (2016); FAO (1989).
* **Operational Feasibility Status:** Средняя (ограничена доступным временным буфером рампы до выставления штрафов за простой автотранспорта).
* **Authority Dependency `[UNKNOWN / CONTRACT-DEPENDENT]`:** Приостановка погрузки выполняется диспетчером; снятие технологического карантина требует подписи службы качества.
* **Data Dependency:** Предотгрузочные данные качества `pre_dispatch`, профиль аномалий телеметрии камеры.
* **Validation Status:** Candidate Proposal. Эффективность предотвращения рекламаций не калибрована.
* **Whether Human Review is Required:** **ДА** (APR-01 candidate corrective actions require human review; the existing field defaults to true, while any broader production invariant would require a shared-contract/product decision).

#### Класс 3: Предрейсовое доохлаждение партии (Pre-cooling / Re-cooling Treatment)
* **Evidence / Source `[DOMAIN FACT]`:** FAO (2004) Bulletin 151; UC Davis Kader (2002); Thompson et al. (2008).
* **Operational Feasibility Status:** Условно-доступная (зависит от наличия свободных камер быстрого охлаждения `Rapid Pre-Cooling` на конкретном предприятии).
* **Authority Dependency `[UNKNOWN / CONTRACT-DEPENDENT]`:** Требует согласования между диспетчером, технологом холодильного комплекса и водителем ТС.
* **Data Dependency:** `sensor_readings.produce_surface_temperature_c`, `batches.harvest_temperature_c`, `batches.field_precooled`, `storage_zones.zone_type`, `shipments.vehicle_type`.
* **Validation Status:** Candidate Proposal. Количественный выигрыш в снижении потерь не наблюдаем в данных.
* **Whether Human Review is Required:** **ДА** (APR-01 candidate corrective actions require human review; the existing field defaults to true, while any broader production invariant would require a shared-contract/product decision).

#### Класс 4: Рекомендация назначения рефрижератора (Refrigerated Transport Reassignment)
* **Evidence / Source `[DOMAIN FACT]`:** Соглашение СПС / ATP UNECE; GCCA (2018); FAO (2004).
* **Operational Feasibility Status:** Проблематичная в регионах (доступность свободного рефрижераторного транспорта на спотовом рынке Молдовы в сезон сбора урожая ограничена `[UNKNOWN]`).
* **Authority Dependency `[UNKNOWN / CONTRACT-DEPENDENT]`:** Выходит за рамки полномочий рампы; требует санкции отдела логистики и согласования разницы в стоимости фрахта.
* **Data Dependency:** `shipments.vehicle_type`, `shipments.planned_duration_hours`, `batches.crop_type`.
* **Validation Status:** Candidate Proposal (мотивирован VDR-04A). Фактическая доступность машин неизвестна.
* **Whether Human Review is Required:** **ДА** (APR-01 candidate corrective actions require human review; the existing field defaults to true, while any broader production invariant would require a shared-contract/product decision).

#### Класс 5: Сокращение маршрута или сдача на переработку (Commercial Route Shortening / Processing Diversion)
* **Evidence / Source `[DOMAIN FACT]`:** Andrés F. López Camelo (2004) FAO Bulletin 151; FAO (1989); Kitinoja & Kader (2002).
* **Operational Feasibility Status:** Критически сложная (сопряжена с юридическими штрафами за срыв экспортной поставки и потерей выручки).
* **Authority Dependency `[UNKNOWN / CONTRACT-DEPENDENT]`:** Исключительная компетенция коммерческого руководства предприятия или владельца груза.
* **Data Dependency:** Высокий уровень предиктивного риска, `shipments.destination_market`, `shipments.planned_duration_hours`, комплекс предотгрузочных признаков деградации.
* **Validation Status:** Candidate Proposal / Extreme Contingency. Соотношение штрафов сети и убытка от утилизации не калибровано в датасете (`[UNKNOWN]`).
* **Whether Human Review is Required:** **ДА** (APR-01 candidate corrective actions require human review; the existing field defaults to true, while any broader production invariant would require a shared-contract/product decision).

---

## 7. Семантика горизонта порчи (Deterioration Horizon — VDR-03 Anchor)

Относительно вопроса челленджа *«when quality may begin to deteriorate»* исследование VDR-03 установило строгие ограничения `[DATA FACT — VDR-03]`:
1. В датасете **отсутствует метка времени начала порчи** ($T_{\text{deterioration\_start}}$). Замеры качества строго дискретны (ровно 3 инспекции на партию);
2. Данные **не поддерживают вычисление непрерывного математического таймера деградации** (countdown clock) или точного срока Remaining Shelf Life в часах;
3. CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping deterioration_horizon null until later evidence + integration decision support population;
4. Поле `planned_duration_hours` рассматривается исключительно как **контекстный предиктор риска некондиции к моменту доставки**. Запрещено утверждать точку времени, когда деградация фактически начнётся.

---

## 8. Звено 6: Что остаётся неизвестным (Mandatory Open UNKNOWNs Register)

В соответствии с методологическими правилами проекта ни одно из следующих 14 открытых неизвестных **не закрывается моделью волюнтаристски** и сохраняет открытый статус:

| № | Неизвестное (UNKNOWN) | Гейт / Орган принятия решения | Текущий статус в модели решений |
| :-: | :--- | :---: | :--- |
| **1** | **Primary Smart Harvest persona** | `[TEAM DECISION / UNKNOWN]` | Предложен *Dispatch Supervisor / Ramp Inspector* как кандидатная роль (`RECOMMENDATION — requires TEAM DECISION`). |
| **2** | **Точные полномочия выбранной persona** | `[UNKNOWN / CONTRACT-DEPENDENT]` | Отраслевые процедуры описывают проверку и задержку (`Hold`). Полномочия по отмене рейсов или смене ТС зависят от контракта объекта. |
| **3** | **Фактический operational dispatch workflow конкретных объектов** | `[CANDIDATE PROPOSAL / UNKNOWN]` | 4-звенная модель решений ($D_1 \dots D_4$) является аналитическим синтезом нормативных практик и требует подтверждения на реальных складах Молдовы. |
| **4** | **Permitted action space challenge** | `[CHALLENGE CLARIFICATION / UNKNOWN]` | Бриф челленджа не содержит закрытого перечня действий для исхода 4. Предложенные 5 классов действий имеют статус кандидатных опций. |
| **5** | **Deterioration-onset semantics** | `[DATA/EVALUATION DECISION / UNKNOWN]` | VDR-03 доказал отсутствие метки начала порчи. CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping deterioration_horizon null until later evidence + integration decision support population; continuous countdown запрещён. |
| **6** | **Production target** | `[DATA/EVALUATION DECISION (VLD-02B) / UNKNOWN]` | Выбор финальной целевой переменной контракта передан на гейт интегратора VLD-02B. |
| **7** | **Risk threshold / band semantics** | `[DATA/EVALUATION DECISION / TEAM DECISION / UNKNOWN]` | Продукт не вводит субъективных порогов. Семантика диапазонов `risk.band` (`low`, `moderate`, `high`) остаётся открытой до калибровки ML. |
| **8** | **Telemetry sufficiency / staleness policy** | `[DATA/EVALUATION DECISION / UNKNOWN]` | Правила перевода оценки в `status: 'insufficient_data'` при пропусках телеметрии подлежат утверждению в политике валидации данных. |
| **9** | **Treatment 204 truncated batches** | `[DATA/EVALUATION DECISION / UNKNOWN]` | Порядок обработки 204 партий 2026 года с усечённой телеметрией ожидает утверждения политики валидации. |
| **10** | **Actual costs / capacity corrective actions** | `[UNKNOWN]` | Коммерческая стоимость простоя автотранспорта, тарифы рефрижераторов в Молдове и доступность свободных мощностей охлаждения количественно не определены. |
| **11** | **Validated intervention effects** | `[UNKNOWN — NO COUNTERFACTUAL DATA IN DATASET]` | Датасет не содержит контрфактических данных о результатах вмешательств. Количественный эффект предотвращения потерь не может быть рассчитан без натурного пилота. |
| **12** | **Accepted agronomic thresholds / rules** | `[UNKNOWN — PENDING DOMAIN RULE ADMISSION]` | Физиологические пороги приведены из литературы и ожидают формального утверждения в каноническом своде `docs/domain_rules.md`. |
| **13** | **Evaluation split / metric / baseline** | `[DATA/EVALUATION DECISION (Viktor VDR-04 / VLD-02B)]` | Метрики ранжирования (Precision@K, NDCG@K) исследованы в VDR-04A и подлежат утверждению в VLD-02B. |
| **14** | **Quantitative loss-reduction claims** | `[UNKNOWN / PROHIBITED CLAIM WITHOUT DEPLOYMENT]` | Любые численные обещания эффекта («сокращение потерь на X%») строго запрещены как неподтверждённые до проведения полевых испытаний. |

---

## 9. Междисциплинарные связи и зависимости модели решений

* **Implementation dependencies (Backend / Shared Contract):**
  * Временной срез инференса: strictly $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$;
  * Статус горизонта деградации: CURRENT PRODUCT POSITION: exact horizon remains unsupported by VDR-03, therefore APR-01 recommends keeping `deterioration_horizon` null until later evidence + integration decision support population;
  * Буквальная схема перечислений из `backend/app/domain/assessment.py`:
    * `RiskBand`: `low`, `moderate`, `high` (значение `medium` отсутствует в контракте);
    * `RecommendationPriority`: `informational`, `low`, `medium`, `high` (значение `critical` отсутствует в контракте);
    * `FactorCategory`: только `data_quality`, `environmental`, `storage`, `transport`, `inventory`, `historical`;
  * Первичный ключ сессии хранения: `storage_sessions.storage_session_id`;
  * При отсутствии валидированного модуля рекомендаций возвращать `recommendation: None`;
  * APR-01 candidate corrective actions require human review; the existing field defaults to true, while any broader production invariant would require a shared-contract/product decision.
* **Questions for Data & Evaluation / Proposed VLD-02B decision:**
  * Доказательство ранжирования VDR-04A (Precision@10, NDCG@10) рассматривается как benchmark feasibility evidence; K=10 не является операционной квотой;
  * Выбор итогового таргета (`loss_fraction_pct`, `quality_status`, `quality_score`) и калибровка порогов `risk.band` переданы на утверждение в рамках гейта VLD-02B;
  * Определение политики достаточности телеметрии и порядка обработки 204 усечённых партий 2026 года.
* **UX candidate — pending TEAM/INTEGRATOR decision:**
  * Предлагаемый интерфейс ранжирования очереди по риску носит статус `RECOMMENDATION / candidate product framing — requires VLD-02B / human integration decision`;
  * Интерфейс не отображает таймеров обратного отсчёта до порчи;
  * Карточка партии формирует объяснения факторов риска с учётом составной природы `condensation_flag = (surface <= dew) OR defrost_on`.
