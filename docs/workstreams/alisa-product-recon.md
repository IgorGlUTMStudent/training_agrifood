# APR-01 — Product & Requirements Recon

**Owner:** Alisa — Product Owner\
**Team:** SoS\
**Challenge:** Smart Harvest — Reduce Post-Harvest Losses\
**Status:** Training workflow\
**Repository:** `https://github.com/Slave-of-Skynet/training_agrifood`

---

## Цель

Твоя задача — провести **APR-01: Product & Requirements Recon**.

От тебя **не требуется опыт работы в сельском хозяйстве**. Твоя задача — правильно организовать исследование:

- поставить вопросы нейросети;
- отделить факты от предположений;
- найти и проверить источники;
- сопоставить evidence с продуктовыми вопросами;
- собрать понятный результат для команды;
- не позволить AI превратить догадки в требования проекта.

Не пытайся провести весь research одним большим запросом.

## Source hierarchy and role boundary

Use sources in this order:

1. current training challenge materials: `sponsor_pack/README.md`, the challenge brief, and relevant schema/data-dictionary material;
2. accepted SoS challenge decisions and shared contracts;
3. current challenge canon;
4. process guidance;
5. this workflow and its research notes.

The sponsor pack is a **SIMULATION / training source**. It does not prove facts about a real GigaHack provider or real Moldovan operations.

Alisa may inspect the supplied schema and targeted source records to understand product context. She does not own dataset-wide profiling, observed integrity, label usability, temporal/leakage measurement, or evaluation design; those remain Viktor's responsibility.

Работай по шагам:

`0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8`

Каждый следующий шаг выполняй **после просмотра результата предыдущего**.

---

# Пункт 0. Подготовить repository и познакомить с ним AI

## 0.1. Если repository ещё не скачан

Открой PowerShell:

```powershell
cd "$HOME\Documents"

git clone https://github.com/Slave-of-Skynet/training_agrifood.git

cd training_agrifood
```

Если repository уже скачан, просто перейди в его папку.

---

## 0.2. Обновить `main`

Выполни:

```powershell
git fetch origin

git switch main

git pull --ff-only origin main

git status --short

git rev-parse HEAD
```

В нормальной ситуации:

```powershell
git status --short
```

ничего не выводит.

Если там уже есть изменённые файлы — **STOP**.

Не делай:

```text
git reset
git restore
git clean
```

и ничего не удаляй.

Покажи вывод Владимиру.

Сохрани SHA из:

```powershell
git rev-parse HEAD
```

Это твоя `starting base`.

---

## 0.3. Создать свою ветку

```powershell
git switch -c alisa/apr-01-product-recon
```

Проверь:

```powershell
git branch --show-current
git status --short
```

Текущая ветка должна быть:

```text
alisa/apr-01-product-recon
```

Если у тебя есть доступ на запись в командный repository, ветку можно опубликовать:

```powershell
git push -u origin alisa/apr-01-product-recon
```

Это **не merge в `main`**.

---

## 0.4. Открыть repository в Antigravity

Открой папку:

```text
training_agrifood
```

как Project в Antigravity.

Создай новый чат:

```text
APR-01 Product & Requirements Recon
```

Весь APR-01 веди в одном этом чате.

Не создавай новый чат для каждого пункта: следующие prompts — этапы одной задачи.

---

## Prompt 0 — знакомство AI с repository

Отправь:

