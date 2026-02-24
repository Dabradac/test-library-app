import logging
import json
from flask import Flask, request, jsonify, render_template

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

log_config = config['logging']

log_handlers = []
console_handler = logging.StreamHandler()
log_handlers.append(console_handler)

if log_config.get('log_to_file', False):
    file_handler = logging.FileHandler(
        filename=log_config['filename'],
        mode=log_config.get('filemode', 'a'),
        encoding='utf-8'
    )
    log_handlers.append(file_handler)

logging.basicConfig(
    level=getattr(logging, log_config['level'].upper()),
    format=log_config['format'],
    datefmt=log_config['datefmt'],
    handlers=log_handlers
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

books = [
    {"id": 1, "title": "Война и мир", "author": "Лев Толстой", "year": 1869},
    {"id": 2, "title": "Преступление и наказание", "author": "Фёдор Достоевский", "year": 1866}
]
next_id = 3

def find_book(book_id):
    return next((book for book in books if book["id"] == book_id), None)

@app.before_request
def log_request_info():
    logger.debug(f"Запрос: {request.method} {request.path}")

# API endpoints
@app.route('/')
def index():
    logger.info("Главная страница запрошена")
    return jsonify({"message": "Добро пожаловать в API библиотеки. Используйте /books для работы с книгами."})

@app.route('/books', methods=['GET'])
def get_books():
    logger.info("Получен запрос на список всех книг")
    return jsonify(books)

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    logger.info(f"Запрос книги с id {book_id}")
    book = find_book(book_id)
    if book is None:
        logger.warning(f"Книга с id {book_id} не найдена")
        return jsonify({"error": "Книга не найдена"}), 404
    return jsonify(book)

@app.route('/books', methods=['POST'])
def create_book():
    global next_id
    logger.info("Запрос на создание новой книги")
    data = request.get_json()
    if not data:
        logger.error("Не предоставлены данные в теле запроса")
        return jsonify({"error": "Не предоставлены данные"}), 400
    required_fields = ['title', 'author', 'year']
    for field in required_fields:
        if field not in data:
            logger.error(f"Отсутствует обязательное поле '{field}'")
            return jsonify({"error": f"Отсутствует обязательное поле '{field}'"}), 400
    new_book = {
        "id": next_id,
        "title": data['title'],
        "author": data['author'],
        "year": data['year']
    }
    books.append(new_book)
    next_id += 1
    logger.info(f"Книга создана: {new_book}")
    return jsonify(new_book), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    logger.info(f"Запрос на полное обновление книги id {book_id}")
    book = find_book(book_id)
    if book is None:
        logger.warning(f"Книга с id {book_id} не найдена для обновления")
        return jsonify({"error": "Книга не найдена"}), 404
    data = request.get_json()
    if not data:
        logger.error("Не предоставлены данные в теле запроса")
        return jsonify({"error": "Не предоставлены данные"}), 400
    required_fields = ['title', 'author', 'year']
    for field in required_fields:
        if field not in data:
            logger.error(f"Отсутствует обязательное поле '{field}'")
            return jsonify({"error": f"Отсутствует обязательное поле '{field}'"}), 400
    book.update({
        'title': data['title'],
        'author': data['author'],
        'year': data['year']
    })
    logger.info(f"Книга id {book_id} обновлена")
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['PATCH'])
def patch_book(book_id):
    logger.info(f"Запрос на частичное обновление книги id {book_id}")
    book = find_book(book_id)
    if book is None:
        logger.warning(f"Книга с id {book_id} не найдена для частичного обновления")
        return jsonify({"error": "Книга не найдена"}), 404
    data = request.get_json()
    if not data:
        logger.error("Не предоставлены данные в теле запроса")
        return jsonify({"error": "Не предоставлены данные"}), 400
    if 'title' in data:
        book['title'] = data['title']
    if 'author' in data:
        book['author'] = data['author']
    if 'year' in data:
        book['year'] = data['year']
    logger.info(f"Книга id {book_id} частично обновлена")
    return jsonify(book)

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    logger.info(f"Запрос на удаление книги id {book_id}")
    book = find_book(book_id)
    if book is None:
        logger.warning(f"Книга с id {book_id} не найдена для удаления")
        return jsonify({"error": "Книга не найдена"}), 404
    books = [b for b in books if b['id'] != book_id]
    logger.info(f"Книга id {book_id} удалена")
    return '', 204

# Новые API endpoints
@app.route('/books/stats', methods=['GET'])
def books_stats():
    """Возвращает статистику по книгам."""
    total = len(books)
    if total == 0:
        return jsonify({"total": 0, "unique_authors": 0, "avg_year": 0})
    unique_authors = len(set(book['author'] for book in books))
    avg_year = sum(book['year'] for book in books) // total  # целочисленное среднее
    return jsonify({
        "total": total,
        "unique_authors": unique_authors,
        "avg_year": avg_year
    })

@app.route('/books/search', methods=['GET'])
def search_books():
    """Поиск книг по названию или автору (параметр q)."""
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    results = [book for book in books if 
               query in book['title'].lower() or 
               query in book['author'].lower()]
    return jsonify(results)

# UI маршруты
@app.route('/ui')
def ui():
    logger.debug("Рендеринг UI главной страницы")
    return render_template('index.html')

@app.route('/ui/about')
def ui_about():
    logger.debug("Рендеринг страницы 'О проекте'")
    return render_template('about.html')

@app.route('/ui/stats')
def ui_stats():
    logger.debug("Рендеринг страницы статистики")
    return render_template('stats.html')

@app.route('/ui/search')
def ui_search():
    logger.debug("Рендеринг страницы поиска")
    return render_template('search.html')

if __name__ == '__main__':
    logger.info("Запуск сервера на http://127.0.0.1:5000")
    app.run(debug=True)