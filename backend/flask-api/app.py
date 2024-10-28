import os
import json
import requests
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, make_response, request, session

from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import check_password_hash, generate_password_hash

from models import (GroupMessage,  # Importa o banco e as classes de modelo
                    MessageQueue, MessageTopic, TopicMembership, Friends,
                    User, FriendList, LinkQueue, db, create_triggers, 
                    and_, or_, distinct, joinedload, text)

from get_ip import get_local_ip

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração para permitir solicitações de qualquer origem
CORS(app)

socketio = SocketIO(app)
app.config['SECRET_KEY'] = os.urandom(24)

IP = get_local_ip()
API_URL = [f'http://{IP}:8080', f'http://{IP}:8081']  # A URL do seu serviço Java
BROKER_URL = f"tcp://{IP}:61616"
Flask_URL = f'http://{IP}:5000/messages'


# Inicializa o status de conexão
status = "disconnected"


# Verifica se está rodando em um ambiente Docker
if os.environ.get('DB_URL'):
    # Configuração para Docker
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL')
else:
    # Configuração para ambiente local
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')


# Inicializa o banco de dados
db.init_app(app)


with app.app_context():
    db.create_all()
    create_triggers(db)


@app.route('/test', methods=['GET'])
def test():
    return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return make_response(
            jsonify({'users': [user.json() for user in users]}), 200
        )
    except Exception as e:
        return make_response(
            jsonify({'message': f'error retrieving users: {e}'}), 500
        )

@app.route('/users/update_user', methods=['PUT'])
def update_username():
    try:
        # Verifica se o usuário está logado
        if 'user_id' not in session:
            return make_response(jsonify({'message': 'unauthorized'}), 401)
        
        user_id = session['user_id']  # ID do usuário logado
        user = User.query.filter_by(id=user_id).first()

        if user:
            data = request.get_json()
            new_username = data.get('username').upper()
            
            # Verifica se o novo nome de usuário já existe
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user and existing_user.id != user.id:
                return make_response(jsonify({'message': 'username already taken'}), 409)

            # Atualiza o nome de usuário
            user.username = new_username
            if 'password' in data:
                user.password_hash = generate_password_hash(data['password'])

            db.session.commit()
            return make_response(jsonify({'message': 'user updated'}), 200)

        return make_response(jsonify({'message': 'user not found'}), 404)

    except Exception as e:
        return make_response(jsonify({'message': 'error updating user', 'error': str(e)}), 500)


@app.route('/user/delete', methods=['POST'])  # Alterando para POST
def delete_user():
    try:
        # Verifica se o usuário está logado
        if 'id_user' not in session:
            return make_response(jsonify({'message': 'ação não autorizada faça login primeiro'}), 401)

        # Obtém os dados do corpo da requisição
        data = request.get_json()  # Obtém os dados JSON enviados no corpo da requisição
        username = data.get('username').upper()  # Obtém o nome de usuário do JSON

        if not username:  # Verifica se o nome de usuário foi fornecido
            return make_response(jsonify({'message': 'username is required'}), 400)

        if session['username'] != username:
            return make_response(jsonify({'message': 'ação não autorizada esse não é você!'}), 401)

        user = User.query.filter_by(id=session['id_user']).first()  # Busca o usuário pelo nome

        if user:
            db.session.delete(user)  # Deleta o usuário
            db.session.commit()  # Confirma a deleção
            return make_response(jsonify({'message': 'user deleted successfully'}), 200)

        return make_response(jsonify({'message': 'user not found'}), 404)

    except Exception as e:
        # Retorna um erro caso algo dê errado
        return make_response(jsonify({'message': 'error deleting user', 'error': str(e)}), 500)



