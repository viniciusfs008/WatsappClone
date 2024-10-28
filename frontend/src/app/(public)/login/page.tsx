"use client";

import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

import { fetchDataPost } from "@/controler/controler";
import { redirect } from "next/dist/server/api-utils";
import { useState } from "react"; // Importando useState
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
// import { toast } from "sonner";
import { toast, ToastContainer } from "react-toastify"; // Importando o Toast
import "react-toastify/dist/ReactToastify.css"; // Importando estilos do Toast

export default function Login() {
  const router = useRouter();

  function cadastrar(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);
    const params = {
      username: formData.get("newusername"),
      password: formData.get("newpassword"),
    };

    // Chama a função para enviar dados de login
    fetchDataPost("/register", params)
      .then((response) => {
        console.log(response);
        // Supondo que o login seja bem-sucedido, redirecione para a página de chat
        if (response?.status === 201) {
          toast.success("Cadastro realizado com sucesso!", {
            position: "top-right", // Posição do toast
            autoClose: 5000, // Fechar automaticamente após 5 segundos
          });
        } else {
          toast.error("Usuario já cadastrado. Tente novamente.", {
            position: "top-right", // Posição do toast
            autoClose: 5000, // Fechar automaticamente após 5 segundos
          });
        }
      })
      .catch((error) => {
        toast.error("Ocorreu um erro. Tente novamente mais tarde.", {
          position: "top-right", // Posição do toast
          autoClose: 5000, // Fechar automaticamente após 5 segundos
        });
      });
  }

  function logar(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);
    const username = formData.get("username");
    const params = {
      username: username,
      password: formData.get("password"),
    };

    // Chama a função para enviar dados de login
    fetchDataPost("/login", params)
      .then((response) => {
        // Supondo que o login seja bem-sucedido, redirecione para a página de chat
        if (response?.status === 200) {
          if (username) {
            // Filtra os dados que você deseja armazenar
            const filteredMessages = response.data.message
              .map((msg: any) => {
                if (msg.topic_name) {
                  return {
                    nome: msg.topic_name,
                    msg: msg.last_message,
                    url: null,
                  };
                } else if (msg.friend_name) {
                  return {
                    nome: msg.friend_name,
                    msg: msg.last_message,
                    url: msg.queue_name,
                  };
                }
                return null; // Ignora itens sem os campos desejados
              })
              .filter(Boolean); // Remove qualquer null do array
              
            localStorage.setItem("messages", JSON.stringify(filteredMessages));
            localStorage.setItem("username", JSON.stringify(username));
          }
          router.push("/chat");
        } else {
          toast.error("Usuario ou Senha incorretos. Tente novamente.", {
            position: "top-right", // Posição do toast
            autoClose: 5000, // Fechar automaticamente após 5 segundos
          });
        }
      })
      .catch((error) => {
        toast.error("Ocorreu um erro. Tente novamente mais tarde.", {
          position: "top-right", // Posição do toast
          autoClose: 5000, // Fechar automaticamente após 5 segundos
        });
      });
  }

  return (
    <div className="w-full h-screen flex items-center justify-center">
      <ToastContainer /> {/* Adiciona o container para os toasts */}
      <Tabs defaultValue="entrar" className="w-[400px]">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="entrar">Entrar</TabsTrigger>
          <TabsTrigger value="cadastrar">Cadastrar</TabsTrigger>
        </TabsList>

        {/* Tab de Login */}
        <TabsContent value="entrar">
          <Card>
            <CardHeader>
              <CardTitle>Entrar</CardTitle>
              <CardDescription>
                Entre com um usuário já cadastrado.
              </CardDescription>
            </CardHeader>
            <form onSubmit={logar}>
              <CardContent className="space-y-2">
                <div className="space-y-1">
                  <Label htmlFor="username">Usuário</Label>
                  <Input
                    id="username"
                    name="username"
                    placeholder="usuário"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="password">Senha</Label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Senha"
                    required
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit">Entrar</Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>

        {/* Tab de Cadastro */}
        <TabsContent value="cadastrar">
          <Card>
            <CardHeader>
              <CardTitle>Cadastrar</CardTitle>
              <CardDescription>Cadastre um novo usuário.</CardDescription>
            </CardHeader>
            <form onSubmit={cadastrar}>
              <CardContent className="space-y-2">
                <div className="space-y-1">
                  <Label htmlFor="newusername">Usuário</Label>
                  <Input
                    id="newusername"
                    name="newusername"
                    placeholder="usuário"
                    required
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="newpassword">Senha</Label>
                  <Input
                    id="newpassword"
                    name="newpassword"
                    type="password"
                    placeholder="Senha"
                    required
                  />
                </div>
              </CardContent>
              <CardFooter>
                <Button type="submit">Cadastrar</Button>
              </CardFooter>
            </form>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
