STATUS: RESEARCH NOTE — NOT CANON

# APR-01: Source Strategy and Search Map (Step 3)

**Owner:** Alisa — Product Owner
**Workstream:** APR-01 Product & Requirements Recon
**Status:** Step 3 Research Note (NOT CANON)

---

## 1. Методология отбора и иерархия источников

Для формирования объективной доказательной базы продуктового исследования (APR-01) установлена строгая четырехуровневая иерархия источников (Source Tier Hierarchy). Ни одно ключевое решение или требование к системе не может основываться исключительно на вторичных или непроверенных материалах.

### Иерархия уровней (Source Tiers):
* **Tier 1 (Высший авторитет — нормативные и институциональные источники):**
  - Продовольственная и сельскохозяйственная организация ООН (FAO);
  - Государственные сельскохозяйственные ведомства и службы (USDA AMS, USDA ARS);
  - Международные стандарты качества и инспекции (UNECE Working Party on Agricultural Quality Standards);
  - Университетские службы сельскохозяйственного консультирования и исследований (University Extension Services: UC Davis Postharvest Technology Center, University of Florida IFAS, Cornell AgriTech, NC State Extension, University of Minnesota Extension);
  - Национальные институты аграрных исследований (INRAE, Embrapa).
* **Tier 2 (Академические рецензируемые издания и отраслевые стандарты):**
  - Рецензируемые научные статьи в профильных журналах (*Postharvest Biology and Technology*, *Computers and Electronics in Agriculture*, *Agricultural Systems*, *Food Control*, *HortScience*);
  - Академические обзоры и справочники (Elsevier, Springer, Wiley);
  - Отраслевые ассоциации холодильной цепи (Global Cold Chain Alliance — GCCA, International Institute of Refrigeration — IIR).
* **Tier 3 (Профессиональные отраслевые материалы):**
  - Технические руководства операторов логистических комплексов и перевозчиков рефрижераторных грузов (Carrier Transicold, Thermo King);
  - Профессиональные отраслевые регламенты и руководства ассоциаций производителей (Moldova Fruct, Freshfel Europe).
* **Tier 4 (Вторичные материалы — только для discovery):**
  - Профессиональные блоги, сайты коммерческих поставщиков IoT/WMS, статьи отраслевых порталов.
  - *Правило применения Tier 4:* Материалы Tier 4 допустимы **исключительно** для первичного поиска терминов, гипотез и отраслевого сленга. Они категорически не могут служить единственным доказательством для принятия решений или формулирования продуктовых требований.

---

## 2. Матрица стратегии поиска по ключевым вопросам (P0 Research Questions)

---

### Q1.1. Ключевой операционный пользователь системы
* **Целевой уровень источников:** Tier 1 (FAO, USDA AMS, UC Davis) + Tier 2 (GCCA, отраслевые стандарты складского менеджмента).
* **Поисковые запросы (English):**
  1. `"packhouse operations" "job roles" fresh produce cold storage manager quality inspector`
  2. `USDA AMS "shipping point inspection" roles duties inspector dispatch`
  3. `FAO "prevention of post-harvest food losses" packhouse management dispatch responsibilities`
  4. `GCCA cold storage standard operating procedures warehouse shipping supervisor`
* **Критерии достаточного доказательства (Sufficient Evidence):** Наличие в регламентах или учебных пособиях описания штатных ролей, разделения обязанностей между контролем качества (QC), технологическим управлением микроклиматом и диспетчеризацией отгрузки на рампе.
* **Ограничения источников:** Зарубежные регламенты крупных распределительных центров могут предполагать узкую специализацию персонала, тогда как в малых фермерских хозяйствах роли совмещаются.
* **Риски переноса (Transfer Risks):** Нельзя механически переносить структуру управления распределительного центра ритейла (DC Walmart/Tesco) на упаковочно-холодильный комплекс в регионе производства (Молдова).

---

### Q1.2. Границы полномочий и зона операционного контроля пользователя
* **Целевой уровень источников:** Tier 1 (UNECE Guidelines on Inspection, USDA AMS PACA) + Tier 2 (GCCA SOPs).
* **Поисковые запросы (English):**
  1. `fresh produce dispatch inspection "hold authority" rejection procedure packhouse`
  2. `UNECE inspection guidelines fruit vegetables pre-shipment surveyor powers`
  3. `PACA "shipping point" rejection cancellation authority seller buyer carrier`
  4. `cold storage loading dock protocol quarantine batch non-conformance`
