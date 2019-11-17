from app import app
from flaskext.mysql import MySQL

mysql = MySQL()


# Setting up a SQL Server connection
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mimikrija1337'
app.config['MYSQL_DATABASE_DB'] = 'test'
app.config['MYSQL_DATABASE_HOST'] = '159.69.154.56'
mysql.init_app(app)