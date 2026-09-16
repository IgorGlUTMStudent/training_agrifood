# IGR-01 — Technical Recon / Backend Map

## Для кого

**Owner:** Игорь — Technical Deputy\
**Reviewer / Integrator:** Владимир\
**Project:** SoS — Training AgriFood / Smart Harvest\
**Repository:** `https://github.com/Slave-of-Skynet/training_agrifood`\
**Task type:** technical reconnaissance / architecture mapping\
**Implementation:** **нет**\
**Разрешённая запись:** только итоговый recon-отчёт\
**Следующий dependency gate:** evidence-specific: VDR-01 for inventory/integrity, VDR-02 for assessment-time/leakage semantics, later approved Viktor contracts for target/evaluation/model readiness, and Alisa's evidence for product/action meaning

---

# 1. Что это за задача простыми словами

Сейчас в репозитории уже есть рабочий технический каркас Smart Harvest:

- React + TypeScript + Vite frontend;
- Python + FastAPI + Pydantic backend;
- API;
- публичный `RiskAssessment`;
- synthetic demo assessment;
- тесты;
- архитектурные документы.

Но пока нет настоящего технического пути:

```text
challenge dataset
    ↓
ingestion
    ↓
validation / canonicalization
    ↓
analytics
    ↓
risk assessment
    ↓
explanation
    ↓
recommendation
    ↓
API
    ↓
operator UI
```

Задача IGR-01 — **не реализовать этот путь**, а сначала полностью понять текущее состояние репозитория и составить точную техническую карту:

1. что уже реально существует;
2. что является только skeleton / placeholder;
3. какие public/shared contracts уже нельзя случайно сломать;
4. где должны подключаться будущие ingestion, analytics, explain и recommend;
5. какие следующие технические шаги зависят от результатов Виктора;
6. где есть технические риски или несогласованность документации;
7. какой минимальный порядок implementation steps позволит дальше строить backend без преждевременного redesign.

Игорь должен после IGR-01 уметь своими словами объяснить Владимиру:

> «Вот как сейчас проходит запрос через систему, вот где заканчивается реальная реализация, вот какие интерфейсы уже зафиксированы, вот какие компоненты пока пустые, какой конкретный evidence должен прийти из VDR-01, VDR-02, later Data & Evaluation contracts и Product work, и вот в каком порядке безопасно начинать реализацию после соответствующих handoff».

---

# 2. Почему IGR-01 можно делать уже сейчас

IGR-01 **не требует ждать окончания VDR-01**.

Игорь уже может:

- изучить committed application state;
- поднять backend и frontend;
- запустить существующие проверки;
- проследить текущий request/response path;
- изучить текущие Pydantic contracts;
- понять module boundaries;
- сопоставить code skeleton с `docs/architecture.md`;
- определить dataset-dependent decision points;
- отметить места и конкретный evidence stage, который должен их разблокировать.

Но Игорь **не должен до появления соответствующего принятого evidence**:

- проектировать production raw input schema;
- выбирать join strategy на реальных данных;
- придумывать feature engineering;
- придумывать risk formula;
- выбирать ML model;
- задавать thresholds;
- создавать crop-specific rules;
- решать, какие поля пригодны для prediction;
- определять target/split/metrics;
- делать выводы о data quality;
- реализовывать ingestion на основании догадок.

Эти решения должны опираться на подходящий evidence, а не на один catch-all handoff:

- **VDR-01** поддерживает supplied dataset inventory, entity/table structure и observed integrity/data-quality evidence;
- **VDR-02** поддерживает assessment-time availability, temporal boundaries, leakage rules, shared-zone/time risks и split constraints, относящиеся к leakage;
- **later separately contracted Viktor work** требуется для usable analytical target, risk-target interpretation, deterioration-horizon feasibility, selected evaluation protocol, baseline comparison и model/evaluation readiness;
- **Alisa** предоставляет product/domain meaning, user requirements и поддерживаемую интерпретацию actions/recommendations.

---

# 3. Классификация контекста

Во время работы обязательно различай:

- **FACT** — непосредственно подтверждено challenge material, repository или реально выполненной проверкой.
- **DECISION** — уже принятое командой техническое или продуктово-техническое решение.
- **OBSERVED PRACTICE** — конкретно наблюдаемое текущее поведение кода.
- **INFERENCE** — вывод из фактов, но не установленное требование.
- **RECOMMENDATION** — предложение по следующему техническому шагу.
- **UNKNOWN** — данных пока недостаточно.
- **SIMULATION** — искусственная часть тренировочного challenge.

Не превращай `INFERENCE`, `RECOMMENDATION` или `SIMULATION` в факт о реальном GigaHack, provider или AgriFood-индустрии.

