// Define o pacote onde está localizada a classe MessageQueueProducer
package org.example.producers;

// Importa as classes necessárias para a implementação JMS (Java Message Service)
import javax.jms.*;

import org.example.models.Message;
import org.apache.activemq.ActiveMQConnectionFactory;

// Classe MessageQueueProducer que implementa AutoCloseable para garantir que os recursos sejam liberados automaticamente
public class MessageQueueProducer implements AutoCloseable {

    // URL base do broker de mensagens
    private String baseUrl;

    // Fábrica de conexões para estabelecer a conexão com o broker
    private ConnectionFactory connectionFactory;

    // Conexão com o broker JMS
    private Connection connection;

    // Sessão JMS para criar e gerenciar mensagens
    private Session session;

    // Fila onde as mensagens serão enviadas
    private Queue queue;

    // Produtor JMS responsável por enviar as mensagens para a fila
    private MessageProducer producer;

    // Indicador de erro para sinalizar se ocorreu algum problema
    private boolean inError;

    // Mensagem de erro em caso de falha
    private String error;

    // Instância única da classe (singleton) para garantir que apenas uma instância seja usada
    private static MessageQueueProducer instance;

    // Construtor privado que inicializa a conexão e os componentes do JMS (singleton)
    private MessageQueueProducer(String brokerUrl, String queueName) {
        baseUrl = brokerUrl;
        connectionFactory = new ActiveMQConnectionFactory(baseUrl);
        
        // Tenta estabelecer a conexão com o broker
        try {
            connection = connectionFactory.createConnection();
            System.out.println("Connection created: " + connection.getMetaData());
            connection.start();
        } catch (Exception e) {
            inError = true;
            error = "Failed to connect to ActiveMQ: " + e.getMessage();
            return;
        }
        
        // Cria uma sessão JMS com confirmação automática
        try {
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ session: " + ex.getMessage();
            return;
        }
        
        // Define a fila onde as mensagens serão enviadas
        try {
            queue = session.createQueue(queueName);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ queue: " + ex.getMessage();
            return;
        }
        
        // Inicializa o produtor de mensagens associado à fila
        try {
            producer = session.createProducer(queue);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ producer: " + ex.getMessage();
            return;
        }
        
        inError = false; // Marca a inicialização como bem-sucedida se nenhum erro ocorreu
    }

    // Método que publica uma mensagem na fila configurada
    private void publish(Message message) {
        try {
            var msg = session.createObjectMessage();
            
            // Define propriedades da mensagem, como nome do usuário e conteúdo
            msg.setStringProperty("username", message.getUsername());
            msg.setStringProperty("message", message.getMessage());

            // Envia a mensagem para a fila através do produtor
            producer.send(msg);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ message: " + ex.getMessage();
            return;
        }
    }

    // Sobrescreve o método close para fechar e liberar os recursos (produtor, sessão e conexão)
    @Override
    public void close() {
        System.out.println("Closing message producer");
        try {
            producer.close();     // Fecha o produtor
            session.close();      // Fecha a sessão
            connection.close();   // Fecha a conexão
        } catch (Exception ignored) {} // Ignora exceções para garantir que os recursos sejam liberados
    }

    // Método estático para verificar se ocorreu algum erro
    public static boolean inError() {
        return instance.inError;  
    }

    // Método estático para retornar a mensagem de erro atual
    public static String error() {
        return instance.error;
    }

    // Método estático para inicializar a instância (singleton) do MessageQueueProducer
    public static void initialize(String baseUrl, String queueName) {
        instance = new MessageQueueProducer(baseUrl, queueName);
    }

    // Método estático para encerrar a instância e liberar os recursos
    public static void terminate() {
        instance.close();
    }

    // Método estático para adicionar uma mensagem à fila
    public static void add(Message message) {
        if (instance != null) {
            instance.publish(message);
        } else {
            System.out.println("Erro instancia vazia!!"); // Caso a instância ainda não tenha sido inicializada
        }
    }
}
