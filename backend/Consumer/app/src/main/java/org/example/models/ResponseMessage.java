package org.example.models;



// Padrão de Requisição resposta quando Consumer 
// quer enviar uma resposta de mensagem enviada com sucesso ou uma bad request
public class ResponseMessage {
    private String status;
    private String message;

    public ResponseMessage(String status, String message) {
        this.status = status;
        this.message = message;
    }

    public String getStatus() {
        return status;
    }

    public String getMessage() {
        return message;
    }
}
