import pytest
import json
from app import app  # импортируем само Flask-приложение

@pytest.fixture
def client():
    """Создаём тестовый клиент для приложения."""
    with app.test_client() as client:
        yield client

def test_index(client):
    """Проверка главной страницы."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data

def test_get_books(client):
    """Получение списка книг."""
    response = client.get('/books')
    assert response.status_code == 200
    books = json.loads(response.data)
    assert isinstance(books, list)
    # Проверяем, что есть как минимум две начальные книги
    assert len(books) >= 2

def test_get_book_by_id(client):
    """Получение конкретной книги (id=1)."""
    response = client.get('/books/1')
    assert response.status_code == 200
    book = json.loads(response.data)
    assert book['id'] == 1
    assert book['title'] == "Война и мир"

def test_get_book_not_found(client):
    """Запрос несуществующей книги должен вернуть 404."""
    response = client.get('/books/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data

def test_create_book(client):
    """Создание новой книги."""
    new_book = {
        "title": "Тестовая книга",
        "author": "Тестовый Автор",
        "year": 2024
    }
    response = client.post('/books', 
                          data=json.dumps(new_book),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['id'] == 3  # следующий id
    assert data['title'] == new_book['title']

def test_create_book_missing_field(client):
    """Попытка создать книгу без обязательного поля."""
    invalid_book = {
        "title": "Неполная книга",
        "author": "Автор"
        # нет поля year
    }
    response = client.post('/books',
                          data=json.dumps(invalid_book),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_update_book(client):
    """Полное обновление книги."""
    updated_data = {
        "title": "Обновлённое название",
        "author": "Новый автор",
        "year": 2000
    }
    response = client.put('/books/1',
                         data=json.dumps(updated_data),
                         content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == updated_data['title']
    # Проверим, что изменения действительно сохранились
    response2 = client.get('/books/1')
    data2 = json.loads(response2.data)
    assert data2['title'] == updated_data['title']

def test_patch_book(client):
    """Частичное обновление книги."""
    patch_data = {"year": 1999}
    response = client.patch('/books/1',
                           data=json.dumps(patch_data),
                           content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['year'] == 1999
    # Остальные поля не должны измениться
    assert data['title'] == "Война и мир"  # или уже обновлённый, если до этого обновляли

def test_delete_book(client):
    """Удаление книги."""
    response = client.delete('/books/2')
    assert response.status_code == 204
    # Проверяем, что книга действительно удалена
    response2 = client.get('/books/2')
    assert response2.status_code == 404