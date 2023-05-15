from flask import Flask, render_template,request,redirect,url_for,flash
from flask_mysqldb import MySQL

app = Flask (__name__)

#coneccion a MYSQl
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'micondominio'
mysql = MySQL(app)

#settings
app.secret_key = 'mysecretkey'

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM reservas')
    data = cur.fetchall()
    return render_template('index.html', reservas =data)

@app.route('/add_reserva', methods= ['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form ['nombre']
        tipo = request.form ['tipo']
        fecha = request.form ['fecha']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO reservas (nombre_reserva, tipo_reserva, fecha_reserva) VALUES(%s, %s, %s)',
                    (nombre,tipo,fecha))
        mysql.connection.commit()
        flash('SE HIZO LA RESERVA EXITOSAMENTE ')
        return redirect( url_for('Index'))   

@app.route('/edit/<id>')
def get_reserva (id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM reservas WHERE id_reservas = %s', (id,))
    data = cur.fetchall()
    return render_template('edit-reservas.html', reserva = data[0])

@app.route('/update/<id>', methods = ['POST'])
def update_reserva(id):
    if request.method == 'POST':
        nombre =request.form['nombre']
        tipo =request.form['tipo']
        fecha =request.form['fecha']
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE reservas 
        SET nombre_reserva = %s,
            tipo_reserva = %s,
            fecha_reserva =%s
        WHERE id_reservas = %s
    """, (nombre, tipo, fecha, id ))
    mysql.connection.commit()
    flash('LA RESERVA SE ACTUALIZO CORRECTAMENTE')
    return redirect(url_for('Index'))

@app.route('/delete/<string:id>')
def delete_reserva(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM reservas WHERE id_reservas = {0}'.format(id))
    mysql.connection.commit()
    flash('Reserva eliminada correctamente')
    return redirect(url_for('Index'))


if __name__ == '__main__':
    app.run(port=3000, debug= True )