import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, and_, or_
from werkzeug.security import generate_password_hash


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(
        db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )  # UUID
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_online = db.Column(db.Boolean, default=False)

    # Relacionamento com FriendList
    friends = db.relationship('FriendList', backref='User', cascade='all, delete-orphan')
    
    # Relacionamento com LinkQueue para user_one
    queues_as_user_one = db.relationship('LinkQueue', 
                                          backref='user_one_relation', 
                                          primaryjoin='User.id == LinkQueue.user_one', 
                                          cascade='all, delete-orphan')

    # Relacionamento com LinkQueue para user_two
    queues_as_user_two = db.relationship('LinkQueue', 
                                          backref='user_two_relation', 
                                          primaryjoin='User.id == LinkQueue.user_two', 
                                          cascade='all, delete-orphan')


    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

class FriendList(db.Model):
    __tablename__ = 'friend_list'
    user_id = db.Column(
        db.String(36), db.ForeignKey('User.id'), primary_key=True
    )

    friends = db.relationship('Friends', backref='friend_list', cascade='all, delete-orphan')


class Friends(db.Model):
    __tablename__ = 'friends'
    id_user = db.Column(db.String(36), db.ForeignKey('friend_list.user_id'), primary_key=True)  # Chave primária composta
    id_friend = db.Column(db.String(36), db.ForeignKey('User.id'), primary_key=True) # Chave

    def __init__(self, id_user, id_friend):
        self.id_user = id_user
        self.id_friend = id_friend


class LinkQueue(db.Model):
    __tablename__ = 'link_queue'

    name = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    queue_name = db.Column(db.String(100), unique=True, nullable=False)
    user_one = db.Column(db.String(36), db.ForeignKey('User.id'), nullable=False)
    user_two = db.Column(db.String(36), db.ForeignKey('User.id'), nullable=False) 


class MessageQueue(db.Model):
    __tablename__ = 'message_queue'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID numérico e autoincrementado
    queue_name = db.Column(db.String(36), db.ForeignKey('link_queue.name'), nullable=False)  # Chave estrangeira para a tabela 'link_queue'
    sender_id = db.Column(db.String(36), db.ForeignKey('User.id'), nullable=False)  # Chave estrangeira para a tabela 'User'
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)  # Timestamp da mensagem
    message = db.Column(db.Text, nullable=False)  # Conteúdo da mensagem
    is_read = db.Column(db.Boolean, default=False)  # Status de leitura da mensagem

    def __init__(self, queue_name, sender_id, message):
        self.queue_name = queue_name
        self.sender_id = sender_id
        self.message = message


class MessageTopic(db.Model):
    __tablename__ = 'message_topic'

    name = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_name = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(
        db.String(36), db.ForeignKey('User.id'), nullable=False
    )
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, group_name, owner_id):
        self.group_name = group_name
        self.owner_id = owner_id


class TopicMembership(db.Model):
    __tablename__ = 'topic_membership'

    topic_id = db.Column(
        db.String(36), db.ForeignKey('message_topic.name'), primary_key=True
    )
    user_id = db.Column(
        db.String(36), db.ForeignKey('User.id'), primary_key=True
    )

    def __init__(self, topic_id, user_id):
        self.topic_id = topic_id
        self.user_id = user_id


class GroupMessage(db.Model):
    __tablename__ = 'group_message'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(
        db.String(36), db.ForeignKey('message_topic.name'), nullable=False
    )
    sender_id = db.Column(
        db.String(36), db.ForeignKey('User.id'), nullable=False
    )
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_read = db.Column(db.Boolean, default=False)

    def __init__(self, topic_id, sender_id, message):
        self.topic_id = topic_id
        self.sender_id = sender_id
        self.message = message


class LastMessageTopic(db.Model):
    __tablename__ = 'last_message_topic'

    id_from = db.Column(db.String(36), db.ForeignKey('message_topic.name'), primary_key=True) # UUID
    id_last_message = db.Column(db.Integer, db.ForeignKey('group_message.id'), nullable=True)


class LastMessageQueue(db.Model):
    __tablename__ = 'last_message_queue'

    id_from = db.Column(db.String(36), db.ForeignKey('link_queue.name'), primary_key=True) # UUID
    id_last_message = db.Column(db.Integer, db.ForeignKey('message_queue.id'), nullable=True)


