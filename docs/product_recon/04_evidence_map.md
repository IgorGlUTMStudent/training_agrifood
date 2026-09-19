STATUS: RESEARCH NOTE — NOT CANON

# APR-01: Reconciled Evidence-to-Question Mapping (Calibrated)

**Owner:** Alisa — Product Owner
**Workstream:** APR-01 Product & Requirements Recon
**Status:** Calibrated Evidence Map (NOT CANON)

---

## 0. Иерархия доказательств и согласование с репозиторием

В настоящем документе все утверждения строго разграничены по уровням достоверности:
1. **CHALLENGE FACT:** Официальные правила и факты тренировочного челленджа Smart Harvest (`sponsor_pack/brief/`, `sponsor_pack/README.md`, `docs/challenge_canon.md`).
2. **DATA FACT — VDR-01 / VDR-02:** Эмпирически измеренные характеристики датасета из отчетов инвентаризации ([VDR-01](data_recon/01_dataset_inventory.md)) и хронологического/leakage-аудита ([VDR-02](data_recon/02_temporal_leakage.md)), а также решения по входным границам ([ADR 0002 / VLD-02A](decisions/0002-predictive-input-semantics.md)).
3. **DOMAIN FACT:** Факты из внешних отрецензированных источников (FAO, USDA, UNECE, университетские службы Extension, научные публикации).
4. **INFERENCE:** Аналитические выводы, модели предметной области, инженерные гипотезы и предлагаемые кандидатные наборы решений команды.
5. **TEAM DECISION:** Зафиксированные архитектурные и продуктовые решения команды Slave of Skynet (SoS).
6. **UNKNOWN:** Неразрешенные вопросы, требующие дальнейшего исследования, прояснения у организаторов или формализации отдельными решениями (decision gates).

### Ключевые согласованные факты (Reconciliation Anchors):
* **CHALLENGE FACT / ADR 0002:** Момент предиктивной оценки $T_{assess} \equiv T_{dispatch} = \text{storage_sessions.dispatch_datetime}$ жестко зафиксирован sponsor pack и ADR 0002 как единственный нормативный временной якорь (assessment clock).
* **CHALLENGE FACT / ADR 0002:** Для предиктивной оценки партии допустима только информация, существовавшая до момента $T_{dispatch}$. Данные контроля прибытия (`quality_checks.stage == 'arrival'`), фактические транзитные реализации (`actual_departure_datetime`, `actual_arrival_datetime`, `actual_delay_minutes`, `cold_chain_incident`, `transit_temp_mean_c`) и коммерческие исходы (`historical_quality_outcomes.*`) строго исключены из входного контракта инференса как `FORBIDDEN_FUTURE` и `LABEL_OR_EVALUATION_ONLY`.
* **DATA FACT — VDR-02:** Во всех 1,800 партиях соблюдается физическая последовательность событий: $T_{harvest} < T_{harvest\_qc} < T_{entry} < T_{pre\_dispatch\_qc} < T_{dispatch} \le T_{actual\_departure} < T_{actual\_arrival} = T_{arrival\_qc}$. Зафиксировано 0 нарушений хронологической последовательности.
* **DATA FACT — VDR-01:** В датасете представлены строго 8 культур: `apples` (673), `plums` (350), `table_grapes` (310), `tomatoes` (180), `pears` (114), `strawberries` (63), `apricots` (60), `raspberries` (50). Культуры вне этого списка (например, огурцы или лук) в данных отсутствуют.
* **DATA FACT — VDR-01 / VDR-02:** Доступный состав микроклиматических полей сенсоров полностью известен: `air_temperature_c`, `produce_surface_temperature_c`, `relative_humidity_pct`, `dew_point_c`, `condensation_flag`, `co2_ppm`, `o2_pct`, `cooling_on`, `defrost_on`.
* **DATA FACT — VDR-01:** Поля `produce_surface_temperature_c` и `dew_point_c` присутствуют во всех камерах (641,299 строк), за исключением отсутствия канала измерения температуры поверхности в камере `ZONE-006` (28,366 nulls).
* **DATA FACT — VDR-01:** Флаг `condensation_flag` подчиняется составной логике: $T_{surface} \le T_{dew}$ ИЛИ `defrost_on = True`. В `ZONE-006` он активируется исключительно во время циклов разморозки в 04:00.
* **DATA FACT — VDR-01:** Газовые датчики (`co2_ppm`, `o2_pct`) присутствуют только в 5 камерах РГС (CA); в остальных 20 обычных камерах они на 100% NULL.
* **DATA FACT — VDR-01 / VDR-02:** Наблюдается глобальный обрыв телеметрии 2025-12-31 23:30:00. Для 1,596 партий (88.67%) телеметрия непрерывна вплоть до момента отгрузки (максимальный лаг 29.4 мин, средний 14.5 мин). Для 204 партий (11.33%, преимущественно яблоки и груши сезона 2025), отгруженных в 2026 году, предотгрузочный лаг составляет от 0.56 до 92.54 суток (средний 29.01 суток). Обрыв телеметрии может привести к `insufficient_data` только в том случае, если будущая policy минимальной достаточности данных признает оставшиеся наблюдения недостаточными. Конкретные minimum telemetry sufficiency, staleness threshold, imputation/rejection policy и degradation policy на данный момент остаются UNKNOWN (VDR-02 / ADR 0002).
* **DATA FACT — VDR-02:** 1,734 из 1,800 партий (96.33%) одновременно находились в камерах с другими партиями (37,861 парное пересечение в 157 изолированных кластерах «камера-время»).
* **CHALLENGE FACT:** Объяснимость (*explainability*) и применимость (*usability*) являются официальными критериями оценки челленджа (`docs/challenge_canon.md`).

