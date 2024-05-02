from flask import Flask, Blueprint, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI

# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Настройки подключения к базе данных MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Определение моделей
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Text)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    quantity = db.Column(db.Integer)

# Создаем Blueprint
bp = Blueprint('main', __name__)

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


# Определяем маршрут и представление для обновления количества товара
@bp.route('/update_quantity', methods=['POST'])
def update_quantity():
    data = request.form
    product_id = data.get('productId')
    new_quantity = data.get('newQuantity')
    location_id = data.get('updateLocation')  # Получаем ID выбранной локации

    # Проверяем, что все необходимые данные были предоставлены
    if not all([product_id, new_quantity, location_id]):
        return jsonify({'error': 'Missing data'})

    # Находим запись в инвентаре по идентификатору продукта и локации
    inventory_item = Inventory.query.filter_by(product_id=product_id, location_id=location_id).first()
    if inventory_item:
        # Обновляем количество товара
        inventory_item.quantity = new_quantity
        db.session.commit()
        return jsonify({'message': 'Quantity updated successfully'})
    else:
        return jsonify({'error': 'Inventory item not found'})

# Регистрируем Blueprint в приложении Flask
app.register_blueprint(bp)

# Регистрация маршрута и представления
@app.route('/')
def index():
    # Получаем данные из базы данных с помощью объединения таблиц
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
        'quantity': inventory.quantity
    } for inventory, product, location in inventory_data]

    locations = Location.query.all()

    # Передаем данные в шаблон
    return render_template('index.html', inventory=inventory, locations=locations)

if __name__ == '__main__':
    # Создаем все таблицы, определенные в моделях
    with app.app_context():
        db.create_all()

    # Запуск приложения Flask
    app.run(debug=True)
