// src/hooks/useChat.ts
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface Message {
  username: string;
  message: string;
}

const useChat = (room: string, username: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    // Conecta ao servidor Socket.IO
    const newSocket = io('http://192.168.0.110:5000'); // Substitua com o endereço do seu backend
    setSocket(newSocket);

    // Quando conectado, entre na sala especificada
    newSocket.emit('join', { room, username });

    // Recebe novas mensagens do servidor
    newSocket.on('new_message', (data: Message) => {
      setMessages((prevMessages) => [...prevMessages, data]);
    });

    // Cleanup ao sair da sala e desconectar o socket
    return () => {
      newSocket.emit('leave', { room });
      newSocket.disconnect();
    };
  }, [room]);

  return { messages, socket };
};

export default useChat;
