# Prscr — UX, Demo + QA workflow для Training AgriFood

## Роль

Твоя основная зона ответственности в этом challenge:

**сделать так, чтобы решение было понятно пользователю, удобно показывалось на demo и не разваливалось в пользовательских сценариях.**

То есть твоя задача — не просто «сделать красивый frontend».

Ты отвечаешь за цепочку:

**данные/аналитика → понятный экран → понятная причина риска → понятное действие → надёжная демонстрация**

При этом ты не должен сам придумывать сельскохозяйственные правила, risk thresholds, модель расчёта риска или поля dataset. Этим занимаются другие workstreams.

---

# 0. Подготовь рабочее окружение

## 0.1. Скачай репозиторий

Репозиторий:

`https://github.com/Slave-of-Skynet/training_agrifood`

Если его ещё нет:

```powershell
git clone https://github.com/Slave-of-Skynet/training_agrifood.git
cd training_agrifood
```

Если уже скачан:

```powershell
cd training_agrifood
git fetch origin
git switch main
git pull --ff-only origin main
```

После этого создай отдельную рабочую ветку:

```powershell
git switch -c prscr/ux-demo-qa
```

Проверь:

```powershell
git status --short
git branch --show-current
git rev-parse HEAD
```

Ожидаемо:

```text
prscr/ux-demo-qa
```

Сохрани полный SHA из `git rev-parse HEAD` как actual starting/base SHA для этого запуска. `git status --short` перед работой должен быть пустым. Если видны неожиданные локальные изменения, **STOP**: не reset, restore, clean, stash или overwrite; передай Владимиру фактический status/diff.

Если какая-либо Git-команда выдаёт ошибку — **не пытайся чинить историю репозитория самостоятельно**. Скопируй Владимиру команду и полный текст ошибки.

Не делай `force push`, reset общей ветки, merge в `main` и не изменяй чужие ветки.

## 0.2. Compact execution contract for PUX-00–07

This phase is research and design reconnaissance, not frontend implementation.

Source precedence:

1. current sponsor pack, challenge brief, and relevant schema/data dictionary;
2. accepted SoS decisions and shared contracts;
3. challenge canon;
4. process guidance;
5. this workflow and non-canonical research notes.

The sponsor pack is a **SIMULATION / training source**, not proof about a real GigaHack provider.

Read-only AI reconnaissance may remain in chat. Reviewed research that needs to persist may be saved only as:

```text
docs/recon/PUX-00-07-ux-demo-qa.md
```

That artifact must start with:

```text
STATUS: RESEARCH NOTE — NOT CANON
```

Do not save raw AI transcripts. Do not modify frontend, backend, sponsor files, shared contracts, dependencies, lockfiles, configuration, schema, architecture, or canonical documentation during PUX-00–07.

Positive acceptance requires a reviewed context inventory, UX questions, sourced pattern notes, a provisional operator flow, semantic low-fi specification, demo skeleton, and QA plan that preserve current failure/degraded states and identify all unresolved dependencies.

Failure cases include invented dataset fields, agronomic thresholds, risk probabilities, deterioration times, actions, use of future information in a dispatch prediction, or claims that planned QA cases were actually executed.

Evidence/handoff must include starting SHA, branch, current HEAD, `git status --short`, changed/untracked files, sources actually reviewed, the research artifact if saved, planned QA cases, QA checks actually executed with results, remaining blockers, and explicit confirmation that application code/contracts/dependencies/config/sponsor files were unchanged.

---

## 0.3. Познакомь AI с проектом

Открой репозиторий в Antigravity.

На этом этапе **ничего не меняй**.

Дай Antigravity следующий prompt.

## PROMPT PUX-00 — Repository reconnaissance

