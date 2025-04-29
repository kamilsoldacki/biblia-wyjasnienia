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
                        "Wyjaśnij znaczenie wybranego fragmentu Biblii, uwzględniając jego kontekst biblijny, tło kulturowe i językowe. "
                        "Opisz znaczenie kluczowych słów w oryginalnych językach (hebrajski, aramejski, grecki), historyczne tło oraz możliwe odniesienia do innych fragmentów. "
                        "Nie używaj nagłówków ani tytułów sekcji. Nie dodawaj podsumowań. "
                        "Napisz płynną, spójną odpowiedź językiem zrozumiałym dla osoby, która zna Biblię, ale nie jest specjalistą od teologii. "
                        "Nie cytuj wersetu – zakładamy, że czytelnik go już zna."
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
