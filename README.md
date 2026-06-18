# Chatbot Inteligente para Agendamento de Compromissos

## Sobre o Projeto

Este projeto consiste no desenvolvimento de um chatbot inteligente para o Telegram capaz de auxiliar usuários no gerenciamento de compromissos por meio de linguagem natural.

O sistema utiliza Inteligência Artificial para interpretar mensagens enviadas pelo usuário, identificar sua intenção e realizar operações de cadastro, consulta e cancelamento de compromissos.

A aplicação foi desenvolvida utilizando Python, FastAPI, Flask, PostgreSQL e a API da Groq, proporcionando uma comunicação simples e intuitiva através do Telegram.


## Objetivos

O projeto tem como objetivo desenvolver um assistente virtual capaz de:

* Interpretar mensagens escritas em linguagem natural;
* Identificar a intenção do usuário;
* Agendar compromissos;
* Consultar compromissos cadastrados;
* Cancelar compromissos existentes;
* Armazenar o histórico de conversas para fornecer contexto durante as interações.


## Tecnologias Utilizadas

* Python 3
* FastAPI
* Flask
* PostgreSQL
* Groq API (Llama 3.3 70B Versatile)
* Telegram Bot API
* Pydantic
* Requests
* Psycopg2
* Python Dotenv

## Estrutura do Projeto

```text
Projeto/
│
├── app.py
├── main.py
├── database.py
├── requirements.txt
├── requirements_fastapi.txt
├── .env
└── README.md
```


## Descrição dos Arquivos

### app.py

Responsável por receber as mensagens enviadas pelo Telegram através do webhook e encaminhá-las para a API principal.


### main.py

Contém toda a lógica da aplicação.

É responsável por:

* receber as mensagens;
* recuperar o histórico do usuário;
* enviar a mensagem para a IA;
* interpretar a resposta;
* realizar operações no banco de dados;
* enviar a resposta ao usuário.

### database.py

Responsável pelas operações de banco de dados, incluindo:

* criação das tabelas;
* armazenamento do histórico;
* cadastro de eventos;
* consulta de eventos;
* cancelamento de eventos.

## Funcionamento

O chatbot segue o seguinte fluxo:

1. O usuário envia uma mensagem pelo Telegram.
2. O webhook recebe essa mensagem.
3. A mensagem é enviada para a API desenvolvida em FastAPI.
4. O histórico da conversa é recuperado.
5. A IA interpreta a intenção do usuário.
6. O sistema executa a operação correspondente.
7. A resposta é enviada novamente ao Telegram.

## Exemplos de Uso

### Agendar

> Marque uma reunião amanhã às 14h na sala de reuniões.


### Consultar

> Quais compromissos tenho amanhã?


### Cancelar

> Cancelar a reunião de amanhã às 14h.


## Tratamento de Erros

O sistema realiza verificações para:

* mensagens inválidas;
* datas em formato incorreto;
* ausência de informações obrigatórias;
* conflitos de horários;
* falhas de comunicação com a IA.


## Possíveis Melhorias

* Alteração de compromissos existentes;
* Definição de duração do evento;
* Envio de lembretes automáticos;
* Interface Web para gerenciamento;
* Suporte a múltiplos idiomas;
* Melhor tratamento de exceções e logs.

## Equipe

Hugo Martins 

João Marcos

Karine Araujo dos Santos

Mariana Nascimento

## Licença

Projeto desenvolvido exclusivamente para fins acadêmicos.