```text
Мы начинаем APR-01 Product & Requirements Recon для тренировочного AgriFood challenge Smart Harvest.

Сначала проведи ТОЛЬКО read-only reconnaissance repository.

Прочитай как минимум:

- README и основные документы repository;
- docs/challenge_canon.md
- docs/assumptions_unknowns.md
- docs/team_roles.md
- docs/domain_rules.md
- docs/data_contract.md
- docs/evaluation.md
- sponsor_pack/README.md
- sponsor_pack/brief/Training Challenge #3 — AgriFood.md
- sponsor_pack/data/data_dictionary.xlsx and the relevant CSV headers/schema material

Также можешь читать любые другие относящиеся к задаче файлы.

Цель этого шага:
1. понять назначение repository;
2. определить, какие документы являются challenge/product context;
3. определить, какие вопросы уже считаются UNKNOWN;
4. определить границы роли Product Owner;
5. найти ограничения, которые особенно важны для product/domain research.

Apply this precedence: sponsor materials first for supplied challenge facts, then accepted SoS decisions/contracts, then challenge canon, then process guidance, then workstream notes. Treat sponsor content as SIMULATION. Inspect schema only to understand product context; do not perform Viktor's dataset-wide profiling.

Ничего не изменяй.
Не создавай файлы.
Не редактируй documentation.
Не исследуй пока интернет.
Не пытайся решить challenge.

В результате верни:

- какие файлы ты прочитал;
- краткое назначение каждого релевантного файла;
- какие ограничения для APR-01 уже видны;
- какие потенциальные конфликты или неопределённости заметил.

Отдельно подтверди, что никаких файлов не изменял.
```

Прочитай ответ.

Если AI начинает предлагать:

- ML-модель;
- конкретные агрономические пороги;
- готовый продукт;
- новые requirements;

пока игнорируй эти предложения.

---

# Пункт 1. Разобрать уже известный контекст

Теперь нужно установить, что мы уже знаем **до внешнего исследования**.

На этом шаге используем только:

- исходный AgriFood challenge;
- repository documentation;
- уже зафиксированные решения команды.

Интернет пока **не используется**.

---

## Prompt 1 — Context inventory

```text
Теперь выполни второй этап APR-01.

Используй ТОЛЬКО:
- официальный текст тренировочного Smart Harvest challenge;
- уже прочитанную repository documentation.

Не используй внешние знания об агросекторе.
Не используй web search.
Не достраивай отсутствующую информацию.

Раздели известный контекст на шесть категорий.

A. SUPPLIED / DOCUMENTED FACT

Только то, что прямо документировано sponsor pack, challenge или repository canon.

Для каждого FACT укажи точный источник:
- challenge;
или
- путь repository-файла.

B. OBSERVED EVIDENCE

То, что было установлено прямой проверкой repository, schema/header или выполненной проверкой. Не выдавай заявленное в документации за наблюдаемое качество данных.

C. ACCEPTED DECISION

Только явно зафиксированные внутренние решения команды SoS.

Не превращай архитектурные предположения или skeleton behaviour в продуктовые решения.

D. ASSUMPTION / INFERENCE

Логичные или рабочие выводы, которые ещё не подтверждены. Для каждого укажи исходные факты и evidence, способный подтвердить или опровергнуть вывод.

E. PENDING VALIDATION

То, что sponsor pack документирует, но что ещё требует проверки Виктором или другим owner: например observed integrity, coverage, label usability или evaluation-safe semantics.

F. REMAINING UNKNOWN

Вопросы, на которые сейчас нет подтверждённого ответа, но которые могут быть важны для продукта.

Для каждого UNKNOWN укажи:
- почему это важно;
- какое продуктовое решение этот UNKNOWN блокирует;
- может ли его закрыть domain research, Viktor Data Recon или только mentor/challenge clarification.

Особенно проверь темы:

- кто пользователь;
- какую работу он выполняет;
- какие решения принимает;
- какие четыре ответа должен дать Smart Harvest;
- какие данные предполагаются challenge;
- storage;
- transportation;
- deterioration;
- loss;
- actions;
- explainability;
- business usefulness.

Отдельно зафиксируй `T_assess = T_dispatch`: какая информация документированно известна к dispatch, какая доступность ещё требует проверки, и какая post-dispatch/arrival/final информация запрещена как predictive input. Публичное наличие исторической future information не делает её допустимой feature.

Не предлагай пока продуктовый дизайн.
Не создавай агрономические правила.
Не устанавливай пороги.
Не придумывай dataset fields.

Верни сначала результат в чат. Файлы пока не меняй.
```

После ответа проверь, не записала ли нейросеть предположение в `FACT`.

Если утверждение выглядит сомнительно, спроси:

