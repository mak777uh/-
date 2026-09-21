# Morphogenesis Project

Проект морфогенетического управления нейронными клеточными автоматами (NCA).

## Описание

Система реализует когнитивный цикл агента, управляющего NCA через:
- Анализ метрик (topology loss, stress, chamfer distance)
- Принятие решений о вмешательствах (INJECT_MORPHOGEN, MODIFY_DT, CONTINUE_TRAINING)
- Отчётность и валидацию действий

## Установка

```bash
cd morphogenesis
pip install -r requirements.txt
pip install pytest>=7.0.0  # для тестирования
```

## Быстрый старт

### Запуск smoke теста
```bash
cd morphogenesis
python smoke_test.py
```

### Запуск тестов
```bash
cd morphogenesis
python -m pytest tests/ -p no:libtmux -v
```

### Эксперименты
```bash
cd morphogenesis
python experiment_manager.py --help
```

## Структура репозитория

```
/workspace/
├── README.md                 # Этот файл
├── morphogenesis/            # Основной код проекта
│   ├── nca_core.py          # Ядро NCA
│   ├── cognition/           # Когнитивный модуль
│   │   ├── protocol.py      # Протокол принятия решений
│   │   ├── reporter.py      # Система отчётности
│   │   ├── cognitive_loop.py # Цикл восприятия-действия
│   │   └── ...
│   ├── tests/               # Тесты
│   ├── smoke_test.py        # Быстрый тест работоспособности
│   ├── experiment_manager.py # Менеджер экспериментов
│   └── requirements.txt     # Зависимости
└── repo/                    # Пустая директория (удалить или заполнить)
```

## Основные компоненты

### NCA Core
Базовый класс `NeuralCA` реализует:
- Двухканальную систему (видимый + скрытый каналы)
- Стресс-механизм для обнаружения аномалий
- Морфогенные инъекции для локального управления

### Cognition Module
- **protocol.py**: Эвристики принятия решений (Rev.7)
- **reporter.py**: Генерация Markdown-отчётов
- **cognitive_loop.py**: Цикл perception-decision-action

## Тестирование

Все 43 теста проходят успешно:
- ✅ test_action_validator (11 тестов)
- ✅ test_budget_edge_cases (6 тестов)
- ✅ test_death_invariant (4 теста)
- ✅ test_fresh_state (5 тестов)
- ✅ test_report_schedule (5 тестов)
- ✅ test_stress_ablation (4 теста)
- ✅ test_topology (8 тестов)

## Лицензия

[Указать лицензию]