# Python
Estamos utilizando a instalação `/home/michael/.venv/bin/python`.

# Variáveis de ambiente
As variáveis de ambiente abaixo estão definidas no arquivo `.env`. Utilze dotenv para importar as variáveis.

```bash
OPENROUTER_API_KEY
ARTIFICIAL_ANALYSIS_API_KEY
OPENROUTER_MODEL
SERPAPI_API_KEY
RUN_LIVE_API_TESTS
```

# Documentação
O diretório `docs` contém documentação sobre.
- openrouter_<topic>.md 
   Os modelos de linguagem utilizados no projeto utilizam a API do OpenRouter.
- openalex_<topic>.md
   Api da OpenAlex sobre o grafo artigos científicos.
- langgraph_<topic>.md
   O LangGraph é o framework utilizado para a codificação dos agentes.

**Leia a documentação antes de iniciar a codificação.**

# Metodologia de Desenvolvimento
Adote o ciclo **Red–Green–Refactor** do Test Driven Development (TDD):

1. **Red**: escrever um teste que falha (porque a funcionalidade ainda não existe).
2. **Green**: implementar o código mínimo necessário para o teste passar.
3. **Refactor**: melhorar a implementação, mantendo todos os testes passando.

Adote Design Patterns (ou Padrões de Projeto) que sejam reutilizáveis e comprovados para problemas recorrentes de design.

Evite códigos complexos. Sempre adote uma solução simples e minimalista. 

# Tests
O diretório `tests` contém os testes codificados. Abaixo detalhamos cada um dos grupos de testes:
- test_usage_<provider>.py
   Exemplos de uso dos diferentes provedores. 