---

# 4. Авторитет источников для IGR-01

Используй источники в следующем порядке.

## 4.1. Материалы текущего training challenge

В первую очередь:

```text
sponsor_pack/brief/Training Challenge #3 — AgriFood.md
sponsor_pack/README.md
sponsor_pack/data/
```

Это материалы текущего **SIMULATION / training challenge**.

Не выдавай сведения из них за требования реального спонсора GigaHack.

## 4.2. Challenge-specific решения SoS

Обязательно прочитать:

```text
docs/team_roles.md
docs/architecture.md
docs/decisions/0001-foundation-architecture.md
docs/data_contract.md
docs/domain_rules.md
docs/evaluation.md
docs/assumptions_unknowns.md
docs/challenge_canon.md
docs/demo_runbook.md
```

## 4.3. Текущее committed состояние приложения

Application repository является authoritative source того, **что реально реализовано**.

Особенно внимательно изучить:

```text
backend/app/main.py
backend/app/api/routes.py
backend/app/domain/assessment.py
backend/app/services/demo_assessment.py

backend/app/ingestion/
backend/app/analytics/
backend/app/explain/
backend/app/recommend/

backend/tests/test_api.py
backend/tests/test_contract.py
backend/pyproject.toml

frontend/src/
frontend/package.json
frontend/vite.config.ts

README.md
.env.example
```

Разрешено читать любые другие связанные файлы, если они нужны для понимания вызовов, типов, frontend consumption или runtime.

---

# 5. Важный known issue, который надо проверить

На reference-состоянии, по которому подготовлено это задание:

```text
main SHA:
72ab453f52d3bb7909001d0403fc62f89dce117d
```

в repository уже присутствует `sponsor_pack`, включая:

```text
batches.csv
facilities.csv
historical_quality_outcomes.csv
quality_checks.csv
sensor_readings.csv
shipments.csv
storage_sessions.csv
storage_zones.csv
data_dictionary.xlsx
```

При этом существующий `docs/challenge_canon.md` всё ещё содержит старую формулировку о том, что actual files/schema ещё не inspected.

Это потенциальная **canonical staleness / synchronization issue**.

### Что делать Игорю

- проверить, сохраняется ли это противоречие на его актуальном base;
- если да — зафиксировать в recon report;
- указать, какие downstream decisions оно может затрагивать;
- передать Владимиру.

### Что НЕ делать

Не изменять:

```text
docs/challenge_canon.md
docs/assumptions_unknowns.md
docs/data_contract.md
```

в рамках IGR-01.

Обновление canon — отдельное человеческое решение после сопоставления источников и workstream handoff.

---

# 6. Пункт 0 — подготовить рабочую копию

Если repository ещё не клонирован:

```powershell
cd C:\Users\<YOUR_USER>\Documents
git clone https://github.com/Slave-of-Skynet/training_agrifood.git
cd training_agrifood
```

Если repository уже есть:

```powershell
cd <путь-к-training_agrifood>
```

Затем:

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
git status --short
git rev-parse HEAD
```

## Ожидаемое состояние

`git status --short` должен быть пустым.

Скопируй полный SHA из:

```powershell
git rev-parse HEAD
```

и сохрани его как **Starting/base SHA**.

### Важно

SHA

```text
72ab453f52d3bb7909001d0403fc62f89dce117d
```

— это reference SHA на момент подготовки этой инструкции.

Если `origin/main` уже ушёл вперёд, **не откатывай repository к этому SHA**. Работай от нового актуального `origin/main` и запиши фактический SHA.

Если перед созданием ветки `git status --short` показывает чужие/старые локальные изменения:

**STOP.**

Не делай:

```text
git reset --hard
git clean -fd
git checkout .
```

Не удаляй чужую работу автоматически.

Сначала покажи Владимиру:

```powershell
git status --short
git diff
git rev-parse HEAD
```

---

# 7. Создать ветку IGR-01

После подтверждения clean main:

```powershell
git switch -c igor/igr-01-technical-recon
```

Проверить:

```powershell
git branch --show-current
git status --short
git rev-parse HEAD
```

Ожидается:

```text
branch: igor/igr-01-technical-recon
status: clean
HEAD: тот же Starting/base SHA
```

---

# 8. Открыть repository в Antigravity

Из корня repository:

```powershell
code .
```

либо открыть папку `training_agrifood` через интерфейс Antigravity.

Перед началом работы объясни агенту:

- repository уже содержит принятый foundation;
- IGR-01 — reconnaissance, не redesign;
- приложение менять нельзя;
- разрешено читать весь релевантный repository;
- единственный write scope — recon report;
- данные глубоко профилировать не надо: этим занимается VDR-01;
- нельзя придумывать отсутствующие решения.

---

# 9. Сначала проверить, что существующий foundation реально работает

Не полагайся только на README.

Нужно самому выполнить существующие проверки.

## 9.1. Backend environment

Из root repository:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".\backend[test]"
```

