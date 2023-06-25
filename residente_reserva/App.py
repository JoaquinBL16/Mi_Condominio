from flask import Flask, render_template,request,redirect,url_for,flash,jsonify,session
from flask_mysqldb import MySQL
from flask_session import Session
from flask_cors import CORS
import requests
import json
import paypalrestsdk

app = Flask (__name__)


app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AUpn-5NF8EYtrDCngmhuj_BoIvrBmGwdwY1WNeVg4y7SZz3UAAeTmLapWIbtsMFgt1bZesWbjD_4PkCV",
  "client_secret": "EH043BMufzQUmfgIoRgSvqqNjL4N9o-WqqEFlDPaVhKqbaqYv3QFr537TPR4fbIDJIGL8bnewo6BICES" })

#conexion a MYSQl
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'micondominio'
mysql = MySQL(app)



#settings
app.secret_key = 'mysecretkey'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_reserva = request.form['nombre_reserva']
        
        # Verificar si el usuario es administrador
        if nombre_reserva == 'administrador':
            # Almacenar los datos de administrador en la sesión
            session['nombre_reserva'] = nombre_reserva
            session['es_administrador'] = True
            
            # Redirigir a la página de reservas para administrador
            return redirect(url_for('obtener_reservas'))
        
        # Verificar si el nombre de reserva existe en la base de datos
        cursor = mysql.connection.cursor()
        consulta = "SELECT COUNT(*) FROM reservas WHERE nombre_reserva = %s"
        cursor.execute(consulta, (nombre_reserva,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Almacenar los datos de reserva en la sesión
            session['nombre_reserva'] = nombre_reserva
            session['es_administrador'] = False
            
            # Redirigir a la página de reservas para usuarios normales
            return redirect(url_for('obtener_reservas'))
        
        # Si no se cumple ninguna condición, mostrar mensaje de error
        error_message = "Nombre de reserva no válido. Por favor, intente nuevamente."
        return render_template('login.html', error_message=error_message)
    
    # Si es una solicitud GET, mostrar el formulario de inicio de sesión
    return render_template('login.html')


@app.route('/logout')
def logout():
    # Eliminar el nombre de reserva de la sesión al cerrar sesión
    session.pop('nombre_reserva', None)
    return redirect(url_for('login'))

    
@app.route('/reservass', methods=['GET'])
def obtener_reservas():
    if 'nombre_reserva' in session:
        nombre_reserva = session['nombre_reserva']
        
        if session['es_administrador']:
            consulta = "SELECT * FROM reservas"
            cursor = mysql.connection.cursor()
            cursor.execute(consulta)
            resultados = cursor.fetchall()
            cursor.close()
            
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
            
            precios = {
                'Quincho': 100000,
                'Sala de eventos': 200000,
                'piscina': 50000
            }
            
            for reserva in reservas:
                tipo_reserva = reserva['tipo_reserva']
                if tipo_reserva in precios:
                    reserva['precio_reserva'] = precios[tipo_reserva]
            
            return render_template('admin_reservas.html', reservas=reservas, total=total)
        else:
            consulta = "SELECT * FROM reservas WHERE nombre_reserva = %s"
            cursor = mysql.connection.cursor()
            cursor.execute(consulta, (nombre_reserva,))
            resultados = cursor.fetchall()
            cursor.close()
            
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
            
            precios = {
                'Quincho': 100000,
                'Sala de eventos': 200000,
                'piscina': 50000
            }
        # Calcula el total
        # Actualiza los precios de las reservas en base al diccionario de precios
        for reserva in reservas:
            tipo_reserva = reserva['tipo_reserva']
            if tipo_reserva in precios:
                reserva['precio_reserva'] = precios[tipo_reserva]
        total = sum(reserva['precio_reserva'] for reserva in reservas)
        # Cierra el cursor
        cursor.close()
        # Renderiza la plantilla HTML 'consulta.html' con los datos de las reservas y el total
        return render_template('consulta.html', reservas=reservas, total=total)
        #return jsonify({'reservas':reservas, 'total':total})
    return redirect(url_for('login'))

#@app.route('/reservass', methods=['GET'])
#def obtener_reservas():
#    # Verificar si el usuario ha iniciado sesión como residente
#    if 'nombre_reserva' in session and session['nombre_reserva']:
#        nombre_reserva = session['nombre_reserva']
#        
#        # Prepara la consulta SQL
#        consulta = "SELECT * FROM reservas WHERE nombre_reserva = %s"
#        
#        # Ejecuta la consulta con el nombre de la persona como parámetro
#        cursor = mysql.connection.cursor()
#        cursor.execute(consulta, (nombre_reserva,))
#        
#        # Obtiene todas las filas resultantes de la consulta
#        # Obtiene todas las filas resultantes de la consulta
#        resultados = cursor.fetchall()
#    
#        # Transforma los resultados en una lista de diccionarios
#        reservas = []
#        total = 0
#        for fila in resultados:
#            reserva = {
#                'id_reserva': fila[0],
#                'nombre_reserva': fila[1],
#                'tipo_reserva': fila[2],
#                'fecha_reserva': fila[3],
#                'precio_reserva': fila[4]
#            }
#            reservas.append(reserva)
#            total += fila[4]
#    
#        # Crea un diccionario con los precios para cada tipo de reserva
#        precios = {
#            'Quincho': 100000,
#            'Sala de eventos': 200000,
#            'piscina': 50000
#        }
#        # Calcula el total
#        
#        # Actualiza los precios de las reservas en base al diccionario de precios
#        for reserva in reservas:
#            tipo_reserva = reserva['tipo_reserva']
#            if tipo_reserva in precios:
#                reserva['precio_reserva'] = precios[tipo_reserva]
#        total = sum(reserva['precio_reserva'] for reserva in reservas)
#        # Cierra el cursor
#        cursor.close()
#    
#        # Renderiza la plantilla HTML 'consulta.html' con los datos de las reservas y el total
#        return render_template('consulta.html', reservas=reservas, total=total)
#        #return jsonify({'reservas':reservas, 'total':total})
#    
#    else:
#        # El usuario no ha iniciado sesión, redirigir al formulario de inicio de sesión
#        return redirect(url_for('login'))


@app.route('/payment', methods=['POST'])
def payment():
    reservas = [
        {
            "fecha_reserva": "Fri, 26 May 2023 00:00:00 GMT",
            "id_reserva": 2667,
            "nombre_reserva": "felipe",
            "precio_reserva": 50,
            "tipo_reserva": "piscina"
        },
        {
            "fecha_reserva": "Fri, 02 Jun 2023 00:00:00 GMT",
            "id_reserva": 2668,
            "nombre_reserva": "felipe",
            "precio_reserva": 100,
            "tipo_reserva": "Quincho"
        },
        {
            "fecha_reserva": "Sat, 01 Jul 2023 00:00:00 GMT",
            "id_reserva": 2696,
            "nombre_reserva": "felipe",
            "precio_reserva": 50,
            "tipo_reserva": "piscina"
        }
    ]

    total = sum(reserva["precio_reserva"] for reserva in reservas)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://localhost:3001/payment/execute",
            "cancel_url": "http://localhost:3001/"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Total De Reserva",
                    "sku": "12345",
                    "price": str(total),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(total),
                "currency": "USD"
            },
            "description": "This is the payment transaction description."
        }]
    })

    if payment.create():
        print('Payment success!')
    else:
        print(payment.error)

    return jsonify({'paymentID': payment.id})

