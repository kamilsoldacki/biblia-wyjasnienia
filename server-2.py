from flask import Flask, request, jsonify, send_from_directory
import openai
import os
import requests
import re

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")
BIBLE_API_KEY = os.environ.get("BIBLE_API_KEY")

book_map = {'Rodzaju': 'Genesis', 'Wyjścia': 'Exodus', 'Kapłańska': 'Leviticus', 'Liczb': 'Numbers', 'Powtórzonego': 'Deuteronomy', 'Jozuego': 'Joshua', 'Sędziów': 'Judges', 'Ruty': 'Ruth', '1 Samuela': '1 Samuel', '2 Samuela': '2 Samuel', '1 Królewska': '1 Kings', '2 Królewska': '2 Kings', '1 Kronik': '1 Chronicles', '2 Kronik': '2 Chronicles', 'Ezdrasza': 'Ezra', 'Nehemiasza': 'Nehemiah', 'Ester': 'Esther', 'Hioba': 'Job', 'Psalmów': 'Psalms', 'Przysłów': 'Proverbs', 'Kaznodziei': 'Ecclesiastes', 'Pieśń': 'Song of Songs', 'Izajasza': 'Isaiah', 'Jeremiasza': 'Jeremiah', 'Lamentacje': 'Lamentations', 'Ezechiela': 'Ezekiel', 'Daniela': 'Daniel', 'Ozeasza': 'Hosea', 'Joela': 'Joel', 'Amosa': 'Amos', 'Abdiasza': 'Obadiah', 'Jonasza': 'Jonah', 'Micheasza': 'Micah', 'Nahuma': 'Nahum', 'Habakuka': 'Habakkuk', 'Sofoniasza': 'Zephaniah', 'Aggeusza': 'Haggai', 'Zachariasza': 'Zechariah', 'Malachiasza': 'Malachi', 'Mateusza': 'Matthew', 'Marka': 'Mark', 'Łukasza': 'Luke', 'Jana': 'John', 'Dzieje': 'Acts', 'Rzymian': 'Romans', '1 Koryntian': '1 Corinthians', '2 Koryntian': '2 Corinthians', 'Galacjan': 'Galatians', 'Efezjan': 'Ephesians', 'Filipian': 'Philippians', 'Kolosan': 'Colossians', '1 Tesaloniczan': '1 Thessalonians', '2 Tesaloniczan': '2 Thessalonians', '1 Tymoteusza': '1 Timothy', '2 Tymoteusza': '2 Timothy', 'Tytusa': 'Titus', 'Filemona': 'Philemon', 'Hebrajczyków': 'Hebrews', 'Jakuba': 'James', '1 Piotra': '1 Peter', '2 Piotra': '2 Peter', '1 Jana': '1 John', '2 Jana': '2 John', '3 Jana': '3 John', 'Judy': 'Jude', 'Objawienie': 'Revelation'}

def convert_book_name(reference):
    for polish, english in book_map.items():
        if reference.startswith(polish):
            rest = reference[len(polish):].strip()
            return f"{english} {rest}"
    return reference

def get_verse_text(reference):
    bible_id = "1c9761e0230da6e0-01"
    headers = {
        "api-key": BIBLE_API_KEY
    }

    eng_reference = convert_book_name(reference)

    search_url = f"https://api.scripture.api.bible/v1/bibles/{bible_id}/search?query={eng_reference}&limit=1"
    search_response = requests.get(search_url, headers=headers)
    search_data = search_response.json()

    try:
        verse_id = search_data["data"]["verses"][0]["id"]
    except (KeyError, IndexError):
        return None

    verse_url = f"https://api.scripture.api.bible/v1/bibles/{bible_id}/verses/{verse_id}"
    verse_response = requests.get(verse_url, headers=headers)
    verse_data = verse_response.json()

    raw_html = verse_data["data"]["content"]
    clean_text = re.sub('<.*?>', '', raw_html).strip()
    return clean_text

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
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ]
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({'answer': answer, 'verse': verse_text})
    except Exception as e:
        return jsonify({'answer': f'Wystąpił błąd: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
