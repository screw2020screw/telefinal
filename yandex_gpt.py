import requests
import logging  # модуль для сбора логов
# подтягиваем константы из config файла
from config import *

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")



# запрос к GPT
def ask_gpt(message):
    """Запрос к Yandex GPT"""

    #Получаем токен и folder_id, так как время жизни токена 12 часов
    token = IAM_TOKEN
    folder_id = FOLDER_ID

    url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "modelUri": f"gpt://{folder_id}/{GPT_MODEL}/latest",
        "completionOptions": {
            "stream": False,
            "temperature": MODEL_TEMPERATURE,
            "maxTokens": 100
        },
        "messages": []
    }

    collection=[{'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': message}]

    for row in collection:
        content = row['content']
        data["messages"].append(
                {
                    "role": row["role"],
                    "text": content
                }
            )

    result_for_test_mode = 'Empty message for test mode'
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            logging.debug(f"Response {response.json()} Status code: {response.status_code} Message {response.text}")
            result = f"Status code {response.status_code}. Подробности см. в журнале."
            return result
        result = response.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        #logging.ERROR(f"An unexpected error occured: {e}")
        result = "Произошла непредвиденная ошибка. Подробности см. в журнале."

    return result

if __name__ == "__main__":
    pass


def count_gpt_tokens(message):
    my_string = " ".join(str(element) for element in message)
    headers = { # заголовок запроса, в котором передаем IAM-токен
        'Authorization': f'Bearer {IAM_TOKEN}', # token - наш IAM-токен
        'Content-Type': 'application/json'
    }
    data = {
       "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest", # указываем folder_id
       "maxTokens": MAX_MODEL_TOKENS,
       "text": my_string # text - тот текст, в котором мы хотим посчитать токены
    }
    return len(
        requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize",
            json=data,
            headers=headers
        ).json()['tokens']
    ) # здесь, после выполнения запроса, функция возвращает количество токенов в text


