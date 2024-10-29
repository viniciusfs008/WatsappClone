package org.example.services;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class SendToApi {
    // Método para enviar mensagens consumidas para a API Flask
    public static void sendToApi(String username, String message, String apiUrl) {
        try {
            // Criar objeto JSON corretamente formatado
            String jsonInputString = String.format("{\"username\": \"%s\", \"message\": \"%s\"}", username, message);
            
            System.out.println("URL da API: " + apiUrl); // Adicionando um log para depuração

            // Configuração da conexão HTTP
            URL url = new URL(apiUrl);
            HttpURLConnection con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("POST");
            con.setRequestProperty("Content-Type", "application/json; utf-8");
            con.setRequestProperty("Accept", "application/json");
            con.setDoOutput(true);

            // Enviar os dados
            try (OutputStream os = con.getOutputStream()) {
                byte[] input = jsonInputString.getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            // Verificar a resposta
            int responseCode = con.getResponseCode();
            System.out.println("Response Code: " + responseCode);

        } catch (Exception e) {
            System.out.println("Error sending data to API: " + e.getMessage());
        }
    }
}
