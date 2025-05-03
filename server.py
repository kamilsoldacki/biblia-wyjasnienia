import os
import requests
import openai
from flask import Flask, request, jsonify

# Inicjalizacja aplikacji Flask, serwujemy pliki z folderu "static"
# Serwowanie plików z katalogu głównego (index.html w repo root)
app = Flask(__name__, static_folder=".", static_url_path="")

# Klucze API z env vars
openai.api_key = os.environ.get("OPENAI_API_KEY")
BIBLE_API_KEY = os.environ.get("BIBLE_API_KEY")
BIBLE_ID = os.environ.get("BIBLE_ID", "nwb")

# Mapowanie polskich nazw ksiąg na angielskie nazwy
book_map = {
    'Rodzaju': 'Genesis', 'Wyjścia': 'Exodus', 'Kapłańska': 'Leviticus',
    'Liczb': 'Numbers', 'Powtórzonego Prawa': 'Deuteronomy', 'Jozuego': 'Joshua',
    'Sędziów': 'Judges', 'Rut': 'Ruth', '1 Samuela': '1 Samuel', '2 Samuela': '2 Samuel',
    '1 Królewska': '1 Kings', '2 Królewska': '2 Kings', '1 Kronik': '1 Chronicles',
    '2 Kronik': '2 Chronicles', 'Ezdrasza': 'Ezra', 'Nehemiasza': 'Nehemiah',
    'Estery': 'Esther', 'Hioba': 'Job', 'Psalmów': 'Psalms', 'Przysłów': 'Proverbs',
    'Kaznodziei': 'Ecclesiastes', 'Pieśń nad Pieśniami': 'Song of Solomon',
    'Izajasza': 'Isaiah', 'Jeremiasza': 'Jeremiah', 'Lamentacje': 'Lamentations',
    'Ezechiela': 'Ezekiel', 'Daniela': 'Daniel', 'Ozeasza': 'Hosea', 'Joela': 'Joel',
    'Amosa': 'Amos', 'Abdiasza': 'Obadiah', 'Jonasza': 'Jonah', 'Micheasza': 'Micah',
    'Nahuma': 'Nahum', 'Habakuka': 'Habakkuk', 'Sofoniasza': 'Zephaniah',
    'Aggeusza': 'Haggai', 'Zachariasza': 'Zechariah', 'Malachiasza': 'Malachi',
    'Mateusza': 'Matthew', 'Marka': 'Mark', 'Łukasza': 'Luke', 'Jana': 'John',
    'Dziejów Apostolskich': 'Acts', 'Rzymian': 'Romans', '1 Koryntian': '1 Corinthians',
    '2 Koryntian': '2 Corinthians', 'Galacjan': 'Galatians', 'Efezjan': 'Ephesians',
    'Filipian': 'Philippians', 'Kolosan': 'Colossians', '1 Tesaloniczan': '1 Thessalonians',
    '2 Tesaloniczan': '2 Thessalonians', '1 Tymoteusza': '1 Timothy', '2 Tymoteusza': '2 Timothy',
    'Tytusa': 'Titus', 'Filemona': 'Philemon', 'Hebrajczyków': 'Hebrews', 'Jakuba': 'James',
    '1 Piotra': '1 Peter', '2 Piotra': '2 Peter', '1 Jana': '1 John', '2 Jana': '2 John',
    '3 Jana': '3 John', 'Judy': 'Jude', 'Objawienie': 'Revelation',
}

def convert_book_name(reference: str) -> str:
    parts = reference.strip().split(' ', 1)
    if len(parts) != 2:
        return reference
    book_pol, verses = parts
    eng = book_map.get(book_pol)
    return f"{eng} {verses}" if eng else reference


def get_verse_text(ref: str) -> str:
    url = f"https://api.scripture.api.bible/v1/bibles/{BIBLE_ID}/passages"
    headers = {"api-key": BIBLE_API_KEY}
    resp = requests.get(url, headers=headers, params={"q": ref})
    if not resp.ok:
        return None
    data = resp.json().get("data")
    return data.get("content") if data and "content" in data else None

@app.route('/')
def index():
    # Serwujemy statyczny index.html z katalogu public/static
    return app.send_static_file('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'answer': 'Nie otrzymano promptu.'}), 400

    verse_text = get_verse_text(prompt)
    if not verse_text:
        return jsonify({'answer': 'Nie udało się znaleźć wersetu.'}), 404

    full_prompt = f"Wyjaśnij fragment Biblii {prompt}: {verse_text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Pomóż czytelnikowi głębiej zrozumieć znaczenie wybranego fragmentu Biblii. Twoim zadaniem jest odsłonić ukryte warstwy tekstu – znaczenia, które mogą nie być widoczne w zwykłym tłumaczeniu. Skup się na tych elementach kontekstu biblijnego, historycznego i językowego (greckiego, hebrajskiego, aramejskiego), które rzeczywiście zmieniają sposób rozumienia fragmentu lub rzucają na niego nowe światło. Nie tłumacz każdego słowa – tylko te, które mają znaczenie kluczowe, nietypowe, pogłębiające lub zaskakujące. Szczególnie zwracaj uwagę na słowa, które w językach oryginalnych mają znaczenie bogatsze lub inne niż sugeruje tłumaczenie. Jeśli takie słowo wpływa na sens tekstu, koniecznie je omów – nawet krótko. Twoim zadaniem jest pomóc czytelnikowi zobaczyć coś, czego nie widać w samym tłumaczeniu. Zwróć uwagę na słowa o dużym ładunku znaczeniowym – emocjonalnym, egzystencjalnym, relacyjnym, historycznym lub teologicznym. Uwzględnij także imiona, nazwy miejsc, czasowniki i formy gramatyczne, jeśli niosą dodatkowy sens. Jeśli analizujesz konkretne słowo, wyraźnie zaznacz, do którego się odnosisz, i pokaż, jak wpływa ono na znaczenie zdania lub fragmentu. Unikaj mechanicznego omawiania kolejnych słów z wersetu. Każdy element, który komentujesz, powinien być istotny dla zrozumienia głównego sensu tekstu. Nie streszczaj wersetu ani przesłania całej Ewangelii czy Nowego Testamentu. Nie dodawaj refleksji, przesłań, duchowych lekcji ani zachęt. Nie opisuj, czym jest lub powinno być życie chrześcijańskie. Nie pisz w stylu kaznodziei, nauczyciela ani akademika. Traktuj czytelnika jak osobę uważną, myślącą, która zna tekst, ale chce go zrozumieć jeszcze lepiej – nie potrzebuje pouczeń. Pisz rzeczowo, precyzyjnie, ale z wyczuciem i głębią. Nie używaj nagłówków, podsumowań ani zamykających interpretację sformułowań. Zakończ, gdy kończy się analiza."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem."},
                {"role": "user", "content": full_prompt}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({'answer': answer, 'verse': verse_text})
    except Exception as e:
        return jsonify({'answer': f'Wystąpił błąd: {str(e)}'}), 500

if __name__ == '__main__':
    print('>>> Flask uruchomiony – oczekuję na /ask <<<')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