def validate_user(username, password):
    try:
        user = User.query.filter_by(
            username=username
        ).first()  # Busca o usuário no banco de dados
        if user and check_password_hash(
            user.password_hash, password
        ):  # Verifica a senha
            return user  # Retorna o objeto do usuário se a senha for válida
        return None
    except Exception as e:
        raise ValueError(f"Erro na validação do usuario: {e}") 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Obtendo os dados do JSON
            data = request.get_json()

            # Verifica se os dados necessários estão presentes
            if 'username' not in data or 'password' not in data:
                return make_response(jsonify({'message': 'Username and password are required.'}), 400)

            
            # Criação do novo usuário
            new_user = User(
                username=data['username'].upper(),  # Armazenando o nome de usuário em maiúsculas
                password=data['password']  # Considerar usar hash aqui
            )
            db.session.add(new_user)
            db.session.commit()  # Commit da sessão do banco de dados

            # Atualiza a sessão do Flask para armazenar o usuário logado
            session['user_id'] = new_user.id  # Aqui você pode armazenar o ID do usuário na sessão do Flask

            flash('Registro de usuário bem-sucedido!')  # Mensagem de sucesso
            return make_response(jsonify({'message': 'Registro bem-sucedido!'}), 201)  # Código de sucesso 201
        
        except Exception as e:
            db.session.rollback()  # Se houver erro, faz rollback
            return make_response(jsonify({'message': f'Erro ao tentar registrar usuário: {e}'}), 500)

    return make_response(jsonify({'error': 'Método não suportado.'}), 405)

@app.route('/logout', methods=['POST'])
def logout():
    if 'id_user' in session:
        try:
            user_id = session.get('id_user')
            user = User.query.get(user_id)  # Obtém o usuário da sessão
            user.is_online = False  # Define is_online como False
            db.session.commit()  # Salva a alteração no banco de dados

            session.pop('username', None)  # Remove o usuário da sessão
            session.pop('id_user', None)  # Remove o ID do usuário da sessão, se existir
            flash('Você saiu com sucesso!', 'success')  # Mensagem de sucesso
            return make_response(
                jsonify({'message': 'Logout realizado com sucesso!'}), 200
            )
        except Exception as e:
            db.session.rollback()  # Se houver erro, faz rollback
            return make_response(jsonify({'message': f'Erro ao tentar deslogar usuário: {e}'}), 500)
    else:
        flash('Não há usuário logado.', 'info')  # Mensagem de informação
        return make_response(jsonify({'error': 'Nenhum usuário logado.'}), 400)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:

            # Verifica se já há um usuário logado
            if 'username' in session:
                logout()  # Encerra a sessão atual

            data = request.get_json()

            username = data['username'].upper()
            password = data['password']

            user = validate_user(username, password)  # Função para validar usuário

            if user:
                session['username'] = user.username
                session['id_user'] = user.id
                user.is_online = True  # Define is_online como True
                db.session.commit()  # Salva a alteração no banco de dados
                
                query_queue = f"""
                SELECT 
                    u.username AS user_username,
                    lq.name AS queue_name,
                    mq.message AS last_message,
                    mq.timestamp AS last_message_timestamp,
                    CASE 
                        WHEN u.id = lq.user_one THEN u2.username  -- Captura o nome do amigo se o usuário for 'user_one'
                        ELSE u1.username  -- Captura o nome do amigo se o usuário for 'user_two'
                    END AS friend_name
                FROM 
                    "User" u
                JOIN 
                    link_queue lq ON u.id = lq.user_one OR u.id = lq.user_two
                LEFT JOIN 
                    last_message_queue lmq ON lq.name = lmq.id_from
                LEFT JOIN 
                    message_queue mq ON lmq.id_last_message = mq.id
                LEFT JOIN 
                    "User" u1 ON u1.id = lq.user_one  -- Amigo potencial, se `user_one`
                LEFT JOIN 
                    "User" u2 ON u2.id = lq.user_two  -- Amigo potencial, se `user_two`
                WHERE 
                    u.id = '{user.id}';
                """
                # Executa a consulta na view e converte para uma lista de dicionários
                results_queue = db.session.execute(text(query_queue)).fetchall()

                query_topic = f"""
                SELECT 
                    u.username AS user_username,
                    mt.group_name AS topic_name,
                    gm.message AS last_message,
                    gm.timestamp AS last_message_timestamp
                FROM 
                    "User" u
                JOIN 
                    topic_membership tm ON u.id = tm.user_id
                JOIN 
                    message_topic mt ON tm.topic_id = mt.name
                LEFT JOIN 
                    last_message_topic lmt ON mt.name = lmt.id_from
                LEFT JOIN 
                    group_message gm ON lmt.id_last_message = gm.id
                WHERE 
                    u.id = '{user.id}'; 
                """
                # Executa a consulta na view e converte para uma lista de dicionários
                results_topic = db.session.execute(text(query_topic)).fetchall()


                print(results_topic)
                print(results_queue)

                # Criar uma lista para os chats
                chats = []

                # Adicionar resultados da consulta de filas
                for user_username, topic_name, last_message, timestamp in results_topic:
                    chats.append({
                        #'user_username': user_username,
                        'topic_name': topic_name,
                        'last_message': last_message,
                        #'timestamp': timestamp.isoformat()  # Converter para string
                    })

                # Adicionar resultados da consulta de tópicos
                for user_username, queue_name, last_message, timestamp, friend_name in results_queue:
                    chats.append({
                        #'user_username': user_username,
                        'queue_name': queue_name,
                        'last_message': last_message,
                        #'timestamp': timestamp.isoformat() if timestamp else None,  # Converter para string ou None
                        'friend_name': friend_name
                    })

                print(chats)

                info = ({'id_user': user.id, 'username': user.username})

                return make_response(
                    jsonify({'message': chats, 'session': info}), 200
                )
            else:
                flash('Usuário ou senha incorretos.')
                return make_response(
                    jsonify({'error': 'Usuário ou senha incorretos.'}), 401
                )
        except Exception as e:
            db.session.rollback()  # Se houver erro, faz rollback
            return make_response(jsonify({'message': f'Erro no login de usuário: {e}'}), 500)
        
    return make_response(jsonify({'error': 'Método não suportado.'}), 405)