```text
You are helping me as a UX, Demo + QA owner for the SoS Training AgriFood project.

Repository:
https://github.com/Slave-of-Skynet/training_agrifood

This is reconnaissance only.

DO NOT edit files.
DO NOT create files.
DO NOT change dependencies, configuration, schemas, contracts, architecture, or application code.

First inspect the actual repository.

At minimum read:

- README.md
- docs/challenge_canon.md
- docs/team_roles.md
- docs/assumptions_unknowns.md
- docs/data_contract.md
- docs/demo_runbook.md
- docs/architecture.md
- docs/evaluation.md
- relevant docs/decisions/*
- sponsor_pack/README.md
- sponsor_pack/brief/Training Challenge #3 — AgriFood.md
- sponsor_pack/data/data_dictionary.xlsx and relevant supplied CSV headers/schema material
- frontend/package.json
- frontend/src/**
- relevant backend API contracts used by the frontend

You may inspect any additional relevant files.

My role is:

UX, Demo + QA.

My responsibility includes:

- frontend and operator-facing workflow;
- usability and clarity;
- loading / empty / insufficient-data / failure states;
- demo flow and demo reliability;
- exploratory QA;
- checking whether a user can understand the product without knowing its implementation.

Important:

Use the source precedence stated in this workflow. Treat sponsor materials as SIMULATION.

The predictive decision moment is `T_assess = T_dispatch`. Distinguish information genuinely known/planned by dispatch from retrospective arrival, realized transport, post-dispatch telemetry, and final outcome information.

Do not infer challenge requirements from code.

Distinguish:

FACT
DECISION
OBSERVED PRACTICE
INFERENCE
RECOMMENDATION
UNKNOWN
SIMULATION

Do not convert synthetic/demo data into real agricultural facts.

Report:

1. Current committed product state.
2. What the frontend currently actually does.
3. Current user-visible states.
4. Existing API/frontend contracts relevant to UX.
5. Existing demo behaviour.
6. What is already implemented versus only planned.
7. Important UNKNOWNs blocking final UX design.
8. Files that are likely to matter for future UX work.
9. Things I must NOT assume yet.
10. Questions that should be answered by Product/Data/Integrator before implementation.

For every important claim, cite the repository path that supports it.

End with:

READ FILES
CURRENT STATE
KNOWN CONTRACTS
UX DEPENDENCIES
UNKNOWN
RISKS
QUESTIONS FOR TEAM

Do not propose implementation yet.
```

---

# Что сейчас фактически происходит

Сейчас репозиторий содержит только foundation приложения.

Текущий frontend уже умеет показывать несколько состояний:

- подключение к backend;
- успешное соединение;
- backend unavailable;
- retry;
- synthetic assessment;
- `insufficient_data`.

Но это пока **не готовый Smart Harvest dashboard**.

Текущий demo также не доказывает agricultural usefulness, prediction accuracy или reduction of food loss.

Поэтому сейчас твоя работа начинается **не с переписывания HomePage**, а с определения того, каким должен стать пользовательский workflow.

---

# 1. Разбери challenge именно с точки зрения UX

В challenge есть четыре вещи, которые пользователь в конечном итоге должен понять:

**какие партии наиболее рискованные;**

**когда может начаться ухудшение качества;**

**что создаёт риск;**

**какое действие нужно выполнить первым.**

Но это ещё не означает, что мы знаем:

- каким будет risk score;
- будет ли score вообще процентом;
- будет ли точная дата deterioration;
- какие факторы есть в dataset;
- какие рекомендации реально можно доказать;
- какие agricultural thresholds допустимы.

Поэтому сначала раздели известное и неизвестное.

Дай AI отдельный prompt.

## PROMPT PUX-01 — UX facts / decisions / unknowns

