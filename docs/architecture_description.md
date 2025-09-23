# Архитектурное описание решения для ЦОДД

## 1. Архитектурная диаграмма (UML Component + Deployment)

**Компонентная диаграмма:**
- Frontend (React + Tailwind CSS)
  * Публичная часть: главная страница, новости, сервисы, статистика
  * Админ-панель: CRUD, импорт/экспорт, аналитические дашборды
- Backend (FastAPI + SQLAlchemy)
  * REST API с ролевой авторизацией (API-ключи)
  * Сервис аналитики (агрегации, данные для графиков)
  * Сервис импорта/экспорта (CSV/XLSX с маппингом колонок)
- База данных (PostgreSQL)
  * Публичные данные: ДТП, светофоры, статистика нарушений
  * Приватные данные: финансовые показатели, служебная информация
- Файловое хранилище (S3-совместимое)
  * Загрузки CSV/XLSX
  * Медиафайлы (WebP)

**Способы коммуникации:**
- Frontend ↔ Backend: REST API (HTTPS/JSON)
- Backend ↔ БД: ORM SQLAlchemy
- Backend ↔ Хранилище: S3 API
- Асинхронные задачи: Redis Queue для импорта данных

**Диаграмма развертывания:**
- Клиент (Браузер) → Frontend (Vercel/Netlify)
- Backend API (Docker контейнер) → Облачный хостинг (Railway/Render)
- PostgreSQL → Managed Database (Supabase/Cloud PostgreSQL)
- Файловое хранилище → AWS S3 или совместимый сервис

## 2. Функциональная схема базы данных (ER Diagram)

**Сущности и связи:**
- Users (id, role, api_key) ←→ ContentPages (создатель/редактор)
- Vehicles → Fines (1:N) - транспортные средства и штрафы
- Vehicles → Evacuations (1:N) - эвакуации транспорта
- Locations → TrafficLights (1:N) - светофорные объекты
- Locations → Accidents (1:N) - места ДТП
- Locations → Fines (1:N) - места нарушений ПДД

## 3. Ключевые таблицы, индексы, ограничения

**Таблицы:**
- users: PK(id), UNIQUE(api_key), CHECK(role IN {'guest', 'redactor', 'admin'})
- fines: PK(id), FK(vehicle_id, location_id), INDEX(issued_at), INDEX(visibility)
- evacuations: PK(id), FK(vehicle_id, location_id), INDEX(evacuated_at) 
- traffic_lights: PK(id), FK(location_id), INDEX(status), INDEX(install_date)
- accidents: PK(id), FK(location_id), INDEX(occurred_at), CHECK(severity IN {'minor', 'injury', 'fatal'})

**Ограничения целостности:**
- CASCADE DELETE для связанных записей
- NOT NULL для обязательных атрибутов
- CHECK constraints для валидации значений
- UNIQUE constraints для избежания дубликатов

## 4. Принципы хранения и обработки данных

**Разделение данных:**
- Публичные данные (visibility = 'public'): статистика ДТП, реестр светофоров
- Приватные данные (visibility = 'private'): детальная финансовая информация
- Административные данные (admin_only): служебные отчеты, аудит-логи

**Обработка данных:**
- Импорт: CSV/XLSX → валидация → маппинг колонок → пакетная вставка
- Экспорт: SQL запросы → сериализация в XLSX/CSV → кэширование
- Аналитика: агрегации по периодам, сравнение год-к-году, кэширование результатов

**Производительность:**
- Индексы по датам для временных диапазонов
- Составные индексы для частых запросов
- Кэширование агрегированных данных в Redis
- Оптимизация запросов с помощью EXPLAIN ANALYZE
