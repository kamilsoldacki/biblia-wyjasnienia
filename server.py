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
                        "Wyjaśnij znaczenie wybranego fragmentu Biblii, odwołując się do jego kontekstu biblijnego, historycznego i językowego – ale tylko tam, gdzie rzeczywiście wnosi to nową perspektywę lub odkrywa coś istotnego. Unikaj szablonowych wstępów i powtarzalnych sformułowań. Jeśli odwołujesz się do języka greckiego, hebrajskiego lub aramejskiego, rób to tylko wtedy, gdy dane słowo znacząco zmienia zrozumienie tekstu. Nie dodawaj refleksji, zastosowań duchowych ani podsumowań. Nie używaj tonu kazania. Pisz klarownie, rzeczowo, ale z wyczuciem i głębią – jak osoba, która pomaga dostrzec coś, co mogło umknąć czytelnikowi. Nie używaj nagłówków, nie cytuj wersetu."
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
