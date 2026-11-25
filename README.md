# TTFIT — Time to Fitness

## 1. Identificação do Projeto

- **Nome:** TTFIT — Time to Fitness
- **Curso:** Análise e Desenvolvimento de Sistemas (ADS)
- **Instituição:** Fatec Antônio Russo — São Caetano do Sul
- **Ano:** 2026
- **Tipo:** Projeto acadêmico de desenvolvimento de software
- **Integrantes:**
  - André Carvalho Ferreira
  - Gabriel Augusto Rosendo da Silva
  - Pedro Victor Blanco Nogueira
  - Pedro Paulo Tiozzo

## 2. Contexto e Justificativa

O TTFIT é uma aplicação voltada ao acompanhamento da alimentação e da evolução nutricional. A proposta é facilitar o registro de alimentos consumidos, permitindo visualizar a quantidade de calorias e macronutrientes ingeridos ao longo do dia.

O projeto busca reunir informações importantes para o acompanhamento de hábitos alimentares e, futuramente, de atividades físicas em uma única plataforma.

## 3. Objetivos

- Desenvolver uma aplicação para acompanhamento nutricional.
- Permitir o registro de alimentos e suas respectivas porções.
- Calcular calorias, proteínas, carboidratos e gorduras.
- Apresentar os dados nutricionais de maneira visual.
- Desenvolver futuramente recursos de acompanhamento de atividades físicas e reconhecimento de alimentos por imagem.

## 4. Público-alvo

Pessoas interessadas em acompanhar sua alimentação, monitorar o consumo de calorias e macronutrientes e melhorar seus hábitos relacionados à saúde e ao condicionamento físico.

## 5. Escopo Funcional

| Funcionalidade | Descrição | Situação |
|---|---|---|
| Painel de desempenho | Exibe o consumo diário de calorias e macronutrientes. | Implementado |
| Registro de alimentos | Permite selecionar alimentos e informar a quantidade consumida em gramas. | Implementado |
| Diário alimentar | Exibe os alimentos registrados durante o dia. | Implementado |
| Remoção de registros | Permite excluir um alimento ou limpar o diário do dia. | Implementado |
| Distribuição de macronutrientes | Apresenta a proporção de proteínas, carboidratos e gorduras em gráfico. | Implementado |
| Banco de alimentos | Disponibiliza alimentos com informações nutricionais demonstrativas. | Implementado |
| Acompanhamento de atividades físicas | Permite registrar e acompanhar exercícios. | Planejado |
| Metas personalizadas | Possibilita configurar objetivos nutricionais e físicos. | Planejado |
| Reconhecimento por imagem | Sugere alimentos a partir de fotografias, com confirmação do usuário. | Planejado |

## 6. Escopo Não Funcional

- Interface responsiva para diferentes tamanhos de tela.
- Navegação simples e intuitiva.
- Organização do código em arquivos e módulos.
- Armazenamento local dos registros nutricionais em SQLite e suporte configurável a MySQL para contas e perfis.
- Comunicação entre frontend e backend por meio de API.
- Utilização de tecnologias acessíveis e adequadas ao desenvolvimento acadêmico.

## 7. Mapa do Site

- **Página inicial / Painel:** resumo do consumo nutricional diário.
- **Alimentação:** seleção e registro de alimentos.
- **Progresso:** visualização da distribuição de macronutrientes.
- **Diário alimentar:** consulta e gerenciamento dos registros do dia.

## 8. Conteúdo e Identidade Visual

A identidade visual do TTFIT utiliza uma proposta esportiva, moderna e minimalista, com predominância de tons escuros, verde e elementos em branco.

A interface apresenta:
- Logotipo e identidade visual próprios.
- Painel com indicadores nutricionais.
- Gráficos para visualização de macronutrientes.
- Componentes organizados em cartões.
- Layout adaptável para dispositivos móveis.

**Slogan:** TIME TO FITNESS.

## 9. Tecnologias e Ferramentas

| Tecnologia / Ferramenta | Aplicação |
|---|---|
| HTML5 | Estrutura das páginas |
| CSS3 | Estilização e responsividade |
| JavaScript | Interatividade e atualização dos dados |
| Python | Desenvolvimento do backend |
| FastAPI | Construção da API |
| SQLite | Armazenamento dos dados |
| MySQL | Armazenamento opcional de contas e perfis para consulta no phpMyAdmin |
| Chart.js | Geração de gráficos |
| Visual Studio Code | Ambiente de desenvolvimento |
| Git e GitHub | Controle de versão e hospedagem do código |

## 10. Cronograma e Divisão de Tarefas

O desenvolvimento está organizado em etapas:

1. Definição da proposta e identidade visual.
2. Desenvolvimento da interface frontend.
3. Implementação da API em Python.
4. Criação do banco de dados e integração com a interface.
5. Implementação do registro e acompanhamento nutricional.
6. Testes e ajustes da aplicação.
7. Desenvolvimento das funcionalidades futuras.

## 11. Riscos e Restrições

- Os valores nutricionais atualmente cadastrados são demonstrativos e precisam ser substituídos por informações de uma fonte confiável.
- O reconhecimento de alimentos por imagem ainda não foi implementado.
- O diário alimentar continua no SQLite local; contas e perfis usam MySQL quando a conexão é configurada.
- A conexão MySQL depende de credenciais próprias do banco e de o banco selecionado já existir.
- A disponibilidade da aplicação depende da execução local do frontend e do backend.

