import os
import time
import re


import requests
from dotenv import load_dotenv

def get_get_gpt_info(subject, class_int, description, theme, hard, time_lesson,tests,homework, language):
    load_dotenv()
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    api_key = os.getenv("YANDEX_API_KEY")
    gpt_model = 'yandexgpt-lite'
    
    if language == 'ru':
        system_prompt = """
        Ответ должен быть обычным текстом без форматирования. 
        Запрещено использовать **жирный текст**, *курсив* или `кодовые блоки`. 
        Не используй markdown-разметку.

        Создай подробный план урока с учётом следующих параметров: 

        Общие параметры: 

        - Предмет: (пользователь укажет название предмета)
        - Класс: (укажи класс или уровень обучения)
        - Тема урока: (пользователь укажет  основную тему занятия)
        - Личные пожелания: (личные пожелания учителя - ОНИ СТОЯТ ВЫШЕ ВСЕГО ОПИСАННОГО ТЕКСТА)
        - Сложность: (базовый или продвинутый)
        - Время: (укажи продолжительность урока в минутах) - ОБЯЗАТЕЛЬНО УЧИТЫВАТЬ

        ОЧЕНЬ ВАЖНО Во-первых и самое важное: Не делай форматирование, всё должно быть обычным текстом, без жирного шрифта, по пунктам
        ОБЯЗАТЕЛЬНО Также убери Маркапы, особенно в виде **   

        Базовая структура урока, если учитель не вводил общие параметры или же ввёл их некорректно или ввёл не разборчивые слова, которых не существует в языке (но помни, что в этих словах могут быть одна-две опечатки): 

        важно: пиши текст, не используя маркапы, жирные шрифты, курсивы и так далее
        
        - Название урока 

        1. Введение (время): 

        - Постановка целей урока и краткий обзор темы. 

        - Мотивация учащихся: почему тема важна и как она будет применяться. 

    

        2. Основная часть (время): 
        - Детальное изложение нового материала с примерами. 

        - Демонстрация, визуальные материалы или мультимедийные средства. 

        - Интерактивные методы обучения: обсуждения, вопросы, работа в парах или группах. 

        - Промежуточные проверки понимания (опросы, мини-упражнения). 

    

        3. Практическая работа (время): 

        - Индивидуальные или групповые задания для закрепления материала. 

        - Практические примеры, кейс-стади или упражнения. 

        - Инструкции по выполнению и временные рамки. 

    

        4. Заключение (время): 

        - Обобщение ключевых моментов урока. 

        - Ответы на вопросы и обсуждение сложных моментов. 

        - Обратная связь от учеников (рефлексия). 

        - Информация о домашнем задании (если требуется) и критерии оценки. 

    

        5. Дополнительные разделы (по необходимости): 

        - Использование интерактивных технологий и мультимедиа. 

        - Литература 

        - Какую геймофикацию можно добавить для интересного проведения урока. какие активности для вовлечения учеников по теме можно использовать.

        ОЧЕНЬ ВАЖНО Во-первых и самое важное: Не делай форматирование, всё должно быть обычным текстом, без жирного шрифта, по пунктам
        ОБЯЗАТЕЛЬНО Также убери Маркапы, особенно в виде ** 

        Во-вторых: Постарайся акцентировать внимание на активном вовлечении учеников в процесс обучения. Чаще это в пятом пункте, подробно опиши его

        Также убедись, что урок должен быть интересным - добавь геймофикацию, и что-то ещё, что может сделать урок интересный в промт - предложи нестандарнтный вариант урока 
        По возможности добавь термины и другие важные вещи, которые необходимо рассказать детям в рамках урока. 
        Ответ должен быть обычным текстом без форматирования. 
        Запрещено использовать **жирный текст**, *курсив* или `кодовые блоки`. 
        Не используй markdown-разметку.

        """

        user_prompt = f"""Пожелания пользователя 
        Предмет: {subject}, класс: {class_int}, Тема: {theme}, Личные пожелания:{description} Сложность: {hard}, 
        Время урока: {time_lesson}"""


    else:
        system_prompt = """
        WHRITE ON ENGLISH
        The response must be plain text without formatting.
        Bold text, italics, and code blocks are strictly forbidden.
        Do not use markdown.

        Create a detailed lesson plan considering the following parameters:

        General parameters:

        - Subject: (user will specify the subject name)
        - Grade/Class: (specify grade or educational level)
        - Lesson Topic: (user will specify the main topic)
        - Personal Wishes: (teacher's personal preferences—these have the highest priority over everything described)
        - Difficulty Level: (basic or advanced)
        - Lesson Duration: (specify the duration in minutes) – THIS MUST BE TAKEN INTO ACCOUNT

        VERY IMPORTANT First and foremost: Do not use formatting, everything must be plain text, no bold fonts, presented as numbered lists.
        ALSO IMPORTANT: Remove all markdown, especially symbols like **.

        Basic lesson structure if the teacher did not provide general parameters correctly or clearly, or if the words contain minor typos but are recognizable:

        Important: Write text without using markdown, bold fonts, italics, etc.

        - Lesson Title

        1. Introduction (time):

        - Setting lesson objectives and a brief overview of the topic.

        - Student motivation: why this topic is important and how it will be applied.

        2. Main Part (time):

        - Detailed presentation of new material with examples.

        - Demonstration, visual aids, or multimedia resources.

        - Interactive teaching methods: discussions, Q&A, pair or group work.

        - Periodic checks for understanding (quizzes, short exercises).

        3. Practical Work (time):

        - Individual or group tasks to reinforce material.

        - Practical examples, case studies, or exercises.

        - Instructions for task completion and time allocation.

        4. Conclusion (time):

        - Summary of key lesson points.

        - Q&A session and clarification of difficult points.

        - Student feedback and reflections.

        - Information on homework (if required) and assessment criteria.

        5. Additional Sections (if needed):

        - Use of interactive technologies and multimedia.

        - Recommended literature.

        - Ideas for gamification to make the lesson engaging, including specific activities to actively involve students.

        VERY IMPORTANT First and foremost: Do not use formatting, everything must be plain text, no bold fonts, presented as numbered lists.
        ALSO IMPORTANT: Remove all markdown, especially symbols like **.

        Secondly: Focus explicitly on actively engaging students throughout the learning process. Typically, this is in the fifth section; describe it thoroughly.

        Ensure the lesson is interesting—add gamification and suggest unconventional approaches or activities.
        Include terms and other essential concepts to be taught during the lesson.

        The response must be plain text without formatting.
        Bold text, italics, and code blocks are strictly forbidden.
        Do not use markdown.
        """

        user_prompt = f"""User Preferences
        Subject: {subject}, Grade/Class: {class_int}, Topic: {theme}, Personal Wishes: {description}, Difficulty Level: {hard}, Lesson Duration: {time_lesson}"""

    body = {
        'modelUri': f'gpt://{folder_id}/{gpt_model}',
        'completionOptions': {'stream': False, 'temperature': 0.9, 'maxTokens': 2000},
        'messages': [
            {'role': 'system', 'text': system_prompt},
            {'role': 'user', 'text': user_prompt},
        ],
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {api_key}'
    }

    response = requests.post(url, headers=headers, json=body)
    operation_id = response.json().get('id')

    url = f"https://llm.api.cloud.yandex.net:443/operations/{operation_id}"
    headers = {"Authorization": f"Api-Key {api_key}"}

    while True:
        response = requests.get(url, headers=headers)
        done = response.json()["done"]
        if done:
            break
        time.sleep(2)

    data = response.json()
    answer = data['response']['alternatives'][0]['message']['text']

    def clean_response(text):
        text = re.sub(r'\*', ' ', text)
        text = re.sub(r'--', '', text)   
        return text

    answer = clean_response(answer)

    return answer