* **Критерии достаточного доказательства:** Документированное подтверждение процедур наложения карантина (*hold*), требований повторного охлаждения, допуска/недопуска транспортного средства и права отмены рейса.
* **Ограничения источников:** Юридическая сила распоряжений оператора жестко зависит от условий контракта (собственная продукция агрохолдинга vs ответственное хранение для сторонних садоводов).
* **Риски переноса:** Права независимого государственного инспектора качества не тождественны полномочиям штатного складского диспетчера.

---

### Q2.1. Решения непосредственно на этапе отгрузки ($T_{dispatch}$)
* **Целевой уровень источников:** Tier 1 (UNECE, FAO, USDA AMS) + Tier 2 (GCCA).
* **Поисковые запросы (English):**
  1. `fruit vegetable dispatch checklist "pre-loading" temperature check procedures`
  2. `FAO manual preparation sale fruits vegetables dispatch transportation decisions`
  3. `cold chain dispatch decision tree carrier acceptance pallet release`
  4. `loading dock quality control produce truck temperature pulp check`
* **Критерии достаточного доказательства:** Описание последовательности верификационных действий оператора рампы перед подписанием транспортной накладной (замер температуры плодов, осмотр тары, проверка санитарии кузова, контроль термографа).
* **Ограничения источников:** Нормативные документы формулируют перечень проверок, но редко формализуют оптимизационную логику («что делать, если машина теплее нормы на 2 градуса»).
* **Риски переноса:** Процедуры приемочного контроля на стороне супермаркета-получателя не должны путаться с процедурами выпуска партии со склада отправителя.

---

### Q2.2. Приоритеты отгрузки: FIFO vs FEFO
* **Целевой уровень источников:** Tier 1 (FAO post-harvest bulletins) + Tier 2 (Academic literature on warehouse inventory management for perishables).
* **Поисковые запросы (English):**
  1. `perishable inventory FIFO vs FEFO fresh fruit cold storage dispatch rule`
  2. `FAO post-harvest storage management stock rotation bags bins`
  3. `condition-based dispatching fresh produce cold chain shelf life expiry`
  4. `first expired first out horticultural produce cold warehouse trade-offs`
* **Критерии достаточного доказательства:** Академические и институциональные исследования, сравнивающие потери продукции и коммерческие последствия при отгрузке по дате поступления (FIFO) и по остаточному сроку годности (FEFO).
* **Ограничения источников:** Большинство логистических моделей FEFO созданы для розничной торговли с маркировкой срока годности (*expiry date*), тогда как свежие фрукты навалом не имеют жесткого юридического срока годности.
* **Риски переноса:** Перенос жесткого FEFO из фарминдустрии или молочного сектора на свежие фрукты не учитывает требований конкретного заказа (покупатель А заказывает спелый фрукт для немедленной продажи, покупатель Б — плотный для последующей дозревательной камеры).

---

### Q2.3. Правила валидации транспорта и совместимости с маршрутом
* **Целевой уровень источников:** Tier 1 (FAO, UNECE) + Tier 2 (IIR, Transfrigoroute, GCCA) + Tier 3 (Carrier/Thermo King guides).
* **Поисковые запросы (English):**
  1. `reefer truck vs insulated van ambient transport fruit perishable distance limit`
  2. `FAO transportation of fresh horticultural produce vehicle selection guidelines`
  3. `refrigerated transport ATP agreement fresh fruit vegetables temperature rules`
  4. `cold chain transit duration ambient truck failure fresh produce`
* **Критерии достаточного доказательства:** Инженерные стандарты холодовой цепи (Соглашение СПС / ATP), определяющие допустимость перевозки нерефрижераторным транспортом в зависимости от температуры окружающей среды, длительности рейса и типа груза.
* **Ограничения источников:** Соглашение СПС обязательно для международных перевозок, но внутренние локальные перевозки часто регулируются менее жестко.
* **Риски переноса:** Использование неохлаждаемого транспорта допустимо для плотных зимних яблок на коротких плечах осенью, но смертельно для свежей малины или спелых персиков в летнюю жару.

---