Если virtual environment уже существует и заведомо соответствует этому repository, можно использовать его.

## 9.2. Backend tests

```powershell
python -m pytest backend/tests
```

Зафиксировать:

- точную команду;
- exit code;
- сколько тестов прошло / упало;
- полный текст ошибки, если есть failure.

Не писать «tests pass», если команда не запускалась.

## 9.3. Backend runtime

Запустить:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload
```

В другом PowerShell:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
Invoke-RestMethod http://localhost:8000/api/v1/demo/assessment
```

Зафиксировать реальные ответы.

Особенно проверить, что demo assessment действительно остаётся synthetic и не изображает production assessment.

## 9.4. Frontend build

В новом терминале:

```powershell
cd frontend
npm ci
npm run build
```

Зафиксировать фактический результат.

### Не делать

Не исправлять environment/config/code только потому, что какая-то команда упала.

Если обнаружен неожиданный defect:

1. диагностировать read-only;
2. записать факты;
3. определить, blocker ли это для recon;
4. если исправление требует изменения application code/config/dependencies — **STOP по этой правке**;
5. включить finding в handoff Владимиру.

Environment failure **не расширяет scope**.

---

# 10. Проследить текущий backend request path

Нужно не просто прочитать файлы отдельно, а проследить реальный путь вызова.

Минимально восстановить цепочку:

```text
FastAPI app
    ↓
/api/v1
    ↓
route
    ↓
service
    ↓
Pydantic domain contract
    ↓
serialized HTTP response
```

Для каждого звена указать:

- файл;
- функция / класс;
- что принимает;
- что возвращает;
- содержит ли business logic;
- является ли production logic или fixture;
- кто от него зависит.

Например, если текущий route вызывает synthetic fixture builder, это надо записать как:

```text
OBSERVED PRACTICE:
GET /api/v1/demo/assessment
→ build_demo_assessment()
→ RiskAssessment
```

а не как:

```text
"backend already performs risk assessment"
```

---

# 11. Разобрать публичный `RiskAssessment`

Особенно внимательно изучить:

```text
backend/app/domain/assessment.py
docs/data_contract.md
backend/tests/test_contract.py
backend/tests/test_api.py
```

Нужно понять:

- какие поля уже являются public/shared application contract;
- какие enum/status semantics уже закреплены;
- какие invariants enforced Pydantic;
- что обязан содержать `assessed`;
- что запрещено при `insufficient_data`;
- как устроены:
  - `risk`;
  - `deterioration_horizon`;
  - `factors`;
  - `recommendation`;
  - `reliability`;
  - `provenance`;
- какие поля frontend уже может ожидать;
- какие будущие implementation tiers предусмотрены.

Отдельно ответить:

> Можно ли реализовать будущий deterministic baseline, не ломая текущую публичную семантику `RiskAssessment`?

Ответ должен быть основан на реальном коде/контракте, а не на предположении.

---

# 12. Разобрать module boundaries

Для каждой директории:

```text
backend/app/ingestion/
backend/app/analytics/
backend/app/explain/
backend/app/recommend/
backend/app/services/
backend/app/domain/
backend/app/api/
```

зафиксировать:

1. что сейчас реально находится внутри;
2. что architecture docs предполагают для этого слоя;
3. существует ли уже implementation;
4. какой тип будущего input/output boundary логично потребуется;
5. от какого evidence зависит boundary: VDR-01, VDR-02, later Viktor contract, Alisa/product evidence или integration decision;
6. какие shared contracts нельзя придумывать в IGR-01.

Важно:

**описать boundary ≠ спроектировать implementation.**

Например допустимо:

> `ingestion` должен стать границей чтения/validation/canonicalization согласно принятой architecture, но production input models нельзя определить до data handoff.

Недопустимо:

> «Создадим `BatchInput` с полями X/Y/Z», если соответствующий contract ещё не принят.

---

# 13. Сопоставить architecture docs с кодом

Проверить:

```text
docs/architecture.md
docs/decisions/0001-foundation-architecture.md
```

и фактический repository.

Для каждого существенного архитектурного утверждения определить:

- **IMPLEMENTED** — реально существует;
- **SKELETON** — место/модуль существует, но бизнес-реализации нет;
- **DOCUMENTED FUTURE BOUNDARY** — только описано;
- **MISMATCH** — docs и code расходятся;
- **UNKNOWN** — недостаточно evidence.

