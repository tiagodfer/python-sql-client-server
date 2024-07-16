from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/get-person-by-name/<name>")
def get_person_by_name(name):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
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
def get_person_by_exact_name(name):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
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

@app.route("/get-person-by-cpf/<cpf>")
def get_person_by_cpf(cpf):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
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
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'CPF não encontrado'}), 404

@app.route("/get-person-cnpj-by-name/<name>")
def get_person_cnpj_by_name(name):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
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
def get_person_cnpj_by_cpf(name, cpf):
    conn_cnpj = sqlite3.connect('db/cnpj.db')
    conn_cpf = sqlite3.connect('db/cpf.db')
    cursor_cnpj = conn_cnpj.cursor()
    cursor_cpf = conn_cpf.cursor()
    cursor_cnpj.execute("SELECT * FROM socios WHERE cpf_cnpj LIKE ? AND nome LIKE ?", ('%' + cpf[3:9] + '%', '%' + name + '%',))
    results = cursor_cnpj.fetchall()
    if results:
        cpf_list = []
        for row in results:
            cpf_info = {
                'cpf': row[3],
                'nome': row[2],
            }
            cpf_list.append(cpf_info)
            cursor_cnpj.execute("SELECT * FROM estabelecimentos WHERE radical = ?", (row[0],))
            if results:
                cpf_info['nome fantasia'] = row[2]
        return jsonify({'results': cpf_list}), 200
    else:
        return jsonify({'error': 'Não é sócio de nenhuma empresa'}), 404

if __name__ == "__main__":
    app.run(debug=True)