### Q3.1. Критические отклонения микроклимата при хранении
* **Целевой уровень источников:** Tier 1 (USDA Agriculture Handbook 66, UC Davis Produce Facts, FAO).
* **Поисковые запросы (English):**
  1. `USDA Handbook 66 commercial storage fruits vegetables temperature humidity limits`
  2. `postharvest chilling injury critical temperature threshold commodities`
  3. `relative humidity deficit fruit storage weight loss transpiration FAO`
  4. `controlled atmosphere CO2 O2 tolerance limits apple plum table grape tomato`
* **Критерии достаточного доказательства:** Справочные таблицы оптимальных температур, критических точек подмораживания, порогов чувствительности к холодовому ожогу (*chilling injury*) и рекомендуемых концентраций газов для каждой из 8 культур датасета.
* **Ограничения источников:** Литературные оптимумы выведены для идеальных условий; реакция плода зависит от зрелости при сборе, подвоя, погодных условий сезона и помологического сорта.
* **Риски переноса:** Объединение норм хранения разнородных культур (например, попытка охладить томаты до 0°C, как яблоки, приведет к холодовому ожогу и гибели плодов).

---

### Q3.2. Физиологическое и микробиологическое влияние поверхностной конденсации
* **Целевой уровень источников:** Tier 1 (Extension Engineering Bulletins: NC State, UC Davis, Univ of Florida) + Tier 2 (Postharvest pathology journals).
* **Поисковые запросы (English):**
  1. `sweating surface condensation fruit postharvest Botrytis infection dew point`
  2. `produce surface temperature dew point condensation postharvest pathology`
  3. `free water fruit skin pathogen spore germination cold store humidity`
  4. `evaporator defrost cycle condensation risk packaged fruit cold storage`
* **Критерии достаточного доказательства:** Микробиологические данные о времени контакта свободной влаги с поверхностью плода, необходимом для прорастания спор серой гнили (*Botrytis cinerea*) и бактериальных гнилей при температурах хранения.
* **Ограничения источников:** Лабораторные исследования часто заражают плоды искусственно с повреждением кожицы, тогда как на складе неповрежденный восковой налет плода служит барьером.
* **Риски переноса:** Путаница между физической конденсацией влаги на плодах и техническим включением тэнов оттайки испарителя холодильной машины.

---

### Q6.1. Каталог корректирующих действий на этапе подготовки к отгрузке ($T_{dispatch}$)
* **Целевой уровень источников:** Tier 1 (FAO, UNECE Guidelines) + Tier 2 (Postharvest management reviews).
* **Поисковые запросы (English):**
  1. `packhouse dispatch corrective actions non-conforming batch fruit cold chain`
  2. `pre-cooling prior to loading reefer transport produce temperature management`
  3. `quarantine divert to processing fresh fruit packhouse standard procedure`
  4. `re-sorting re-packing fresh fruit postharvest loss mitigation options`
* **Критерии достаточного доказательства:** Документированные регламенты технологических операций по исправлению дефектов партии перед отправкой (доохлаждение, ручная переборка, замена транспорта, перевод в промпереработку).
* **Ограничения источников:** Наличие технологии не означает ее доступности на конкретном молдавском складе в момент отгрузки.
* **Риски переноса:** Рекомендация «перенаправить на локальный соковый завод» бессмысленна, если завод не принимает данную культуру или находится за 300 км.

---

### Q6.2. Факторы, ограничения и издержки выбора действий
* **Целевой уровень источников:** Tier 1 (FAO Agricultural Services Bulletins) + Tier 2 (Agricultural economics and logistics studies) + Tier 3 (Local industry reports: Moldova Fruct).
* **Поисковые запросы (English):**
  1. `cost benefit analysis postharvest intervention fresh fruit loss reduction`
  2. `cold chain transport cost reefer vs ambient truck fresh fruit export`
  3. `economic viability fruit repacking sorting labor cost postharvest`
  4. `fresh produce handling costs diverted processing price markdown`
* **Критерии достаточного доказательства:** Экономические модели оценки эффективности корректирующих воздействий (сопоставление затрат на интервенцию с предотвращенным ущербом).
* **Ограничения источников:** Ценовые параметры сильно варьируются по годам и регионам (инфляция, энерготарифы, логистические кризисы в Черноморском регионе).
* **Риски переноса:** Цены и логистические плечи Западной Европы или США неприменимы к молдавскому экспорту в ЕС или страны СНГ.

---