---

## 1. Дополненный Evidence Pack: Вопросы Q1.1, Q1.2, Q2.1 (Step 4 Baseline)

*Примечание к комплекту документов:* Данный раздел фиксирует результат Шага 4 (Evidence Pack по вопросам пользователя и операционным действиям), дополненный по результатам ревизии и синхронизированный с каноном.

### Q1.1. Кто является ключевым операционным пользователем системы на объектах коммерческого хранения и отгрузки?

* **SOURCE:**
  * FAO (1989) *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*, FAO Training Series No. 17/2, Rome. ISBN 92-5-102766-8 (Section 4: Packhouse operations);
  * USDA Agricultural Marketing Service (AMS) *Shipping Point and Market Inspection Handbooks*;
  * UC Davis Postharvest Technology Center (Kader, A. A., ed., 2002) *Postharvest Technology of Horticultural Crops*, 3rd ed., University of California Agriculture and Natural Resources Publication 3311 (Ch. Packhouse Operations & Quality Assurance).
* **SUPPORTS:**
  * **Реально встречающиеся роли в источниках (DOMAIN FACT):** в литературе по коммерческим складам и упаковочным цехам выделяются следующие штатные специализации:
    1. *Packhouse / Cold Store Manager* (управляющий складом/цехом — общий надзор, планирование графиков);
    2. *Quality Control (QC) Inspector / Technician* (контролер качества — инструментальные замеры сахара и твердости, отбраковка, визуальный контроль дефектов);
    3. *Shipping / Dispatch Supervisor* (диспетчер отгрузки — осмотр поданного транспорта, контроль погрузочных операций на рампе, подписание товарно-транспортных накладных);
    4. *Refrigeration Technician / Operator* (оператор холодильного оборудования — технический мониторинг установок и микроклимата камер).
  * **Подтвержденные обязанности (DOMAIN FACT):** проверка соответствия партии спецификации покупателя, визуальный и инструментальный осмотр плодов перед погрузкой, контроль чистоты и предрейсовой температуры кузова транспортного средства, фиксация времени отправки.
  * **Роль в Smart Harvest (TEAM DECISION / UNKNOWN):** бриф челленджа задает лишь обобщенную формулировку *«farmer or storage operator»*. Определение конкретной целевой персоны (технолог по качеству хранения vs линейный диспетчер рампы) является проектным решением команды SoS (TEAM DECISION), пока спонсорский бриф не специфицирует конкретную должность.
* **SCOPE:** Отраслевые практики управления упаковочно-складскими хабами плодоовощной продукции.
* **STATUS:** **PARTIALLY ANSWERED** (роли и обязанности в отрасли установлены; выбор целевого пользователя для интерфейса Smart Harvest требует решения команды).
* **LIMITATIONS:** В малых фермерских хозяйствах функции контролера качества и диспетчера отгрузки часто совмещены в одном лице; на крупных индустриальных хабах они организационно и функционально разделены.

---

### Q1.2. Каковы границы полномочий и зона операционного контроля этого пользователя?

* **SOURCE:**
  * FAO (1989) *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*, FAO Training Series No. 17/2, Rome (Section: Packhouse operations and quality control);
  * Global Cold Chain Alliance (GCCA, 2018) *Cold Storage Standard Operating Procedures: Shipping & Loading*;
  * UNECE (2017) *Guidelines on the Inspection of Fresh Fruit and Vegetables*, United Nations Economic Commission for Europe, Geneva (ECE/TRADE/C/WP.7/2017/3).
* **SUPPORTS:**
  * **Документированные операционные действия (DOMAIN FACT):** замер температуры мякоти плодов (*pulp temperature*), визуальный осмотр состояния тары и целостности паллет, проверка пломб, подписание отгрузочных документов (CMR, ТТН).
  * **Документированные проверки качества и транспорта (DOMAIN FACT):** фиксация процента видимых дефектов, проверка предварительного охлаждения кузова рефрижератора (*pre-cooling*), проверка санитарно-гигиенического состояния ТС и отсутствия посторонних запахов.
  * **Организационные и юридические полномочия (CONTEXT-DEPENDENT / UNKNOWN):** право наложить временный запрет на погрузку партии (*hold/quarantine*) до повторной проверки подтверждается регламентами службы контроля качества (QC). Однако право линейного сотрудника рампы единолично отменить запланированный рейс, произвольно изменить очередность партий или отклонить перевозчика зависит от регламентов конкретного предприятия и формы владения товаром (собственная продукция агрохолдинга vs продукция сторонних фермеров на ответственном хранении). Одностороннее расторжение договоров поставки или изменение коммерческих условий не входит в компетенцию операционного персонала рампы.
