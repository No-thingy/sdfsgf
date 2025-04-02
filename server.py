from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)
    logging.info(f'Response: {response!r}')
    return jsonify(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'stage': 'elephant',
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = 'Привет! Купи слона!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if sessionStorage[user_id]['stage'] == 'elephant':
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'куплю',
            'покупаю',
            'хорошо',
            'я куплю',
            'я покупаю'
        ]:
            sessionStorage[user_id]['stage'] = 'rabbit'
            sessionStorage[user_id]['suggests'] = ["Зачем?", "Не хочу!", "Опять?!"]
            res['response']['text'] = 'Слона можно найти на Яндекс.Маркете! А теперь купи кролика!'
            res['response']['buttons'] = get_suggests(user_id)
            return

        res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи слона!"
        res['response']['buttons'] = get_suggests(user_id)
        return

    if sessionStorage[user_id]['stage'] == 'rabbit':
        if req['request']['original_utterance'].lower() in [
            'ладно',
            'куплю',
            'покупаю',
            'хорошо',
            'я куплю',
            'я покупаю'
        ]:
            res['response']['text'] = 'Кролика можно найти на Яндекс.Маркете! Спасибо за покупки!'
            res['response']['end_session'] = True
            return

        res['response']['text'] = f"Все говорят '{req['request']['original_utterance']}', а ты купи кролика!"
        res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=кролик" if
            session['stage'] == 'rabbit' else "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()