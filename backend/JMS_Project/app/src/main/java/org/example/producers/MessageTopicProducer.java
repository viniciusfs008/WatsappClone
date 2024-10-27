package org.example.producers;

import javax.jms.*;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.example.models.Message;

public class MessageTopicProducer implements AutoCloseable{
    
    private Connection connection;

    private Session session;

    private MessageProducer producer;

    private boolean inError;

    private String error;

    public MessageTopicProducer(String brokerUrl, String topicName) {
        var factory = new ActiveMQConnectionFactory();
        try {
            connection = factory.createConnection();
            connection.start();
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
            var destinationTopic = session.createTopic(topicName);
            producer = session.createProducer(destinationTopic);
        } catch (Exception ex) {
            inError = true;
            error = "Failed to create ActiveMQ connection: " + ex.getMessage();
        }
    }

    public boolean isInError() {
        return inError;
    }

    public String getError() {
        return error;
    }

    public void publish(Message message) {
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
        try {
            producer.close();
            session.close();
            connection.close();
        } catch (Exception ignored) {}
    }
}
