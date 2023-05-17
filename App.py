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

@app.route('/mover-datos/<string:id>')
def mover_datos(id):
    cur = mysql.connection.cursor()

    # Consultar los datos de la tabla original
    cur.execute('SELECT nombre_reserva, tipo_reserva, fecha_reserva FROM reservas WHERE id_reservas = {0}'.format(id))
    datos = cur.fetchall()

    # Insertar los datos en la nueva tabla
    for fila in datos:
        cur.execute("INSERT INTO reservas_nulas (nombre_nula, tipo_nula, fecha_nula) VALUES (%s, %s, %s)", fila)

    # Eliminar los datos de la tabla original
    cur.execute('DELETE FROM reservas WHERE id_reservas = {0}'.format(id))

    # Confirmar los cambios y cerrar la conexión
    mysql.connection.commit()
    mysql.connection.close()

    return redirect(url_for('Index'))

#@app.route('/mover-datos/<id>', methods=['POST'])
#def mover_datos():
#    cur = mysql.connection.cursor()
#    # Obtén los datos que deseas mover de la tabla original
#    cur.execute("SELECT * FROM reservas WHERE id_reservas = %s", [request.form.get('id_reservas')])
#    datos = cur.fetchall()
#
#    # Inserta los datos recuperados en la nueva tabla
#    for fila in datos:
#        cur.execute("INSERT INTO reservas_nulas (nombre_nula, tipo_nula, fecha_nula) VALUES (%s, %s, %s)", [fila[0], fila[1], fila[2]])
#
#    # Guarda los cambios en la base de datos
#    mysql.connection.commit()
#
#    # Devuelve una respuesta exitosa al cliente
#    return 'Datos movidos exitosamente'




#@app.route('/mover-datos/<string:id>')
#def mover_datos():
#    try:
#        # Crea un cursor para ejecutar las consultas
#        cur = mysql.connection.cursor()
#
#        # Ejecuta una consulta SELECT para obtener los datos que deseas modificar
#        select_query = "SELECT * FROM reservas WHERE id_reservas= {0}".format(id)
#        cur.execute(select_query)
#        datos_originales = cur.fetchall()
#
#        # Itera sobre los datos obtenidos y ejecuta las operaciones de inserción y eliminación en las tablas
#        for dato_original in datos_originales:
#            # Ejecuta una consulta INSERT para insertar los datos en la tabla de destino
#            insert_query = "INSERT INTO reservas_nulas (nombre_nula, tipo_nula, fecha_nula) VALUES (%s, %s, %s)"
#            cur.execute(insert_query, dato_original)
#
#            # Ejecuta una consulta DELETE o UPDATE para eliminar o marcar los registros que se hayan movido en la tabla original
#            delete_query = "DELETE FROM reservas WHERE id_reservas = %s"
#            cur.execute(delete_query, (dato_original[0],))  # asumiendo que el ID está en la primera columna
#
#        # Confirma los cambios realizados en la base de datos
#            mysql.connection.commit()
#
#        return 'Datos movidos correctamente'
#    except mysql.connector.Error as error:
#        # Maneja los errores de la base de datos
#        print('Error al mover los datos:', error)
#        return 'Error al mover los datos'
#    finally:
#        # Cierra la conexión a la base de datos
#        cur.close()
#        mysql.connection.close()


if __name__ == '__main__':
    app.run(port=3000, debug= True )