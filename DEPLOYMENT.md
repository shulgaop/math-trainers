# Публикация через GitHub Pages и CI/CD

Этот проект готов к автоматической публикации без сборщика, backend, FTP и API-ключей. Исходники остаются в репозитории, а GitHub публикует только содержимое папки `site`.

## Как устроен процесс

Workflow: `.github/workflows/deploy.yml`.

- **Pull Request в `main`:** запускаются только проверки; публикации нет.
- **Push в `main`:** проверка сайта → подготовка публичного артефакта из `site` → деплой на GitHub Pages.
- **Actions → Validate and deploy to GitHub Pages → Run workflow:** ручной запуск для ветки `main`.
- Если проверка завершилась ошибкой, деплой не запускается и прежняя опубликованная версия остаётся доступной.
- Повторный push в ту же ветку отменяет устаревший запуск, чтобы не публиковать промежуточные состояния после более нового.

Проверка `tests/validate_site.py` контролирует:

- наличие `index.html`, `procenty.html` и `luch.html`;
- уникальность `id`;
- существование локальных HTML, видео, изображений и других ресурсов;
- внутренние якоря, включая ссылки между страницами;
- отсутствие корневых путей `/...`, которые ломаются в подпапке GitHub Pages;
- `rel="noopener"` у ссылок с `target="_blank"`;
- синтаксис всех встроенных блоков JavaScript через `node --check`.

Внешние сайты и воспроизведение внешних видео автоматическая проверка не подтверждает.

## 1. Создайте репозиторий

1. Войдите в GitHub.
2. Создайте репозиторий, например `math-trainers`.
3. Для бесплатного GitHub Pages проще использовать **Public**. Не помещайте в репозиторий пароли, персональные данные и другие секреты: опубликованный сайт общедоступен.
4. Создайте пустой репозиторий **без README, .gitignore и license**, чтобы первый push прошёл без слияния чужой начальной истории.

## 2. Отправьте проект в GitHub

### Windows PowerShell

Команды выполнять в **Windows PowerShell**. Путь замените на свой:

```powershell
cd D:\KIMI\math-trainers
git init
git branch -M main
git add .
git commit -m "Initial site with GitHub Pages CI/CD"
git remote add origin https://github.com/shulgaop/math-trainers.git
git push -u origin main
```

### Windows 11 + WSL

Если проект находится в `D:\KIMI\math-trainers`, команды выполнять в **терминале WSL**:

```bash
cd /mnt/d/KIMI/math-trainers
git init
git branch -M main
git add .
git commit -m "Initial site with GitHub Pages CI/CD"
git remote add origin https://github.com/shulgaop/math-trainers.git
git push -u origin main
```

При первом подключении GitHub может попросить авторизацию. Пароль аккаунта вместо токена для HTTPS обычно не принимается; используйте стандартную авторизацию Git Credential Manager или GitHub CLI. Токены не записывайте в файлы проекта.

## 3. Включите GitHub Pages

1. Откройте репозиторий → **Settings** → **Pages**.
2. В **Build and deployment → Source** выберите **GitHub Actions**.
3. Откройте вкладку **Actions**.
4. Если первый запуск произошёл до выбора этого источника и деплой не выполнился, выберите **Validate and deploy to GitHub Pages** → **Run workflow** для `main` либо повторите завершившийся запуск через **Re-run jobs**.
5. Дождитесь зелёных статусов `validate` и `deploy`.
6. URL публикации появится в сводке запуска и в настройках Pages. Для project site он обычно имеет вид:

```text
https://shulgaop.github.io/math-trainers/
```

Откройте главную, затем `procenty.html` и `luch.html`. Проверьте запуск локальных видео, тренажёр и раздел «С чего начать».

Официальная инструкция: [Configuring a publishing source for your GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## 4. Обычное обновление сайта

После первичной настройки ZIP и ручная загрузка файлов на хостинг больше не нужны.

### Windows PowerShell

```powershell
cd D:\KIMI\math-trainers
py tests\validate_site.py --require-node
git add .
git commit -m "Update math lessons"
git push
```

### Windows 11 + WSL

```bash
cd /mnt/d/KIMI/math-trainers
python3 tests/validate_site.py --require-node
git add .
git commit -m "Update math lessons"
git push
```

Если Node.js локально не установлен, можно запустить проверку без `--require-node`: HTML, ссылки и ресурсы будут проверены, а синтаксис JavaScript пропущен. В GitHub Actions Node.js обязателен, поэтому там эта проверка всегда выполняется.

После `git push` откройте **Actions** и дождитесь завершения `deploy`. Только после этого обновление считается опубликованным.

## 5. Безопасный откат

Не перезаписывайте общую историю `main`. Отмените ошибочный коммит новым коммитом:

```bash
git log --oneline
git revert ХЭШ_ОШИБОЧНОГО_КОММИТА
git push
```

Этот блок одинаково выполняется в PowerShell и WSL; средой является та, где открыт ваш локальный репозиторий. Push автоматически запустит проверку и публикацию исправленного состояния.

Можно также повторить старый успешный workflow через **Actions → нужный запуск → Re-run jobs**, но `git revert` понятнее в истории и надёжнее как постоянное исправление.

## 6. Рекомендуемая защита публикации

После первого успешного деплоя:

1. **Settings → Environments → github-pages**.
2. В **Deployment branches and tags** разрешите деплой только с `main`.
3. При работе через Pull Request в **Settings → Branches** добавьте защиту `main` и сделайте проверку `validate` обязательной.
4. Ручное подтверждение деплоя через **Required reviewers** добавляйте только если публикация действительно должна требовать отдельного одобрения.

## 7. Собственный домен

Сначала убедитесь, что сайт работает по адресу GitHub Pages. Затем:

1. Откройте **Settings → Pages → Custom domain** и укажите домен.
2. Настройте DNS-записи по инструкции GitHub для вашего типа домена.
3. После успешной DNS-проверки включите **Enforce HTTPS**.

Не добавляйте `CNAME` с выдуманным доменом заранее: это может сломать текущий адрес проекта.

## Диагностика

- **Ошибка в `validate`:** откройте лог шага `Validate HTML, links, assets and JavaScript`; исправьте указанный файл, затем сделайте новый commit и push.
- **`validate` зелёный, но `deploy` не запустился:** проверьте, что ветка называется `main`, событие не Pull Request, а в Pages выбран источник **GitHub Actions**.
- **404 после зелёного деплоя:** проверьте точное имя репозитория в URL и наличие `site/index.html`; дождитесь завершения именно job `deploy`.
- **Изменения не видны:** проверьте, что опубликован последний commit, затем обновите страницу с очисткой кэша браузера.
- **Внешнее видео не открывается:** это доступность внешней платформы, а не ошибка статического деплоя. Локальные MP4 должны продолжать работать.

## Правило для Kimi Code

Перед изменениями прочитайте `AGENTS.md`, `CONTEXT.md` и последнюю запись `CHANGELOG.md`. Изменяйте сайт в `site`, запускайте `tests/validate_site.py --require-node`, обновляйте документацию после итерации. Не заявляйте о публикации без успешного GitHub Actions deploy или фактической проверки опубликованного URL.