* **SCOPE:** Регламенты работы персонала на погрузочно-разгрузочных рампах холодильных комплексов.
* **STATUS:** **PARTIALLY ANSWERED** (набор технологических контрольных действий подтвержден; степень юридической и административной самостоятельности оператора зависит от типа склада и договорных условий).
* **LIMITATIONS:** Источники описывают типовые технологические процедуры контроля, но не устанавливают единого универсального объема коммерческих полномочий складского оператора.

---

### Q2.1. Какие решения принимаются непосредственно на этапе подготовки и выполнения отгрузки ($T_{dispatch}$)?

* **SOURCE:**
  * UNECE (2017) *Guidelines on the Inspection of Fresh Fruit and Vegetables: Pre-shipment and Dispatch Verification*;
  * USDA Agricultural Marketing Service (AMS, 2016) *Fresh Fruit and Vegetable Shipping Point and Market Inspection Instructions*;
  * FAO (2004) Andrés F. López Camelo, *Manual for the preparation and sale of fruits and vegetables: From field to market*, FAO Agricultural Services Bulletin 151, Rome (Section: Dispatch and transportation).
* **SUPPORTS:**
  * **Подтвержденные действия на этапе отгрузки (DOMAIN FACT):** замер температуры плодов в отобранных пробах перед погрузкой, осмотр механической целостности тары, контрольная инструментальная сверка параметров качества (твердость пенетрометром, сахаристость рефрактометром, дефекты), проверка температуры воздуха внутри поданного кузова ТС.
  * **Кандидатный набор операционных решений (INFERENCE / Candidate Decision Set):**
    На основе описанных в источниках процедур для продуктовой логики Smart Harvest формулируется следующий кандидатный набор решений:
    1. *Решение о допуске партии к погрузке (Release vs Hold)* — на основе результатов предотгрузочной инспекции;
    2. *Решение о дополнительном охлаждении (Pre-cool confirmation)* — если температура мякоти плода превышает транспортный норматив;
    3. *Решение о допуске транспортного средства (Carrier acceptance vs rejection)* — проверка температурного режима и санитарного состояния кузова;
    4. *Решение о соответствии транспорта маршруту (Transport-route matching)* — проверка допустимости отправки назначенным типом ТС (Reefer Truck, Insulated Van, Ambient Truck) на плановую дистанцию перевозки.
* **SCOPE:** Процедуры приемо-сдаточного контроля в зоне отгрузки плодоовощной продукции.
* **STATUS:** **PARTIALLY ANSWERED** (перечень контрольных действий подтвержден литературой; четырехзвенная структура решений является аналитической гипотезой команды, а не универсальным догматическим стандартом).
* **LIMITATIONS:** Ни один отдельный источник не предписывает именно такую формализованную последовательность решений как жесткий обязательный протокол.

---

## 2. Полный калиброванный Evidence-to-Question Mapping

---

### QUESTION 1 (Q2.2). По каким правилам формируется очередность отгрузки партий (FIFO, FEFO или иные критерии)?

#### AVAILABLE EVIDENCE
* 1.1 FAO (1989/1993) *Prevention of post-harvest food losses: fruit, vegetable and root crops*, FAO Training Series No. 17/2, Chapter "Storage in bags" (Document T0522E0c).
* 1.2 FAO (1989) *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*, FAO Training Series No. 17/2, Rome.
* 1.3 University of Minnesota Extension (2020) *Postharvest Handling of Fruit and Vegetable Crops*.
* 1.4 DATA FACT — VDR-01 / VDR-02: в датасете 1,734 из 1,800 партий делят камеры хранения с другими партиями (157 кластеров); сроки хранения варьируются от 3 до 175 дней (среднее 59.8 дней).

#### SUPPORTED FINDINGS
* **DOMAIN FACT:** FIFO (First-In, First-Out) является распространенным базовым правилом ротации на складах общего назначения, однако для скоропортящейся плодоовощной продукции фактическое физиологическое состояние партии (*condition*) может служить основанием для изменения приоритета отгрузки.
* **DOMAIN FACT:** Продукция с признаками ускоренного созревания или перенесенного температурного стресса требует более ранней реализации, чем партии с высоким остаточным запасом лежкости.
* **DATA FACT — VDR-01 / VDR-02:** Каждая партия имеет точные физические временные метки: `batches.harvest_datetime`, `storage_sessions.entry_datetime`, `storage_sessions.dispatch_datetime`.
* **INFERENCE:** В практике коммерческих хранилищ конкурируют две логики: календарная ротация поступления (FIFO) и ротация по фактическому биологическому состоянию/риску (FEFO / condition-based priority).

#### LIMITATIONS
* **UNKNOWN:** Является ли FEFO официальным правилом в логистике моделируемых молдавских объектов или отгрузка выполняется строго по заранее заключенным договорам поставки под конкретных покупателей.
* **UNKNOWN:** Имеет ли автоматизированная система право рекомендовать нарушение договорного графика отгрузок без риска коммерческих неустоек.

#### STATUS
**PARTIALLY ANSWERED**

#### PRODUCT RELEVANCE
* **INFERENCE:** Smart Harvest не должен считать FIFO единственным принципом, но рекомендация изменения очереди должна учитывать контрактные обязательства партии.

---

### QUESTION 2 (Q3.1). Какие отклонения параметров микроклимата при хранении являются критическими для качества продукции?