### Q7.1. Биологическое начало ухудшения качества и оценка остаточного срока жизни
* **Целевой уровень источников:** Tier 1 (FAO, UC Davis Postharvest) + Tier 2 (Postharvest Biology and Technology).
* **Поисковые запросы (English):**
  1. `biological senescence vs quality deterioration horticultural crops definition`
  2. `remaining shelf life estimation fresh fruit postharvest kinetic models`
  3. `fruit firmness sugar brix degradation rate postharvest cold storage`
  4. `commercial quality loss threshold fruit marketing standards UNECE`
* **Критерии достаточного доказательства:** Физиологические кинетические модели изменения твердости мякоти плодов (*firmness loss*), деградации кислот и сахаров, а также нормативные пороги товарных стандартов UNECE/OECD.
* **Ограничения источников:** Академические кинетические модели требуют знания точной температуры дыхания и сортовых констант, которые в реальном времени не калибруются.
* **Риски переноса:** Путаница между биологической смертью ткани и коммерческой потерей товарного вида (для супермаркета потеря тургора на 5% уже означает брак).

---

### Q7.2. Предотгрузочные показатели качества: пороговые значения и предиктивная ценность
* **Целевой уровень источников:** Tier 1 (UNECE Standards, USDA Grades) + Tier 2 (Sensory and instrumental quality evaluation literature).
* **Поисковые запросы (English):**
  1. `pre-dispatch quality inspection minimum firmness brix defect tolerance UNECE`
  2. `penetrometer firmness threshold export apple stone fruit table grape`
  3. `predicting transit survival fruit pre-shipment quality parameters`
  4. `maximum allowable defect percentage shipping point inspection fresh produce`
* **Критерии достаточного доказательства:** Официальные стандарты товарных сортов (Extra Class, Class I, Class II) с допустимыми процентами дефектов и минимальными значениями сахаристости (°Brix) и плотности.
* **Ограничения источников:** Товарный стандарт фиксирует статический допуск на момент осмотра, но не гарантирует динамику распада в пути при нарушении температурного режима.
* **Риски переноса:** Требования внутреннего рынка Молдовы могут существенно отличаться от допусков немецких или польских торговых сетей.

---

### Q7.3. Сопоставление остаточного срока жизни и длительности транспортировки
* **Целевой уровень источников:** Tier 1 (USDA AMS PACA, UNECE) + Tier 2 (Cold chain logistics papers).
* **Поисковые запросы (English):**
  1. `PACA suitable shipping condition normal transportation delivery fresh fruit`
  2. `shelf life transit duration matching fresh produce supply chain logistics`
  3. `safety margin shelf life transport duration perishable distribution`
  4. `good delivery standards perishable agricultural commodities act transit time`
* **Критерии достаточного доказательства:** Правовые и логистические формулировки пригодности продукции к транспортировке (PACA 7 C.F.R. § 46.43(i)), принципы назначения партий на короткие vs длинные маршруты.
* **Ограничения источников:** Закон PACA определяет принцип качественного соответствия, но сознательно избегает фиксации универсальной математической формулы «буфера безопасности» в часах или процентах.
* **Риски переноса:** Превращение правового критерия «Suitable Shipping Condition» в жесткую математическую формулу без калибровки на реальных данных.

---

### Q8.1. Классификация и фиксация коммерческих потерь при доставке
* **Целевой уровень источников:** Tier 1 (FAO, USDA AMS PACA) + Tier 2 (Food waste and loss quantification studies).
* **Поисковые запросы (English):**
  1. `fresh produce commercial loss categories arrival inspection claim rejection markdown`
  2. `FAO measurement post-harvest food losses supply chain wholesale retail`
  3. `PACA commercial dispute destination market inspection certificate loss fraction`
  4. `rejection at retail distribution center fresh fruit economic loss structure`
* **Критерии достаточного доказательства:** Отраслевые классификаторы причин рекламаций (температурные повреждения, механический бой, плесень, перезревание, срыв сроков поставки) и формы их финансового урегулирования.
* **Ограничения источников:** Официальные исследования отражают общие агрегированные цифры потерь в процентах, тогда как учет в конкретной компании закрыт коммерческой тайной.
* **Риски переноса:** Синтетическая модель датасета (`loss_fraction_pct` $\to$ 4 класса `quality_status`) является учебной аппроксимацией и не может отождествляться со сложной системой претензионной работы ритейла.