from flask import request, session, jsonify, make_response
@app.route('/create_group', methods=['POST'])
def create_group():

    data = request.get_json()

    session['id_user'] = data['id_user']
    session['username'] = data['username']

    # Verifica se o usuário está logado
    if 'id_user' not in session:
        return make_response(jsonify({'error': 'Você precisa estar logado para criar grupos.'}), 401)

    # Extrai o ID do usuário e os dados do JSON
    user_id = session['id_user']
    

    # Validação dos parâmetros
    if not data or 'amigos' not in data or 'group_name' not in data:
        return make_response(jsonify({'error': 'Nome do grupo e lista de amigos são obrigatórios.'}), 400)

    # Extrai o nome do grupo e lista de amigos
    amigos = data['amigos']
    group_name = data['group_name']

    # Verifica se a lista de amigos tem pelo menos um ID
    if not amigos or not isinstance(amigos, list) or len(amigos) < 1:
        return make_response(jsonify({'error': 'A lista de amigos deve conter pelo menos um amigo.'}), 400)

    try:
        # Verifica se todos os amigos estão na lista de amigos do usuário
        amigos_validos = []
        for amigo in amigos:
            print(amigo)
            # Consulta para verificar a amizade
            friend = User.query.filter_by(username=amigo.upper()).first()
            if not friend:
                return make_response(jsonify({'error': f'O usuário {amigo} não existe.'}), 400)
            amizade = Friends.query.filter_by(id_user=user_id, id_friend=friend.id).first()
            if amizade:
                amigos_validos.append(friend.id)  # Adiciona amigo se for válido
            else:
                return make_response(jsonify({'error': f'O usuário {amigo} não é amigo do usuário logado.'}), 400)

        topic_exists = MessageTopic.query.filter_by(group_name=group_name).first()

        if topic_exists:
            return make_response(jsonify({'error': 'Já existe um grupo com esse nome.'}), 400)
        # Cria uma nova entrada na tabela MessageTopic com o dono como o usuário autenticado
        novo_grupo = MessageTopic(owner_id=user_id, group_name=group_name)
        db.session.add(novo_grupo)
        db.session.commit()  # Salva o grupo para obter o ID

        # Adiciona o criador do grupo como membro
        db.session.add(TopicMembership(topic_id=novo_grupo.name, user_id=user_id))

        # Adiciona os amigos válidos à tabela TopicMembership
        for amigo_id in amigos_validos:
            membership = TopicMembership(topic_id=novo_grupo.name, user_id=amigo_id)
            db.session.add(membership)

        # Faz o commit das alterações no banco de dados
        db.session.commit()

        # Retorna resposta de sucesso
        return make_response(jsonify({'message': 'Grupo criado com sucesso!'}), 201)

    except Exception as e:
        # Em caso de erro, desfaz as transações
        db.session.rollback()
        return make_response(jsonify({'message': f'Erro ao tentar criar grupo: {e}'}), 500)


