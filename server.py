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
                        "Wyjaśnij dokładnie, uwzględniając:\n"
                        "- podstawowe znaczenie wersetu w jego bezpośrednim kontekście biblijnym,\n"
                        "- analizę kluczowych słów w oryginalnych językach Biblii (hebrajski, aramejski, grecki),\n"
                        "- hebrajskie lub aramejskie tło pojęciowe i ich wpływ na zrozumienie treści,\n"
                        "- tło historyczne i kulturowe (żydowskie, greckie, rzymskie), w jakim powstał tekst,\n"
                        "- różnice między świeckim a biblijnym rozumieniem kluczowych terminów,\n"
                        "- wypisz na końcu inne wersety biblijne, do których może nawiązywać analizowany werset (bez ich pełnych treści – tylko odnośniki).\n\n"
                        "Pisz językiem zrozumiałym dla osoby, która zna Biblię, ale nie jest specjalistą od języków oryginalnych ani akademickiej teologii. "
                        "Każdą sekcję zakończ krótkim podsumowaniem. "
                        "Nie cytuj pełnego wersetu – zakładamy, że czytelnik go już zna. "
                        "Formatuj odpowiedź w stylu Markdown. Używaj nagłówków, wypunktowań, pogrubień i nowej linii, aby tekst był przejrzysty."
                    )
                },
                {"role": "user", "content": prompt}
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
