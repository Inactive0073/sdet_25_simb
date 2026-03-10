# Jenkins + Docker setup (CI1..CI5)

## 1. Старт Jenkins

```bash
docker compose up -d --build jenkins
```

Открыть `http://localhost:8080` и войти `admin/admin`.

## 2. Обязательные настройки Jenkins

### Git credential

Создать credential:

- `Kind`: SSH Username with private key
- `ID`: `github-ssh`
- доступ к `git@github.com:Inactive0073/sdet_25_simb.git`

Seed-job создаётся автоматически и поднимает pipeline из SCM (`Jenkinsfile` из репозитория).

### SMTP + email-ext

Настроить SMTP в Jenkins (`Manage Jenkins -> Configure System`) для плагина `email-ext`.

Для публикации Allure отчёта добавить Allure Commandline в `Manage Jenkins -> Tools` (installation name: `allure`).

Получатели уведомлений задаются через переменную окружения контроллера:

- `CI_EMAIL_TO=self@example.com,mentor@example.com`

## 3. Что запускает pipeline

- Checkout из Git (SCM-first).
- Docker stack: `autotests + selenoid + selenoid-ui` (`docker compose --profile ci`).
- Автоподготовка browser image `selenoid/vnc_chrome:123.0` (pull при отсутствии).
- Копирование `allure-results` из контейнера автотестов в workspace Jenkins.
- Публикация Allure в Jenkins UI.
- Архивация `allure-results/**/*` и `allure-report.tar.gz`.
- Публикация JUnit (`allure-results/junit.xml`) и email-рассылка с passed/failed статистикой.

## 4. Триггеры

- Коммит-триггер: `pollSCM('H/5 * * * *')`.
- Ежедневный запуск: `cron('H H * * *')`.

## 5. Проверка acceptance по задачам

- `CI1`: job существует и запускает тесты.
- `CI2`: в каждом build есть собственный Allure report и артефакты.
- `CI3`: работает cron + email с вложением `allure-report.tar.gz`.
- `CI4`: тесты идут в Docker через Selenoid, есть `allure-results/junit.xml`, используется `pip_cache` volume.
- `CI5`: новые коммиты детектируются через polling и запускают build.
