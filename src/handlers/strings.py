# strings.py

LANG_STRINGS = {
    "ru": {
        # Стартовое меню, кнопки
        "start_text": "Привет! Я крутой бот. Введите команду /create, чтобы начать, или выберите опцию:",
        "faq_btn": "Вопросы и ответы",
        "scenarios_btn": "Мои сценарии",
        "top_users_btn": "Топ пользователей",
        "back_btn": "Назад",
        "main_menu_btn": "Главное меню",

        # FAQ
        "faq_text": """1. Как создать новый сценарий?
Для создания сценария необходимо ввести команду /create и следовать указаниям бота. Необходимо ввести предмет, класс учеников, тему урока, уровень подготовки (базовый/профильный) и количество запасного времени.

2. Что делать, если бот присылает сценарий по другой теме?
Постарайтесь подробнее описать тему урока и попробуйте ещё раз :)""",

        # Сценарии: кнопки, сообщения
        "no_scenarios_yet": "У вас пока нет сценариев ^_^",
        "choose_scenario": "Выбери свой сценарий",
        "no_next_page": "Больше некуда",
        "no_prev_page": "Меньше некуда",

        # Фотографии
        "photo_message": "Вы отправили фотографию:",

        # При создании сценария
        "subject_question": "📚 Выберите предмет:",
        "class_question": "👩‍🎓 Выберите класс:",
        "theme_question": "💼 Введите тему урока:",
        "level_question": "👩‍🏫 Выберите уровень подготовки:",
        "time_question": "🕰 Введите количество времени на урок:",
        "desc_question": "✍️ Введите описание вашего урока",

        "level_base_btn": "Базовый",
        "level_profile_btn": "Профильный",

        "back_subject_btn": "Назад к предмету",
        "back_class_btn": "Назад к выбору класса",
        "back_level_btn": "Назад к уровню",
        "back_time_btn": "Назад ко времени",
        "back_theme_btn": "Назад к теме",

        "you_chose_subject": "📚 Вы выбрали предмет: {subject}",
        "you_chose_class": "👩‍🎓 Вы выбрали класс: {school_class}",
        "you_chose_theme": "💼 Вы выбрали тему урока: {theme}",
        "you_chose_level": "👩‍🏫 Уровень подготовки: {level}",
        "you_chose_time": "🕰 Время на урок: {time}",
        "you_chose_desc": "✍️ Описание урока: {desc}",

        "scenario_generating": "Загрузка...",
        "scenario_created": "Сценарий сохранён!",
    },
    "en": {
        # Start menu, buttons
        "start_text": "Hello! I'm a cool bot. Enter /create to start or choose an option:",
        "faq_btn": "FAQ",
        "scenarios_btn": "My scenarios",
        "top_users_btn": "Top users",
        "back_btn": "Back",
        "main_menu_btn": "Main menu",

        # FAQ
        "faq_text": """1. How to create a new scenario?
Use the /create command and follow the bot instructions. You must provide the subject, class, lesson topic, difficulty level (basic/advanced), and the amount of spare time.

2. What if the bot generates a scenario for the wrong topic?
Try to describe your lesson more thoroughly and try again :)""",

        # Scenarios: messages
        "no_scenarios_yet": "You have no scenarios yet ^_^",
        "choose_scenario": "Choose your scenario",
        "no_next_page": "There's no next page",
        "no_prev_page": "There's no previous page",

        # Photos
        "photo_message": "You sent a photo:",

        # Creating scenario
        "subject_question": "📚 Choose the subject:",
        "class_question": "👩‍🎓 Choose the class:",
        "theme_question": "💼 Enter the lesson topic:",
        "level_question": "👩‍🏫 Choose the preparation level:",
        "time_question": "🕰 Enter the lesson duration:",
        "desc_question": "✍️ Enter the lesson description:",

        "level_base_btn": "Basic",
        "level_profile_btn": "Advanced",

        "back_subject_btn": "Back to subject",
        "back_class_btn": "Back to class",
        "back_level_btn": "Back to level",
        "back_time_btn": "Back to time",
        "back_theme_btn": "Back to topic",

        "you_chose_subject": "📚 Subject chosen: {subject}",
        "you_chose_class": "👩‍🎓 Class chosen: {school_class}",
        "you_chose_theme": "💼 Topic chosen: {theme}",
        "you_chose_level": "👩‍🏫 Level: {level}",
        "you_chose_time": "🕰 Lesson duration: {time}",
        "you_chose_desc": "✍️ Lesson description: {desc}",

        "scenario_generating": "Loading...",
        "scenario_created": "Scenario saved!",
    }
}


# src/helpers.py

from config.db_session import SessionLocal
from src.repo.db import UserRepository

# Можно хранить глобальный коннект к БД:
db = SessionLocal()
user_repo = UserRepository(db)

def get_localized_text(user_id: str, key: str, **kwargs) -> str:
    """
    Возвращает текст из LANG_STRINGS по ключу `key` с учётом языка пользователя.
    Если язык пользователя не найден в словаре, вернётся русский вариант.
    Можно подставлять значения через format, передав их как **kwargs.
    """
    lang_code = user_repo.get_language_by_id(user_id)  # "ru" или "en"
    if lang_code not in LANG_STRINGS:
        lang_code = "ru"

    text_template = LANG_STRINGS[lang_code].get(key, "")
    # Если нужно подставить какие-то параметры (например {subject}), используем .format(**kwargs)
    if kwargs:
        return text_template.format(**kwargs)
    return text_template