```text
Покажи точный источник для этого утверждения и объясни, почему ты классифицировал его как FACT, а не INFERENCE.
```

---

# Пункт 2. Составить вопросы для большого исследования

Теперь у нас есть `UNKNOWN` и `INFERENCE`.

Следующая задача — **не искать ответы**, а правильно поставить вопросы.

---

## Prompt 2 — Research Questions

```text
Используй результаты предыдущего шага.

Теперь составь research question set для Product Owner.

Пока НЕ ищи ответы и НЕ проводи web research.

Нам нужно определить, что необходимо узнать о реальном post-harvest workflow, чтобы спроектировать полезный Smart Harvest product.

Составь вопросы по следующим направлениям:

1. User
Кто реально может пользоваться такой системой?

2. Decisions
Какие решения этот человек принимает после harvest, во время storage и transportation?

3. Problems
Какие события или состояния заставляют его вмешиваться?

4. Information needs
Что ему необходимо знать, чтобы решить, чему уделить внимание первым?

5. Risk explanation
Какая информация делает предупреждение понятным и объяснимым?

6. Actions
Какие типы действий вообще доступны оператору после обнаружения проблемы?

7. Timing
Что означает "действовать вовремя" в реальных post-harvest workflows?

8. Business impact
Как на практике проявляются post-harvest losses?

9. Trust / usability
Почему оператор может доверять или не доверять автоматической рекомендации?

10. Constraints
Какие важные ограничения зависят от crop, storage type, transportation или других условий?

11. Decision-time availability
Что оператор действительно знает к `T_dispatch`, какие planned transport facts доступны, и какая retrospective arrival/post-dispatch information не может влиять на prediction или product framing?

Для каждого вопроса укажи:

- Priority: P0 / P1 / P2;
- почему ответ важен для Smart Harvest;
- какое продуктовое решение он поможет принять;
- какого типа evidence нужен;
- кем вопрос вероятнее всего закрывается:
  DOMAIN RESEARCH
  DATA RECON
  CHALLENGE CLARIFICATION
  TEAM DECISION

Не отвечай на вопросы.
Не придумывай факты.
Не начинай web search.

После составления отдельно выбери 10–15 P0 вопросов, с которых должно начаться исследование.
```

После ответа проверь каждый P0 вопрос:

> Если мы получим на него ответ, поможет ли это команде сделать продукт?

Если нет — вопрос можно убрать или понизить приоритет.

---

# Пункт 3. Определить, где искать ответы

Теперь каждому важному вопросу нужно подобрать подходящий тип источников.

На этом шаге AI ещё **не должен делать продуктовые выводы**.

---

## Prompt 3 — Source Strategy

```text
Теперь для каждого P0 research question составь Source Strategy.

Пока не делай выводов о Smart Harvest.

Для каждого вопроса укажи:

1. Какие источники лучше всего подходят для ответа.

Используй следующий приоритет:

Tier 1:
- FAO;
- государственные agricultural agencies;
- official food/agriculture authorities;
- university agricultural extension services;
- recognised post-harvest research institutions.

Tier 2:
- peer-reviewed papers;
- academic reviews;
- recognised agricultural standards / industry organisations.

Tier 3:
- professional industry material.

Tier 4:
- blogs, vendor pages, SEO articles и другие вторичные материалы.

Tier 4 можно использовать только для discovery, но не как единственное доказательство важного утверждения.

2. Какие поисковые запросы использовать.

Для каждого вопроса предложи 2–4 конкретных search queries на английском.

3. Какое evidence будет считаться достаточным.

4. Какие ограничения источника необходимо проверить:
- crop;
- geography;
- storage type;
- transportation conditions;
- date;
- study population;
- experimental vs operational context.

5. Какие ошибки возможны при переносе найденного факта в Smart Harvest.

Не придумывай ответы на вопросы.
Сейчас результат — карта поиска, а не domain conclusions.
```

После этого должна получиться схема:

```text
вопрос → где искать → что считать достаточным evidence → какие ограничения проверить
```

---

# Пункт 4. Провести внешнее исследование

Теперь можно использовать AI с web search.