#### AVAILABLE EVIDENCE
* 2.1 FAO (1989) *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*, FAO Training Series No. 17/2 (Section: Storage).
* 2.2 USDA ARS (2016) Gross, K. C., Wang, C. Y., & Saltveit, M. (Eds.), *The Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks*, Agriculture Handbook Number 66 (AH-66).
* 2.3 DATA FACT — VDR-01 / VDR-02: В датасете непрерывно логируются `air_temperature_c`, `relative_humidity_pct`, `dew_point_c`, `produce_surface_temperature_c`, `condensation_flag`, а также газы (`co2_ppm`, `o2_pct`) в 5 CA-камерах.

#### SUPPORTED FINDINGS
* **DATA FACT — VDR-01 / VDR-02:** Состав полей телеметрии сенсоров эмпирически подтвержден инвентаризацией VDR-01 и решением VLD-02A (ADR 0002).
* **DOMAIN FACT:** Повышенная температура ускоряет интенсивность дыхания плодов и скорость метаболического распада. Слишком низкая температура вызывает подмораживание тканей либо специфический холодовой ожог (*chilling injury*). Дефицит относительной влажности ведет к транспирации, потере тургора и снижению товарной массы.
* **DATA FACT — VDR-01:** В датасете температура воздуха варьируется от -0.05°C до 17.50°C (средняя 3.56°C), влажность от 86.0% до 99.5% (средняя 90.8%).
* **DATA FACT — VDR-01:** Камера `ZONE-004` имеет уставку 11.0°C (Vegetable room), тогда как стандартные фруктовые камеры настроены на 0.5–2.0°C.

#### LIMITATIONS
* **DOMAIN FACT:** Критичность температурного отклонения жестко зависит от биологического вида культуры и накопленной продолжительности воздействия (degree-hours).
* **DATA FACT — VDR-01 / VDR-02:** Для 204 партий 2026 года телеметрия сенсоров глобально прекращается на отметке 2025-12-31 23:30:00 (лаг до $T_{dispatch}$ от 0.56 до 92.54 дней). Обрыв телеметрии может привести к `insufficient_data` только если будущая policy минимальной достаточности признает оставшиеся данные недостаточными; правила достаточности и устаревания остаются UNKNOWN.

#### STATUS
**PARTIALLY ANSWERED** (типы физических отклонений и состав полей установлены; критические пороги требуют привязки к культурам и фактическому размещению партий).

#### PRODUCT RELEVANCE
* **INFERENCE:** Отклонения температуры и влажности не могут оцениваться по единому универсальному порогу для всех 8 культур.

---

### QUESTION 3 (Q3.2). Каково физиологическое и микробиологическое влияние поверхностной конденсации ($T_{surface} \le T_{dew}$)?

#### AVAILABLE EVIDENCE
* 3.1 NC State Extension (Boyette, M. D., Wilson, L. G., & Estes, E. A., Revised 2008 / 1989) *Introduction to Postharvest Engineering for Fresh Fruits and Vegetables*, AG-413-01.
* 3.2 UC Davis Postharvest Technology Center — *Produce Fact Sheets*.
* 3.3 DATA FACT — VDR-01: `produce_surface_temperature_c` и `dew_point_c` присутствуют в датасете (кроме камере `ZONE-006`).
* 3.4 DATA FACT — VDR-01: `condensation_flag = True` зафиксирован в 13,955 измерениях (2.08% датасета). В камере `ZONE-006` датчик поверхности отсутствует (100% null), но флаг выставляется в 591 измерении строго во время ежедневных циклов оттайки в 04:00 (`defrost_on = True`).

#### SUPPORTED FINDINGS
* **DOMAIN FACT:** Наличие свободной капельной влаги на поверхности плода при $T_{surface} \le T_{dew}$ создает водную пленку, необходимую для прорастания спор патогенных грибов (*Botrytis cinerea*, пенициллы) и бактериального инфицирования тканей.
* **DATA FACT — VDR-01:** Поля $T_{surface}$ и $T_{dew}$ физически присутствуют в датасете для 24 из 25 камер.
* **DATA FACT — VDR-01 (Compound Semantics):** Флаг `condensation_flag` в датасете **не является чистым индикатором физической конденсации**. Он отражает составное логическое условие: `(produce_surface_temperature_c <= dew_point_c OR defrost_on = True)`.
* **INFERENCE:** Срабатывание флага `condensation_flag = True` не тождественно факту поверхностной конденсации на плодах, так как может являться отражением технического цикла оттайки испарителя холодильной машины.

#### LIMITATIONS
* **DOMAIN FACT:** Образование конденсата не означает автоматического наступления порчи; критичны температура окружающей среды и продолжительность сохранения свободной влаги на кожице плода.

#### STATUS
**ANSWERED** (биологический механизм понятен; составная логика синтетического флага датасета полностью раскрыта анализом VDR-01).

---

### QUESTION 4 (Q6.1). Каков перечень доступных корректирующих действий на этапе подготовки партии к отгрузке ($T_{dispatch}$)?