```text
Act as a UX/product analyst for the SoS Smart Harvest training challenge.

Use the repository you have already inspected.

Do NOT edit anything.

I need to establish the UX design boundary before designing screens.

Extract information relevant specifically to UX, demo and QA.

Classify every important item as:

FACT
DECISION
OBSERVED PRACTICE
INFERENCE
RECOMMENDATION
UNKNOWN
SIMULATION

Concentrate on:

- who the apparent operator/user is;
- what decisions the product needs to help them make;
- what information the challenge explicitly expects the user to understand;
- what information the repository currently exposes;
- what information does NOT exist yet;
- what must never be fabricated in the UI;
- which states must be explainable;
- which UX decisions depend on Data work;
- which UX decisions depend on Product work;
- which decisions can be made by UX independently.

Also classify what the operator knows at `T_dispatch` versus what exists only retrospectively. Arrival-stage inspection, actual post-dispatch delay/incidents, unavailable post-dispatch telemetry and final outcomes must not be required or shown as explanatory evidence for a dispatch prediction. Distinguish planned transport information from realized transport outcomes.

Pay special attention to these intended outcomes:

1. Which batches are most at risk?
2. When may deterioration begin?
3. What contributes to the risk?
4. What action should be prioritized?

Do NOT invent answers to them.

Instead determine what the eventual UI will need to communicate if the underlying analytics can support them.

Output:

A. FACTS
B. EXISTING TEAM DECISIONS
C. UX-RELEVANT UNKNOWNs
D. SAFE INFERENCES
E. THINGS THE UI MUST NOT CLAIM YET
F. DEPENDENCIES ON VIKTOR / DATA
G. DEPENDENCIES ON ALISA / PRODUCT
H. UX WORK THAT CAN START NOW
```

## Что от тебя требуется после PUX-01

Прочитай результат.

Твоя задача не просто переслать ответ AI.

Проверь, чтобы AI нигде не написал что-нибудь вроде:

> «Tomatoes above 8°C are high risk»

если такого правила нет в наших источниках.

Или:

> «Risk score будет от 0 до 100»

если команда ещё этого не решила.

Такие вещи должны оставаться `UNKNOWN` или `RECOMMENDATION`.

---

# 2. Составь вопросы, на которые UX должен получить ответы

Теперь не ищи ответы сразу.

Сначала составь правильные вопросы.

Для этого отдельный prompt.

## PROMPT PUX-02 — UX research questions

```text
Using the previous UX context analysis, create a research question set for the UX, Demo + QA workstream.

Do not answer the questions yet.

The objective is to understand what must be known before we can build a useful Smart Harvest operator interface.

Group questions around:

1. Operator/user workflow.
2. Batch prioritization.
3. Risk communication.
4. Deterioration timing communication.
5. Explainability / contributing factors.
6. Recommended actions.
7. Inventory / batch navigation.
8. Loading / missing-data / insufficient-data behaviour.
9. Error and degraded states.
10. Demo comprehension.
11. Accessibility and visual hierarchy.
12. Mobile / laptop demo constraints.
13. Trust and avoiding false precision.
14. QA and failure scenarios.

For each question provide:

- question;
- why UX needs the answer;
- who should answer it:
  DATA / PRODUCT / DOMAIN RESEARCH / TECHNICAL / UX;
- whether it blocks:
  NOW / BEFORE WIREFRAME / BEFORE IMPLEMENTATION / BEFORE DEMO;
- whether we currently have evidence or it remains UNKNOWN.

Do not invent agricultural facts.

Do not answer questions that depend on unavailable dataset evidence.
```

---

# 3. Проведи UX reference research

Теперь можно посмотреть, как похожие реальные системы решают такие интерфейсные задачи.

Это **не поиск agricultural thresholds**.

Тебе нужны именно интерфейсные паттерны.

Ищи примеры:

- inventory risk dashboards;
- cold-chain monitoring dashboards;
- warehouse monitoring;
- perishable inventory management;
- supply-chain exception dashboards;
- fleet / logistics alert systems;
- operational decision-support dashboards.

Можно использовать:

- Google;
- официальные страницы продуктов;
- YouTube demo продуктов;
- screenshots;
- Behance/Dribbble только как источник визуальных идей, но не бизнес-логики;
- AI для поиска и сравнения.

