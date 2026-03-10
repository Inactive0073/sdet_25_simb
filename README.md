# Feedback Form UI Tests + CI (Jenkins + Docker + Selenoid)

Автотесты формы обратной связи: <https://practice-automation.com/form-fields/>.

## Структура проекта

- `src/pages` - Page Object слои (`BasePage`, `FeedbackPage`).
- `src/locators` - локаторы страницы формы.
- `tests` - UI тесты (`smoke`, `regression`).
- `docker/autotests` - контейнер запуска pytest.
- `docker/selenoid` - конфигурация Selenoid.
- `docker/jenkins` - кастомный Jenkins с preinstalled plugins и seed-job.
- `Jenkinsfile` - единый CI pipeline (CI1..CI5).

## Локальный запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q
```

Запуск только сбора тестов:

```bash
python -m pytest --collect-only -q
```

## Remote browser (Selenoid)

`conftest.py` поддерживает два режима:

- локальный `webdriver.Chrome` (по умолчанию);
- удалённый `webdriver.Remote`, если задан `SELENIUM_REMOTE_URL`.

Пример:

```bash
set SELENIUM_REMOTE_URL=http://localhost:4444/wd/hub
python -m pytest -q --headless
```

## Jenkins + Docker (CI1..CI5)

### Быстрый старт

```bash
docker compose up -d --build jenkins
```

После старта:

1. Открыть `http://localhost:8080`.
2. Войти `admin/admin`.
3. Убедиться, что создан job `bankingproject-ui-tests`.

### Что реализовано в pipeline

- `CI1`: pipeline job в Jenkins, сборка и запуск автотестов.
- `CI2`: публикация Allure в Jenkins + архивирование `allure-results` отдельно по каждому build.
- `CI3`: `cron('H H * * *')` + email-рассылка через `email-ext` с passed/failed статистикой и вложением `allure-report.tar.gz`.
- `CI4`: запуск в Docker (`autotests + selenoid + selenoid-ui`), автоподготовка browser image, генерация `allure-results/junit.xml`, pip cache volume.
- `CI5`: `pollSCM('H/5 * * * *')` для автозапуска по коммитам.

### Обязательная конфигурация Jenkins

- Credential для Git:
  - `Kind`: SSH Username with private key
  - `ID`: `github-ssh`
  - доступ к `git@github.com:Inactive0073/sdet_25_simb.git`
- Allure Commandline в `Manage Jenkins -> Tools` (installation name: `allure`).
- SMTP в Jenkins global config (для `email-ext`).
- Переменная окружения Jenkins controller:
  - `CI_EMAIL_TO=self@example.com,mentor@example.com`

### Переменные seed-job (из `docker-compose.yml`)

- `JENKINS_GIT_URL=git@github.com:Inactive0073/sdet_25_simb.git`
- `JENKINS_GIT_BRANCH=*/main`
- `JENKINS_GIT_CREDENTIALS_ID=github-ssh`
- `JENKINS_PIPELINE_PATH=Jenkinsfile`

## Команды для проверки

Статическая проверка compose:

```bash
docker compose --profile ci config
```

Контейнерный прогон:

```bash
docker compose --profile ci up --build --abort-on-container-exit --exit-code-from autotests autotests selenoid selenoid-ui
```

Проверить, что после прогона есть:

- `allure-results/`
- `allure-results/junit.xml`

## Примечание по кешу

В задании упомянут кеш Maven. В данном Python-проекте используется persistent `pip` cache (`pip_cache` volume), что даёт фактическое ускорение повторных сборок контейнера автотестов.
