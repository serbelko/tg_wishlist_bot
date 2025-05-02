import os
import requests
import json


def ds_answer(category, label, about) -> str:
    prompt = f"""Ты - оценщик контента на негативное содержание. Используют тебя как API модель,
    поэтому твоя задача дать ответ в виде одной цифры 1 или 0, больше никак. Если ты дашь ответ не в виде одной и цифр, то программа перестанет работать.
    Твоя задача -оценить следущие слова на наличие негативного конетента - оскорбления, нецензурные слова и т.д.
    Если ты их найдёшь негатив - ответь 1, если нет - 0. Помни, что ты API сервис и отходжение от правильного ответа создаст ошибки в работе программы
    Вот данные слова: {category}, {label}, {about}
    ТВОЙ ОТВЕТ ЛИБО 0, ЛИБО 1, НИЧЕГО ДРУГОГО, НИКАКОГО КОДА ИЛИ ЧТО-ТО ЕЩЁ - ТОЛЬКО 0 или 1, НЕ НУЖНО РАЗМЫШЛЕНИЙ ИЛИ ЧЕГО-ТО ЕЩЁ. ТВОЙ ОТВЕТ - ЭТО ОДНА ЦИФРА"""



    API_KEY = os.getenv("API_KEY")
    MODEL = os.getenv("MODEL")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    
    full_response = []
    
    with requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        stream=True
    ) as response:
        if response.status_code != 200:
            print("Ошибка API:", response.status_code)
            return ""
        
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8').replace('data: ', '')
                try:
                    chunk_json = json.loads(chunk_str)
                    if "choices" in chunk_json:
                        content = chunk_json["choices"][0]["delta"].get("content", "")
                        if content:
                            cleaned = content.replace('<think>', '').replace('</think>', '')
                            full_response.append(cleaned)
                except:
                    pass
    
    result = ''.join(full_response)
    print(result)

    if "0" in result or 0 in result:
        return 0
    return 1



def list_ds_answer(text) -> str:
    prompt = f"""Ты - оценщик контента на негативное содержание. Используют тебя как API модель,
    поэтому твоя задача дать ответ в виде одной цифры 1 или 0, больше никак. Если ты дашь ответ не в виде одной и цифр, то программа перестанет работать.
    Твоя задача -оценить следущее слово на наличие негативного конетента - оскорбления, нецензурные слова и т.д.
    Если ты их найдёшь негатив - ответь 1, если нет - 0. Помни, что ты API сервис и отходжение от правильного ответа создаст ошибки в работе программы
    Вот данные слово: {text}
    ТВОЙ ОТВЕТ ЛИБО 0, ЛИБО 1, НИЧЕГО ДРУГОГО, НИКАКОГО КОДА ИЛИ ЧТО-ТО ЕЩЁ - ТОЛЬКО 0 или 1, НЕ НУЖНО РАЗМЫШЛЕНИЙ ИЛИ ЧЕГО-ТО ЕЩЁ. ТВОЙ ОТВЕТ - ЭТО ОДНА ЦИФРА"""



    API_KEY = os.getenv("API_KEY")
    MODEL = os.getenv("MODEL")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    
    full_response = []
    
    with requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        stream=True
    ) as response:
        if response.status_code != 200:
            print("Ошибка API:", response.status_code)
            return ""
        
        for chunk in response.iter_lines():
            if chunk:
                chunk_str = chunk.decode('utf-8').replace('data: ', '')
                try:
                    chunk_json = json.loads(chunk_str)
                    if "choices" in chunk_json:
                        content = chunk_json["choices"][0]["delta"].get("content", "")
                        if content:
                            cleaned = content.replace('<think>', '').replace('</think>', '')
                            full_response.append(cleaned)
                except:
                    pass
    
    result = ''.join(full_response)
    print(result)

    if "0" in result or 0 in result:
        return 0
    return 1