Предпочтительнее реальные operational products, а не красивые концепты.

## PROMPT PUX-03 — UX pattern research

```text
Research existing UX patterns relevant to an operational dashboard for perishable inventory / post-harvest risk.

This is UX research, not agricultural rule research.

Use web research.

Look for real products or documented interfaces involving areas such as:

- inventory risk;
- cold chain monitoring;
- perishable goods;
- warehouse monitoring;
- supply chain exceptions;
- logistics alerts;
- decision-support dashboards.

Prefer primary sources, product documentation, real screenshots and product demos.

For every source record:

SOURCE
WHAT THE PRODUCT DOES
OBSERVED UX PATTERN
WHY THE PATTERN MAY BE RELEVANT
LIMITATIONS
LINK

Separate clearly:

OBSERVED PRACTICE — something actually visible in a source

from

RECOMMENDATION — something you think Smart Harvest could adopt.

Investigate especially:

- how critical items are ranked;
- how severity is communicated;
- how explanations are shown;
- how timelines/deadlines are communicated;
- how recommended actions are surfaced;
- overview → detail navigation;
- filters;
- alerts;
- empty states;
- data-quality warnings;
- confidence/uncertainty communication.

Do NOT copy visual design blindly.

Do NOT infer agricultural thresholds from another product.

Do NOT treat another application's business rules as Smart Harvest requirements.

At the end produce:

1. 5-10 useful patterns.
2. Patterns we should probably avoid.
3. Ideas worth testing in Smart Harvest.
4. Open questions that research did not resolve.
```

### Что тебе важно искать

Например, вопрос не:

> «Какого цвета сделать кнопку?»

А:

> «Как оператор за 5 секунд понимает, какая партия требует внимания первой?»

Не:

> «Нужен ли красивый график?»

А:

> «Поможет ли этот график принять решение или просто занимает место?»

---

# 4. Построй основной user flow

Когда PUX-01 — PUX-03 готовы, можно определить основной пользовательский сценарий.

Предварительная логика challenge выглядит примерно так:

**увидеть проблемные партии → выбрать одну → понять риск → понять причину → понять срочность → понять действие**

Но это пока `INFERENCE`, а не официальный готовый UX.

Попроси AI критически его проверить.

## PROMPT PUX-04 — Operator flow

```text
Using:

- challenge requirements;
- repository canon;
- current frontend behaviour;
- UX research;
- known team decisions;

design a PROVISIONAL operator workflow for Smart Harvest.

Do not edit code.

The challenge expects the system to help the operator understand:

- which batches are most at risk;
- when quality may deteriorate;
- contributing factors;
- prioritized action.

Design the simplest user flow that could communicate those outputs without unnecessary navigation.

For each step describe:

USER QUESTION
SCREEN / STATE
INFORMATION REQUIRED
USER ACTION
EXPECTED RESULT
DATA DEPENDENCY
CURRENTLY SUPPORTED? YES / NO / PARTIAL

Include separately:

PRIMARY FLOW

and failure/alternative flows:

- loading;
- backend unavailable;
- insufficient data;
- missing analytical result;
- partially missing batch data;
- no high-risk batches;
- analytics result unavailable;
- unexpected API failure.

For every predictive screen/state, state which information is available at dispatch and keep retrospective outcomes outside the dispatch-time explanation path.

Do not invent actual dataset fields.

Do not invent risk thresholds.

Do not prescribe a final agricultural action unless supported by Product/Data/Domain evidence.

Mark any hypothetical UI element clearly as PROVISIONAL.

Finish with:

MINIMUM DEMO FLOW
OPTIONAL FEATURES
BLOCKED BY DATA
BLOCKED BY PRODUCT
BLOCKED BY TECH
```

---

# 5. Сделай low-fi wireframe, но пока не код

После user-flow можно переходить к структуре экранов.

На этом этапе не нужен идеальный дизайн.

Лучше сначала сделать **low fidelity**.

Можно использовать:

- Figma;
- Excalidraw;
- Penpot;
- даже бумагу + фото;
- либо сначала попросить AI составить текстовый wireframe.

Не трать много времени на логотипы, анимации, красивые градиенты и идеальные цвета.

Главный вопрос:

> Может ли человек, который впервые видит Smart Harvest, понять ситуацию без объяснения разработчика?

## PROMPT PUX-05 — Wireframe specification

```text
Create a low-fidelity wireframe specification for the Smart Harvest operator interface.

Do NOT implement it.

Use the previously established operator workflow.

Design the minimum interface needed for the primary challenge outcomes.

For every screen or major section specify:

PURPOSE

PRIMARY USER QUESTION

INFORMATION HIERARCHY

PRIMARY ACTION

SECONDARY INFORMATION

DATA REQUIRED

AVAILABLE AT T_DISPATCH / RETROSPECTIVE ONLY

EMPTY STATE

LOADING STATE

ERROR STATE

INSUFFICIENT-DATA STATE

UNCERTAINTY / EXPLAINABILITY REQUIREMENTS

MOBILE CONSIDERATIONS

DEMO IMPORTANCE:
CRITICAL / USEFUL / OPTIONAL

Avoid decorative dashboard widgets without a clear user decision.

Do not invent:

- risk percentages;
- deterioration dates;
- agricultural thresholds;
- recommendations;
- dataset fields.

If something is not established yet, use semantic placeholders such as:

[RISK INDICATOR]
[DETERIORATION HORIZON]
[CONTRIBUTING FACTORS]
[PRIORITIZED ACTION]

rather than fabricated example values.

At the end propose:

1. Minimum viable screen set.
2. Information hierarchy.
3. What a judge/user should understand within the first 5 seconds.
4. What they should understand after opening a batch.
5. Elements that should be removed if implementation time becomes limited.
```

---

# 6. Сразу продумай Demo

Не нужно ждать последнего вечера, чтобы впервые решить, что именно показывать.

Demo должен проектироваться вместе с продуктом.

Но сейчас существует важное ограничение:

настоящего доказанного positive analytical scenario ещё может не быть.

Поэтому сначала готовим **demo skeleton**, а не притворяемся, что система уже умеет предсказывать потери.

## PROMPT PUX-06 — Demo story

```text
Create a provisional Smart Harvest demo story.

Do NOT claim functionality that the repository does not currently implement.

Separate:

CURRENTLY DEMONSTRABLE

from

TARGET DEMO AFTER ANALYTICS INTEGRATION.

The target demo should communicate this causal story:

DATA
→ PROBLEM DETECTED
→ PRIORITIZED BATCH
→ WHY IT IS AT RISK
→ WHEN ACTION IS NEEDED
→ WHAT SHOULD BE PRIORITIZED
→ EXPECTED OPERATOR BENEFIT

But do not fabricate any analytical result.

For the demo design provide:

1. Opening state.
2. First thing the presenter points at.
3. Primary batch-selection moment.
4. Explanation moment.
5. Prioritized-action moment.
6. What should be visible while the presenter speaks.
7. Potential demo failure points.
8. Fallback behaviour if the backend fails.
9. Fallback behaviour if analytics returns insufficient_data.
10. Things the presenter must NOT claim without evaluation evidence.

Create:

CORE DEMO FLOW

and

FAILURE-SAFE DEMO FLOW.

The target story must not reveal retrospective arrival/final-outcome information as if it were evidence available for the dispatch prediction.

Do not specify unsupported business metrics.

Do not claim that food loss was reduced unless evaluation evidence later proves it.
```

---

# 7. Сделай QA-план ещё до реализации

Твоя QA-роль начинается не после написания frontend.

Она начинается сейчас.

Нужно заранее понимать, как интерфейс может сломаться.

Текущий проект уже имеет важные состояния:

- loading;
- connected;
- backend unavailable;
- retry;
- insufficient data.