#### AVAILABLE EVIDENCE
* 4.1 FAO (2004) Andrés F. López Camelo, *Manual for the preparation and sale of fruits and vegetables: From field to market*, FAO Agricultural Services Bulletin 151 (Section: Dispatch and transportation).
* 4.2 UNECE (2017) *Guidelines on the Inspection of Fresh Fruit and Vegetables*.
* 4.3 CHALLENGE FACT / ADR 0002: Момент оценки $T_{dispatch}$ жестко зафиксирован как `storage_sessions.dispatch_datetime`.
* 4.4 DATA FACT — VDR-01: В `shipments.csv` зафиксированы три типа транспорта: `Reefer Truck` (1,129), `Insulated Van` (467), `Ambient Truck` (204) и 8 рынков сбыта.

#### SUPPORTED FINDINGS
* **CHALLENGE FACT / ADR 0002:** Момент принятия решения $T_{dispatch}$ строго определен sponsor pack и ADR 0002 как момент отгрузки со склада.
* **DOMAIN FACT:** В отрасли на этапе отгрузки описаны следующие варианты операционных вмешательств:
  1. Задержка для углубленной инспекции (*Hold & Inspect*);
  2. Дополнительное охлаждение плодов перед погрузкой (*Pre-cool / Re-cool*);
  3. Замена транспортного средства на рефрижератор (*Reassign Vehicle*);
  4. Перенаправление на альтернативный более близкий рынок (*Reroute / Destination Change*);
  5. Отправка на промышленную переработку (*Divert to Processing*);
  6. Отказ в отгрузке некондиционной партии (*Reject / Quarantine*).
* **DATA FACT — VDR-01:** Длительность плановых маршрутов варьируется от 4.0 до 38.0 часов (среднее 18.39 ч).

#### LIMITATIONS
* **UNKNOWN:** Какие конкретно действия из этого отраслевого списка официально признаются платформой челленджа в качестве допустимого пространства решений (*action space*).
* **UNKNOWN:** Имеет ли оператор право задерживать рейс при жестких договорных слотах доставки в распределительные центры ЕС.

#### STATUS
**REQUIRES CHALLENGE CLARIFICATION**

---

### QUESTION 5 (Q6.2). Какие факторы, ограничения и издержки влияют на выбор действия?

#### AVAILABLE EVIDENCE
* 5.1 FAO (1989) *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*, FAO Training Series No. 17/2 (Section: Packaging and cost calculation).
* 5.2 DATA FACT — VDR-01: В датасете присутствуют `harvest_weight_kg`, `economic_loss_eur`, `loss_fraction_pct`, `destination_region`.

#### SUPPORTED FINDINGS
* **DOMAIN FACT:** Выбор корректирующего действия определяется компромиссом между технической осуществимостью, затратами на операцию и объемом предотвращаемого ущерба. Дополнительные манипуляции с продукцией могут вызывать механические повреждения тканей плодов.
* **DATA FACT — VDR-01:** Экономические потери в `historical_quality_outcomes` жестко детерминированы: `round(loss_fraction_pct / 100 * harvest_weight_kg * price_per_kg, 2)` при фиксированных ценах за кг.
* **INFERENCE:** Логика выбора действия зависит от соотношения стоимости партии, расстояния перевозки и доступности инфраструктуры.

#### LIMITATIONS
* **UNKNOWN:** Фактическая стоимость заказа альтернативного транспорта (Reefer vs Ambient) в Республике Молдова.
* **UNKNOWN:** Затраты на ручную переборку или хранение партии сверх плана.
* **UNKNOWN:** Целевая функция оптимизации организаторов челленджа.

#### STATUS
**PARTIALLY ANSWERED**

---

### QUESTION 6 (Q7.1). Что биологически считается началом ухудшения качества и как оценить остаточный срок жизни?

#### AVAILABLE EVIDENCE
* 6.1 FAO (1989) *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*, FAO Training Series No. 17/2 (Section: Perishability and produce losses / Storage).
* 6.2 UC Davis Postharvest Technology Center — *Produce Fact Sheets*.
* 6.3 DATA FACT — VDR-01 / VDR-02: Инспекции `quality_checks` фиксируют `firmness_kg_cm2`, `sugar_brix`, `defect_pct` ровно на трех этапах (`harvest`, `pre_dispatch`, `arrival`) по 1,800 замеров на каждый этап (всего 5,400 записей). При этом замеры этапа `arrival` являются `FORBIDDEN_FUTURE` для инференса на $T_{dispatch}$ (ADR 0002).

#### SUPPORTED FINDINGS
* **DOMAIN FACT:** Свежие плоды остаются живыми тканями после сбора. Созревание само по себе не является порчей, но непрерывно переходит в фазу старения (*senescence*) и естественного распада тканей.
* **DOMAIN FACT:** Понятие «ухудшение качества» в коммерческом обороте означает момент выхода характеристик партии за пределы требований товарного стандарта (падение твердости ниже нормы, размягчение, рост дефектов свыше допуска).
* **DATA FACT — VDR-01:** Средняя твердость плодов падает от сбора (7.50 кг/см²) через предотгрузку (6.41) к прибытию (5.62), а средний процент дефектов растет (2.21% → 4.71% → 9.84%).
* **INFERENCE:** Остаточный срок жизни (*Remaining Shelf Life*) — это расчетное время, в течение которого партия сохраняет кондицию выше допустимого коммерческого порога при заданном температурном режиме.

#### LIMITATIONS
* **DATA FACT — VDR-01 / VDR-02:** В датасете нет непрерывного сенсора качества; инспекции дискретны (ровно 3 замера за весь жизненный цикл партии).
* **UNKNOWN:** Какой конкретно порог твердости или дефектов челлендж считает официальным моментом потери кондиции для каждой из 8 культур.

