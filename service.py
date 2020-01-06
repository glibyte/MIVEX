#pip install flask
#pip install flask-mysql
#pip install Flask-JWT
#pip install cryptography
from flask import Flask, render_template, request, jsonify, make_response
from flaskext.mysql import MySQL
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = 'super-secret'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'mivex'
mysql = MySQL()
mysql.init_app(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

#ruta principal
@app.route('/')
def index():
    return render_template('index.html')

#ruta ragistro
@app.route('/Registro')
def registro():
    return render_template('registration.html')

#ruta productos
@app.route('/Productos')
def productos():
    cur = mysql.get_db().cursor()
    cur.execute('select * from productos')
    data = cur.fetchall()
    cur.close()
    #print(data)
    return render_template('productos.html', contact=data)

#ruta tiendas
@app.route('/Tiendas')
def tiendas():
    cur = mysql.get_db().cursor()
    cur.execute('select * from tiendas')
    data = cur.fetchall()
    cur.close()
    return render_template('tiendas.html', contact=data)

#ruta servicios
@app.route('/Servicios')
def servicios():
    cur=mysql.get_db().cursor()
    cur.execute('SELECT * FROM servicios')
    data=cur.fetchall()
    cur.close()
    return render_template('servicios.html', contact=data)

#ruta productos
@app.route('/Ofertas')
def ofertas():
    cur = mysql.get_db().cursor()
    cur.execute('select * from productos where oferta="si"')
    data = cur.fetchall()
    cur.close()
    #print(data)
    return render_template('productos.html', contact=data)

#users
@app.route('/user', methods=['GET'])
def get_all_users():
    return ''

@app.route('/user/<public_id>', methods=['GET'])
def get_one_user(public_id):
    cur = mysql.get_db().cursor()
    cur.execute('select * from users where public_id=%s;',(public_id))
    user = cur.fetchall()

    if not user:
        return jsonify({'mensaje': 'no funciona el usuario'})
    
    for n in user:
        name = n[2]
        password = n[3]
        admin_ = n[4]

    user_data = {}
    user_data['public_id'] = public_id
    user_data['name'] = name
    user_data['password'] = password
    user_data['admin_'] = admin_
    
    return jsonify({'user' : user_data})


@app.route('/user', methods=['POST'])
def create_user():

    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    public_id = str(uuid.uuid4())
    name = data['name']
    password=hashed_password
    admin_=False
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (public_id,name,password,admin_) VALUES (%s, %s, %s, %s)',
    (public_id,name,password,admin_))
    conn.commit()
    cur.close()
    return jsonify({'mensaje':'new user created!'})

@app.route('/user/<user_id>', methods=['PUT'])
def promote_user():
    return ''

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user():
    return ''

@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})
    
    cur = mysql.get_db().cursor()
    cur.execute('select * from users where name=%s;',(auth.username))
    user = cur.fetchall()
    for n in user:
        public_id = n[1]
        password = n[3]
        admin_ = n[4]

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})

    if check_password_hash(password,auth.password):
        token = jwt.encode({'public_id' : public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    
    return make_response('Could not verify', 401, {'WWW-Authenticate':'Basic realm="Login required!"'})


#Se este ejecutando la webapp
if __name__ == '__main__':
    app.run(debug=True)