@app.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id': request.form['payerID']}):
        success = True

    return jsonify({'success' : success})

#obteniendo el get 
@app.route('/reservas',methods=['GET'])
def obtener_datos():
    try:
        cur = mysql.connection.cursor()
        sql = "SELECT * FROM reservas"
        cur.execute(sql)
        datos=cur.fetchall()
        reservas = []
        for fila in datos:
            reserva= {'id_reservas':fila[0],'nombre_reserva':fila[1],'tipo_reserva':fila[2],'fecha_reserva':fila[3]}
            reservas.append(reserva)
        #return jsonify({'reservas':reservas,'mensaje':"cursos listados"})
        return render_template('consulta.html',reservas =datos)
    except Exception as ex:
        return jsonify({'mensaje':"Error"})

    
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
@app.route('/reservas/<nombre>')
def mostrar_reservas(nombre):
    # Crear un cursor para interactuar con la base de datos
    cur = mysql.connection.cursor()

    # Obtener las reservas del residente específico
    query = "SELECT * FROM reservas WHERE nombre_reserva = %s"
    cur.execute(query, (nombre,))
    data = cur.fetchall()

    # Cerrar el cursor
    cur.close()

    # Pasar los datos de las reservas a la plantilla para mostrarlos
    return render_template('consulta.html', reservas=data)    

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

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM reservas')
    data = cur.fetchall()
    return render_template('login.html', reservas =data)

@app.route('/generar_reserva')
def generar_reserva():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM reservas')
    data = cur.fetchall()
    return render_template('index.html', reservas =data)

@app.route('/add_reserva', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        fecha = request.form['fecha']
        
        # Obtén el precio correspondiente al tipo de reserva desde el diccionario de precios
        precios = {
            'Quincho': 100000,
            'Sala de eventos': 200000,
            'piscina': 50000
        }
        
        if tipo in precios:
            precio = precios[tipo]
        else:
            # Si el tipo de reserva no está en el diccionario de precios, muestra un mensaje de error
            mensaje_error = "Tipo de reserva inválido"
            return render_template('index.html', error=mensaje_error)
        
        cur = mysql.connection.cursor()
        
        # Verifica si la fecha ya está reservada
        query = "SELECT COUNT(*) FROM reservas WHERE fecha_reserva = %s"
        cur.execute(query, (fecha,))
        count = cur.fetchone()[0]

        if count > 0:
            # Si la fecha ya está reservada, mostrar un mensaje de error
            mensaje_error = "La fecha seleccionada ya está reservada. Por favor, elige otra fecha."
            return render_template('index.html', error=mensaje_error)

        # Insertar los datos en la tabla de reservas con el precio correspondiente
        cur.execute('INSERT INTO reservas (nombre_reserva, tipo_reserva, fecha_reserva, precio_reserva) VALUES(%s, %s, %s, %s)',
                    (nombre, tipo, fecha, precio))
        mysql.connection.commit()
        cur.close()
        
        flash('SE HIZO LA RESERVA EXITOSAMENTE')
        return redirect(url_for('generar_reserva'))

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

    return redirect(url_for('generar_reserva'))

if __name__ == '__main__':
    app.run(port=3001, debug= True )