package org.example.models;

public class Message {

    private Integer id; // Uso de Integer para permitir valores nulos, se necessário
    private String username;
    private String message;

    // Atributos adicionais (brokerUrl, name, type) para representar o tópico ou fila
    private String brokerUrl;
    private String name;
    private String type; // Enum para definir o tipo de destino (QUEUE ou TOPIC)

    // Construtor padrão
    public Message() {
    }

    // Construtor com dois argumentos
    public Message(String username, String message) {
        this.username = username;
        this.message = message;

    }

    // Construtor com argumentos
    public Message(String name, String username, String message, String brokerUrl, String type) {
        this.name = name;
        this.username = username;
        this.message = message;
        this.brokerUrl = brokerUrl;
        this.type = type;
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

    public String getBrokerUrl() {
        return brokerUrl;
    }

    public void setBrokerUrl(String brokerUrl) {
        this.brokerUrl = brokerUrl;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    @Override
    public String toString() {
        return "Message{" +
                "id=" + id +
                ", username='" + username + '\'' +
                ", message='" + message + '\'' +
                ", brokerUrl='" + brokerUrl + '\'' +
                ", name='" + name + '\'' +
                ", type=" + type +
                '}';
    }
}
