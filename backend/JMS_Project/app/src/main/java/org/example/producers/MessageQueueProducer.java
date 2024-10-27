package org.example.producers;

import javax.jms.*;

import org.example.models.Message;
import org.apache.activemq.ActiveMQConnectionFactory;

public class MessageQueueProducer implements AutoCloseable {

    private String baseUrl;

    private ConnectionFactory connectionFactory;

    private Connection connection;

    private Session session;

    private Queue queue;

    private MessageProducer producer;

    private boolean inError;

    private String error;

    private static MessageQueueProducer instance;

    private MessageQueueProducer(String brokerUrl, String queueName) {
        baseUrl = brokerUrl;
        connectionFactory = new ActiveMQConnectionFactory(baseUrl);  // Corrigido o nome
        try {
            connection = connectionFactory.createConnection();
            System.out.println("Connection created: "+connection.getMetaData());
            connection.start();
        } catch (Exception e) {
            inError = true;
            error = "Failed to connect to ActiveMQ: " + e.getMessage();
            return;
        }
        try {
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ session: " + ex.getMessage();
            return;
        }
        try {
            queue = session.createQueue(queueName);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ queue: " + ex.getMessage();
            return;
        }
        try {
            producer = session.createProducer(queue);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ producer: " + ex.getMessage();
            return;
        }
        inError = false;
    }

    private void publish(Message message) {
        try {
            var msg = session.createObjectMessage();
            msg.setStringProperty("username", message.getUsername());
            msg.setStringProperty("message", message.getMessage());

            producer.send(msg);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ message: " + ex.getMessage();
            return;
        }
    }

    @Override
    public void close() {
        System.out.println("Closing message producer");
        try {
            producer.close();
            session.close();
            connection.close();
        } catch (Exception ignored) {}
    }

    public static boolean inError() {
        return instance.inError;  
    }

    public static String error() {
        return instance.error;
    }

    public static void initialize(String baseUrl, String queueName) {
        instance = new MessageQueueProducer(baseUrl, queueName);
        
    }

    public static void terminate() {
        instance.close();
    }

    public static void add(Message message) {
        if (instance != null) {
            instance.publish(message);
        }else {
            System.out.println("Erro instancia vazia!!");
        }
    }
}
