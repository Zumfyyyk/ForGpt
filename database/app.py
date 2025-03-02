import asyncio
from flask import Flask, render_template, request, redirect, url_for
from database import create_tables, get_logs, get_support_messages, respond_to_support_message, get_support_message_by_id
from handlers.support import respond_to_user

app = Flask(__name__)

@app.route('/')
def index():
    logs = get_logs()
    support_messages = get_support_messages()
    return render_template('index.html', logs=logs, support_messages=support_messages)

@app.route('/respond', methods=['POST'])
def respond():
    message_id = request.form['message_id']
    response = request.form['response']
    respond_to_support_message(message_id, response)
    message = get_support_message_by_id(message_id)
    if message:
        user_id, _ = message
        asyncio.run(respond_to_user(app.telegram_context, user_id, response))
    return redirect(url_for('index'))

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)