#### STATUS
**PARTIALLY ANSWERED**

---

### QUESTION 7 (Q7.3). Как сопоставляются прогнозируемый срок сохраняемости продукции и плановая длительность транспортировки?

#### AVAILABLE EVIDENCE
* 7.1 USDA AMS PACA (Perishable Agricultural Commodities Act), 7 C.F.R. § 46.43(i) *Suitable Shipping Condition / PACA Good Delivery Guidelines*.
* 7.2 DATA FACT — VDR-01 / ADR 0002: В `shipments.csv` зафиксированы `planned_duration_hours` (от 4.0 до 38.0 ч, среднее 18.39 ч) и `planned_arrival_datetime` (классифицированы как `CONDITIONALLY_ELIGIBLE`).

#### SUPPORTED FINDINGS
* **DOMAIN FACT (PACA Definition):** Согласно стандарту USDA AMS PACA (7 C.F.R. § 46.43(i) "Suitable shipping condition"), товар на момент отгрузки считается находящимся в надлежащем отгрузочном состоянии, если при нормальных условиях транспортировки (*under normal conditions of transportation*) он прибудет в пункт назначения без ненормального ухудшения качества (*without abnormal deterioration*).
* **CHALLENGE FACT / ADR 0002:** Плановые параметры перевозки (`destination_market`, `vehicle_type`, `planned_duration_hours`, `planned_departure_datetime`, `planned_arrival_datetime`) зафиксированы в схеме данных и доступны на момент $T_{dispatch}$. Фактические события в пути (`actual_*`, `cold_chain_incident`, `transit_temp_mean_c`) и результаты приемки (`arrival`) строго исключены из инференса как `FORBIDDEN_FUTURE` (VDR-02 / ADR 0002).
* **INFERENCE:** Сопоставление прогнозируемого остаточного ресурса сохраняемости (remaining shelf life) партии и планового времени в пути (`planned_duration_hours`) является инженерно-аналитической гипотезой для моделирования операционного риска, а не формализованной законодательной формулой.

#### LIMITATIONS
* **UNKNOWN:** Нормативный численный буфер безопасности (safety margin) между остаточным сроком жизни и плановым временем в пути в официальных правилах отсутствует и подлежит определению в рамках продуктовой логики.

#### STATUS
**PARTIALLY ANSWERED**

---

### QUESTION 8 (Q8.1). Как на практике классифицируются и фиксируются коммерческие потери при доставке плодоовощной продукции?

#### AVAILABLE EVIDENCE
* 8.1 FAO (1989) *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*, FAO Training Series No. 17/2 (Section: Packaging and post-harvest losses).
* 8.2 USDA AMS PACA / UNECE Quality tolerances.
* 8.3 DATA FACT — VDR-01: Таблица `historical_quality_outcomes` содержит поля `quality_status`, `loss_fraction_pct`, `quality_score`, `economic_loss_eur`.

#### SUPPORTED FINDINGS
* **DOMAIN FACT:** В реальной коммерческой практике потери при доставке включают уценку за снижение сортности, частичные списания по дефектам, штрафы за срыв сроков поставки и полную утилизацию некондиционного брака.
* **DATA FACT — VDR-01:** В учебном датасете статус качества синтетически детерминирован диапазонами потерь:
  * `optimal`: loss < 5%
  * `degraded`: 5% $\le$ loss < 15%
  * `severe_degradation`: 15% $\le$ loss < 35%
  * `lost`: loss $\ge$ 35%
* **INFERENCE:** Данная формула датасета представляет собой синтетическое модельное упрощение организаторов симуляции, раскрытое инвентаризацией VDR-01, а не исчерпывающий отраслевой стандарт коммерческого учета убытков.

#### LIMITATIONS
* **UNKNOWN:** Применяются ли штрафные санкции торговых сетей сверх стоимости списанной продукции в модели челленджа.

#### STATUS
**PARTIALLY ANSWERED** (модель датасета понятна, но ее обобщение на отраслевые стандарты ограничено рамками симулятора).

---

### QUESTION 9 (Q9.1). Какие факторы влияют на принятие или отклонение оператором рекомендаций автоматизированных DSS?

#### AVAILABLE EVIDENCE
* 9.1 Rose, D. C., Sutherland, W. J., Parker, C., Lobley, M., Winter, M., Morris, C., Twining, S., Ffoulkes, C., Amano, T., & Dicks, L. V. (2016). Decision support tools in agriculture: Towards effective design and delivery. *Agricultural Systems*, 149, 165–174. DOI: 10.1016/j.agsy.2016.09.009.
* 9.2 Greer, J. E., Greer, G. J., & Ward, G. (1994). Explaining and justifying recommendations in an agriculture decision support system. *Computers and Electronics in Agriculture*, 11(2–3), 195–214. DOI: 10.1016/0168-1699(94)90006-4.
* 9.3 Grant, K., et al. (2026). Algorithm aversion in agricultural decision-making: Trust dynamics, barriers, and fertiliser-related decision support. Advance publication / Working paper.
* 9.4 Ara, I., Turner, L., Gyasi-Agyei, Y., & Li, M. (2021). Application, adoption and opportunities for improving decision support systems in irrigated agriculture: A review. *Agricultural Water Management*, 257, 107161. DOI: 10.1016/j.agwat.2021.107161.
* 9.5 CHALLENGE FACT: Критерии оценки решения жюри включают «Usability and Explainability» (`docs/challenge_canon.md`).

