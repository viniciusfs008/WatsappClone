package org.example.messaging;

import java.util.ArrayList;
import java.util.List;

import javax.jms.Connection;
import javax.jms.MessageConsumer;
import javax.jms.Session;

import org.example.models.Message;

import org.apache.activemq.ActiveMQConnectionFactory;

public class UserTopicConsumer implements AutoCloseable {

    private Connection connection;

    private Session session;

    private MessageConsumer consumer;

    private boolean inError;

    private String error;

    private Thread worker;

    private boolean isRunning;

    // Lista para armazenar mensagens recebidas
    private List<Message> messageList = new ArrayList<>();


    public UserTopicConsumer(String brokerUrl, String topicName){
        var factory = new ActiveMQConnectionFactory(brokerUrl);

        try {
            connection = factory.createConnection();
            connection.start();
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
            System.out.println("Connection created: "+ connection);
            var topicDestination = session.createTopic(topicName);
            consumer = session.createConsumer(topicDestination);
            worker = new Thread(this::doWork);
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

    public void start() {
        isRunning = true;
        worker.start();
    }

    public void stop() {
        isRunning = false;
        try {
            worker.join();
        } catch (Exception ignored) {}
    }
    
    @Override
    public void close() {
        stop();
        try {
            consumer.close();
            session.close();
            connection.close();
        } catch (Exception ignored) {}
    }

    private void doWork() {
        while (isRunning) {
            try {
                // Espera por uma mensagem com um timeout de 1 segundo (1000ms)
                var userMsg = consumer.receive(1000); // Define um timeout

                if (userMsg != null) {
                    String username = userMsg.getStringProperty("username"); // Nome de usuário
                    String msgContent = userMsg.getStringProperty("message"); // Mensagem

                    Message Msg = new Message(username, msgContent);
                    if (Msg != null) {
                        // Armazena a mensagem recebida
                        messageList.add(Msg);
                        System.out.println("Mensagem recebida e armazenada.");
                    }
                }

                
            } catch (Exception ex) {
                inError = true;
                error = ex.getMessage();
            }
        }
    }

    // Método para receber a próxima mensagem
    public Message receive() {
        if (!messageList.isEmpty()) {
            return messageList.remove(0); // Remove e retorna a primeira mensagem da lista
        }
        return null; // Retorna null se não houver mensagens
    }
}