Не надо исправлять mismatch в IGR-01.

Надо его доказать ссылкой на конкретный путь/символ/наблюдение.

---

# 14. Проверить frontend/backend boundary

Хотя IGR-01 в первую очередь backend recon, Technical Deputy должен понимать end-to-end trunk.

Найди в `frontend/src/`:

- API client;
- TypeScript response representations;
- место вызова health endpoint;
- место вызова demo assessment;
- loading/error/unavailable states;
- компоненты, которые читают `RiskAssessment`.

Проследи:

```text
React component
    ↓
frontend API client
    ↓
HTTP endpoint
    ↓
FastAPI route
    ↓
service
    ↓
RiskAssessment
    ↓
JSON
    ↓
frontend representation
```

Нужно определить:

- дублируется ли public contract вручную на frontend;
- какие поля сейчас реально используются UI;
- какие изменения backend contract потенциально будут breaking;
- что можно будет добавлять за backend contract без изменения frontend semantics;
- где later integration с Prscr потребует согласования.

**Не изменять frontend.**

---

# 15. Разобрать supplied sponsor pack только на уровне технических зависимостей

IGR-01 не заменяет Data & Evaluation workstream Виктора. На этом этапе VDR-01 означает только inventory/integrity recon, а VDR-02 — temporal/leakage recon.

Разрешено установить только то, что непосредственно нужно для technical mapping.

Например:

- какие файлы физически присутствуют;
- что sponsor documentation заявляет о relational structure;
- где лежит data dictionary;
- что указан assessment moment;
- какие материалы являются future source для ingestion;
- какие части будущей implementation явно зависят от data semantics.

Не надо в IGR-01:

- считать null rates;
- строить распределения;
- анализировать labels;
- проверять leakage статистически;
- проектировать joins;
- выбирать features;
- оценивать class imbalance;
- выбирать split;
- обучать модели;
- рассчитывать metrics.

Это workstream Виктора.

Если техническая карта требует отсутствующий evidence, пометь конкретный gate:

```text
UNKNOWN — blocked by VDR-01 inventory/integrity evidence
UNKNOWN — blocked by VDR-02 temporal/leakage evidence
UNKNOWN — blocked by later approved Data & Evaluation contract
UNKNOWN — blocked by Alisa product/domain evidence
```

---

# 16. Найти evidence-specific dependencies

Сделай отдельный раздел отчёта:

```text
## Evidence-specific dependency gates
```

Раздели зависимости минимум на четыре группы.

### VDR-01 — inventory / integrity

Может поддержать:

- supplied dataset inventory;
- entity/table structure and documented joins;
- observed uniqueness, cardinality, missingness, data quality and referential integrity;
- dataset size/runtime evidence.

### VDR-02 — temporal / leakage

Может поддержать:

- assessment-time availability and temporal boundaries;
- safe/forbidden predictive inputs;
- shared-zone/time and entity leakage risks;
- split constraints relevant to leakage;
- evaluation-safe feature-window constraints.

### Later separately approved Viktor contracts

Требуются до claims или implementation, зависящих от:

- usable analytical target and risk-target interpretation;
- deterioration-horizon feasibility;
- selected evaluation protocol and metrics;
- deterministic baseline definition/comparison;
- learned-tier or model/evaluation readiness.

### Alisa — product/domain meaning

Требуется для:

- user requirements and operator decision meaning;
- supported interpretation of actions/recommendations;
- domain limitations and product claims.

Не относить всё перечисленное ниже к VDR-01. Для каждого пункта назвать правильную группу evidence:

- production raw input model;
- canonical entity model;
- join keys;
- timestamp semantics in implementation;
- minimum evidence for an assessment;
- handling missing/noisy records;
- aggregation windows;
- deterministic baseline inputs;
- target availability;
- deterioration-horizon feasibility;
- leakage-safe feature availability;
- recommendation evidence;
- persistence need;
- dataset-size/runtime constraints.

Для каждого пункта укажи:

1. какое решение заблокировано;
2. какой конкретный evidence нужен и от какого owner/task stage;
3. какой будущий module зависит от этого решения;
4. можно ли начать часть implementation до получения evidence.

---

# 17. Найти точки зависимости от Алисы / domain research

Отдельно перечислить вопросы, которые **не могут быть решены кодом или dataset profiling**.

Например:

- валидные agronomic thresholds;
- crop-specific safe ranges;
- допустимые intervention rules;
- смысл конкретной рекомендации для оператора;
- внешние ограничения/практики, требующие источника.

Не предлагай hardcoded agricultural rules как готовое решение.

