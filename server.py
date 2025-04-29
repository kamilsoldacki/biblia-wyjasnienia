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
                        "Wyjaśnij znaczenie wybranego fragmentu Biblii, jak dojrzały interpretator – łącząc biblijną wiedzę, znajomość języków oryginalnych i kontekstu historycznego – ale pisząc językiem zrozumiałym i pobudzającym do myślenia. Nie analizuj każdego aspektu – skup się tylko na tym, co rzeczywiście wnosi nową perspektywę, odkrywa coś zaskakującego lub głęboko znaczącego duchowo. Jeśli oryginalne słowo w hebrajskim, aramejskim czy greckim zmienia sposób zrozumienia, przywołaj je – ale tylko wtedy. Unikaj tonu kazania czy rozważania. Nie pouczaj, nie moralizuj. Pisz jak osoba, która zna tekst, zna świat Biblii, ale wciąż z pokorą go bada – i dzieli się tym, co może pomóc innym czytać głębiej, nie tylko szerzej. Nie używaj nagłówków, tytułów ani podsumowań. Nie cytuj wersetu – zakładamy, że czytelnik go zna."
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
