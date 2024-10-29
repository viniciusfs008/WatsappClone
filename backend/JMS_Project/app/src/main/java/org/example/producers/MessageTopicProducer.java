// Define o pacote onde está localizada a classe MessageTopicProducer
package org.example.producers;

// Importa as classes necessárias para conexão e envio de mensagens via JMS (Java Message Service)
import javax.jms.*;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.example.models.Message;

// Classe MessageTopicProducer que implementa AutoCloseable para garantir que recursos sejam liberados automaticamente
public class MessageTopicProducer implements AutoCloseable {
    
    // Conexão JMS para conectar ao broker de mensagens
    private Connection connection;

    // Sessão JMS para criar e gerenciar mensagens
    private Session session;

    // Produtor JMS responsável por enviar mensagens para o tópico
    private MessageProducer producer;

    // Indicador de erro para sinalizar se ocorreu algum problema
    private boolean inError;

    // String para armazenar a mensagem de erro, caso ocorra algum
    private String error;

    // Construtor que recebe o brokerUrl e o nome do tópico para configurar o produtor de mensagens
    public MessageTopicProducer(String brokerUrl, String topicName) {
        // Cria uma fábrica de conexões ActiveMQ
        var factory = new ActiveMQConnectionFactory();
        try {
            // Cria uma nova conexão JMS e inicia a conexão
            connection = factory.createConnection();
            connection.start();

            // Cria uma sessão JMS com confirmação automática (AUTO_ACKNOWLEDGE)
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

            // Define o destino da mensagem como um tópico (topic) com o nome especificado
            var destinationTopic = session.createTopic(topicName);

            // Cria um produtor de mensagens para o tópico especificado
            producer = session.createProducer(destinationTopic);
        } catch (Exception ex) {
            // Em caso de erro, define inError como true e armazena a mensagem de erro
            inError = true;
            error = "Failed to create ActiveMQ connection: " + ex.getMessage();
        }
    }

    // Método para verificar se houve erro na criação da conexão ou do produtor
    public boolean isInError() {
        return inError;
    }

    // Método para obter a mensagem de erro em caso de falha
    public String getError() {
        return error;
    }

    // Método para publicar uma mensagem no tópico configurado
    public void publish(Message message) {
        try {
            // Cria uma mensagem do tipo ObjectMessage para enviar dados complexos
            var msg = session.createObjectMessage();
            
            // Define propriedades da mensagem, como o nome do usuário e o conteúdo da mensagem
            msg.setStringProperty("username", message.getUsername());
            msg.setStringProperty("message", message.getMessage());

            // Envia a mensagem para o tópico através do produtor
            producer.send(msg);
        } catch (Exception ex) {
            // Em caso de erro, define inError como true e armazena a mensagem de erro
            inError = true;
            error = "Failed to create ActiveMQ message: " + ex.getMessage();
            return;
        }
    }

    // Método close sobrescrito para fechar e liberar os recursos (produtor, sessão e conexão)
    @Override
    public void close() {
        try {
            producer.close();     // Fecha o produtor de mensagens
            session.close();      // Fecha a sessão JMS
            connection.close();   // Fecha a conexão com o broker
        } catch (Exception ignored) {} // Ignora exceções ao fechar, para garantir liberação de recursos
    }
}