#### SUPPORTED FINDINGS
* **CHALLENGE FACT:** Объяснимость (*explainability*) и удобство использования (*usability*) — официальные нормативные критерии оценки решения жюри челленджа.
* **DOMAIN FACT:** Внедрение агро-DSS (Rose et al., 2016; Ara et al., 2021) определяется соответствием системы существующим рабочим процессам пользователей, надежностью алгоритмов, удобством интерфейса и прозрачностью логики рекомендаций (Greer et al., 1994). Неприятие алгоритмов (*algorithm aversion*) усиливается при отсутствии объяснения причин выдачи рекомендаций (Grant et al., 2026).
* **INFERENCE:** Гипотеза об усталости оператора от предупреждений (*alarm fatigue*) и снижении доверия из-за частых ложных тревог является общепринятым принципом когнитивной эргономики и human-machine interaction, однако в проанализированных агрономических источниках прямое эмпирическое тестирование эффекта alarm fatigue конкретно на диспетчерах холодильных складов не проводилось.
* **INFERENCE:** Отображение физических факторов риска (накопленные градусо-часы температурного стресса, отпотевание плодов) вместо абстрактного числового скора необходимо для соответствия обязательному критерию Explainability.

#### LIMITATIONS
* **UNKNOWN:** Прямые исследования восприятия рекомендаций DSS именно операторами коммерческих фруктохранилищ и диспетчерами рампы в литературе отсутствуют (исследованная в литературе популяция — фермеры, агрономы, консультанты).

#### STATUS
**PARTIALLY ANSWERED**

---

### QUESTION 10 (Q10.1). Какие культуры представлены в датасете Молдавии и каковы их биологические различия по стойкости?

#### AVAILABLE EVIDENCE
* 10.1 DATA FACT — VDR-01: В датасете строго **8 культур**:
  * `apples` (673 партии, 37.4%)
  * `plums` (350 партий, 19.4%)
  * `table_grapes` (310 партий, 17.2%)
  * `tomatoes` (180 партий, 10.0%)
  * `pears` (114 партий, 6.3%)
  * `strawberries` (63 партии, 3.5%)
  * `apricots` (60 партий, 3.3%)
  * `raspberries` (50 партий, 2.8%)
* 10.2 USDA ARS (2016) Gross, K. C., Wang, C. Y., & Saltveit, M. (Eds.), *The Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks*, Agriculture Handbook Number 66 (AH-66).
* 10.3 UC Davis Postharvest Technology Center — *Produce Fact Sheets*.

#### SUPPORTED FINDINGS (Биологический профиль 8 культур датасета):
* **DATA FACT — VDR-01:** Полный видовой состав и пропорции культур в датасете точно установлены (8 культур, 34 сорта).
* **DOMAIN FACT — Климактеричность и этилен:**
  * *Климактерические:* яблоки, груши, сливы, абрикосы, томаты.
  * *Неклимактерические:* столовый виноград, земляника (клубника), малина.
* **DOMAIN FACT — Оптимальные температуры и чувствительность к холоду:**
  * *Чувствительные к холодовому ожогу (Chilling Sensitive):* **томаты** (оптимум 10–13°C для зрелых плодов; при температуре ниже 10°C возникает риск физиологического повреждения тканей).
  * *Холодостойкие семечковые и косточковые:* яблоки (0..4°C), груши (-1..0°C), сливы (-0.5..0°C), абрикосы (-0.5..0°C), столовый виноград (-1..0°C).
  * *Ягоды:* земляника и малина (0°C, 90–95% RH).
* **DOMAIN FACT — Потенциал хранения:**
  * *Длительное хранение (месяцы):* яблоки (3–8 мес.), груши (2–6 мес.), столовый виноград (1–4 мес.).
  * *Среднее хранение (недели):* сливы (2–4 нед.), томаты (1–3 нед.), абрикосы (1–3 нед.).
  * *Сверхскоропортящиеся (дни):* земляника (5–10 дней), малина (2–5 дней).
* **OUT-OF-DATASET EXAMPLES:** Огурцы и сухой репчатый лук исключены из доказательной базы, так как отсутствуют в датасете челленджа.

#### LIMITATIONS
* **DATA FACT — VDR-01 / VDR-02:** Тот факт, что в `storage_zones.csv` комната `ZONE-004` имеет уставку 11.0°C (что совпадает с оптимумом томатов), зафиксирован инвентаризацией. Однако agronomic compatibility и товарное сожительство культур в 157 пространственно-временных кластерах требуют валидации в рамках моделирования признаков.

#### STATUS
**PARTIALLY ANSWERED** (биологические нормы 8 культур верифицированы; влияние совместного хранения и сортовой специфики требует калибровки в VDR-03/VDR-04).

---

## 3. Сводка статусов исследования

