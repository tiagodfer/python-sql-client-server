from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/connectSuccess', methods=['POST'])
@cross_origin()  # This enables CORS for this specific route
def connect_success():
    # Your route logic
    return "Success message"

@app.route("/get-person-by-name/<name>")
@cross_origin()  # This enables CORS for this specific route
def get_person_by_name(name):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/basecpf.db')
    print('conn_cpf', conn_cpf)
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    cursor_cpf.execute("SELECT * FROM cpf WHERE nome LIKE UPPER(?)", ('%' + name + '%',))
    results = cursor_cpf.fetchall()
    if results:
        cpf_list = []
        for row in results:
            cpf_info = {
                'cpf': row[0],
                'nome': row[1],
                'sexo': row[2],
                'nasc': row[3]
            }
            cpf_list.append(cpf_info)
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'Nome não encontrado'}), 404

@app.route("/get-person-by-exact-name/<name>")
@cross_origin()  # This enables CORS for this specific route
def get_person_by_exact_name(name):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/basecpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    cursor_cpf.execute("SELECT * FROM cpf WHERE nome = UPPER(?)", (name,))
    results = cursor_cpf.fetchall()
    if results:
        cpf_list = []
        for row in results:
            cpf_info = {
                'cpf': row[0],
                'nome': row[1],
                'sexo': row[2],
                'nasc': row[3]
            }
            cpf_list.append(cpf_info)
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'Nome não encontrado'}), 404

@app.route("/get-person-by-cpf/<cpf>", methods=['GET'])
@cross_origin()  # This enables CORS for this specific route
def get_person_by_cpf(cpf):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/basecpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    cursor_cpf.execute("SELECT * FROM cpf WHERE cpf = ?", (cpf,))
    results = cursor_cpf.fetchall()
    if results:
        cpf_list = []
        for row in results:
            cpf_info = {
                'cpf': row[0],
                'nome': row[1],
                'sexo': row[2],
                'nasc': row[3]
            }
            cpf_list.append(cpf_info)
            print(cpf_list)
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'CPF não encontrado'}), 404

@app.route("/get-person-cnpj-by-name/<name>")
@cross_origin()  # This enables CORS for this specific route
def get_person_cnpj_by_name(name):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/basecpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    cursor_cnpj.execute("SELECT * FROM socios WHERE nome LIKE UPPER(?)", ('%' + name + '%',))
    results = cursor_cnpj.fetchall()
    if results:
        cpf_list = []
        for row in results:
            cpf_info = {
                'cpf': row[3],
                'nome': row[2],
            }
            cpf_list.append(cpf_info)
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'Nome não encontrado'}), 404

@app.route("/get-person-cnpj-by-name-cpf/<name>-<cpf>")
@cross_origin()  # This enables CORS for this specific route
def get_person_cnpj_by_cpf(name, cpf):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/basecpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    cursor_cnpj.execute("SELECT * FROM socios WHERE representante_legal LIKE ? AND nome_representante LIKE ?", ('%' + cpf[3:9] + '%', '%' + name + '%',))
    results = cursor_cnpj.fetchall()
    if results:
        cpf_list = []
        for row in results:
            cpf_info = {
                'nome fantasia': row[2],
                'nome': row[8],
                'cpf': row[7]
            }
            cpf_list.append(cpf_info)
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'Não é sócio de nenhuma empresa'}), 404

@app.route("/get-person-cnpj-by-name-cpf-radical/<name>-<cpf>")
def get_person_cnpj_by_cpf_radical(name, cpf):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/basecpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    cursor_cnpj.execute("SELECT * FROM socios WHERE cpf_cnpj LIKE ? AND nome LIKE ?", ('%' + cpf[3:9] + '%', '%' + name + '%',))
    results = cursor_cnpj.fetchall()
    if results:
        cpf_list = []
        for row in results:
            cpf_info = {
                '0 - cpf': row[3],
                '0 - nome': row[2],
            }
            cpf_list.append(cpf_info)
            cursor_cnpj.execute("SELECT * FROM estabelecimentos WHERE radical = ?", (row[0],))
            results = cursor_cnpj.fetchall()
            num_empresa = 0
            if results:
                for row in results:
                    num_empresa += 1
                    key = f'{num_empresa} nome fantasia'
                    key2 = f'{num_empresa} rua'
                    key3 = f'{num_empresa} num'
                    key4 = f'{num_empresa} estado'
                    cpf_info[key] = row[4]
                    cpf_info[key2] = row[14]
                    cpf_info[key3] = row[15]
                    cpf_info[key4] = row[19]
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'Não é sócio de nenhuma empresa'}), 404

@app.after_request
def after_request(response):
    print("Status:", response.status)
    print("Headers:", response.headers)
    print("Response data:", response.get_data(as_text=True))
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
