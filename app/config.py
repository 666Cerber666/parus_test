# config.py

# Параметры подключения к базе данных MySQL
MYSQL_HOST = '147.45.151.45'
MYSQL_PORT = 3306
MYSQL_USER = 'gen_user'
MYSQL_PASSWORD = 'sB$6_^Ctf4-(~{'
MYSQL_DBNAME = 'default_db'

# Строка подключения SQLAlchemy к базе данных MySQL
SQLALCHEMY_DATABASE_URI = f'mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DBNAME}'

# Отключение вывода сигналов изменений
SQLALCHEMY_TRACK_MODIFICATIONS = False
