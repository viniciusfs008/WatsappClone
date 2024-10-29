package org.example.models;


//Classe mensagem para envio da requisição para API Flask
public class Message {

    private String username;
    private String message;

    // Construtor padrão
    public Message() {
    }

    // Construtor com argumentos
    public Message(String username, String message) {  
        this.username = username;
        this.message = message;

    }

    // Getters e Setters
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }


    @Override
    public String toString() {
        return "Message{" +
                "username='" + username + '\'' +
                ", message='" + message + '\'' +
                '}';
    }
}
