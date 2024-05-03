from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import db
from routes import bp as main_bp
from config import SQLALCHEMY_DATABASE_URI

# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Настройки подключения к базе данных MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализируем SQLAlchemy с помощью нашего приложения Flask
db.init_app(app)

# Регистрируем Blueprint в приложении Flask
app.register_blueprint(main_bp)

# Создание таблиц в базе данных
with app.app_context():
    db.create_all()

# Регистрация маршрута и представления
@app.route('/')
def index():
    from models import Inventory, Product, Location
    # Получаем данные из базы данных без фильтрации по локации
    inventory_data = db.session.query(Inventory, Product, Location).\
        join(Product, Inventory.product_id == Product.id).\
        join(Location, Inventory.location_id == Location.id).\
        all()

    # Преобразуем данные в формат, который передадим в шаблон
    inventory = [{
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'location': location.name,
        'quantity': inventory.quantity,
        'product_id': inventory.product_id,
        'location_id': inventory.location_id
    } for inventory, product, location in inventory_data]

    locations = Location.query.all()

    # Передаем данные в шаблон
    return render_template('index.html', inventory=inventory, locations=locations)

@app.route('/data', methods=['GET'])
def get_data():
    from models import Inventory, Product, Location
    # Получаем данные из базы данных без фильтрации по локации
    inventory_data = db.session.query(Inventory, Product, Location).\
        join(Product, Inventory.product_id == Product.id).\
        join(Location, Inventory.location_id == Location.id).\
        all()

    # Преобразуем данные в список словарей
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

# Определяем маршрут и представление для обновления количества товара
@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    from models import Inventory  # Импортируем здесь, чтобы избежать циклического импорта
    data = request.json
    product_id = data.get('productId')
    new_quantity = data.get('newQuantity')
    location_id = data.get('locationId') 

    # Проверяем, что все необходимые данные были предоставлены
    if not all([product_id, new_quantity, location_id]):
        return jsonify({'error': 'Missing data'}), 400  # Возвращаем статус 400 Bad Request

    # Находим запись в инвентаре по идентификатору продукта и локации
    inventory_item = Inventory.query.filter_by(product_id=product_id, location_id=location_id).first()
    if inventory_item:
        # Обновляем количество товара
        inventory_item.quantity = new_quantity
        db.session.commit()
        return jsonify({'message': 'Quantity updated successfully'}), 200  # Возвращаем статус 200 OK
    else:
        return jsonify({'error': 'Inventory item not found'}), 404  # Возвращаем статус 404 Not Found
    
# Запуск приложения Flask
if __name__ == '__main__':
    app.run(debug=True)
