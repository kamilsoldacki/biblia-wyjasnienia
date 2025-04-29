from flask import Flask, request, jsonify, send_from_directory
import openai
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/style.css')
def style():
    return send_from_directory('', 'style.css')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'answer': 'Nie otrzymano promptu.'}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Wyjaśnij znaczenie wybranego fragmentu Biblii w sposób, który porusza ducha, duszę i ciało. Nie skupiaj się na każdym zadaniu ani każdym słowie – wybierz tylko to, co naprawdę wnosi nową perspektywę lub ma głębokie znaczenie duchowe. Uwzględnij kontekst biblijny, tło kulturowe i językowe tylko wtedy, gdy pomaga to zobaczyć coś głębiej, szerzej, inaczej. Jeśli jakieś słowo w języku hebrajskim, aramejskim lub greckim naprawdę zmienia zrozumienie tekstu – przytocz je i wyjaśnij, ale nie rób tego mechanicznie. Unikaj suchych analiz. Zamiast tego pomóż czytelnikowi odkryć coś, co może zainspirować go do głębszego czytania i osobistego spotkania z Bogiem przez ten tekst. Nie używaj nagłówków ani podsumowań. Nie cytuj wersetu – zakładamy, że czytelnik go zna. Pisz płynnie, prosto, ale głęboko – dla osoby, która zna Biblię, ale nie jest teologiem."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.5
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f'Wystąpił błąd: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