@app.route('/add_friend', methods=['POST'])
def add_friend():

    data = request.get_json()

    session['id_user'] = data['id_user']
    session['username'] = data['username']


    if 'id_user' not in session:
        return make_response(jsonify({'error': 'Você precisa estar logado para adicionar amigos.'}), 401)

    try:
        

        if 'friend_username' not in data:
            return make_response(jsonify({'error': 'Nome de usuário do amigo é necessário.'}), 400)

        user_id = session.get('id_user')
        friend_username = data['friend_username'].upper()

        friend_list = FriendList.query.filter_by(user_id=user_id).first()

        # Verifica se o amigo existe
        friend = User.query.filter_by(username=friend_username).first()
        
        if not friend:
            return make_response(jsonify({'error': 'Usuário amigo não encontrado.'}), 404)

        # Verifica se a amizade já existe
        existing_friendship = Friends.query.filter_by(id_user=friend_list.user_id, id_friend=friend.id).first()
        if existing_friendship:
            return make_response(jsonify({'error': 'Vocês já são amigos.'}), 400)

        # Adiciona o amigo à lista de amigos
        new_friendship = Friends(id_user=friend_list.user_id, id_friend=friend.id)
        new_queue = LinkQueue(user_one=friend_list.user_id, user_two=friend.id)
        db.session.add(new_friendship)
        db.session.add(new_queue)
        db.session.commit()

        return make_response(jsonify({'message': f'{friend_username} foi adicionado como amigo com sucesso!'}), 201)

    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'message': f'Erro ao tentar adicionar amigo: {e}'}), 500)


