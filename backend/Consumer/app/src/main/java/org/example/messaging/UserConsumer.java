package org.example.messaging;

import java.util.ArrayList;
import java.util.List;

import javax.jms.*;
import org.example.models.Message;

import org.apache.activemq.ActiveMQConnectionFactory;

public class UserConsumer  implements AutoCloseable {
    
    private String baseUrl;

    private ConnectionFactory connectionFactory;

    private Connection connection;

    private Session session;

    private Queue queue;

    private MessageConsumer consumer;

    private boolean inError;

    private String error;

    private static UserConsumer instance;

    // Lista para armazenar mensagens recebidas
    private static List<Message> messageList = new ArrayList<>();

    private UserConsumer(String brokerUrl, String queueName){
        baseUrl = brokerUrl;
        connectionFactory = new ActiveMQConnectionFactory(baseUrl);

        try {
            connection = connectionFactory.createConnection();
            
            //System.out.println("Connection created: "+connection);
            connection.start();
        } catch (Exception ex) {
            inError = true;
            error = ex.getMessage();
            return;
        }
        try {
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
        } catch (Exception ex) {
            inError = true;
            error = ex.getMessage();
            return;
        }
        try {
            queue = session.createQueue(queueName);
        } catch (Exception ex) {
            inError = true;
            error = ex.getMessage();
            return;
        }

        try {
            consumer = session.createConsumer(queue);
            consumer.setMessageListener(message -> {
                try {
                    // Recuperando os parâmetros da mensagem
                    String username = message.getStringProperty("username"); // Nome de usuário
                    String msgContent = message.getStringProperty("message"); // Mensagem
            
                    // Criando uma nova instância da classe Message
                    Message userMsg = new Message(username, msgContent);

                    if (userMsg != null) {
                        // Armazena a mensagem recebida
                        messageList.add(userMsg);
                        System.out.println("Mensagem recebida e armazenada.");
                    }
                    
                    // Exibindo os detalhes da mensagem recebida
                    System.out.println("Received: \n");
                    System.out.println("| User: " + userMsg.getUsername() + " | Message: " + userMsg.getMessage());
                } catch (Exception ex) {
                    System.out.println("Error in message consumer: " + ex);
                }
            });
        } catch (Exception ex) {
            inError = true;
            error = ex.getMessage();
            return;
        }
    }

    public boolean isInError() {
        return inError;
    }

    public String getError() {
        return error;
    }
    
    @Override
    public void close() {
        try {
            consumer.close();
            session.close();
            connection.close();
        } catch (Exception ignored) {}
    }

    public static void initialize(String baseUrl, String queueName) {
        instance = new UserConsumer(baseUrl, queueName);
    }

    public static boolean inError() {
        return instance.inError;
    }

    public static String error() {
        return instance.error;
    }

    public static void terminate() {
        instance.close();
    }

    // Método para receber a próxima mensagem
    public static Message receive() {
        if (!messageList.isEmpty()) {
            return messageList.remove(0); // Remove e retorna a primeira mensagem da lista
        }
        return null; // Retorna null se não houver mensagens
    }
}
