"use client";

import { useState, useEffect } from "react";

export default function ChatPage() {
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    // Recupera o valor de "messages" do localStorage e converte para um objeto
    const storedMessages = localStorage.getItem("messages");
    if (storedMessages) {
      try {
        const parsedMessages = JSON.parse(storedMessages);
        console.log("Mensagens:", parsedMessages);
        setItems(parsedMessages);
      } catch (error) {
        console.error("Erro ao parsear mensagens:", error);
      }
    }
  }, []);

  return (
    <div>
      <h1>Chat</h1>
      {items.length > 0 ? (
        items.map((message, index) => (
          <p key={index}>{JSON.stringify(message)}</p>
        ))
      ) : (
        <p>Nenhuma mensagem encontrada.</p>
      )}
    </div>
  );
}
