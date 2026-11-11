from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eletro_kurumin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELOS (BANCO DE DADOS) =================
class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class Categoria(db.Model):
    id_categoria = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))

class Componente(db.Model):
    id_componente = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255))
    preco = db.Column(db.Float, nullable=False)
    quantidade_estoque = db.Column(db.Integer, nullable=False)

# ================= ROTAS (REQUISITOS) =================

# 1. Autenticação (Login)
@app.route('/login', methods=['POST'])
def login():
    dados = request.json
    usuario = Usuario.query.filter_by(email=dados.get('email')).first()
    if usuario and check_password_hash(usuario.senha, dados.get('senha')):
        return jsonify({"mensagem": "Login realizado com sucesso", "id_usuario": usuario.id_usuario}), 200
    return jsonify({"erro": "Credenciais inválidas"}), 401

# 2. Gestão de Componentes (CRUD)
@app.route('/componentes', methods=['POST'])
def criar_componente():
    dados = request.json
    novo_comp = Componente(
        id_categoria=dados['id_categoria'],
        id_usuario=dados['id_usuario'],
        nome=dados['nome'],
        descricao=dados['descricao'],
        preco=dados['preco'],
        quantidade_estoque=dados['quantidade_estoque']
    )
    db.session.add(novo_comp)
    db.session.commit()
    return jsonify({"mensagem": "Componente registado com sucesso"}), 201

@app.route('/componentes', methods=['GET'])
def listar_componentes():
    componentes = Componente.query.all()
    resultado = [{"id": c.id_componente, "nome": c.nome, "preco": c.preco, "estoque": c.quantidade_estoque} for c in componentes]
    return jsonify(resultado), 200

@app.route('/componentes/<int:id>', methods=['PUT'])
def editar_componente(id):
    dados = request.json
    componente = Componente.query.get_or_404(id)
    componente.nome = dados.get('nome', componente.nome)
    componente.preco = dados.get('preco', componente.preco)
    componente.quantidade_estoque = dados.get('quantidade_estoque', componente.quantidade_estoque)
    db.session.commit()
    return jsonify({"mensagem": "Componente atualizado com sucesso"}), 200

@app.route('/componentes/<int:id>', methods=['DELETE'])
def eliminar_componente(id):
    componente = Componente.query.get_or_404(id)
    db.session.delete(componente)
    db.session.commit()
    return jsonify({"mensagem": "Componente eliminado com sucesso"}), 200

# 3. Relatórios
@app.route('/relatorio', methods=['GET'])
def relatorio_estoque():
    componentes = Componente.query.all()
    detalhes = []
    valor_total_estoque = 0

    for c in componentes:
        valor_item = c.preco * c.quantidade_estoque
        valor_total_estoque += valor_item
        detalhes.append({
            "nome": c.nome,
            "quantidade": c.quantidade_estoque,
            "preco_unitario": c.preco,
            "valor_total_item": valor_item
        })

    return jsonify({
        "componentes_registados": detalhes,
        "valor_total_estoque": valor_total_estoque
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Cria o banco de dados e as tabelas automaticamente
    app.run(debug=True)