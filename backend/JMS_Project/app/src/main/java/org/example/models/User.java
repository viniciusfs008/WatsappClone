package org.example.models;

public class User {
    
    private int id; // ou Integer, dependendo do seu uso
    private String name;

    // Construtor padrão
    public User() {
    }

    // Construtor com argumentos (opcional)
    public User(int id, String name) {
        this.id = id;
        this.name = name;
    }

    // Getters e Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