@app.route('/send_message', methods=['POST'])
def send_message():

    data = request.get_json()

    session['id_user'] = data['id_user']
    session['username'] = data['username']

    # Verifica se o usuário está logado
    if 'id_user' not in session:
        return jsonify({'error': 'Acesso negado: usuário não autenticado.'}), 403

    try:

        # Obtém o nome de usuário da sessão
        username = session['username']
        user_id = session['id_user']
        
        broker_url = BROKER_URL        

        # Obtém os dados do JSON recebido
        

        name = data.get('name')
        msg_content = data.get('message')
        msg_type = data.get('type').upper()

        if 'chat' not in session:
            return jsonify({'error': 'Você não se conectou ao chat ainda!'}), 404

        # Verifica se todos os dados necessários estão presentes
        if not all([name, msg_content, broker_url, msg_type]):
            return jsonify({'error': 'Todos os campos (name, message, brokerUrl e type) devem ser fornecidos.'}), 400


        if msg_type == "QUEUE":
                friend = User.query.filter_by(username=name.upper()).first()
                if friend:
                    friends = Friends.query.filter_by(id_user=user_id, id_friend=friend.id)
                    if friends:
                        
                        query = (
                            db.session.query(LinkQueue)
                            .filter(
                                or_(
                                    (LinkQueue.user_one == user_id) & (LinkQueue.user_two == friend.id),
                                    (LinkQueue.user_two == user_id) & (LinkQueue.user_one == friend.id)
                                )
                            )
                        ) 


                        result = query.first()  # Obtém o primeiro resultado correspondente, ou `None` se não encontrar
                    else:
                        return jsonify({'error': 'Vocês não são amigos'}), 403
                else:
                    return jsonify({'error': 'Usuário não encontrado'}), 404
                
                if not result:
                    return jsonify({'error': 'Você não tem permissão para acessar esse chat ou ele não existe'}), 403
        
                name = result.name
                
        elif msg_type == "TOPIC":
            topic = MessageTopic.query.filter_by(group_name=name).first()
            if topic :        
                result = TopicMembership.query.filter_by(user_id=user_id).first()
                
                if not result:
                    return jsonify({'error': 'Você não tem permissão para acessar esse chat'}), 403
        
                name = topic.name
            else:         
                return jsonify({'error': 'Chat não encontrado!'}), 404
        else:
            return jsonify({'error': 'Tipo de chat inválido! Use QUEUE ou TOPIC.'}), 400
        

        if name != session['chat']:
            return jsonify({'error': 'Você não se conectou ao chat ainda!'}), 404


        # Prepara o payload para enviar ao serviço Java, incluindo o username da sessão
        payload = {
            'name': name,
            'username': username,  # Usa o username da sessão
            'message': msg_content,
            'brokerUrl': broker_url,
            'type': msg_type
        }

        # Envia a solicitação POST para o serviço Java
        response = requests.post(f'{API_URL[0]}/send_message', json=payload)

        # Retorna a resposta do serviço Java
        if response and response.status_code == 200:
            try:
                # Verifica o tipo de mensagem e cria a instância apropriada
                if msg_type == 'QUEUE':
                    new_message = MessageQueue(queue_name=name, sender_id=user_id, message=msg_content)
                else:
                    new_message = GroupMessage(topic_id=name, sender_id=user_id, message=msg_content)

                # Adiciona e faz o commit da nova mensagem
                db.session.add(new_message)
                db.session.commit()

            except Exception as e:
                db.session.rollback()  # Desfaz a transação em caso de erro
                return jsonify({'error': f'Falha ao enviar mensagem para o banco de dados: {str(e)}'}), 500

            return jsonify({'response': response.json()}), 200
            
        else:
            return jsonify({'error': f'Falha ao enviar mensagem: {response.text}'}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Erro de conexão com o serviço Java: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro inesperado: {str(e)}'}), 500


# Variável global para armazenar o status da conexão e o consumidor
consumer = None

@app.route('/connect', methods=['POST'])
def connect():
    global consumer, status
    data = request.get_json()

    session['id_user'] = data['id_user']
    session['username'] = data['username']

    if 'id_user' not in session:
        return jsonify({"status": "error", "message": "Você não está logado."}), 403

    # Validação dos parâmetros da requisição
    if not data or 'name' not in data or 'type' not in data:
        status = "disconnect"
        return jsonify({"status": "error", "message": "Todos os campos (name e type) devem ser fornecidos."}), 400

    try:

        type = data['type'].upper() 
        
        if type == "QUEUE":
            
            username = data['name'].upper()

            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({"status": "error", "message": "Amigo não encontrado."}), 404
            
            # Executa a consulta corretamente
            query = (
                db.session.query(LinkQueue)
                .filter(
                    or_(
                        (LinkQueue.user_one == session['id_user']) & (LinkQueue.user_two == user.id),
                        (LinkQueue.user_two == session['id_user']) & (LinkQueue.user_one == user.id)
                    )
                )
            ) 
            result = query.first()

            
            if not result:
                return jsonify({"status": "error", "message": "Chat não encontrado."}), 404
            
            # Certifique-se de que a coluna name exista
            name = result.name

            query = f"""
            SELECT * FROM v_message_queue
            WHERE queue_name = '{result.name}'
            ORDER BY timestamp;
            """
            messages = db.session.execute(text(query)).fetchall()  # Executa a consulta na view
            


        elif type == "TOPIC":
            group_name = data['name']
            topic = MessageTopic.query.filter_by(group_name=group_name).first()
            if not topic:
                return jsonify({"status": "error", "message": "Chat em grupo não encontrado."}), 404
            
            name = topic.name

            messages = (
                db.session.query(GroupMessage.id, GroupMessage.message, GroupMessage.timestamp, User.username)  # Incluindo username
                .join(User, GroupMessage.sender_id == User.id)  # Realiza a junção
                .filter(GroupMessage.topic_id == name)  # Filtra
                .order_by(GroupMessage.timestamp)  # Ordena
                .all()  # Executa a consulta
            )
        
        RECEIVE_URL = Flask_URL+"/"+name

        session['chat'] = name

        print(f'name: {name}')

        payload = {
            'brokerUrl': BROKER_URL,
            'apiUrl': RECEIVE_URL,
            'name': name,
            'type': type,
        }

        # Envia a solicitação POST para o serviço Java

        status = "connected"
    
        response = requests.post(f'{API_URL[1]}/connect', json=payload)

        # Retorna a resposta do serviço Java
        if response.status_code == 200:
            result = [{'id': message.id, 'message': message.message, 'timestamp': message.timestamp, 'username': message.username} for message in messages]
            
            info = ({'id_user': session['id_user'], 'username': session['username']})
            return jsonify({'status': 'success', 'messages': result, "session": info}), 200
        else:
            status = "disconnect"
            return jsonify({'error': f'Falha ao enviar mensagem: {response.text}'}), response.status_code

    except Exception as ex:
        status = "disconnect"

        return jsonify({"status": "error", "message": f"Erro no processamento. {ex}"}), 500



@app.route('/load_messages', methods=['POST'])
def load_messages():
    data = request.get_json()

    if 'chat' not in session:
        return jsonify({'status': 'error', 'message': 'Você não se conectou a nenhum chat'}), 400
            

    if not data or 'type' not in data:
        status = "disconnect"
        return jsonify({"status": "error", "message": "Todos os campos (type) devem ser fornecido."}), 400

    user = session['id_user']

    type = data.get('type').upper()
    

    if 'name' in data:
        if type == 'QUEUE':
            return jsonify({"status": "error", "message": "parametro (name) devem ser fornecido apenas em requisiçao TOPIC."}), 400
        name = data.get('name')
    if 'friend' in data:
        if type != 'QUEUE':
            return jsonify({"status": "error", "message": "Erro requisição na requisição este tipo de requisição deve ser QUEUE!"}), 400
        
        friend = data.get('friend').upper()
    
    try:
        if type == 'QUEUE':
            friend = User.query.filter_by(username=friend).first()

            if not friend:
                return jsonify({'status': 'error', 'message': 'Amigo não encontrado.'}), 404
            
            query = (
                db.session.query(LinkQueue)
                .filter(
                    or_(
                        (LinkQueue.user_one == user) & (LinkQueue.user_two == friend.id),
                        (LinkQueue.user_two == user) & (LinkQueue.user_one == friend.id)
                    )
                )
            ) 
            result = query.first()  

            if not result:
                return jsonify({'status': 'error', 'message': 'Chat não encontrado.'}), 404

            if session['chat'] != result.name:
                return jsonify({'status': 'error', 'message': 'Sala inválida.'}), 400
            
            query = f"""
            SELECT * FROM v_message_queue
            WHERE queue_name = '{result.name}'
            ORDER BY timestamp;
            """
            messages = db.session.execute(text(query)).fetchall()  # Executa a consulta na view
            

            if not result:
                return jsonify({'status': 'error', 'message': 'Chat não encontrado.'}), 404
        elif type == 'TOPIC':
            group_name = name
            topic = MessageTopic.query.filter_by(group_name=group_name).first()
            if not topic:
                return jsonify({"status": "error", "message": "Chat em grupo não encontrado."}), 404
            
            member = TopicMembership.query.filter_by(topic_id=topic.name, user_id=user).first()

            if not member:
                return jsonify({'status': 'error', 'message': 'Você não é membro deste chat.'}), 404
            
            name = topic.name
            # Supondo que 'name' seja o ID do tópico que você está filtrando
            # Consulta para pegar as mensagens, agora incluindo o username
            messages = (
                db.session.query(GroupMessage.id, GroupMessage.message, GroupMessage.timestamp, User.username)  # Incluindo username
                .join(User, GroupMessage.sender_id == User.id)  # Realiza a junção
                .filter(GroupMessage.topic_id == name)  # Filtra
                .order_by(GroupMessage.timestamp)  # Ordena
                .all()  # Executa a consulta
            )
        else:
            return jsonify({'status': 'error', 'message': 'Tipo de chat inválido.'}), 400

                    # Formata os resultados
        result = [{'id': message.id, 'message': message.message, 'timestamp': message.timestamp, 'username': message.username} for message in messages]

        return jsonify({'status': 'success', 'messages': result}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erro de processamento: {e}'}), 400
    

@app.route('/messages/<value>', methods=['POST'])
def receive_message(value):
    data = request.get_json()

    # Verificação se os campos necessários estão presentes
    if not data or 'username' not in data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'username e message são obrigatórios.'}), 400

    username = data['username'].upper()
    message = data['message']

    print(f'message receive from {username}: {message}')

    # Emitir a mensagem para a sala correspondente ao valor
    socketio.emit('new_message', {'username': username, 'message': message}, room=value)

    return jsonify({'status': 'success', 'message': 'Mensagem recebida e emitida.'}), 200


# Evento para quando um cliente entra em uma sala
@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    print(f'{data["username"]} entrou na sala {room}.')

# Evento para quando um cliente sai da sala
@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    print(f'{data["username"]} saiu da sala {room}.')

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global status

    if status == "connected":
        status = "disconnected"

        payload = {
            
        }

        response = requests.post(f'{API_URL[1]}/disconnect',  json=payload)


        # Retorna a resposta do serviço Java
        if response.status_code == 200:
            status = "disconnect"
            return jsonify({"status": "success", "message": "Desconectado com sucesso."}), 200
        else:
            return jsonify({'error': f'Falha ao enviar mensagem: {response.text}'}), response.status_code

    return jsonify({"status": "error", "message": "Não há uma conexão ativa para desconectar."}), 400


if __name__ == '__main__':
    print(IP)
    socketio.run(app, host='0.0.0.0', port=5000)