def create_triggers(db):
    session = db.session()  # Iniciar sessão
    try:

        # Remover o trigger se ele já existir
        session.execute(text('''
            DROP TRIGGER IF EXISTS insert_last_message_topic ON message_topic;
        '''))

        # Função para a tabela message_topic
        session.execute(text('''
            CREATE OR REPLACE FUNCTION insert_last_message_topic_function()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO last_message_topic (id_from)
                VALUES (NEW.name);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        '''))

        # Trigger que chama a função insert_last_message_topic_function
        session.execute(text('''
            CREATE TRIGGER insert_last_message_topic
            AFTER INSERT ON message_topic
            FOR EACH ROW
            EXECUTE FUNCTION insert_last_message_topic_function();
        '''))

        session.execute(text('''
        DROP TRIGGER IF EXISTS insert_last_message_queue ON link_queue;
        '''))

        # Função para a tabela link_queue
        session.execute(text('''
            CREATE OR REPLACE FUNCTION insert_last_message_queue_function()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO last_message_queue (id_from)
                VALUES (NEW.name);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        '''))

        # Trigger que chama a função insert_last_message_queue_function
        session.execute(text('''
            CREATE TRIGGER insert_last_message_queue
            AFTER INSERT ON link_queue
            FOR EACH ROW
            EXECUTE FUNCTION insert_last_message_queue_function();
        '''))


        session.execute(text('''
        DROP TRIGGER IF EXISTS update_last_message_topic ON group_message;
        '''))

        # Função para atualizar a tabela last_message_topic
        session.execute(text("""
            CREATE OR REPLACE FUNCTION update_last_message_topic_function()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Atualiza o campo id_last_message na tabela last_message_topic
                UPDATE last_message_topic
                SET id_last_message = NEW.id
                WHERE id_from = NEW.topic_id;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))

        # Trigger para a função de update da tabela group_message
        session.execute(text("""
            CREATE TRIGGER update_last_message_topic
            AFTER INSERT ON group_message
            FOR EACH ROW
            EXECUTE FUNCTION update_last_message_topic_function();
        """))


        session.execute(text('''
        DROP TRIGGER IF EXISTS update_last_message_queue ON message_queue;
        '''))

        # Função para atualizar a tabela last_message_queue
        session.execute(text("""
            CREATE OR REPLACE FUNCTION update_last_message_queue_function()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Atualiza o campo id_last_message na tabela last_message_queue
                UPDATE last_message_queue
                SET id_last_message = NEW.id
                WHERE id_from = NEW.queue_name;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))

        # Trigger para a função de update da tabela message_queue
        session.execute(text("""
            CREATE TRIGGER update_last_message_queue
            AFTER INSERT ON message_queue
            FOR EACH ROW
            EXECUTE FUNCTION update_last_message_queue_function();
        """))

        session.execute(text('''
        DROP TRIGGER IF EXISTS after_user_insert ON "User";
        '''))

        # Função e trigger para criar a friend_list quando um novo usuário for inserido
        session.execute(text('''
            CREATE OR REPLACE FUNCTION create_friend_list()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO friend_list (user_id) VALUES (NEW.id);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        '''))

        session.execute(text('''
            CREATE TRIGGER after_user_insert
            AFTER INSERT ON "User"
            FOR EACH ROW
            EXECUTE FUNCTION create_friend_list();
        '''))

        session.execute(text('''
        DROP TRIGGER IF EXISTS after_friend_insert ON friends;
        '''))

        # Função para adicionar amigo mutuo
        session.execute(text('''
            CREATE OR REPLACE FUNCTION add_mutual_friend()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Verifica se a relação inversa já existe
                IF NOT EXISTS (
                    SELECT 1 FROM friends 
                    WHERE id_user = NEW.id_friend AND id_friend = NEW.id_user
                ) THEN
                    -- Adiciona o usuário à lista de amigos do amigo recém-adicionado
                    INSERT INTO friends (id_user, id_friend) 
                    VALUES (NEW.id_friend, NEW.id_user);
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        '''))

        # Criar o trigger que chama a função após inserção na tabela friends
        session.execute(text('''
            CREATE TRIGGER after_friend_insert
            AFTER INSERT ON friends
            FOR EACH ROW
            EXECUTE FUNCTION add_mutual_friend();
        '''))

        # Confirmar a transação
        session.commit()

    except Exception as e:
        # Em caso de erro, reverter a transação
        session.rollback()
        raise e

    finally:
        # Fechar a sessão
        session.close()
