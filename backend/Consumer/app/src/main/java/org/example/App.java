package org.example;

import org.example.messaging.UserConsumer;
import org.example.messaging.UserTopicConsumer;
import org.example.services.SendToApi; 
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.example.models.Message;
import org.example.models.Request;
import org.example.models.ResponseMessage;

@RestController
@SpringBootApplication
public class App {

    private static Thread activeConsumerThread; // Variável estática para armazenar a thread ativa

    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }

    @PostMapping("/connect")
    public ResponseEntity<ResponseMessage> sendMessage(@RequestBody Request request) {

        // Validação dos parâmetros da requisição
        if (request == null || request.getApiUrl() == null || request.getBrokerUrl() == null || 
            request.getName() == null || request.getType() == null) {
            return ResponseEntity.badRequest().body(new ResponseMessage("error", 
                "Todos os campos (apiUrl, brokerUrl, name e type) devem ser fornecidos."));
        }

        String name = request.getName();
        String apiUrl = request.getApiUrl();
        String brokerUrl = request.getBrokerUrl();
        String type = request.getType();

        try {
            // Finaliza qualquer thread ativa antes de iniciar uma nova
            if (activeConsumerThread != null && activeConsumerThread.isAlive()) {
                activeConsumerThread.interrupt();
            }

            if (type.equals("QUEUE")) {
                UserConsumer.initialize(brokerUrl, name);

                activeConsumerThread = new Thread(() -> {
                    while (!Thread.currentThread().isInterrupted()) { // Interrompe a thread se solicitado
                        try {
                            if (UserConsumer.inError()) {
                                System.out.println("Error in consumer: " + UserConsumer.error());
                                break;
                            }

                            Message message = UserConsumer.receive();
                            if (message != null) {
                                String msgContent = message.getMessage();
                                String username = message.getUsername();

                                // Enviar dados para a API Flask
                                SendToApi.sendToApi(username, msgContent, apiUrl);

                                // Log da mensagem recebida
                                System.out.println("Received User with ID: " + username);
                                System.out.println("Received User with Name: " + msgContent);
                            }

                            Thread.sleep(1000);

                        } catch (InterruptedException ex) {
                            System.out.println("Consumer thread interrupted.");
                            Thread.currentThread().interrupt(); // Restaura o sinal de interrupção
                            break;
                        } catch (Exception ex) {
                            System.out.println("Error in main loop: " + ex);
                            break;
                        }
                    }
                    UserConsumer.terminate(); // Encerra a conexão ao sair do loop
                });
                activeConsumerThread.start();

            } else if (type.equals("TOPIC")) {
                UserTopicConsumer userConsumer = new UserTopicConsumer(brokerUrl, name);
                userConsumer.start();

                activeConsumerThread = new Thread(() -> {
                    while (!Thread.currentThread().isInterrupted()) {
                        try {
                            if (userConsumer.isInError()) {
                                System.out.println("Error in topic consumer: " + userConsumer.getError());
                                break;
                            }

                            Message message = userConsumer.receive();
                            if (message != null) {
                                String msgContent = message.getMessage();
                                String username = message.getUsername();

                                // Enviar dados para a API Flask
                                SendToApi.sendToApi(username, msgContent, apiUrl);

                                // Log da mensagem recebida
                                System.out.println("Received name: " + username);
                                System.out.println("msg: " + msgContent);
                            }

                            Thread.sleep(1000);

                        } catch (InterruptedException ex) {
                            System.out.println("Topic consumer thread interrupted.");
                            Thread.currentThread().interrupt();
                            break;
                        } catch (Exception ex) {
                            System.out.println("Error in main loop: " + ex);
                            break;
                        }
                    }
                    userConsumer.close();
                });
                activeConsumerThread.start();

            } else {
                return ResponseEntity.badRequest().body(new ResponseMessage("error", "Tipo inválido. Use 'QUEUE' ou 'TOPIC'."));
            }

            return ResponseEntity.ok(new ResponseMessage("success", "Conectado com sucesso."));

        } catch (Exception ex) {
            System.out.println("Erro na função principal: " + ex);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(new ResponseMessage("error", "Erro no processamento."));
        }
    }
}