`docs/domain_rules.md` прямо задаёт guardrail: candidate rule не становится active только потому, что он кажется логичным.

---

# 18. Составить minimal implementation sequence после IGR-01

В конце recon Игорь должен предложить **не архитектурный redesign**, а последовательность следующих технических шагов.

Формат примерно такой:

```text
IGR-02 — ...
Dependency:
Required evidence:
Likely write scope:
Shared contract impact:
STOP condition:
```

Ожидается только последовательность и зависимости.

Не надо писать готовые implementation contracts для всех будущих шагов.

Они будут составляться отдельно после review IGR-01 и получения именно тех VDR-01, VDR-02, later Viktor или Alisa outputs, от которых зависит конкретный step.

---

# 19. Write scope

В IGR-01 разрешено создать только:

```text
docs/recon/IGR-01-technical-recon.md
```

Если директории `docs/recon/` нет — её можно создать.

## Запрещено изменять

```text
backend/**
frontend/**
sponsor_pack/**
data/**
scripts/**
README.md
.env.example
.gitignore
docs/architecture.md
docs/challenge_canon.md
docs/data_contract.md
docs/domain_rules.md
docs/evaluation.md
docs/assumptions_unknowns.md
docs/demo_runbook.md
docs/decisions/**
docs/team_roles.md
dependency files
lockfiles
configuration files
```

Также запрещено:

- менять dependencies;
- менять `pyproject.toml`;
- менять `package.json`;
- менять `package-lock.json`;
- менять API;
- менять Pydantic contracts;
- менять schema;
- добавлять production models;
- добавлять scripts для data analysis;
- добавлять notebooks;
- добавлять ML code;
- добавлять persistence;
- делать deployment work.

Если для recon кажется, что нужно что-то из этого изменить:

**STOP и включить это как finding / proposed next task.**

---

# 20. Готовый prompt для Antigravity

Скопируй в новый Planning Mode chat Antigravity целиком.

