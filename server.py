import os
import re
import requests
import openai
from flask import Flask, request, jsonify

# Inicjalizacja aplikacji Flask, serwujemy pliki z folderu "static"
+ app = Flask(__name__, static_folder=".", static_url_path="")

# Klucze API ustaw w zmiennych środowiskowych
openai.api_key = os.environ.get("OPENAI_API_KEY")
BIBLE_API_KEY = os.environ.get("BIBLE_API_KEY")
BIBLE_ID = os.environ.get("BIBLE_ID", "nwb")

# Mapowanie polskich nazw ksiąg na angielskie
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

# Serwujemy główny plik HTML z folderu static
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Endpoint API dla POST /ask
@app.route('/ask', methods=['POST'])
def ask():
    payload = request.get_json() or {}
    user_ref = payload.get('prompt') or payload.get('question') or ''
    ref = convert_book_name(user_ref)
    verse_text = get_verse_text(ref) or ""

    full_prompt = (
        f"Użytkownik prosi o komentarz do wersetu Biblii: '{user_ref}'.\n"
        f"Tekst wersetu: {verse_text}\n"
        f"Napisz krótki, zrozumiały komentarz do tego wersetu."
    )

    try:
        response = openai.ChatCompletion.create(
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