---

### Q9.1. Факторы доверия оператора и принятия рекомендаций DSS
* **Целевой уровень источников:** Tier 2 (Peer-reviewed human-computer interaction, agricultural decision support systems literature).
* **Поисковые запросы (English):**
  1. `agricultural decision support systems adoption barriers trust Rose 2016`
  2. `explaining justifying recommendations agricultural DSS Greer 1994`
  3. `algorithm aversion decision support farm logistics Grant 2026`
  4. `operator compliance decision support system alarm fatigue false alarms review`
* **Критерии достаточного доказательства:** Эмпирические исследования барьеров внедрения агро-DSS, влияния объяснимого ИИ (XAI) на комплаенс операторов и факторов отказа от рекомендаций.
* **Ограничения источников:** Практически все опубликованные работы по агро-DSS исследовались на фермерах в поле (орошение, удобрения, защита растений), а не на диспетчерах холодильных складов скоропорта.
* **Риски переноса:** Прямой перенос выводов о поведении фермера на линейного оператора рампы должен маркироваться как гипотеза (INFERENCE).

---

### Q10.1. Биологические особенности и стойкость 8 культур датасета
* **Целевой уровень источников:** Tier 1 (USDA Agriculture Handbook 66, UC Davis Postharvest Produce Facts) + Tier 2 (Horticultural monographs).
* **Поисковые запросы (English):**
  1. `USDA Handbook 66 storage requirements apples pears plums grapes tomatoes strawberries raspberries apricots`
  2. `UC Davis produce fact sheets postharvest storage life respiration ethylene`
  3. `chilling injury temperature thresholds tomato vs apple postharvest`
  4. `Moldova fruit export storage varieties Stanley Gala Victoria postharvest`
* **Критерии достаточного доказательства:** Авторитетные таблицы температурного, влажностного и газового режимов, чувствительности к этилену и предельных сроков хранения именно для 8 культур датасета: `apples`, `plums`, `table_grapes`, `tomatoes`, `pears`, `strawberries`, `apricots`, `raspberries`.
* **Ограничения источников:** Справочники дают усредненные диапазоны по видам; лежкость сильно дифференцирована по помологическим сортам (например, сорт яблок Голден Делишес хранится дольше, чем ранние летние сорта).
* **Риски переноса:** Включение культур, отсутствующих в учебном датасете (огурцы, лук, картофель), искажает фокус аналитики команды.

---

## 3. Стандарты оформления библиографического аппарата

Все привлекаемые источники должны верифицироваться по полной цепочке атрибуции:
$$\text{Title} \longrightarrow \text{Authors} \longrightarrow \text{Year} \longrightarrow \text{Journal / Publisher / Agency} \longrightarrow \text{Volume / Pages / Report ID} \longrightarrow \text{DOI / Official URL}$$

Примеры нормативного цитирования:
1. *Rose, D. C., Sutherland, W. J., Parker, C., Lobley, M., Winter, M., Morris, C., Twining, S., Ffoulkes, C., Amano, T., & Dicks, L. V.* (2016). Decision support tools in agriculture: Towards effective design and delivery. *Agricultural Systems*, 149, 165–174. DOI: [10.1016/j.agsy.2016.09.009](https://doi.org/10.1016/j.agsy.2016.09.009)
2. *Greer, J. E., Greer, G. J., & Ward, G.* (1994). Explaining and justifying recommendations in an agriculture decision support system. *Computers and Electronics in Agriculture*, 11(2–3), 195–214. DOI: [10.1016/0168-1699(94)90006-4](https://doi.org/10.1016/0168-1699(94)90006-4)
3. *Ara, I., Turner, L., Gyasi-Agyei, Y., & Li, M.* (2021). Application, adoption and opportunities for improving decision support systems in irrigated agriculture: A review. *Agricultural Water Management*, 257, 107161. DOI: [10.1016/j.agwat.2021.107161](https://doi.org/10.1016/j.agwat.2021.107161)
4. *Gross, K. C., Wang, C. Y., & Saltveit, M.* (Eds.). (2016). *The Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks*. Agriculture Handbook Number 66, USDA Agricultural Research Service.
5. *FAO* (1989). *Prevention of post-harvest food losses: fruit, vegetable and root crops a training manual*. FAO Training Series No. 17/2, Rome.
