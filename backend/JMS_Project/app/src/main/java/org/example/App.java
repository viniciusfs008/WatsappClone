// Define o pacote principal onde o código está localizado
package org.example;

// Importa as classes necessárias, incluindo modelos de dados e produtores para mensagens, 
// bem como as bibliotecas do Spring para criação de um aplicativo web
import org.example.models.Message;
import org.example.models.ResponseMessage;
import org.example.producers.MessageQueueProducer;
import org.example.producers.MessageTopicProducer;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

// Anotação que indica que esta classe é um controlador REST que gerencia endpoints HTTP
@RestController
// Anotação que indica que esta é uma aplicação Spring Boot
@SpringBootApplication
public class App {

    // Método principal que inicializa o aplicativo Spring Boot
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }

    // Define o endpoint POST "/send_message" para enviar uma mensagem
    @PostMapping("/send_message")
    public ResponseEntity<ResponseMessage> sendMessage(@RequestBody Message message) {
        // Verifica se a mensagem ou campos importantes da mensagem são nulos e retorna erro caso algum seja
        if (message == null || message.getUsername() == null || message.getMessage() == null || 
            message.getType() == null || message.getBrokerUrl() == null) {
            return ResponseEntity.badRequest().body(new ResponseMessage("error", 
                "Todos os campos (username, message, type e brokerUrl) devem ser fornecidos."));
        }

        // Extrai dados da mensagem, como nome, usuário, conteúdo, URL do broker e tipo de mensagem
        String name = message.getName();
        String userName = message.getUsername();
        String msgContent = message.getMessage();
        String brokerUrl = message.getBrokerUrl();
        String type = message.getType().toUpperCase();

        try {
            // Se o tipo de mensagem for "TOPIC", cria um produtor de tópico
            if (type.equals("TOPIC")) {
                var topicProducer = new MessageTopicProducer(brokerUrl, name);

                // Verifica se o produtor de tópico está em estado de erro
                if (topicProducer.isInError()) {
                    topicProducer.close();
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(new ResponseMessage("error", topicProducer.getError()));
                } else {
                    // Publica a mensagem no tópico e fecha o produtor após o uso
                    topicProducer.publish(message);
                    topicProducer.close();
                    return ResponseEntity.ok(new ResponseMessage("success", 
                        "TOPIC Message sent by " + userName + ": " + msgContent));
                }

            // Se o tipo de mensagem for "QUEUE", inicializa um produtor de fila
            } else if (type.equals("QUEUE")) {
                MessageQueueProducer.initialize(brokerUrl, name);

                // Verifica se há erro na inicialização do produtor de fila
                if (MessageQueueProducer.inError()) {
                    MessageQueueProducer.terminate();
                    return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(new ResponseMessage("error", "Failed to initialize Queue Producer"));
                } 

                // Adiciona a mensagem na fila e encerra o produtor após o uso
                MessageQueueProducer.add(message);
                MessageQueueProducer.terminate();
                return ResponseEntity.ok(new ResponseMessage("success", 
                    "QUEUE Message sent by " + userName + ": " + msgContent));
                
            // Retorna erro caso o tipo de mensagem não seja "TOPIC" ou "QUEUE"
            } else {
                return ResponseEntity.badRequest().body(new ResponseMessage("error", 
                    "tipo de mensagem '" + type + "' é inválido!"));
            }
        } catch (Exception e) {
            // Captura exceções inesperadas e retorna uma resposta de erro interno
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ResponseMessage("error", "Erro durante o envio da mensagem: " + e.getMessage()));
        }
    }
}
