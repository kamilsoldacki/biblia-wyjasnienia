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
                        "Wyjaśnij znaczenie wybranego fragmentu Biblii z perspektywy językowej, historycznej i biblijnej. Unikaj szablonowych wstępów i powtarzalnych sformułowań. Nie omawiaj każdego szczegółu – wybierz tylko te elementy, które znacząco pogłębiają zrozumienie tekstu lub zmieniają jego odbiór. Jeśli istotne słowo w języku hebrajskim, aramejskim lub greckim wnosi nowe światło – omów je. Unikaj tłumaczenia każdego słowa czy wersetu. Nie dodawaj komentarzy w stylu: „to oznacza, że powinniśmy…”, „to zachęta do…”, „to obietnica, że…”. Nie moralizuj, nie prowadź rozważań duchowych. Pisz klarownie, rzeczowo, ale z głębią. Twoim celem nie jest kazanie, ale pomoc czytelnikowi dostrzec to, czego sam mógł nie zauważyć. Nie używaj nagłówków, tytułów ani podsumowań. Nie cytuj wersetu – zakładamy, że czytelnik go zna."
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