Работай небольшими группами:

```text
3–5 P0 вопросов за один research pass
```

Не проси AI исследовать сразу все вопросы.

---

## Prompt 4 — Web Research

```text
Проведи evidence-oriented web research по следующим research questions:

[ВСТАВЬ 3–5 ВОПРОСОВ]

Следуй нашей Source Strategy.

Приоритет источников:
1. FAO / government agricultural agencies;
2. university agricultural extension / recognised research institutions;
3. peer-reviewed research;
4. recognised industry sources.

Не используй случайные блоги как основное доказательство.

Для каждого найденного источника верни:

SOURCE
- название;
- организация / автор;
- дата, если доступна;
- URL.

SUPPORTS
- какой research question он помогает закрыть;
- какое конкретное утверждение поддерживает.

SCOPE
- crops;
- geography;
- storage/transport context;
- другие существенные ограничения.

EVIDENCE STATUS
- strong;
- partial;
- contextual;
- insufficient.

LIMITATIONS
- почему этот источник нельзя автоматически распространить на весь Smart Harvest challenge.

IMPORTANT:

Не превращай crop-specific evidence в универсальное правило.

Не устанавливай thresholds для нашего продукта.

Не утверждай, что конкретное поле существует в нашем dataset.

Не создавай рекомендации Smart Harvest.

Не называй external domain information официальным challenge requirement.

Если надёжного evidence нет — пиши UNKNOWN.

Предпочитай краткий paraphrase вместо длинного цитирования.
```

---

## Ручная проверка источников

Для основных источников обязательно сама открой ссылку.

Не нужно читать каждую научную работу полностью.

Проверь хотя бы:

- источник действительно существует;
- организация соответствует заявленной;
- материал действительно относится к нужной теме;
- утверждение AI действительно поддерживается источником;
- вывод не относится только к конкретной культуре;
- контекст исследования не отличается критически от нашего случая.

Только после этого источник можно пометить:

```text
REVIEWED
```

---

# Пункт 5. Сопоставить evidence с вопросами

Когда источники проверены, возвращаемся к research questions.

---

## Prompt 5 — Evidence Mapping

```text
Теперь сопоставь ПРОВЕРЕННЫЕ источники с research questions.

Используй только материалы, которые я обозначу как reviewed.

Для каждого research question покажи:

QUESTION

AVAILABLE EVIDENCE
Какие reviewed sources к нему относятся.

SUPPORTED FINDINGS
Что действительно можно утверждать на основании источников.

LIMITATIONS
Что источник не позволяет утверждать.

STATUS
Один из вариантов:
- ANSWERED
- PARTIALLY ANSWERED
- STILL UNKNOWN
- REQUIRES DATA RECON
- REQUIRES CHALLENGE CLARIFICATION

PRODUCT RELEVANCE
Почему этот вывод важен для Smart Harvest.

Очень важно различать:

CHALLENGE FACT
То, что требует challenge.

DOMAIN FACT
То, что подтверждают внешние источники.

INFERENCE
Наш аналитический вывод.

RECOMMENDATION
Предложение команде.

UNKNOWN
То, что всё ещё неизвестно.

Не смешивай эти категории.

Не создавай ещё финальный product workflow.
```

На этом этапе должно стать понятно:

```text
что мы действительно узнали
vs
что всё ещё только выглядит логичным
```

---

# Пункт 6. Построить модель пользователя и решений

Теперь domain research можно превратить в продуктовый смысл.

Пока **без проектирования UI**.

---

## Prompt 6 — User Decision Model

