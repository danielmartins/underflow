Underflow
=========
:License: GPLv3


Pesquisa no StackOverflow
-------------------------

Este projeto disponibiliza um comando CLI que coordena ações com o objetivo
de realizar pesquisa no StackOverflow, possui 2 interfaces de uso:

  * Pesquisas por CLI
  * Pesquisas por Bot Telegram


Arquitetura do projeto
----------------------

O Projeto está dividido hein:

  * API de Comunicação com StackOverflow
    * Executa pesquisa na API;
    * Executa paginação preemptiva
    * Captura token de autenticação com a API do Stack OverFlow (Para permitir maior quota de requisições)
  * CLI de interação com a API de Comunicação
    * Interage com a API interna de comunicação
    * Redireciona requisição de autenticação OAuth pro StackOverFlow, modo implicito.
  * Bot Server
    * Responde as solicitações de pessoas interagindo com o bot


Pré-requisitos
--------------

Antes de qualquer interação de pesquisa, você precisa iniciar a API de comunicação com o StackOverflow.

Portanto abra um novo terminal e execute:

  $ underflow start-api

Pesquisas via CLI
^^^^^^^^^^^^^^^^^

É permitido o uso da CLI sem pre-requisitos de autenticação.

  $ underflow ask "python + fastapi"


Authenticação
^^^^^^^^^^^^^

Existe um limite de requisições. Caso necessite de autenticação, será preciso que você se autentique e
autorize este aplicativo a realizar pesquisas.

Para viabilizar essa autenticação é necessário algumas informações sensíveis que podem
ser obtidas com o author deste projeto. De posse dessas informações,
coloque as informações como variaveis de ambiente e siga os passos.

Após inserir, você pode executar o comando de autenticação:

  $ underflow authenticate

O comando abrirá o Google Chrome, redirecionando você para mecanismo de autenticação e autorização do StackOverflow,
uma vez autorizado, você será redirecionado para uma página localhost para que a API interna possa capturar o token e
salvar em memória. Após isso pode continuar realizando as consultas.



Telegram BOT
^^^^^^^^^^^^

O nome do bot no Telegram é UnderflowBot. Para responder as solicitações oriundas do bot, você precisa de algumas
informações secretas de integração, solicitar para o author. De posse dessa informações, voce exporta para variaveis
de ambiente e executar o comando abaixo para responder as solicitações.

  $ underflow bot start


Desenvolvimento
---------------

Projeto foi desenvolvido principalemente com poetry + fastapi + typer + pytest, as demais dependências são utilitários.



Instalaçao de dependências
--------------------------

  $ poetry install 


Testes
------

  $ poetry run pytest



Possível Roadmap Futuro
-----------------------

  * Desenvolvedor botserver em arquitetura serverless(aws lambda)
  * Implementar autenticação entre as camadas
  * Implementar controle de background e foreground
  * Implementar respostas interativas para o bot do Telegram
