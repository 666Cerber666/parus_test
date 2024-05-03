from flask import Blueprint, render_template, request, jsonify
from models import db, Product, Location, Inventory

bp = Blueprint('main', __name__)

# Здесь поместите все ваши маршруты и представления, которые были в вашем приложении Flask

# Маршруты и представления
# =============================================================================

# Определяем маршрут и представление для добавления товара
@bp.route('/add_product', methods=['POST'])
def add_product():
    data = request.form
    product_name = data.get('productName')
    product_description = data.get('productDescription')
    product_price = data.get('productPrice')
    location_id = data.get('productLocation')  # Получаем ID выбранной локации

    # Проверяем, что все необходимые данные были предоставлены
    if not all([product_name, product_description, product_price, location_id]):
        return jsonify({'error': 'Missing data'})

    # Создаем новый продукт
    new_product = Product(name=product_name, description=product_description, price=product_price)
    db.session.add(new_product)
    db.session.commit()

    # Создаем запись в инвентаре для нового продукта на выбранной локации
    new_inventory_item = Inventory(product_id=new_product.id, location_id=location_id, quantity=0)  # Изначальное количество товара - 0
    db.session.add(new_inventory_item)
    db.session.commit()

    return jsonify({'message': 'Product added successfully'})

# Определяем маршрут и представление для добавления локации
@bp.route('/add_location', methods=['POST'])
def add_location():
    location_name = request.form.get('locationName')

    # Проверяем, что имя локации было предоставлено
    if not location_name:
        return jsonify({'error': 'Missing location name'})

    # Создаем новую локацию
    new_location = Location(name=location_name)
    db.session.add(new_location)
    db.session.commit()

    return jsonify({'message': 'Location added successfully'})

@bp.route('/delete_product', methods=['POST'])
def delete_product():
    # Получите ID продукта из данных запроса
    product_id = request.json.get('productId')

    # Проверьте, предоставлен ли ID продукта
    if not product_id:
        return jsonify({'error': 'Отсутствует ID продукта'}), 400  # Верните ошибку 400 Bad Request, если ID продукта отсутствует

    # Найдите продукт в базе данных по его ID
    product = Product.query.get(product_id)

    # Проверьте, существует ли продукт
    if not product:
        return jsonify({'error': 'Продукт не найден'}), 404  # Верните ошибку 404 Not Found, если продукт не существует

    # Удалите все записи инвентаря, связанные с удаляемым продуктом
    Inventory.query.filter_by(product_id=product_id).delete()
    db.session.commit()

    # Удалите продукт из базы данных
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Продукт и связанные с ним записи инвентаря успешно удалены'}), 200  # Верните сообщение об успешном удалении с кодом состояния 200 OK

@bp.route('/search_product', methods=['POST'])
def search_product():
    search_term = request.json.get('searchTerm')

    # Проверяем, предоставлен ли поисковый запрос
    if not search_term:
        # Выполняем запрос для получения всей таблицы инвентаря
        inventory_data = db.session.query(Inventory, Product, Location).\
            join(Product, Inventory.product_id == Product.id).\
            join(Location, Inventory.location_id == Location.id).\
            all()
    else:
        # Выполняем поиск товаров по названию в базе данных
        inventory_data = db.session.query(Inventory, Product, Location).\
            join(Product, Inventory.product_id == Product.id).\
            join(Location, Inventory.location_id == Location.id).\
            filter(Product.name.ilike(f"%{search_term}%")).\
            all()

    # Преобразуем данные в формат JSON с помощью jsonify
    inventory = [{
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'location': location.name,
        'quantity': inventory.quantity,
        'product_id': inventory.product_id,
        'location_id': inventory.location_id
    } for inventory, product, location in inventory_data]

    # Возвращаем данные в формате JSON
    return jsonify(inventory)

# Определяем маршрут и представление для фильтрации по выбранной локации
@bp.route('/filter_by_location', methods=['POST'])
def filter_by_location():
    data = request.json
    location_id = data.get('locationId')

    if not location_id:
       # Выполняем запрос для получения всей таблицы инвентаря
        inventory_data = db.session.query(Inventory, Product, Location).\
            join(Product, Inventory.product_id == Product.id).\
            join(Location, Inventory.location_id == Location.id).\
            all()
    else:
        # В противном случае, получаем данные с фильтрацией по выбранной локации
        inventory_data = db.session.query(Inventory, Product, Location).\
            join(Product, Inventory.product_id == Product.id).\
            join(Location, Inventory.location_id == Location.id).\
            filter(Location.id == location_id).\
            all()


    # Преобразуем данные в формат, который передадим в ответе JSON
    filtered_inventory = [{
         'name': product.name,
        'description': product.description,
        'price': product.price,
        'location': location.name,
        'quantity': inventory.quantity,
        'product_id': inventory.product_id,
        'location_id': inventory.location_id
    } for inventory, product, location in inventory_data]

    # Отправляем отфильтрованные данные в формате JSON
    return jsonify(filtered_inventory)

@bp.route('/sort_by_field', methods=['POST'])
def sort_by_field():
    data = request.json
    order = data.get('order')
    sortField = data.get('sortField')  # Получаем sortField из данных запроса

    # Проверяем, присутствует ли sortField в списке допустимых полей
    valid_sort_fields = ["price", "quantity", "name", "description"]
    if sortField not in valid_sort_fields:
        return jsonify({'error': 'Недопустимое поле сортировки'}), 400

    # Определяем поле сортировки и направление сортировки
    if sortField == "price":
        field_to_sort = Product.price
    elif sortField == "quantity":
        field_to_sort = Inventory.quantity
    elif sortField == "name":
        field_to_sort = Product.name
    elif sortField == "description":
        field_to_sort = Product.description

    # Выполняем запрос сортировки
    if order == "asc":
        sorted_inventory_data = db.session.query(Inventory, Product).join(Product, Inventory.product_id == Product.id).order_by(field_to_sort).all()
    elif order == "desc":
        sorted_inventory_data = db.session.query(Inventory, Product).join(Product, Inventory.product_id == Product.id).order_by(field_to_sort.desc()).all()

    # Преобразуем данные в формат, который передадим в ответе JSON
    sorted_inventory = [{
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'location': Location.query.get(item.location_id).name,
        'quantity': item.quantity,
        'product_id': item.product_id,
        'location_id': item.location_id
    } for item, product in sorted_inventory_data]

    return jsonify(sorted_inventory)