```text
You are performing IGR-01 Technical Recon for the SoS Smart Harvest
training challenge repository.

ROLE AND PURPOSE

The human owner is Igor, Technical Deputy.
The Integrator/reviewer is Vladimir.

This is a reconnaissance task, not an implementation task.

Your job is to inspect the current committed repository, verify the
existing foundation where possible, reconstruct the real end-to-end
technical trunk, identify preserved contracts and future dependency
boundaries, and produce one evidence-based recon report.

Do not redesign or implement the missing system.

SOURCE / CONTEXT HIERARCHY

1. Current training-challenge materials under sponsor_pack/.
2. Challenge-specific SoS decisions and docs under docs/.
3. Current committed application repository state for what is actually
   implemented.
4. General preparation guidance only where needed.

This is a SIMULATION / training challenge. Do not turn simulated sponsor
material into claims about a real GigaHack provider or real-world
competition requirements.

STARTING STATE

Before analysis, report:

- current branch;
- full HEAD SHA;
- git status --short;
- whether HEAD matches the human-provided starting/base state.

If there are unexpected pre-existing local changes, STOP before writing.
Do not reset, clean, stash, overwrite, or absorb unrelated work.

REFERENCE STATE AT TASK PREPARATION

The task was prepared against main SHA:

72ab453f52d3bb7909001d0403fc62f89dce117d

This is reference information, NOT an instruction to reset to that SHA.
If origin/main is newer, use the actual fresh base selected by the human
and record it.

RELEVANT INSPECTION

You may read any repository file necessary to understand:

- FastAPI app setup;
- routing;
- service orchestration;
- Pydantic assessment contracts;
- tests;
- ingestion / analytics / explain / recommend boundaries;
- frontend API consumption and TypeScript representations;
- architecture decisions;
- current challenge materials;
- current sponsor pack structure;
- build/runtime configuration.

At minimum inspect:

README.md

sponsor_pack/brief/Training Challenge #3 — AgriFood.md
sponsor_pack/README.md
sponsor_pack/data/ directory structure

docs/team_roles.md
docs/architecture.md
docs/decisions/0001-foundation-architecture.md
docs/data_contract.md
docs/domain_rules.md
docs/evaluation.md
docs/assumptions_unknowns.md
docs/challenge_canon.md
docs/demo_runbook.md

backend/app/main.py
backend/app/api/routes.py
backend/app/domain/assessment.py
backend/app/services/demo_assessment.py
backend/app/ingestion/
backend/app/analytics/
backend/app/explain/
backend/app/recommend/
backend/tests/test_api.py
backend/tests/test_contract.py
backend/pyproject.toml

frontend/src/
frontend/package.json
frontend/vite.config.ts

You may inspect more files if required to trace calls, types and runtime
behaviour.

IMPORTANT DIVISION OF RESPONSIBILITY

Do NOT perform Viktor's VDR-01 inventory/integrity reconnaissance or
VDR-02 temporal/leakage reconnaissance.

You may inspect sponsor documentation and file structure for technical
dependency mapping, but do not perform data profiling, feature
engineering, target analysis, split design, leakage analysis, model
selection, metric selection, or statistical evaluation.

Whenever implementation depends on unavailable evidence, classify the
specific gate as one of:

UNKNOWN — blocked by VDR-01 inventory/integrity evidence
UNKNOWN — blocked by VDR-02 temporal/leakage evidence
UNKNOWN — blocked by later approved Data & Evaluation contract
UNKNOWN — blocked by Alisa product/domain evidence

VDR-01 can support supplied dataset inventory, table/entity structure
and observed integrity/data-quality evidence. VDR-02 can support
assessment-time availability, temporal boundaries, leakage rules,
shared-zone/time risks and leakage-relevant split constraints. Later
separately contracted Viktor work is required for usable target,
horizon feasibility, selected evaluation protocol, baseline comparison
and model/evaluation readiness. Alisa supplies product/domain meaning,
user requirements and supported action/recommendation interpretation.

Do not invent a production BatchInput or canonical schema.

Do not invent joins, fields, thresholds, features, labels, model
families, agronomic rules or recommendation effects.

EXISTING CONTRACTS TO PRESERVE

Treat the existing RiskAssessment semantics and validated Pydantic
invariants as preserved shared application contracts during this task.

In particular, inspect and explain the actual semantics of:

- assessed;
- insufficient_data;
- risk;
- deterioration_horizon;
- factors;
- recommendation;
- reliability;
- provenance.

Do not modify them.

Also inspect whether frontend types/consumers create additional coupling.

KNOWN RECON QUESTION

At the historical task-preparation reference state, sponsor_pack was
present while docs/challenge_canon.md retained pre-sponsor wording. Do
not presume that mismatch remains. Verify the actual current base.

If it is true:

- classify it as a documentation/canon synchronization finding;
- explain the exact evidence;
- explain possible downstream impact;
- surface it to the Integrator.

Do NOT edit challenge_canon.md or any other canonical document in IGR-01.

RUNTIME / VERIFICATION

Use the repository's documented commands where the environment permits.

Backend:

python -m pytest backend/tests

Run the FastAPI service and check:

GET /api/v1/health
GET /api/v1/demo/assessment

Frontend:

cd frontend
npm ci
npm run build

Record exact commands and actual results.

Do not report a check as PASS unless you actually ran it.

If an environment or implementation failure occurs, diagnose only as far
as possible without expanding write scope. Record the blocker and stop
any fix that would require application/config/dependency changes.

PRIMARY INVESTIGATION QUESTIONS

1. What is actually implemented today?
2. What exists only as skeleton or documented future boundary?
3. What is the real current request path from FastAPI route to response?
4. What exact role does build_demo_assessment play?
5. Which public/shared contracts already constrain future work?
6. Which RiskAssessment invariants are enforced in code/tests?
7. How does the frontend consume backend responses?
8. Which backend changes would be contract-breaking?
9. What does the accepted architecture expect from ingestion, analytics,
   explain and recommend?
10. Which decisions need VDR-01 inventory/integrity evidence?
11. Which decisions need VDR-02 temporal/leakage evidence or later
    separately approved Viktor target/evaluation work?
12. Which decisions instead require domain/product evidence from Alisa
    or another validated source?
13. Are docs and code currently consistent?
14. Are there stale canonical statements after sponsor_pack was added?
15. What is the minimum safe implementation sequence after recon and
    the relevant evidence-specific handoffs?
16. What should explicitly NOT be implemented yet?

CLASSIFICATION

For material findings use:

FACT
DECISION
OBSERVED PRACTICE
INFERENCE
RECOMMENDATION
UNKNOWN
SIMULATION

Do not silently upgrade an inference or recommendation into fact.

WRITE SCOPE

You may create only:

docs/recon/IGR-01-technical-recon.md

You may create the docs/recon directory if absent.

NO OTHER REPOSITORY FILE MAY BE MODIFIED.

FORBIDDEN CHANGES

Do not modify application code.
Do not modify frontend.
Do not modify backend.
Do not modify sponsor data.
Do not modify canonical docs.
Do not modify dependencies.
Do not modify lockfiles.
Do not modify config.
Do not modify schemas.
Do not change shared contracts.
Do not create production input models.
Do not add notebooks or analysis scripts.
Do not implement ingestion.
Do not implement analytics.
Do not implement ML.
Do not implement recommendations.
Do not implement persistence.
Do not perform deployment work.
Do not commit, push, merge, rebase, reset, clean or release.

REPORT REQUIREMENTS

Create docs/recon/IGR-01-technical-recon.md with these sections:

# IGR-01 Technical Recon

## 1. Recon identity
- repository
- branch
- starting/base SHA
- inspected HEAD
- working-tree state before recon

## 2. Executive technical summary
A concise description of what actually exists today.

## 3. Verified foundation behaviour
For each executed command:
- exact command
- result
- relevant output / exit status
- what it proves
- what it does NOT prove

## 4. Current technical trunk
Trace the actual runtime path:
frontend -> API -> route -> service -> domain model -> response -> frontend.

Include concrete file paths and symbols.

## 5. Backend module map
For api/domain/services/ingestion/analytics/explain/recommend:
- present implementation;
- intended boundary from accepted docs;
- status: IMPLEMENTED / SKELETON / DOCUMENTED FUTURE BOUNDARY /
  MISMATCH / UNKNOWN;
- dependencies.

## 6. Preserved contracts
Document the existing RiskAssessment semantics and other shared contracts
that future implementation must preserve unless separately changed by an
approved integration decision.

## 7. Frontend/backend coupling
Document current TypeScript/API coupling and likely contract-sensitive
surfaces.

## 8. Sponsor-pack technical boundary
Only describe information needed for technical dependency mapping.
Do not perform VDR-01 or VDR-02.

## 9. Evidence-specific dependency gates
For every blocked decision state:
- decision;
- required evidence and owner/task stage;
- affected module;
- whether any safe implementation can begin before it.

Use explicit subsections for:
- VDR-01 inventory/integrity evidence;
- VDR-02 temporal/leakage evidence;
- later approved Viktor target/evaluation work;
- Alisa product/domain evidence.

## 10. Decisions blocked by domain/product evidence
List questions that cannot be legitimately answered from code or dataset
profiling alone.

## 11. Documentation/code consistency findings
Include the sponsor_pack vs stale challenge_canon issue if confirmed.
Give exact evidence.

## 12. Technical risks
Evidence-based risks only.
Separate defect, unknown, inference and preference.

## 13. Proposed minimal implementation sequence
Propose IGR-02+ ordering only.
For each step give:
- objective;
- prerequisite evidence;
- likely write area;
- shared-contract risk;
- STOP condition.

Do not write full implementation contracts yet.

## 14. Explicit non-decisions
List things intentionally NOT decided during IGR-01.

## 15. Questions for Integrator / Viktor / Alisa
Route each question to the appropriate human owner.

## 16. Final handoff
Include:
- starting/base SHA;
- current HEAD;
- git status --short;
- all changed/untracked files;
- actual checks executed and results;
- checks not executed;
- shared contract/config/dependency changes: must be "none";
- unresolved blockers;
- one-sentence conclusion.

ACCEPTANCE

IGR-01 is acceptable only if:

- the current foundation was inspected from a recorded fresh base;
- current behaviour was actually verified where environment permits;
- the current runtime path is traceable to concrete files/symbols;
- implemented vs skeleton vs unknown is clearly separated;
- preserved shared contracts are identified;
- no production schema/risk formula/model/rule was invented;
- VDR-01, VDR-02, later Viktor and Alisa dependencies are distinguished;
- domain/product dependencies are explicit;
- stale/conflicting documentation is surfaced rather than silently fixed;
- the proposed next-step ordering is dependency-aware and minimal;
- only docs/recon/IGR-01-technical-recon.md was written;
- no commit/push/merge was performed;
- final evidence includes git status and all checks actually run.

NEGATIVE / FAILURE ACCEPTANCE

The task is NOT complete if any of the following happened:

- application code was changed;
- a raw input schema was invented;
- dataset profiling duplicated VDR-01 or temporal/leakage analysis duplicated VDR-02;
- an ML/model choice was made without evidence;
- agronomic thresholds were invented;
- a documented future boundary was described as existing implementation;
- README claims were repeated without checking code/runtime;
- test/build success was claimed without execution;
- a canonical document was silently updated;
- sponsor simulation material was presented as a real GigaHack/provider
  fact;
- unexpected local changes were overwritten or absorbed;
- report omits base SHA/status/evidence.

STOP CONDITIONS

Stop the relevant action and report to the human owner if:

- the working tree is unexpectedly dirty before work;
- actual base materially differs from task assumptions in a way that
  invalidates the contract;
- required repository files are missing;
- fixing a failure requires application/config/dependency/schema changes;
- recon appears to require defining a new shared contract;
- a question cannot be resolved without the named VDR-01, VDR-02,
  later Data & Evaluation, or product/domain evidence;
- another workstream has already changed the same technical boundary and
  its state is unclear.

At a STOP condition, do not broaden scope. Preserve evidence and ask for
an integration decision.
```

