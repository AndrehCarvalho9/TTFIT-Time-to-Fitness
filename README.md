
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
- Armazenamento dos registros em banco de dados SQLite.
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
- O protótipo utiliza banco de dados SQLite local.
- A aplicação ainda não possui autenticação e gerenciamento de múltiplos usuários.
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
│   │   └── app.js
│   │
│   └── index.html
│
├── backend/
│   ├── main.py
│   └── requirements.txt
│
├── iniciar_ttfit.py
└── README.md
```

O banco de dados `ttfit.db` é criado automaticamente pelo backend durante a execução.

## 14. Situação do Projeto

**Status: Em desenvolvimento.**

O TTFIT possui um protótipo com interface web, API em Python e banco de dados SQLite. As funcionalidades iniciais de registro alimentar e acompanhamento nutricional estão implementadas.

As próximas etapas incluem a ampliação do cadastro de alimentos, a integração com fontes nutricionais confiáveis, o acompanhamento de atividades físicas, a configuração de metas e o reconhecimento de alimentos por imagem.