| № | Вопрос | Первоначальный статус | Согласованный статус | Основание калибровки |
|---|---|---|---|---|
| **Q1.1** | Ключевой пользователь | *Пропущен* | **PARTIALLY ANSWERED** | Роли описаны в литературе; конкретная персона для Smart Harvest — TEAM DECISION |
| **Q1.2** | Границы полномочий | *Пропущен* | **PARTIALLY ANSWERED** | Контрольные процедуры подтверждены; объем юридических прав зависит от контракта |
| **Q2.1** | Решения на $T_{dispatch}$ | *Пропущен* | **PARTIALLY ANSWERED** | Действия подтверждены; 4-шаговый цикл является кандидатным набором команды (INFERENCE) |
| **Q2.2** | Очередность FIFO vs FEFO | PARTIALLY ANSWERED | **PARTIALLY ANSWERED** | FEFO подтвержден в домене; статус в бизнес-процессах хабов не подтвержден |
| **Q3.1** | Отклонения микроклимата | PARTIALLY ANSWERED | **PARTIALLY ANSWERED** | Поля сенсоров установлены; критические пороги требуют привязки к культурам |
| **Q3.2** | Поверхностная конденсация | ANSWERED (качественно) | **ANSWERED** | Механизм подтвержден; составная логика синтетического флага раскрыта VDR-01 |
| **Q6.1** | Каталог действий на $T_{dispatch}$ | REQUIRES CLARIFICATION | **REQUIRES CHALLENGE CLARIFICATION** | Внешний каталог сформирован; допустимый action space челленджа открыт |
| **Q6.2** | Факторы и издержки действий | PARTIALLY ANSWERED | **PARTIALLY ANSWERED** | Формула потерь в EUR раскрыта VDR-01; затраты на логистические операции неизвестны |
| **Q7.1** | Начало ухудшения и остаточный срок | PARTIALLY ANSWERED | **PARTIALLY ANSWERED** | Поля инспекций известны; целевой эндпоинт челленджа не зафиксирован |
| **Q7.3** | Стойкость партии vs длительность рейса | PARTIALLY ANSWERED | **PARTIALLY ANSWERED** | PACA Suitable Shipping Condition = DOMAIN FACT; формула сопоставления = INFERENCE |
| **Q8.1** | Коммерческие потери | PARTIALLY ANSWERED | **PARTIALLY ANSWERED** | Таксономия датасета установлена VDR-01; отраслевой перенос ограничен симуляцией |
| **Q9.1** | Восприятие DSS оператором | PARTIALLY ANSWERED | **PARTIALLY ANSWERED** | Explainability подтверждена каноном; гипотеза alarm fatigue классифицирована как INFERENCE |
| **Q10.1**| Биология 8 культур датасета | REQUIRES DATA RECON | **PARTIALLY ANSWERED** | 8 культур подтверждены VDR-01, нормы верифицированы; размещение по камерам открыто |

---

## 4. Список оставшихся UNKNOWN после reconciliation с VDR-01, VDR-02 и ADR 0002

1. **UNKNOWN — Целевая персона Smart Harvest (Primary Persona):**
   Кто конкретно является главным действующим лицом в интерфейсе: технолог по качеству хранения или диспетчер рампы/логист отгрузки (требует решения команды SoS — TEAM DECISION).
2. **UNKNOWN — Реальные полномочия оператора (Operational Authority):**
   Имеет ли право выбранная персона самостоятельно отменять отгрузку или менять назначенный транспорт без согласования с коммерческим отделом и владельцем партии.
3. **UNKNOWN — Пошаговый операционный регламент (Operational Dispatch Workflow):**
   Какова точная последовательность действий диспетчера при оформлении выезда ТС на исследуемых складах Молдовы.
4. **UNKNOWN — Допустимое пространство действий челленджа (Permitted Action Space):**
   Какие именно варианты рекомендаций жюри челленджа признает корректными ответами на вопрос №4 брифа (только логистические маневры или технологические вмешательства).
5. **UNKNOWN — Целевой эндпоинт начала ухудшения (Deterioration Endpoint):**
   Какое конкретно событие в данных принимается за точку начала порчи для ответа на вопрос №2 челленджа (порог твердости, дефектов или переход в статус `degraded`).
6. **UNKNOWN — Эмпирическое поведение операторов складов при работе с DSS:**
   Специфические триггеры недоверия и частота отклонения алгоритмических подсказок операторами коммерческих фруктохранилищ.
7. **UNKNOWN — Фактические затраты и ограничения корректирующих действий:**
   Реальная стоимость заказа рефрижератора, переборки или уценки продукции в экономических условиях Молдовы 2024–2025 гг.
8. **UNKNOWN — Политика обработки усеченной телеметрии 2026 года (Telemetry Truncation Policy):**
   Какую стратегию оценки применять для 204 партий (11.33% датасета), у которых телеметрия сенсоров оборвана 31 декабря 2025 г. за 0.56–92.54 дня до момента отгрузки ($T_{dispatch}$): отказ в оценке (`insufficient_data`), срез окна, экстраполяция или деградация уверенности (зависит от будущих feature/evaluation решений VDR-03/VDR-04 и VLD-02).
9. **UNKNOWN — Агрономические правила и обобщаемость между культурами (Agronomic Rules & Generalization):**
   Валидные границы применения правил микроклимата для конкретных культур, биологическая совместимость при совместном хранении в 157 выявленных кластерах и степень применимости общих эвристик к специфическим помологическим сортам.
