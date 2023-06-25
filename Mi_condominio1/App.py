from flask import Flask, render_template,request,redirect,url_for,flash,jsonify
from flask_mysqldb import MySQL
import smtplib
import urllib.parse
from twilio.rest import Client


app = Flask (__name__)




#conexion a MYSQl
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'micondominio'
mysql = MySQL(app)

#class Reserva(mysql.Model):
#    id_reservas = mysql.column(mysql.Integer,Primary_key=True)
#    nombre_reserva = mysql.column(mysql.String(255))
#    tipo_reserva = mysql.column(mysql.String(255))
#    fecha_reserva = mysql.column(mysql.Date)
#
#    def __init_(self,nombre_reserva,tipo_reserva,fecha_reserva):

account_sid = 'AC18714923d9038c7e19ff885aebdf7c1c'
auth_token = '0cb61f831d985b26c812b73ef378e8cf'
twilio_phone_number = '+13613145412'

client = Client(account_sid, auth_token)
    

#settings
app.secret_key = 'mysecretkey'


@app.route('/email')
def home():
    return render_template('wsp.html')

@app.route('/enviar_whatsapp', methods=['POST'])
def enviar_whatsapp():
    phone_number = request.form['phone']
    message = request.form['message']

    try:
        message = client.messages.create(
            from_=twilio_phone_number,
            body=message,
            to='whatsapp:' + phone_number
        )
        return 'Mensaje de WhatsApp enviado exitosamente.'
    except Exception as e:
        return 'Error al enviar el mensaje de WhatsApp: ' + str(e)
    
#obteniendo el get My Project 77120 
@app.route('/reservas', methods=['GET'])
def obtener_reservas():
    # Prepara la consulta SQL
    consulta = "SELECT * FROM reservas"

    # Ejecuta la consulta
    cursor = mysql.connection.cursor()
    cursor.execute(consulta)

    # Obtiene todas las filas resultantes de la consulta
    resultados = cursor.fetchall()

    # Transforma los resultados en una lista de diccionarios
    reservas = []
    total = 0
    for fila in resultados:
        reserva = {
            'id_reserva': fila[0],
            'nombre_reserva': fila[1],
            'tipo_reserva': fila[2],
            'fecha_reserva': fila[3],
            'precio_reserva': fila[4]
        }
        reservas.append(reserva)
        total += fila[4]

    # Crea un diccionario con los precios para cada tipo de reserva
    precios = {
        'Quincho': 100000,
        'Sala de eventos': 200000,
        'piscina': 50000
    }

    # Actualiza los precios de las reservas en base al diccionario de precios
    for reserva in reservas:
        tipo_reserva = reserva['tipo_reserva']
        if tipo_reserva in precios:
            reserva['precio_reserva'] = precios[tipo_reserva]

    # Cierra el cursor
    cursor.close()

    # Renderiza la plantilla HTML 'consulta.html' con los datos de las reservas y el total
    return render_template('consulta.html', reservas=reservas, total=total)
    #return jsonify({'reservas':reservas, 'total':total})
#@app.route('/reservas',methods=['GET'])
#def obtener_datos():
#    try:
#        cur = mysql.connection.cursor()
#        sql = "SELECT * FROM reservas"
#        cur.execute(sql)
#        datos=cur.fetchall()
#        reservas = []
#        for fila in datos:
#            reserva= {'id_reservas':fila[0],'nombre_reserva':fila[1],'tipo_reserva':fila[2],'fecha_reserva':fila[3],
#                    'precio_reserva':fila[4]}
#        
#            reservas.append(reserva)
#        #return jsonify({'reservas':reservas,'mensaje':"cursos listados"})
#        return render_template('consulta.html',reservas =datos)
#    except Exception as ex:
#        return jsonify({'mensaje':"Error"})
    
@app.route('/reservas/<id>',methods=['GET'])
def leer_reserva(id):
    try:
        cur = mysql.connection.cursor()
        sql = "SELECT * FROM reservas where id_reservas = {0}".format(id)
        cur.execute(sql)
        datos=cur.fetchone()
        if datos != None:
            reserva= {'id_reservas':datos[0],'nombre_reserva':datos[1],'tipo_reserva':datos[2],'fecha_reserva':datos[3]}
            return jsonify({'reserva':reserva,'mensaje':"reserva encontrada"})
        else:
            return jsonify({'mensaje':"Reserva no encontrada"})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})
    

@app.route('/reservas',methods=['POST'])   
def registrar_reserva():
    #print(request.json)
    try:
        cur = mysql.connection.cursor()
        sql = """INSERT INTO reservas(id_reservas, nombre_reserva, tipo_reserva, fecha_reserva)
             VALUES ('{0}', '{1}', '{2}', '{3}')""".format(request.json['id_reservas'],
            request.json['nombre_reserva'], request.json['tipo_reserva'], request.json['fecha_reserva'])
        cur.execute(sql)
        mysql.connection.commit()#confirma la accion que estamos haciendo 
        return jsonify({'mensaje':"Reserva registrada"})
    except Exception as ex:
        return jsonify({'mensaje':"Reserva no encontrada"})


@app.route('/reservas/<id>',methods=['DELETE'])   
def eliminar_reserva(id):
    try:
        cur = mysql.connection.cursor()
        sql = "DELETE FROM reservas where id_reservas = {0}".format(id)
        cur.execute(sql)
        mysql.connection.commit()#confirma la accion que estamos haciendo 
        return jsonify({'mensaje':"Reserva Eliminada"})
    except Exception as ex:
            return jsonify({'mensaje':"Error"})

#api datos 
#@app.route('/api/datos')
#def obtener_datos():
#    print('Se ha llamado a la función obtener_datos()')  # Mensaje de prueba
#    cur = mysql.connection.cursor()
#    cur.execute("SELECT * FROM reservas")
#    datos2 = cur.fetchall()
#    resultados = []
#    for fila in datos2:
#        resultado = {
#            'nombre_reserva': fila[0],
#            'tipo_reserva': fila[1],
#            'fecha_reserva': fila[2]
#        }
#        resultados.append(resultado)
#    cur.close()
#    mysql.connection.close()
#    return jsonify(resultados)


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
def get_reserva(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM reservas WHERE id_reservas = %s', (id,))
    data = cur.fetchone()
    cur.close()
    return render_template('edit-reservas.html', reserva=data)

@app.route('/update/<id>', methods=['POST'])
def update_reserva(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        fecha = request.form['fecha']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE reservas 
            SET nombre_reserva = %s,
                tipo_reserva = %s,
                fecha_reserva = %s
            WHERE id_reservas = %s
        """, (nombre, tipo, fecha, id))
        mysql.connection.commit()
        cur.close()
        flash('La reserva se ha actualizado correctamente', 'success')
        return redirect(url_for('obtener_reservas'))

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