## 12. Documentação

A documentação do projeto será mantida neste repositório, incluindo informações sobre a proposta, tecnologias utilizadas, funcionalidades implementadas e etapas futuras de desenvolvimento.

## 13. Estrutura de Arquivos

```text
TTFIT/
│
├── frontend/
│   ├── assets/
│   │   ├── ttfit-logo.png
│   │   ├── ttfit-mark.png
│   │   └── ttfit-watermark.png
│   │
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   ├── app.js
│   │   └── auth.js
│   │
│   ├── index.html
│   ├── login.html
│   └── perfil.html
│
├── backend/
│   ├── auth_store.py
│   ├── mysql_schema.sql
│   ├── main.py
│   └── requirements.txt
│
├── .env.example
├── index.html
├── iniciar_api.py
├── iniciar_ttfit.py
└── README.md
```

O banco de dados `ttfit.db` é criado automaticamente pelo backend durante a execução.

## 14. Situação do Projeto

**Status: Em desenvolvimento.**

O TTFIT possui um protótipo com interface web, API em Python e banco de dados SQLite. As funcionalidades iniciais de registro alimentar e acompanhamento nutricional estão implementadas.

As próximas etapas incluem a ampliação do cadastro de alimentos, a integração com fontes nutricionais confiáveis, o acompanhamento de atividades físicas, a configuração de metas e o reconhecimento de alimentos por imagem.

## Ferramentas de dados em Python (Linguagem de Programacao I)

O script `backend/data_tools.py` integra leitura e cadastro de alimentos em CSV/JSON ao banco SQLite usado pelo TTFIT. Ele tambem pesquisa alimentos, calcula totais nutricionais do diario e exporta o catalogo ou o diario em CSV/JSON. As funcoes podem ser importadas por outros modulos Python; a interface de linha de comando permite demonstrar cada operacao.

Execute os comandos na pasta principal do projeto, com as dependencias do backend instaladas:

```text
python backend/data_tools.py list-foods
python backend/data_tools.py search arroz
python backend/data_tools.py add-food "Batata doce" --calorias 86 --proteina 1.6 --carboidratos 20.1 --gordura 0.1
python backend/data_tools.py import-foods alimentos.json
python backend/data_tools.py import-foods alimentos.csv
python backend/data_tools.py summary
python backend/data_tools.py summary --date 2026-11-25
python backend/data_tools.py export-foods alimentos-exportados.json
python backend/data_tools.py export-entries diario.csv
```

Os arquivos de entrada devem conter alimentos com os campos `name`, `calories_100g`, `protein_100g`, `carbs_100g` e `fat_100g`. O JSON pode ser uma lista de objetos ou um objeto com a propriedade `foods`. O CSV deve usar esses mesmos nomes como cabecalho. Valores devem ser nao negativos; nomes repetidos ou registros invalidos cancelam a importacao inteira. Exporte para uma pasta fora do repositorio quando nao quiser adicionar arquivos de dados ao projeto.

O script compartilha a base local `backend/ttfit.db` com a API: alimentos importados ficam disponíveis na interface, e os comandos `summary` e `export-entries` processam os mesmos registros feitos pelo site.

## Contas, login e perfil

As páginas `frontend/login.html` e `frontend/perfil.html` permitem criar conta, entrar, consultar e editar os dados do perfil, sair e excluir a conta. O botão do cabeçalho mostra **Entrar** quando não há sessão e **Perfil** quando o usuário está autenticado. As senhas são armazenadas como hashes PBKDF2; a sessão usa cookie assinado.

Inicie o sistema por `python iniciar_ttfit.py`. O inicializador prepara as dependências e só abre o site depois de confirmar que a API respondeu em `http://127.0.0.1:8000/api/health`. Abrir apenas `frontend/index.html` ou iniciar apenas um servidor estático não inicia a API necessária para login e cadastro.

Se estiver usando o Live Server para o frontend, inicie somente a API em outra janela do terminal com `python iniciar_api.py`. A página do Live Server deve estar em `http://127.0.0.1:5500` para que a origem seja aceita pela API. O processo da API permanece aberto no terminal até Ctrl+C.

Para guardar as contas em MySQL e consultá-las no phpMyAdmin:

1. Crie/seleciona um banco de dados no phpMyAdmin com o usuário MySQL da aplicação.
2. Copie `.env.example` para `.env` e preencha `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` e `MYSQL_DATABASE` com os parâmetros de conexão MySQL (não os do login do painel).
3. Defina `TTFIT_SESSION_SECRET` com um segredo aleatório. Em hospedagem HTTPS, defina `TTFIT_HTTPS_ONLY=true`.
4. Inicie o TTFIT. O backend cria a tabela `g01_users` automaticamente; alternativamente, execute `backend/mysql_schema.sql` no banco selecionado.

Sem as variáveis MySQL, as contas ficam no SQLite local para desenvolvimento. O diário de alimentação continua no SQLite nas duas configurações. A conta inclui nome/e-mail e os campos opcionais idade, altura, peso e objetivo. O perfil não armazena senha em texto puro.
