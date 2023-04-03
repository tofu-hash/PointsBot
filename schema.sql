CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT,
    points INTEGER DEFAULT 0,        -- Количество "Поинтов"
    created INTEGER                 -- Unix время создания пользователя
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,                -- Пользователь, создавший задачу
    photo_id TEXT,                  -- Фото, прикреплённое к задаче (если есть)
    description TEXT,               -- Описание задачи
    completed INTEGER DEFAULT 0,    -- Завершено ли задание
    completed_in INTEGER,           -- Unix время завершения задачи
    created INTEGER                 -- Unix время создания задачи
);