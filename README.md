# Chatbot WhatsApp para Agendamento de Eventos


Este projeto tem como objetivo o desenvolvimento de um chatbot integrado ao WhatsApp, capaz de realizar o agendamento automático de eventos por meio de processamento de linguagem natural (NLP). O sistema permite que usuários interajam de forma intuitiva, utilizando linguagem natural para criar, consultar e cancelar compromissos.

O projeto foi desenvolvido como parte de um trabalho acadêmico na área de Inteligência Artificial, demonstrando a aplicação prática de modelos de linguagem, integração de APIs e manipulação de banco de dados.


## Objetivo
Criar um sistema capaz de interpretar mensagens em linguagem natural e convertê-las em ações estruturadas de agendamento, oferecendo uma experiência automatizada e eficiente para o usuário.


## Arquitetura do Sistema

O sistema é composto por diferentes camadas que se comunicam entre si:

Usuário (WhatsApp)
→ Evolution API (integração com WhatsApp)
→ Flask (Webhook)
→ FastAPI (Backend principal)
→ Modelo de IA (Groq – LLM)
→ PostgreSQL (Banco de dados)
→ Retorno da resposta ao usuário

## Funcionamento

O usuário envia uma mensagem pelo WhatsApp, por exemplo:

“Quero marcar uma reunião sexta às 14h na sala 3”

O sistema realiza os seguintes passos:

1. Recebe a mensagem via webhook.
2. Envia a mensagem ao backend.
3. O modelo de IA interpreta a intenção e extrai os dados relevantes.
4. O backend processa a lógica de negócio.
5. O banco de dados é consultado ou atualizado.
6. Uma resposta é gerada e enviada ao usuário.


## Processamento de Linguagem Natural (NLP)

A aplicação utiliza um modelo de linguagem para:

* Identificar a intenção do usuário (marcar, consultar ou cancelar)
* Extrair entidades relevantes (evento, data, hora e local)
* Lidar com linguagem natural e expressões informais

Exemplo de interpretação:

Entrada do usuário:
“Marca reunião amanhã às 14h na sala 3”

Saída estruturada:
intencao: marcar
evento: reunião
data: 08/05/2026
hora: 14:00
local: sala 3


## Tecnologias Utilizadas

* Linguagem: Python
* Backend: FastAPI
* Webhook: Flask
* Integração com WhatsApp: Evolution API
* Inteligência Artificial: Groq (modelo LLM)
* Banco de Dados: PostgreSQL
* Ferramenta de teste: ngrok

## Estrutura do Projeto

app.py
Responsável por receber as mensagens do WhatsApp através do webhook e encaminhá-las ao backend.

main.py
Contém a lógica principal da aplicação, incluindo integração com IA, regras de negócio e comunicação com o banco de dados.

database.py
Implementa as operações relacionadas ao banco de dados, como criação de tabelas, inserção, consulta e atualização de eventos.

.env
Arquivo de configuração contendo as variáveis de ambiente necessárias para execução do sistema.


## Configuração do Ambiente

1. Clonar o repositório
2. Criar e ativar ambiente virtual
3. Instalar dependências
4. Configurar variáveis de ambiente (API keys e conexão com banco)
5. Iniciar o backend FastAPI
6. Iniciar o webhook Flask
7. Expor o serviço com ngrok


## Banco de Dados

A tabela principal do sistema armazena os eventos agendados com os seguintes campos:

* id
* evento
* data
* hora
* local
* status

O sistema implementa validação para evitar conflitos de agendamento, impedindo a criação de eventos duplicados no mesmo horário e local.


## Funcionalidades

* Agendamento de eventos via linguagem natural
* Consulta de compromissos por data
* Cancelamento de eventos
* Tratamento de mensagens incompletas
* Conversão automática de formatos de data

## Formato de Datas

O sistema foi adaptado para o padrão brasileiro:

Entrada do usuário: DD/MM/AAAA
Armazenamento interno: YYYY-MM-DD
Saída exibida: DD/MM/AAAA

Essa abordagem garante compatibilidade com o banco de dados e uma melhor experiência para o usuário.


## Regras

* Não permite agendamento duplicado no mesmo horário e local
* Solicita informações adicionais quando a mensagem estiver incompleta
* Retorna mensagens claras em caso de erro ou conflito


## O projeto demonstra a aplicação prática dos seguintes conceitos:

* Processamento de linguagem natural
* Integração de APIs
* Desenvolvimento de sistemas distribuídos
* Persistência de dados
* Construção de chatbot inteligente

