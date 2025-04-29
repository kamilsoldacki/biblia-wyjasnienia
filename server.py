from flask import Flask, request, jsonify, send_from_directory
import openai
import os

app = Flask(__name__)

# Pobierz klucz API z Render.com → Environment Variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Serwuj index.html przy wejściu na stronę
@app.route('/')
def index():
    return send_from_directory('', 'index.html')

# Serwuj plik CSS
@app.route('/style.css')
def style():
    return send_from_directory('', 'style.css')

# Endpoint API: odbiera zapytanie, wysyła do OpenAI, zwraca odpowiedź
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
                {"role": "system", "content": "Jesteś ekspertem od Biblii, pomagającym w zrozumieniu wersów w kontekście oryginalnym."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.5
        )
        answer = response['choices'][0]['message']['content']
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': f'Wystąpił błąd: {str(e)}'}), 500

# Uruchom aplikację (Render to obsłuży)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
