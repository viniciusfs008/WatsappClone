# Instalação do Gradle em Linux e macOS

Este guia detalha o processo de instalação do Gradle em sistemas Linux e macOS, permitindo que você configure o ambiente para construir projetos Java, Kotlin e outros.

## Pré-requisitos

- **Java JDK 8 ou superior**: O Gradle requer que o Java esteja instalado e configurado no sistema.
  - Verifique se o Java está instalado executando:
    ```bash
    java -version
    ```
  - Se o Java não estiver instalado, consulte as instruções de instalação:
    - [Instruções de instalação do Java no Linux](https://docs.oracle.com/javase/8/docs/technotes/guides/install/linux_jdk.html)
    - [Instruções de instalação do Java no macOS](https://docs.oracle.com/javase/8/docs/technotes/guides/install/mac_jdk.html)

---

## Instalação do Gradle

### Método 1: Instalação via SDKMAN

#### 1. Instalar o SDKMAN

1. Abra o terminal e instale o SDKMAN, que gerencia versões do Gradle, Java, entre outros:
    ```bash
    curl -s "https://get.sdkman.io" | bash
    source "$HOME/.sdkman/bin/sdkman-init.sh"
    ```
2. Verifique se o SDKMAN foi instalado corretamente:
    ```bash
    sdk version
    ```

#### 2. Instalar o Gradle

1. Instale o Gradle usando o SDKMAN:
    ```bash
    sdk install gradle
    ```
2. Verifique se o Gradle foi instalado com sucesso:
    ```bash
    gradle -v
    ```

### Método 2: Instalação Manual

1. **Baixar a última versão do Gradle**:
   - Visite a [página de download do Gradle](https://gradle.org/releases/) e baixe o arquivo `.zip` da última versão.

2. **Extrair o arquivo**:
   - No terminal, navegue até a pasta onde o arquivo foi baixado e extraia-o:
     ```bash
     mkdir /opt/gradle
     sudo unzip -d /opt/gradle gradle-*.zip
     ```

3. **Configurar o PATH**:
   - Adicione o diretório `bin` do Gradle ao PATH do sistema:
     ```bash
     echo 'export PATH=$PATH:/opt/gradle/gradle-<version>/bin' >> ~/.bashrc
     source ~/.bashrc
     ```
   - Substitua `<version>` pela versão do Gradle baixada, como `7.6`.

4. **Verificar a instalação**:
   - Confirme que o Gradle foi instalado executando:
     ```bash
     gradle -v
     ```

---

## Verificando a Instalação

Para verificar se a instalação foi concluída com sucesso, use:
```bash
gradle -v
```

<br><br><br><br><br>

# Projeto - Inicialização e Configuração

Este documento contém as instruções para configurar e iniciar o projeto utilizando Gradle e Docker. Certifique-se de seguir todos os passos para garantir que os componentes necessários estejam em execução.

## Pré-requisitos

- **Gradle**: Verifique se o Gradle está instalado. Se necessário, consulte a [documentação de instalação do Gradle](https://gradle.org/install/).
- **Docker e Docker Compose**: Verifique se o Docker e o Docker Compose estão instalados e configurados.

---

## Passo a Passo

### 1. Executar o Gradle nas Pastas `Consumer` e `JMS_Project`

1. Abra um terminal e navegue até a pasta `Consumer`:
   ```bash
   cd backend/Consumer
   ```
2. Execute o projeto utilizando o Gradle:
   ```bash
   gradle run
   ```
3. Em um novo terminal, navegue até a pasta `JMS_Project`:
   ```bash
   cd d backend/JMS_Project
   ```
4. Execute o projeto utilizando o Gradle:
   ```bash
   gradle run
   ```

Esses comandos irão iniciar as tarefas definidas no `build.gradle` de cada uma dessas pastas.

### 2 Iniciar Frontend Banco de Dados e API Flask

1. Execute o Docker Compose para construir e iniciar os containers da API e do banco de dados:
   ```bash
   docker compose up --build
   ```

### 3. Inicializar o Banco de Dados e a API Flask separados

1. Abra um terminal e navegue até a pasta `banckend/api-flask`:
   ```bash
   cd api-flask
   ```
2. Execute o Docker Compose para construir e iniciar os containers da API e do banco de dados:
   ```bash
   docker compose up --build
   ```

Esse comando irá:
   - Construir os containers definidos no arquivo `docker-compose.yml`.
   - Inicializar o banco de dados `flask_db` e a API Flask `flask_app`.

### 3. Verificação

Após seguir os passos acima:
- **API Flask**: Verifique se a API está acessível em `http://localhost:<porta_definida>`.
- **Banco de Dados**: O container `flask_db` deve estar em execução e acessível para a API.

### Resumo dos Comandos

```bash
# Executar Gradle nas pastas Consumer e JMS_Project
cd Consumer
gradle run
cd ../JMS_Project
gradle run

# Subir os containers do Docker na pasta api-flask
cd ../WatappClone
ou
cd ../api-flask

docker compose up --build
```

---

Com esses passos, o projeto estará configurado e pronto para uso. Se houver problemas, verifique a saída dos terminais e confirme que as dependências estão instaladas corretamente.

## Suporte

Para dúvidas ou problemas, entre em contato com o administrador do projeto.
