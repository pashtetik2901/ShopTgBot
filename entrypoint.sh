#!/bin/bash

# Обновляем миграции Alembic (если используется, раскомментировать строку ниже)
python -m alembic upgrade head

# Запускаем основное приложение
python main.py