```text
Используя:

- confirmed challenge requirements;
- repository canon;
- reviewed domain evidence;
- current UNKNOWNs;

построй Product User / Decision Model для Smart Harvest.

Не проектируй интерфейс.

Определи:

1. Primary user candidates.
Кто потенциально является основным пользователем.

2. User goal.
Чего он пытается добиться в контексте post-harvest operations.

3. Decisions.
Какие решения ему приходится принимать.

4. Decision triggers.
Какие события или сигналы могут заставить его обратить внимание на batch.

5. Required information.
Что необходимо знать для принятия каждого решения.

6. Prioritisation.
Почему пользователю важно понять, какая проблема требует внимания первой.

7. Explainability.
Что нужно объяснить человеку, чтобы risk warning был полезным.

8. Candidate actions.
Какие классы действий встречаются в reviewed domain evidence.

Для каждого candidate action обязательно укажи:
- evidence;
- scope;
- необходимые данные;
- ограничения;
- потенциальный риск неправильной рекомендации.

Никакое candidate action не считать автоматически разрешённой рекомендацией Smart Harvest.

9. Dataset dependencies.
Какие элементы этой модели должны быть проверены результатами Виктора.

10. Assessment-time boundary.
Для каждого decision trigger, required information и candidate action укажи, доступна ли supporting information к `T_dispatch`. Arrival inspection, actual delay/incidents, final outcomes и другие future observations не могут быть скрытой зависимостью predictive path.

Для каждого существенного утверждения используй маркировку:

CHALLENGE FACT
DOMAIN FACT
INFERENCE
RECOMMENDATION
UNKNOWN

Если evidence недостаточно — оставляй UNKNOWN.
```

---

# Пункт 7. Построить Product Workflow

Только теперь можно перейти к тому, как должен работать продукт на уровне пользовательского решения.

---

## Prompt 7 — Product Workflow

```text
На основе подтверждённого контекста составь proposed Smart Harvest operator workflow.

Это продуктовый workflow, НЕ UI design.

Нужно показать путь:

вход пользователя
→ обнаружение приоритетной проблемы
→ выбор batch
→ понимание риска
→ понимание причин
→ понимание срочности
→ возможное действие
→ решение оператора.

Проверь workflow против четырёх обязательных outcomes challenge:

1. Which batches are most at risk?
2. When may quality begin to deteriorate?
3. What factors contribute to the risk?
4. What action should be prioritised?

Для каждого этапа workflow укажи:

- какой вопрос пользователя закрывается;
- какая информация нужна;
- подтверждает ли это challenge;
- зависит ли это от Viktor Data Recon;
- является ли это FACT / INFERENCE / RECOMMENDATION / UNKNOWN.

На каждом predictive этапе отдельно укажи, что оператор знает к dispatch. Не используй retrospective outcome/arrival information как объяснение dispatch-time prediction. Planned transport information, известную к dispatch, отличай от realized transport outcome.

Также составь:

A. Minimum useful information
Что, вероятно, должно быть доступно оператору в первую очередь.

B. Secondary information
Что можно раскрывать позже.

C. Claims we must NOT make yet
Что Smart Harvest пока не имеет права обещать.

D. Open product questions
Что всё ещё не решено.

Не проектируй конкретные кнопки, layout или visual design.
Это будет отдельный UX workflow.
```

---

# Пункт 8. Провести adversarial review

Теперь попроси AI атаковать собственную работу.

---

## Prompt 8 — проверка на выдумки и requirement drift

```text
Проведи adversarial review всей работы APR-01.

Не улучшай текст автоматически.

Ищи только проблемы.

Проверь:

1. Есть ли assumption, выданный за FACT.

2. Есть ли external domain recommendation, выданная за challenge requirement.

3. Есть ли crop-specific evidence, ошибочно распространённый на все crops.

4. Есть ли придуманные dataset fields.

5. Есть ли придуманные thresholds.

6. Есть ли рекомендация действия без достаточного evidence.

7. Есть ли утверждение, которое на самом деле должен подтвердить Viktor Data Recon.

8. Есть ли слишком сильный business claim.

9. Есть ли обещание точности, deterioration time или loss reduction без evidence.

10. Есть ли product decision, который команда ещё явно не принимала.

11. Есть ли важный UNKNOWN, который потерялся по ходу исследования.

12. Есть ли arrival-stage information, actual post-dispatch event, final outcome или другая future observation, которая стала явной или скрытой зависимостью dispatch-time prediction, explanation, prioritisation или recommendation.

13. Не перепутана ли planned transport information, известная к dispatch, с realized transport outcome.

Для каждой найденной проблемы верни:

- problematic statement;
- classification;
- why it is unsafe;
- evidence needed;
- suggested correction category.

Не переписывай всю работу.
```

