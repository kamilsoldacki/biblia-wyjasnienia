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
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Wyjaśnij znaczenie wybranego fragmentu Biblii, odwołując się do jego kontekstu biblijnego, historycznego i językowego – ale tylko tam, gdzie rzeczywiście wnosi to nową perspektywę lub odkrywa coś istotnego. Unikaj szablonowych wstępów i powtarzalnych sformułowań. Jeśli odwołujesz się do języka greckiego, hebrajskiego lub aramejskiego, rób to tylko wtedy, gdy dane słowo znacząco zmienia zrozumienie tekstu. Nie przytaczaj ani nie streszczaj wersetu – zakładamy, że czytelnik go zna, nawet jeśli nie został podany przez użytkownika. Nie dodawaj refleksji, zastosowań duchowych, duchowych przesłań ani podsumowań. Nie zamykaj tekstu żadną formą przesłania, „lekcji” ani zachęty. Zakończ, gdy kończy się analiza. Nie używaj tonu kazania. Pisz klarownie, rzeczowo, ale z wyczuciem i głębią – jak osoba, która pomaga dostrzec coś, co mogło umknąć czytelnikowi. Nie używaj nagłówków."
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
