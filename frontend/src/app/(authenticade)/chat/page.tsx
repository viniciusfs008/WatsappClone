"use client";

import ThemeSwitcher from "@/components/my/theme-switch";
import { SendHorizontal } from "lucide-react";

import { useEffect, useState } from "react";

// import css
import "./style.css";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@radix-ui/react-avatar";
import { AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Gruppo } from "next/font/google";
import { fetchDataPost } from "@/controler/controler";

interface Message {
  id: number;
  message: string;
  timestamp: string;
  username: string;
}

interface Session {
  id_user: string;
  username: string;
}

interface Conversa {
  messages: Message[];
  session: Session;
  status: string;
}

export default function Chat() {
  const [items, setItems] = useState<
    { nome: string; msg: string; url: string }[]
  >([]);

  // Estado para o usuário
  const [sessao, setSessao] = useState<{ username: string; id_user: string }>();

  useEffect(() => {
    const storedMessages = localStorage.getItem("messages");
    const storedUser = localStorage.getItem("sessao");
    if (storedMessages && storedUser) {
      setItems(JSON.parse(storedMessages));
      setSessao(JSON.parse(storedUser));
    }
  }, []);

  // Estado para a conversa atual, inicializado corretamente
  const [conversa, setConversa] = useState<Conversa>({
    messages: [],
    session: { id_user: "", username: "" },
    status: "",
  });

  // Estado para armazenar o valor do input
  const [inputValue, setInputValue] = useState("");

  // Função para adicionar nova mensagem
  const handleSendMessage = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // Previne o recarregamento da página ao enviar o formulário

    if (inputValue.trim()) {
      const newMessage: Message = {
        id: Date.now(), // Pode usar um ID único, como um timestamp
        message: inputValue,
        timestamp: new Date().toISOString(),
        username: sessao?.username || "",
      };

      // Adiciona a nova mensagem no estado da conversa
      setConversa((prevConversa) => ({
        ...prevConversa,
        messages: [...prevConversa.messages, newMessage],
      }));

      // Limpa o input
      setInputValue("");
    }
  };

  function iniciaChat(nome: string) {
    // Inicializa os parâmetros como um objeto vazio
    let params:
      | { name: string; type: string; id_user?: string; username?: string }
      | undefined;

    // Itera sobre os itens para determinar o tipo e o nome
    items.forEach((item) => {
      if (item.nome === nome) {
        params = {
          name: nome,
          type: item.url === null ? "TOPIC" : "QUEUE",
          id_user: sessao?.id_user,
          username: sessao?.username,
        };
      }
    });
    console.log(params);
    // Verifica se params foi definido antes de fazer a requisição
    if (params) {
      fetchDataPost("/connect", params)
        .then((response) => {
          setConversa({
            messages: response?.data?.messages || [],
            session: {
              id_user: sessao?.id_user || "",
              username: sessao?.username || "",
            },
            status: response?.data?.status || "", // ajuste conforme necessário
          });
        })
        .catch((error) => {
          console.error("Erro ao iniciar o chat:", error);
        });
    } else {
      console.error("Nome não encontrado nos itens.");
    }
  }

  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarHeader className="bg-background p-3 flex flex-row items-center justify-between">
          <h2 className="font-bold text-xl">Conversas</h2>
          <ThemeSwitcher />
        </SidebarHeader>
        <SidebarContent className="bg-background ">
          <SidebarGroup>
            <SidebarGroupContent>
              <SidebarMenu>
                <Command>
                  <CommandInput placeholder="Pesquisar" />
                  <CommandList>
                    <CommandEmpty>Não Encontrado</CommandEmpty>
                    <CommandGroup>
                      {items.map((item) => (
                        <SidebarMenuItem key={item.nome}>
                          <SidebarMenuButton asChild>
                            <CommandItem
                              asChild
                              key={item.nome}
                              value={item.nome}
                            >
                              <a
                                className="h-[64px]"
                                onClick={() => iniciaChat(item.nome)}
                              >
                                <Avatar className="h-10 w-10 flex items-center justify-center dark:bg-slate-600 bg-slate-300 rounded-full">
                                  <AvatarImage src="" />
                                  <AvatarFallback className="font-bold">
                                    {item.nome
                                      .split(" ")
                                      .slice(0, 2)
                                      .map((word) => word[0])
                                      .join("")}
                                  </AvatarFallback>
                                </Avatar>
                                <div className="flex flex-col">
                                  <span className="font-semibold">
                                    {item.nome}
                                  </span>
                                  <span className="text-muted-foreground">
                                    {item.msg}
                                  </span>
                                </div>
                              </a>
                            </CommandItem>
                          </SidebarMenuButton>
                        </SidebarMenuItem>
                      ))}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
      <div className="w-full h-screen flex flex-col">
        <header className="h-[8vh] w-full bg-background p-3 flex items-center border-b">
          <Avatar className="h-10 w-10 flex items-center justify-center dark:bg-slate-600 bg-slate-300 rounded-full">
            <AvatarImage src="" />
            <AvatarFallback className="font-bold">
              {conversa.name
                .split(" ")
                .slice(0, 2)
                .map((word) => word[0])
                .join("")}
            </AvatarFallback>
          </Avatar>
          <h2 className="ps-2 font-semibold text-lg">{conversa.dest}</h2>
        </header>
        <main className="bg-muted w-full h-[84vh]">
          <ScrollArea className="w-full h-[84vh] rounded-md border p-4">
            {conversa.messages.length > 0 ? (
              conversa.messages.map((item) => (
                <div
                  key={item.id}
                  className={`flex my-1 ${
                    item.username === sessao?.username
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  <div
                    className={`p-3 rounded-lg max-w-2xl break-words ${
                      item.username === sessao?.username
                        ? "dark:bg-slate-600 bg-slate-300"
                        : "dark:bg-slate-700 bg-slate-200"
                    }`}
                  >
                    <span>{item.message}</span>
                  </div>
                </div>
              ))
            ) : (
              <div>Nenhuma mensagem para exibir.</div>
            )}
          </ScrollArea>
        </main>
        <footer className="h-[8vh] w-full bg-background flex flex-row items-center">
          <form
            className="w-full flex flex-row items-center py-1 px-3"
            onSubmit={handleSendMessage} // Use onSubmit para capturar o envio do formulário
          >
            <input
              className="w-full border bg-muted text-md p-2 rounded-md"
              placeholder="Digite sua mensagem"
              value={inputValue} // Conecte o estado do input
              onChange={(e) => setInputValue(e.target.value)} // Atualiza o estado conforme o usuário digita
            />
            <button
              className="rounded-md p-3 text-muted-foreground hover:text-accent-foreground"
              type="submit"
            >
              <SendHorizontal className="" />
            </button>
          </form>
        </footer>
      </div>
    </SidebarProvider>
  );
}