---

# 21. Что должен сделать Игорь после ответа Antigravity

Не принимай отчёт агента автоматически.

Пройди его сам.

## Проверка 1 — агент не начал проектировать вместо исследовать

Удали/верни на доработку выводы вроде:

```text
"We should use PostgreSQL"
"We should create BatchInput with..."
"We should train XGBoost"
"We should aggregate sensors into 6-hour windows"
"We should set risk high above..."
```

если для них ещё нет принятого evidence.

В IGR-01 это premature design.

## Проверка 2 — каждый важный вывод привязан к evidence

Хорошо:

```text
OBSERVED PRACTICE:
backend/app/api/routes.py::demo_assessment calls
build_demo_assessment(), which returns a synthetic RiskAssessment.
```

Плохо:

```text
"The backend is ready for production scoring."
```

## Проверка 3 — различены implementation и skeleton

Особенно:

```text
ingestion
analytics
explain
recommend
```

Само наличие package/directory не означает, что соответствующая capability реализована.

## Проверка 4 — нет ли скрытого data analysis

Если Antigravity начал:

- читать миллионы sensor rows;
- вычислять statistics;
- выбирать target;
- оценивать leakage;
- строить features;

останови эту часть.

Это workstream Виктора: inventory/integrity относится к VDR-01, а temporal/leakage analysis — к VDR-02.

