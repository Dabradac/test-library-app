from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Хранилище книг
books = [
    {"id": 1, "title": "Война и мир", "author": "Лев Толстой", "year": 1869},
    {"id": 2, "title": "Преступление и наказание", "author": "Фёдор Достоевский", "year": 1866}
]
next_id = 3

def find_book(book_id):
    return next((book for book in books if book["id"] == book_id), None)

@app.route('/')
def index():
    return jsonify({"message": "Добро пожаловать в API библиотеки. Используйте /books для работы с книгами."})

@app.route('/books', methods=['GET'])
def get_books():
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Книга не найдена"}), 404
    return jsonify(book)

@app.route('/books', methods=['POST'])
def create_book():
    global next_id
    data = request.get_json()
    if not data:
        return jsonify({"error": "Не предоставлены данные"}), 400
    required_fields = ['title', 'author', 'year']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Отсутствует обязательное поле '{field}'"}), 400
    new_book = {
        "id": next_id,
        "title": data['title'],
        "author": data['author'],
        "year": data['year']
    }
    books.append(new_book)
    next_id += 1
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Книга не найдена"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Не предоставлены данные"}), 400
    required_fields = ['title', 'author', 'year']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Отсутствует обязательное поле '{field}'"}), 400
    book.update({
        'title': data['title'],
        'author': data['author'],
        'year': data['year']
    })
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['PATCH'])
def patch_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Книга не найдена"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error": "Не предоставлены данные"}), 400
    if 'title' in data:
        book['title'] = data['title']
    if 'author' in data:
        book['author'] = data['author']
    if 'year' in data:
        book['year'] = data['year']
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = find_book(book_id)
    if book is None:
        return jsonify({"error": "Книга не найдена"}), 404
    books = [b for b in books if b['id'] != book_id]
    return '', 204

# Новый маршрут для UI
@app.route('/ui')
def ui():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)