Их нельзя потерять, когда интерфейс станет красивее.

## PROMPT PUX-07 — UX / exploratory QA plan

```text
Act as an exploratory QA lead for the Smart Harvest user-facing application.

Inspect the current frontend and API contracts.

Do NOT modify code.

Create a UX-oriented QA plan.

Separate test cases into:

A. CURRENT FOUNDATION TESTS

B. FUTURE ANALYTICS UI TESTS

For each case provide:

PRECONDITION
ACTION
EXPECTED USER-VISIBLE RESULT
WHAT MUST NOT HAPPEN
EVIDENCE NEEDED

Include at least:

- initial loading;
- slow backend;
- backend unavailable;
- retry;
- malformed/error response where relevant to existing contracts;
- insufficient_data;
- missing optional information;
- no risk output;
- no deterioration horizon;
- no recommendation;
- long text;
- narrow/mobile viewport;
- keyboard navigation where applicable;
- colour-independent severity communication;
- user understanding without technical terminology;
- rapid retry / reload;
- partial information;
- empty lists where future list UI is planned.
- arrival-stage information is absent/withheld and prediction views still work;
- actual post-dispatch delay, incidents or realized telemetry do not appear as evidence for a dispatch prediction;
- planned transport information is visibly distinct from realized transport outcomes;
- missing or withheld future information is handled without fabricated values or broken required fields.

For future functionality, do not invent API behaviour.

Mark such cases as FUTURE CONTRACT REQUIRED.

Mark every item as either `PLANNED QA CASE` or `EXECUTED QA EVIDENCE`. A written scenario is not execution evidence. For an executed check, record date/base, exact action, observed result, and retained evidence.

Also identify:

DEMO-CRITICAL CASES

REGRESSION RISKS

ACCESSIBILITY RISKS

FALSE-PRECISION RISKS

MISLEADING-UI RISKS

At the end produce a small DEMO SMOKE CHECK that can be executed immediately before presenting the project.
```

---

# 8. Что делать, когда придут результаты Виктора

Вот здесь начинается очень важная точка синхронизации.

До результатов Data workstream можно определить:

- структуру;
- navigation;
- information hierarchy;
- loading/error states;
- provisional user flow;
- demo story;
- QA strategy.

Но после результатов Виктора надо обязательно проверить:

**соответствует ли придуманный интерфейс тому, что данные реально позволяют показать.**

Например, если UX предполагает:

> `Risk: 83%`

а Виктор выяснит, что модель не позволяет интерпретировать output как probability, такой экран использовать нельзя.

Если UX предполагает:

> `Quality will deteriorate in 17 hours`

а данные позволяют только ранжировать риск без такого horizon — нельзя показывать 17 часов.

Если факторов риска нет в explainable output, нельзя просто написать их вручную.

## PROMPT PUX-08 — Data → UX reconciliation

Запускай его после появления Data evidence.

```text
Reconcile the current Smart Harvest UX proposal against the latest Data & Evaluation evidence.

Read the actual Data workstream evidence supplied by Viktor and the relevant current repository state.

For every proposed UI element classify it:

SUPPORTED

SUPPORTED WITH LIMITATION

NOT SUPPORTED

UNKNOWN

Check especially:

- risk indicator;
- risk ordering;
- numeric risk score;
- deterioration horizon;
- contributing factors;
- recommendation/action;
- confidence;
- historical comparison;
- charts;
- alerts.

Also verify that every predictive view respects `T_assess = T_dispatch`, does not require arrival-stage information, and does not use realized post-dispatch events or final outcomes as explanation. Preserve the route `batches <- storage_sessions -> storage_zones -> sensor_readings` when UX references storage telemetry; do not imply a direct batch-sensor relationship.

For each unsupported element explain exactly what evidence is missing.

Do not solve missing data by inventing values.

Then propose the smallest UX revision needed to make the interface truthful.

Output:

KEEP
CHANGE
REMOVE
BLOCKED
NEW UX REQUIREMENTS
```

