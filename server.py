from flask import Flask, request, jsonify, send_from_directory
import openai
import requests
import os

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
BIBLE_API_KEY = os.environ.get("BIBLE_API_KEY")
BIBLE_ID = "1c9761e0230da6e0-01"

# Pełna mapa: polska nazwa → kod API
book_codes = {
    # Stary Testament
    "Rodzaju": "GEN",
    "Wyjścia": "EXO",
    "Kapłańska": "LEV",
    "Liczb": "NUM",
    "Powtórzonego Prawa": "DEU",
    "Jozuego": "JOS",
    "Sędziów": "JDG",
    "Ruty": "RUT",
    "1 Samuela": "1SA",
    "2 Samuela": "2SA",
    "1 Królewska": "1KI",
    "2 Królewska": "2KI",
    "1 Kronik": "1CH",
    "2 Kronik": "2CH",
    "Ezdrasza": "EZR",
    "Nehemiasza": "NEH",
    "Estery": "EST",
    "Hioba": "JOB",
    "Psalmów": "PSA",
    "Przysłów": "PRO",
    "Kaznodziei": "ECC",
    "Pieśń nad pieśniami": "SNG",
    "Izajasza": "ISA",
    "Jeremiasza": "JER",
    "Lamentacje": "LAM",
    "Ezechiela": "EZK",
    "Daniela": "DAN",
    "Ozeasza": "HOS",
    "Joela": "JOL",
    "Amosa": "AMO",
    "Abdiasza": "OBA",
    "Jonasza": "JON",
    "Micheasza": "MIC",
    "Nahuma": "NAM",
    "Habakuka": "HAB",
    "Sofoniasza": "ZEP",
    "Aggeusza": "HAG",
    "Zachariasza": "ZEC",
    "Malachiasza": "MAL",
    # Nowy Testament
    "Ewangelia Mateusza": "MAT",
    "Ewangelia Marka": "MRK",
    "Ewangelia Łukasza": "LUK",
    "Ewangelia Jana": "JHN",
    "Dzieje Apostolskie": "ACT",
    "List do Rzymian": "ROM",
    "1 List do Koryntian": "1CO",
    "2 List do Koryntian": "2CO",
    "List do Galacjan": "GAL",
    "List do Efezjan": "EPH",
    "List do Filipian": "PHP",
    "List do Kolosan": "COL",
    "1 List do Tesaloniczan": "1TH",
    "2 List do Tesaloniczan": "2TH",
    "1 List do Tymoteusza": "1TI",
    "2 List do Tymoteusza": "2TI",
    "List do Tytusa": "TIT",
    "List do Filemona": "PHM",
    "List do Hebrajczyków": "HEB",
    "List Jakuba": "JAS",
    "1 List Piotra": "1PE",
    "2 List Piotra": "2PE",
    "1 List Jana": "1JN",
    "2 List Jana": "2JN",
    "3 List Jana": "3JN",
    "List Judy": "JUD",
    "Objawienie Jana": "REV"
}


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


@app.route("/api/verse")
def get_verse():
    book = request.args.get("book")
    chapter = request.args.get("chapter")
    verse_from = request.args.get("verseFrom")
    verse_to = request.args.get("verseTo")

    if not all([book, chapter, verse_from]):
        return jsonify({"error": "Missing parameters"}), 400

    book_code = book_codes.get(book)
    if not book_code:
        return jsonify({"error": f"Unsupported book: {book}"}), 400

    verse_ref = f"{book_code}.{chapter}.{verse_from}"
    if verse_to:
        verse_ref += f"-{verse_to}"

    url = f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}/passages/{verse_ref}?content-type=text&include-notes=false&include-titles=false&include-chapter-numbers=false&include-verse-numbers=false"
    headers = {"api-key": BIBLE_API_KEY}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("❌ Błąd API Scripture:")
        print("Status:", response.status_code)
        print("URL:", url)
        print("Treść:", response.text)
        return jsonify({"error": "Failed to fetch passage", "details": response.text}), 500

    data = response.json()
    content = data.get("data", {}).get("content", "")

    return jsonify({"text": content})




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
