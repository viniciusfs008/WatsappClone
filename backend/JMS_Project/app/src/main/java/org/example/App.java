package org.example;


import org.example.models.Message;
import org.example.models.ResponseMessage;
import org.example.producers.MessageQueueProducer;
import org.example.producers.MessageTopicProducer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


@RestController
@SpringBootApplication
public class App {

    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }

    @PostMapping("/send_message")
    public ResponseEntity<ResponseMessage> sendMessage(@RequestBody Message message) {
        if (message == null || message.getUsername() == null || message.getMessage() == null || 
            message.getType() == null || message.getBrokerUrl() == null) {
            return ResponseEntity.badRequest().body(new ResponseMessage("error", 
                "Todos os campos (username, message, type e brokerUrl) devem ser fornecidos."));
        }

        String name = message.getName();
        String userName = message.getUsername();
        String msgContent = message.getMessage();
        String brokerUrl = message.getBrokerUrl();
        String type = message.getType().toUpperCase();

        try {
            if (type.equals("TOPIC")) {
                var topicProducer = new MessageTopicProducer(brokerUrl, name);

                if (topicProducer.isInError()) {
                    topicProducer.close();
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(new ResponseMessage("error", topicProducer.getError()));
                } else {
                    topicProducer.publish(message);
                    topicProducer.close(); // Fecha o produtor após uso
                    return ResponseEntity.ok(new ResponseMessage("success", 
                        "TOPIC Message sent by " + userName + ": " + msgContent));
                }

            } else if (type.equals("QUEUE")) {
                MessageQueueProducer.initialize(brokerUrl, name);

                if (MessageQueueProducer.inError()) {
                    MessageQueueProducer.terminate();
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(new ResponseMessage("error", "Failed to initialize Queue Producer"));
                } 

                MessageQueueProducer.add(message);
                MessageQueueProducer.terminate(); // Fecha o produtor após uso
                return ResponseEntity.ok(new ResponseMessage("success", 
                    "QUEUE Message sent by " + userName + ": " + msgContent));
                
            } else {
                return ResponseEntity.badRequest().body(new ResponseMessage("error", 
                    "tipo de mensagem '" + type + "' é inválido!"));
            }
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ResponseMessage("error", "Erro durante o envio da mensagem: " + e.getMessage()));
        }
    }
}
