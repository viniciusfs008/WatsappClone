package org.example.models;

// classe Resquest com o tipo de requisição e parametros
// recebidos da API flask
public class Request {

    // URL da ActiveMQ
    private String brokerUrl;
    // URL da API Flask
    private String apiUrl;
    // Nome da Queue ou TOPIC registrada no ActiveMQ
    private String name;
    // Tipo do destino (QUEUE ou TOPIC)
    private String type;

    private String status;

    // Construtor padrão
    public Request() {
        this.status = "disconnected";
    }

    // Construtor com argumentos
    public Request(String brokerUrl, String apiUrl, String name, String type) {  
        this.brokerUrl = brokerUrl;
        this.apiUrl = apiUrl;
        this.name = name;
        this.type = type;
        this.status = "connected";
    }

    // Getters e Setters
    
    public String getBrokerUrl() {
        return brokerUrl;
    }

    public void setBrokerUrl(String brokerUrl) {
        this.brokerUrl = brokerUrl;
    }

    public String getApiUrl() {
        return apiUrl;
    }

    public void setApiUrl(String apiUrl) {
        this.apiUrl = apiUrl;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getType(){
        return type;
    }

    public void setType(String type){
        this.type = type;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

}