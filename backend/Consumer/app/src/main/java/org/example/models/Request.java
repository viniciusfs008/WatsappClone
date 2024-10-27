package org.example.models;

public class Request {

    private String brokerUrl;
    private String apiUrl;
    private String name;
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