Исправляй только те проблемы, которые понимаешь.

Если непонятно — спроси Владимира.

---

# Что разрешено писать в repository

До завершения research не изменяй:

```text
docs/challenge_canon.md
docs/domain_rules.md
docs/data_contract.md
```

Также не изменяй:

- architecture;
- application code;
- dependencies;
- config;
- schema;
- shared contracts.

Для APR-01 write scope:

```text
docs/product_recon/
```

Каждый research-файл должен начинаться с:

```text
STATUS: RESEARCH NOTE — NOT CANON
```

---

## Рекомендуемая структура

```text
docs/product_recon/
  01_context_inventory.md
  02_research_questions.md
  03_source_map.md
  04_evidence_map.md
  05_user_decision_model.md
  06_proposed_product_workflow.md
```

Не обязательно создавать всё сразу.

Сохраняй результат каждого этапа только после того, как просмотрела его в чате.

---

# Как попросить AI сохранить утверждённый этап

```text
Сохрани утверждённый результат этого этапа в:

docs/product_recon/[ИМЯ_ФАЙЛА]

Добавь в начало:

STATUS: RESEARCH NOTE — NOT CANON

Не изменяй никакие другие файлы.

После записи верни:
- changed files;
- кратко что записано;
- подтверждение, что другие файлы не изменялись.
```

---

# STOP CONDITIONS

Остановись и напиши Владимиру, если:

- AI предлагает изменить `challenge_canon.md`;
- требуется изменить `data_contract.md`;
- требуется поменять schema/API;
- AI хочет добавить dependencies;
- появился конфликт с текущим canon;
- найдено новое требование challenge;
- критический вывод зависит от ещё не полученного Viktor Data Recon;
- два сильных источника противоречат друг другу;
- непонятно, является ли утверждение `FACT` или предположением;
- для продолжения требуется решение всей команды.

Не разрешай AI самостоятельно решать такие конфликты.

---

# Финальный handoff Владимиру

После завершения APR-01 выполни:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git diff --check
git diff
git ls-files --others --exclude-standard
```

Не делай самостоятельно:

```text
commit
merge
release
изменение main
```

без отдельного решения Владимира.

Передай Владимиру:

1. starting base SHA;
2. текущую ветку;
3. `git status --short`;
4. список созданных и изменённых файлов;
5. 3–5 наиболее важных продуктовых выводов;
6. основные `UNKNOWN`;
7. вопросы, которые должен закрыть Viktor Data Recon;
8. вопросы для mentor / challenge owner;
9. список реально просмотренных внешних источников;
10. возможные `Proposed canon updates`, но без изменения canon;
11. что осталось непроверенным;
12. были ли изменены dependencies / config / schema / shared contracts — ожидаемый ответ для APR-01: `нет`.

---

# Главный принцип APR-01

AI помогает:

```text
искать
→ сортировать
→ сопоставлять
→ проверять
→ критиковать
→ структурировать
```

Но AI **не получает право самостоятельно превращать найденное в требования Smart Harvest**.

Цепочка должна оставаться такой:

```text
что мы знаем
→ чего мы не знаем
→ какие вопросы нужно задать
→ где искать evidence
→ что evidence действительно подтверждает
→ что это означает для пользователя
→ что поддерживает dataset
→ что остаётся UNKNOWN
→ какие решения должен принять человек
```

---

# Рекомендуемый gate процесса

Не обязательно выполнять весь APR-01 без остановки.

Предпочтительный порядок:

```text
Пункт 0
→ Пункт 1
→ handoff / review
→ Пункт 2
→ review
→ Пункты 3–5
→ review
→ Пункты 6–8
→ финальный handoff
```

Если Владимир отдельно не сказал продолжать весь workflow сразу, после существенного этапа лучше вернуть результат на review.

`ACCEPTABLE` после review означает только, что evidence достаточно для следующего шага. Это не разрешение на commit, merge или изменение canonical documents.