---

# 22. Финальные Git-проверки

После создания отчёта:

```powershell
git status --short
git diff --check
git ls-files --others --exclude-standard
git diff
```

Так как recon report может быть новым untracked file, дополнительно:

```powershell
Get-Content docs\recon\IGR-01-technical-recon.md
```

Проверить, что единственный новый/изменённый task-файл:

```text
docs/recon/IGR-01-technical-recon.md
```

Если изменилось что-либо ещё — выяснить почему.

Не включать случайные изменения в IGR-01.

---

# 23. Что прислать Владимиру

Игорь должен прислать:

```text
IGR-01 HANDOFF

Branch:
Starting/base SHA:
Current HEAD:

git status --short:
<actual output>

Created/changed files:
- ...

Backend tests:
Command:
Result:
Evidence:

Backend runtime:
Health endpoint:
Demo assessment endpoint:
Evidence:

Frontend build:
Command:
Result:
Evidence:

Main technical findings:
1.
2.
3.
...

Implemented trunk:
...

Skeleton/future boundaries:
...

Evidence-specific dependency gates:
- VDR-01 inventory/integrity:
- VDR-02 temporal/leakage:
- later approved Data & Evaluation work:
- Alisa product/domain evidence:
...

Questions for Viktor:
...

Questions for Alisa:
...

Questions for Integrator:
...

Canon/docs synchronization issues:
...

Shared contracts changed:
none

Dependencies changed:
none

Config changed:
none

Application code changed:
none

Commit:
not performed

Push:
not performed

Merge:
not performed

One-sentence conclusion:
...
```

И приложить содержимое:

```text
docs/recon/IGR-01-technical-recon.md
```

или его полный diff/evidence.

---

# 24. Когда IGR-01 считается завершённым

IGR-01 можно отправлять на review, если Игорь может без помощи AI объяснить:

1. как сегодня реально проходит demo assessment;
2. почему это ещё не настоящий risk engine;
3. какие `RiskAssessment` contracts уже существуют;
4. какие invariants нельзя случайно нарушить;
5. что реально реализовано в каждом backend module;
6. что пока только skeleton;
7. где frontend зависит от backend contract;
8. какие следующие решения заблокированы VDR-01 inventory/integrity evidence;
9. какие решения требуют VDR-02 temporal/leakage evidence или later approved Viktor work;
10. какие решения требуют domain/product evidence;
11. почему нельзя уже сейчас просто «написать ML»;
12. какой минимальный следующий implementation step безопасен;
13. какие findings требуют решения Integrator.

После этого:

```text
IGR-01
    ↓
REVIEW
    ↓
ACCEPTABLE / FIX REQUIRED / BLOCKED: MISSING EVIDENCE
    ↓
relevant VDR-01 + VDR-02 + later evaluation + product/domain evidence
    ↓
отдельный contract для IGR-02
```

**ACCEPTABLE не означает разрешение на merge или изменение architecture.**

IGR-02 формируется отдельно на основании фактического IGR-01 evidence и результатов зависимых workstreams.
