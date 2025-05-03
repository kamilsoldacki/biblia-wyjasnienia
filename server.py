from flask import Flask, request, jsonify, send_from_directory
import openai
import os
import requests

# Klucz do Scripture.Bible (z Render.com env var)
bible_api_key = os.environ.get("BIBLE_API_KEY")
# ID wersji, z której chcesz korzystać
bible_version = "1c9761e0230da6e0-01"

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
    prompt      = data.get('prompt')
    book        = data.get('book')
    chapter     = data.get('chapter')
    verse_start = data.get('verse_start')
    verse_end   = data.get('verse_end')  # może być None

    if not prompt:
        return jsonify({'answer': 'Nie otrzymano promptu.'}), 400

    # 1) Pobranie tekstu wersetu/zakresu z Scripture.Bible
    if verse_end:
        passage_id = f"{book}.{chapter}.{verse_start}-{book}.{chapter}.{verse_end}"
        url = f"https://api.scripture.api.bible/v1/bibles/{bible_version}/passages/{passage_id}?content-type=text"
    else:
        verse_id = f"{book}.{chapter}.{verse_start}"
        url = f"https://api.scripture.api.bible/v1/bibles/{bible_version}/verses/{verse_id}?content-type=text"

    headers = {"api-key": bible_api_key}
    try:
        bib_resp = requests.get(url, headers=headers)
        bib_resp.raise_for_status()
        verse_text = bib_resp.json()['data']['content'].strip()
    except Exception as e:
        verse_text = f"(błąd pobierania wersetu: {e})"

    # 2) Wywołanie OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = response['choices'][0]['message']['content']

    # 3) Zwracamy JSON z odpowiedzią i tekstem wersetu
    return jsonify({
        'verse_text': verse_text,
        'answer': answer
    })

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Pomóż czytelnikowi głębiej zrozumieć znaczenie wybranego fragmentu Biblii. Twoim zadaniem jest odsłonić ukryte warstwy tekstu – znaczenia, które mogą nie być widoczne w zwykłym tłumaczeniu. Skup się na tych elementach kontekstu biblijnego, historycznego i językowego (greckiego, hebrajskiego, aramejskiego), które rzeczywiście zmieniają sposób rozumienia fragmentu lub rzucają na niego nowe światło. Nie tłumacz każdego słowa – tylko te, które mają znaczenie kluczowe, nietypowe, pogłębiające lub zaskakujące. Szczególnie zwracaj uwagę na słowa, które w językach oryginalnych mają znaczenie bogatsze lub inne niż sugeruje tłumaczenie. Jeśli takie słowo wpływa na sens tekstu, koniecznie je omów – nawet krótko. Twoim zadaniem jest pomóc czytelnikowi zobaczyć coś, czego nie widać w samym tłumaczeniu. Zwróć uwagę na słowa o dużym ładunku znaczeniowym – emocjonalnym, egzystencjalnym, relacyjnym, historycznym lub teologicznym. Uwzględnij także imiona, nazwy miejsc, czasowniki i formy gramatyczne, jeśli niosą dodatkowy sens. Jeśli analizujesz konkretne słowo, wyraźnie zaznacz, do którego się odnosisz, i pokaż, jak wpływa ono na znaczenie zdania lub fragmentu. Unikaj mechanicznego omawiania kolejnych słów z wersetu. Każdy element, który komentujesz, powinien być istotny dla zrozumienia głównego sensu tekstu. Nie streszczaj wersetu ani przesłania całej Ewangelii czy Nowego Testamentu. Nie dodawaj refleksji, przesłań, duchowych lekcji ani zachęt. Nie opisuj, czym jest lub powinno być życie chrześcijańskie. Nie pisz w stylu kaznodziei, nauczyciela ani akademika. Traktuj czytelnika jak osobę uważną, myślącą, która zna tekst, ale chce go zrozumieć jeszcze lepiej – nie potrzebuje pouczeń. Pisz rzeczowo, precyzyjnie, ale z wyczuciem i głębią. Nie używaj nagłówków, podsumowań ani zamykających interpretację sformułowań. Zakończ, gdy kończy się analiza."
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
