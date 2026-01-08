from flask import Flask, render_template, request, jsonify
from chatbot import Chatbot
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

# initialize chatbot (loads data/college_details.json)
bot = Chatbot(data_path=os.path.join('data', 'college_details.json'))

@app.route('/')
def index():
    return render_template('index.html', college_name=bot.data.get('name', 'College Chatbot'))

@app.route('/api/chat', methods=['POST'])
def chat_api():
    payload = request.get_json(silent=True) or {}
    text = payload.get('message', '')
    if not text:
        return jsonify({'error': 'No message provided'}), 400
    answer = bot.answer(text)
    return jsonify({'answer': answer})

if __name__ == "__main__":
    app.run(debug=True, port=5004)

