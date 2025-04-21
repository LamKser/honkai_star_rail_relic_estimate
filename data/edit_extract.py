from flask import Flask, request, jsonify, send_from_directory


app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('.', 'lightcone_comparasion.html')


@app.route('/save', methods=['POST'])
def save():
    data = request.json
    content = data.get('content')

    # Save the content to a file
    with open('edit.html', 'w', encoding='utf-8') as f:
        f.write(content)

    return jsonify({'message': 'Content saved successfully!'})


if __name__ == '__main__':
    app.run(debug=True)
