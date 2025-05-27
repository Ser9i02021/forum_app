from flask import Flask, render_template_string, request, redirect, url_for, flash
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback_secret')

# 1) Load the URI correctly:
MONGO_URI = os.environ["MONGODB_URI"]  # e.g. "mongodb://127.0.0.1:27017/forum"

# 2) Create a Mongo client & get the collection:
client = MongoClient(MONGO_URI)
db = client.get_default_database()     # picks 'forum' from the URI
messages_col = db.messages             # a 'messages' collection

template = template = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Forum</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 2em auto; }
        ul { list-style-type: none; padding: 0; }
        li { margin-bottom: 1em; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Simple Forum</h1>

    {% with errors = get_flashed_messages() %}
      {% if errors %}
        <ul class="error">
        {% for e in errors %}
            <li>{{ e }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}

    <ul>
      {% for msg in messages_list %}
        <li><strong>{{ msg['author'] if msg.get('author') else msg[1] }}:</strong>
            {{ msg['text'] if msg.get('text') else msg[2] }}
        </li>
      {% endfor %}
    </ul>

    <form method="post" action="{{ url_for('post_message') }}">
      <div>
        <label for="author">Name:</label><br>
        <input type="text" id="author" name="author" required>
      </div>
      <div>
        <label for="text">Message:</label><br>
        <textarea id="text" name="text" rows="4" required></textarea>
      </div>
      <button type="submit">Post Message</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    # Fetch all messages, sorted by insertion order (_id)
    msgs = list(messages_col.find({}, {"author":1, "text":1}).sort("_id", 1))
    return render_template_string(template, messages_list=msgs)

@app.route('/post', methods=['POST'])
def post_message():
    author = request.form['author'].strip()
    text   = request.form['text'].strip()

    # Pull the single most-recent doc
    last = messages_col.find_one(sort=[("_id", -1)])
    if last and last["author"] == author:
        flash('You cannot post two messages in a row. Please wait for another user.')
    else:
        messages_col.insert_one({"author": author, "text": text})
    return redirect(url_for('index'))

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    # listen on all interfaces so Machine B can hit Machine A
    app.run(host='0.0.0.0', port=port, debug=True)
