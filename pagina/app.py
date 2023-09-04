from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# Connection details
host = "127.0.0.1"
port = "5432"
user = "postgres"
password = "gauss7720"
database = "modelo_opti"

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        return connection
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    status = request.form.get('status')
    olgura = request.form.get('olgura')
    fecha = request.form.get('fecha')
    inicio = request.form.get('inicio')
    final = request.form.get('final')

    connection = get_db_connection()
    if connection is None:
        return jsonify({"status": "Error"})

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO parametros (status, olgura, fecha, inicio, final) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                       (status, olgura, fecha, inicio, final))
        new_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"status": "Success", "id": new_id})
    except psycopg2.Error as e:
        print("Error executing query:", e)
        return jsonify({"status": "Error"})

if __name__ == '__main__':
    app.run(debug=True)
