# NNN: Название статьи

- **Тип:** исследовательская статья / позиционная / протокол / методическая заметка
- **Версия:** v1.0
- **Дата:** ГГГГ-ММ-ДД
- **Статус:** черновик / на проверке / стабильно / устарело
- **Автор(ы):** Лаборатория Morphogenesis
- **Связанные отчёты:** [ссылки](../reports/)
- **Связанные NEG:** NEG-XX, …
- **Артефакты:** [ссылки](../morphogenesis/experiments/)

## Аннотация

3–6 предложений: вопрос, что сделано, главное число, главный вывод и его границы.
Без «революции» и без обещаний.

**Ключевые слова:** NCA, морфогенез, …

## 1. Вопрос

Какой вопрос задан. Почему он важен. Что было бы ответом «да», что — «нет».
Если вопрос спекулятивный — явно пометить.

## 2. Контекст и предшественники

Что уже известно (со ссылками), чего мы не знаем, чем наша постановка отличается.
Чужие работы — без перепубликации текста.

## 3. Методы

- Модель, данные, конфигурация (ссылка на `config.py`/спеку).
- Что обучалось, сколько шагов, какие сиды, какое железо.
- Метрики: определение, формула, что считается первичным эндпоинтом.
- Статистика: тест, число пар, минимально достижимый p.
- Что не делалось (например, не менялись дефолты).

## 4. Результаты

Таблицы/числа со ссылкой на артефакт. Сначала первичный эндпоинт, потом вторичные.
Отдельно — что получилось не так, как ожидалось.

## 5. Обсуждение

Что результат значит. Какие интерпретации конкурируют. Что нельзя вывести.
Не смешивать с метафорой: метафора — отдельным абзацем с пометкой.

## 6. Ограничения

Всё, что может изменить вывод: архитектура, горизонт, число сидов, снимок,
предварительность чисел, смещение метрики.

## 7. Что дальше

Конкретный следующий эксперимент/решение, с критерием успеха и провала.

**Rule added 05.11 (owner's wording: describe the steps and what we find, then take new steps, then a new article).** An
article is *one step*, not a running report, and it has a fixed shape: **(1)** last time we found this — briefly, with the
previous article cited by DOI once it has one — and so we decided to check that; **(2)** here are the results of those checks;
**(3)** here is where we try to move next, with the next step named, and the following step is written up as its own article
rather than folded into this one. Each article restates every definition it needs, so that someone who has not read the earlier
ones can read it alone. Two consequences for the sections below: section 7 ("what comes next") is not optional and names what is
already running with the pre-registration it was claimed under; and a step with no named successor is a step that has not been
thought through.

## 8. Воспроизведение

```bash
cd morphogenesis
../.venv/Scripts/python.exe -u <скрипт>.py <аргументы>
```

Ожидаемые артефакты и поля.

## Ссылки

1. Название — автор, журнал, год. `<URL>`
2. …

## Changelog

- **v1.0** (ГГГГ-ММ-ДД): первая версия.

## Проверка

- Числа сверены с: `<файл>`, поля … (дата).
- Ссылки проверены: (дата).
- Второй проход на переоценку: (кто/дата).
