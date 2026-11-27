# Графы проекта

Файл показывает фактические связи между страницами, ресурсами, проверками и публикацией. При изменении архитектуры графы обновляются вместе с `CONTEXT.md`. GitHub отображает диаграммы Mermaid без дополнительных библиотек в самом проекте.

## Архитектура сайта

```mermaid
flowchart LR
    INDEX["index.html<br>Пропорции"] --> PROCENTY["procenty.html<br>Проценты"]
    PROCENTY --> INDEX
    INDEX --> LUCH["luch.html<br>Координатный луч"]
    LUCH --> INDEX
    PROCENTY --> LUCH
    LUCH --> PROCENTY

    INDEX --> VIDEO_PROP["videos/proporcii.mp4<br>и JPG-обложка"]
    PROCENTY --> VIDEO_PROC["videos/procenty.mp4<br>и JPG-обложка"]
    LUCH --> VIDEO_LUCH["videos/luch.mp4<br>и JPG-обложка"]

    STORAGE["localStorage текущего браузера"] <-- "Маршрут и завершённые узлы" --> INDEX
    TRAINERS["Локальные генераторы заданий<br>без сервера и API"] --- INDEX
    TRAINERS --- PROCENTY
    TRAINERS --- LUCH
    ERRORS["Мои ошибки<br>память открытой страницы"] --- TRAINERS
```

Все три страницы содержат собственные HTML, CSS и JavaScript. Счёт тренажёров и список «Мои ошибки» хранятся только в памяти открытой страницы; в `localStorage` сохраняется только учебный маршрут пропорций. Ответы ученика наружу не отправляются.

## Проверка и публикация

```mermaid
flowchart LR
    PUSH["Push или Pull Request в main"] --> ACTION["GitHub Actions"]
    ACTION --> VALIDATE["tests/validate_site.py<br>HTML, ресурсы, якоря, JavaScript"]
    VALIDATE --> ARTIFACT["Только содержимое site/<br>не для Pull Request"]
    ARTIFACT --> DEPLOY["actions/deploy-pages<br>только main"]
    DEPLOY --> SITE["shulgaop.github.io/math-trainers/"]
```

Публикация запускается только после успешной проверки. Адрес на схеме подтверждён успешным workflow #2 и открытием публичного сайта.

## Учебный граф

```mermaid
flowchart TD
    START["4 вопроса: что я уже знаю?"] --> RATIO["Отношение"]
    RATIO --> PROPORTION["Пропорция<br>a : b = c : d"]
    PROPORTION --> DIRECT["Прямая зависимость<br>y : x = k"]
    PROPORTION --> INVERSE["Обратная зависимость<br>x · y = k"]
    DIRECT --> PRACTICE["Текстовые задачи"]
    INVERSE --> PRACTICE

    RAY["Координатный луч<br>цена деления"] --> DECIMAL["Десятичные дроби"]
    DECIMAL --> PERCENT["Проценты<br>часть, целое, процент"]
    PERCENT --> PERCENT_PRACTICE["Задачи на проценты"]
```

На главной странице раздел «С чего начать» помогает выбрать тему, прочитать объяснение, проверить ответ и перейти к заданиям. Схема показывает связи тем, но не ограничивает свободный переход между уроками через перекрёстные ссылки.