---

# 9. Сверься с Алисой

У Алисы Product ownership.

Поэтому перед финальным UX нужно сверить:

- кто именно primary user;
- какую проблему мы обещаем решить;
- какие действия считаем полезными;
- какой story рассказываем судьям;
- какие assumptions уже приняты командой;
- появились ли новые clarification.

Ты не обязан ждать Алису, чтобы делать первые wireframes.

Но **финальный UI и demo narrative не должны расходиться с Product workstream**.

---

# 10. Только после этого переходи к реализации frontend

Не давай Antigravity команду вроде:

> «сделай нам красивый современный dashboard».

Это почти гарантированно приведёт к тому, что AI сам придумает:

- поля;
- risk scores;
- карточки;
- графики;
- бизнес-логику;
- unnecessary components.

Когда UX будет согласован, Владимир даст отдельный implementation contract с конкретным write scope.

Например:

```text
frontend/src/pages/...
frontend/src/components/...
frontend/src/styles.css
```

а API contracts, backend, dependencies, schemas и architecture останутся вне scope, если они явно не разрешены.

Если во время реализации выяснится:

> «чтобы сделать этот UI, нужно изменить backend API»

не меняй API самостоятельно.

Это STOP condition.

Передай проблему Владимиру/Игорю.

---

# 11. Что конкретно нужно сделать СЕЙЧАС

На первом проходе твоя задача:

**PUX-00**\
Познакомить Antigravity с repository.

↓

**PUX-01**\
Разделить факты, решения, неизвестное и зависимости UX.

↓

**PUX-02**\
Составить UX research questions.

↓

**PUX-03**\
Посмотреть реальные UX patterns похожих operational systems.

↓

**PUX-04**\
Составить provisional operator flow.

↓

**PUX-05**\
Сделать low-fi wireframe specification.

↓

**PUX-06**\
Подготовить demo skeleton.

↓

**PUX-07**\
Подготовить exploratory QA plan.

После этого показать результаты Владимиру.

PUX-08 выполняется уже после того, как появятся результаты Data workstream Виктора.

---

# Что пока НЕ надо делать

Пока не надо:

- полностью переписывать frontend;
- делать final design;
- придумывать agriculture rules;
- придумывать risk formula;
- придумывать dataset fields;
- самостоятельно менять API;
- добавлять библиотеки графиков;
- менять dependencies;
- менять package-lock;
- менять backend;
- менять schema;
- менять architecture;
- удалять существующие error/insufficient-data states;
- делать merge;
- делать release.

---

# Как использовать AI правильно

Не проси:

> Сделай лучший UX для приложения.

Лучше:

> Вот challenge.\
> Вот repository.\
> Вот подтверждённые requirements.\
> Вот current state.\
> Вот UNKNOWN.\
> Сначала проанализируй user decision.\
> Не выдумывай отсутствующие данные.\
> Потом предложи минимальный UX.

AI здесь должен быть не дизайнером, которому сказали «сделай красиво», а помощником по цепочке:

**RECON → QUESTIONS → RESEARCH → FLOW → WIREFRAME → DEMO → QA → IMPLEMENTATION**

---

# Главный критерий твоей работы

Представь человека, который ничего не знает о нашем коде.

Он открывает Smart Harvest.

Через несколько секунд он должен понимать:

**Что сейчас требует моего внимания?**

После открытия конкретной партии:

**Почему она требует внимания?**

После этого:

**Насколько срочно нужно действовать?**

И наконец:

**Что мне имеет смысл сделать первым?**

Если пользователю для понимания этого нужно, чтобы разработчик пять минут объяснял устройство модели — UX ещё не готов.

При этом интерфейс никогда не должен быть понятнее за счёт выдуманной точности.

Лучше честно показать:

**Insufficient data**

чем нарисовать красивый, но ничем не подтверждённый:

**Risk 87% — 14 hours remaining.**
