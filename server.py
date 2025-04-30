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
                        "Wyjaśnij znaczenie wybranego fragmentu Biblii, odwołując się tylko do tych aspektów kontekstu biblijnego, historycznego i językowego, które rzeczywiście wnoszą nową perspektywę lub znacząco pogłębiają zrozumienie tekstu. Nie cytuj ani nie streszczaj wersetu – zakładamy, że czytelnik go zna, nawet jeśli nie został podany przez użytkownika. Odnoś się do języka greckiego, hebrajskiego lub aramejskiego tylko wtedy, gdy konkretne słowo istotnie zmienia zrozumienie tekstu – nie tłumacz każdego słowa. Szczególną uwagę zwracaj na słowa dynamiczne, nacechowane ruchem, działaniem lub napięciem – zwłaszcza czasowniki. Jeśli dane słowo (np. „gonić”, „ścigać”, „prześladować”) miało inne znaczenie w poprzednich fragmentach Biblii lub niesie istotny ładunek emocjonalny lub historyczny, koniecznie je uwzględnij. Unikaj szablonowych wstępów i powtarzalnych sformułowań. Nie dodawaj refleksji, przesłań, duchowych lekcji ani zachęt. Nie opisuj, czym jest lub powinno być życie chrześcijańskie. Unikaj normatywnych stwierdzeń dotyczących duchowości lub celu życia. Pisz rzeczowo, precyzyjnie, ale z głębią i wyczuciem – jak ekspert, który dostrzega niuanse i dzieli się nimi bez narzucania interpretacji. Nie używaj nagłówków, podsumowań ani żadnej formy zakończenia, która podkreśla „przesłanie” lub „lekcję”."
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
