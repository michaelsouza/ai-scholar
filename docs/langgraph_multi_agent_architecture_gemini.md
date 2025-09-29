

# **Orquestrando Inteligência: Uma Análise Profunda de Arquiteturas Multi-agentes com LangGraph**

## **Seção 1: O Paradigma LangGraph: De Cadeias Lineares a Grafos com Estado**

A evolução das aplicações de Modelos de Linguagem Grandes (LLMs) revelou uma transição de fluxos de trabalho simples e sequenciais para sistemas complexos, autônomos e interativos. Esta seção estabelece os princípios fundamentais do LangGraph, argumentando que sua gestão explícita de estado e estrutura de grafo cíclico representam uma mudança de paradigma em relação aos frameworks tradicionais e lineares. Essa mudança é o principal facilitador para a construção de sistemas multi-agentes complexos, autônomos e confiáveis.

### **1.1 Além da Lógica Sequencial: A Necessidade de Grafos Cíclicos**

Frameworks tradicionais, como o LangChain, são construídos em torno da ideia de encadear operações em um Grafo Acíclico Dirigido (DAG), onde as tarefas são executadas em uma ordem específica e linear.1 Essa abordagem é eficaz para fluxos de trabalho simples e sem estado, como o padrão "recuperar \-\> resumir \-\> responder".1 No entanto, a natureza acíclica desses frameworks impõe uma limitação crítica aos sistemas agênticos. A verdadeira autonomia exige a capacidade de iterar, tentar novamente, ramificar a lógica e tomar decisões que alterem o fluxo de controle — capacidades que são inerentemente não lineares.

LangGraph aborda diretamente essa limitação ao introduzir a capacidade de criar grafos cíclicos, que são essenciais para o desenvolvimento de runtimes de agentes sofisticados.1 Isso permite loops, ramificações e a capacidade de revisitar estados anteriores, o que é fundamental para sistemas interativos onde o próximo passo depende de condições em evolução ou da entrada do usuário.1 Ao modelar fluxos de trabalho como máquinas de estado, LangGraph oferece um modelo computacional mais poderoso e flexível.3

Essa transição representa uma mudança fundamental no papel do desenvolvedor. Em vez de simplesmente definir um pipeline de dados estático e unidirecional — uma prática que pode ser descrita como "engenharia de fluxo" 7 —, o desenvolvedor passa a projetar uma "arquitetura cognitiva".8 Com as ferramentas do LangGraph para ciclos, estado e roteamento condicional, o desenvolvedor não está mais apenas definindo os passos, mas as

*regras de pensamento* para o sistema de agentes. Dentro dessa arquitetura, o próprio LLM pode controlar o fluxo de trabalho da aplicação, decidindo quais caminhos seguir, quais ferramentas invocar ou se uma resposta é suficiente.9 Essa é uma abstração muito mais poderosa para construir sistemas inteligentes, pois o foco muda da construção de uma função de entrada-saída para a criação de uma entidade dinâmica e com estado que pode raciocinar e operar autonomamente ao longo do tempo.

### **1.2 A Anatomia de um Fluxo de Trabalho LangGraph**

Para construir essas novas arquiteturas cognitivas, LangGraph fornece um conjunto de componentes primitivos. A compreensão desses blocos de construção é essencial para aproveitar todo o potencial do framework.

#### **Estado: A Memória do Sistema**

O estado é o componente central de um grafo LangGraph. Ele funciona como uma estrutura de dados compartilhada que representa o snapshot atual da aplicação.11 Essencialmente, é a memória do grafo, permitindo-lhe manter o contexto através de múltiplos passos e sessões.13 O estado é tipicamente definido usando um

TypedDict ou um modelo Pydantic para garantir a validação do esquema.11

Uma característica fundamental da gestão de estado em LangGraph é o uso de funções redutoras. Por exemplo, a anotação Annotated\[list, add\_messages\] especifica como uma chave de estado deve ser atualizada. Em vez de substituir o valor existente, a função add\_messages anexa novas mensagens a uma lista existente. Isso permite a acumulação de histórico de conversação e outros dados ao longo do tempo, o que é crucial para agentes com estado.14

**Exemplo de Código: Definição de um Estado Complexo**

Python

from typing import TypedDict, Annotated, List  
from langchain\_core.messages import BaseMessage, HumanMessage, AIMessage  
import operator

\# A função redutora 'operator.add' anexa novas mensagens à lista existente.  
class AgentState(TypedDict):  
    messages: Annotated, operator.add\]  
    \# Outras chaves de estado podem ser adicionadas aqui, como contadores ou flags.

#### **Nós: As Unidades de Computação**

Os nós são as unidades fundamentais de trabalho dentro do grafo. Cada nó é tipicamente uma função Python que recebe o estado atual como entrada e retorna um dicionário com as atualizações para o estado.5 Um nó pode encapsular qualquer tipo de lógica: uma chamada a um LLM, a execução de uma ferramenta, uma consulta a um banco de dados ou qualquer lógica de negócios personalizada.5

**Exemplo de Código: Definição de um Nó Simples**

Python

from langchain\_openai import ChatOpenAI

\# Inicializa o LLM que será usado dentro do nó.  
llm \= ChatOpenAI(model="gpt-4o")

\# O nó recebe o estado e retorna um dicionário para atualizar o estado.  
def call\_model\_node(state: AgentState) \-\> dict:  
    """  
    Um nó que invoca o LLM com o histórico de mensagens atual.  
    """  
    messages \= state\["messages"\]  
    response \= llm.invoke(messages)  
    \# Retorna a resposta do LLM para ser adicionada ao estado 'messages'.  
    return {"messages": \[response\]}

#### **Arestas: Os Caminhos de Controle**

As arestas conectam os nós e definem o fluxo de controle do grafo.11 LangGraph suporta dois tipos principais de arestas:

1. **Arestas Normais:** Definem uma transição estática e incondicional de um nó para o outro.  
2. **Arestas Condicionais:** São o principal mecanismo para implementar a tomada de decisão agêntica. Uma aresta condicional é uma função que avalia o estado atual para determinar dinamicamente qual nó executar em seguida. A função retorna uma string que corresponde ao nome do próximo nó a ser invocado.5

**Exemplo de Código: Adicionando Arestas a um Grafo**

Python

from langgraph.graph import StateGraph, START, END

\# Inicializa o construtor do grafo com a definição do estado.  
workflow \= StateGraph(AgentState)

\# Adiciona os nós ao grafo.  
workflow.add\_node("agent", call\_model\_node)  
workflow.add\_node("tool\_executor", execute\_tools\_node) \# Supondo que este nó exista.

\# Define o ponto de entrada do grafo.  
workflow.set\_entry\_point("agent")

\# Define uma função de aresta condicional.  
def should\_continue(state: AgentState) \-\> str:  
    """  
    Decide se continua executando ferramentas ou termina.  
    """  
    last\_message \= state\["messages"\]\[-1\]  
    if "tool\_calls" in last\_message.additional\_kwargs:  
        return "continue"  
    else:  
        return "end"

\# Adiciona a aresta condicional ao grafo.  
workflow.add\_conditional\_edges(  
    "agent",  
    should\_continue,  
    {  
        "continue": "tool\_executor",  
        "end": END  
    }  
)

\# Adiciona uma aresta normal do executor de ferramentas de volta para o agente.  
workflow.add\_edge("tool\_executor", "agent")

\# Compila o grafo em um objeto executável.  
app \= workflow.compile()

### **1.3 Análise Comparativa: LangChain vs. LangGraph**

Para solidificar a compreensão das distinções fundamentais, a tabela a seguir apresenta uma análise comparativa detalhada entre LangChain e LangGraph, sintetizando informações de múltiplas fontes.1

| Característica | LangChain | LangGraph |
| :---- | :---- | :---- |
| **Estrutura do Fluxo de Trabalho** | Linear ou DAG, principalmente de avanço único.2 | Grafo completo com ciclos, ramificações e loops.1 |
| **Gestão de Estado** | Implícita ou local ao componente. Pode passar informações, mas não mantém estado persistente facilmente entre execuções.1 | Centralizada e explícita. O estado é um componente principal que flui através dos nós, permitindo persistência e checkpointing.2 |
| **Caso de Uso Principal** | Prototipagem rápida, pipelines de dados sequenciais e sem estado (ex: RAG simples, sumarização).1 | Sistemas de agentes complexos, resilientes e de longa duração; fluxos de trabalho com estado e interativos (ex: assistentes virtuais, automação de tarefas multi-agentes).1 |
| **Fluxo de Controle** | Primitivas limitadas de ramificação/tentativa.4 | Condicionais de primeira classe, tentativas, e suporte para intervenção humana (human-in-the-loop).4 |
| **Abstrações Chave** | Chains, Runnables, LangChain Expression Language (LCEL).4 | Nós, Arestas, Estado, Roteadores, Checkpointers.4 |
| **Curva de Aprendizagem** | APIs mais simples, mais fácil para iniciantes.4 | Curva de aprendizagem mais acentuada devido à necessidade de definir explicitamente nós e estado.4 |

## **Seção 2: Arquitetando Sistemas Multi-agentes: Padrões e Implementações**

Esta seção constitui o núcleo do relatório, transitando da teoria para a prática ao detalhar os padrões arquitetônicos mais comuns e poderosos para a construção de sistemas multi-agentes em LangGraph. Cada padrão é tratado como um estudo de caso, com uma visão geral conceitual, uma discussão de suas vantagens e uma implementação de código completa e anotada.

### **2.1 A Arquitetura Supervisor-Trabalhador (Equipes Hierárquicas)**

Este padrão envolve um agente central "supervisor" que atua como um roteador ou orquestrador, delegando tarefas a uma equipe de agentes "trabalhadores" especializados.21 É uma abordagem altamente eficaz para decompor problemas complexos em subtarefas modulares e gerenciáveis, espelhando estruturas organizacionais humanas para gerenciar a complexidade.22

A aplicação deste padrão é particularmente valiosa em ambientes empresariais, onde diferentes tarefas exigem ferramentas ou domínios de conhecimento distintos — por exemplo, um agente para consultas a bancos de dados, outro para pesquisa na web e um terceiro para análise de documentos.22 A especialização de agentes mitiga o risco de falha que ocorre quando um único agente monolítico com dezenas de ferramentas tenta selecionar o caminho de raciocínio correto.25 Ao forçar a modularidade, cada agente trabalhador opera com um conjunto limitado de ferramentas e um prompt focado, tornando seu comportamento mais previsível e confiável.22 Essa modularidade também permite o desenvolvimento, teste e melhoria independentes de cada agente, um requisito crítico para a construção de sistemas agênticos escaláveis, sustentáveis e confiáveis em nível empresarial.

#### **Implementação Detalhada**

A comunicação ocorre através de um estado compartilhado (MessagesState). O supervisor recebe a solicitação do usuário e os trabalhadores anexam seus resultados a este histórico de mensagens compartilhado.22 O nó supervisor utiliza um LLM com capacidades de saída estruturada para decidir para qual trabalhador rotear a seguir ou se deve concluir a tarefa (

FINISH).22 Cada trabalhador é, ele próprio, um grafo LangGraph completo e independente (um subgrafo), e o nó trabalhador no grafo principal atua como um invólucro que invoca seu subgrafo e formata a saída antes de devolver o controle ao supervisor.9

#### **Exemplo de Código: Sistema Supervisor-Trabalhador**

O código a seguir, baseado no exemplo abrangente de 22, demonstra a implementação completa de um sistema Supervisor-Trabalhador.

Python

import operator  
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict, Literal  
from langchain\_core.messages import BaseMessage, HumanMessage  
from langchain\_openai import ChatOpenAI  
from langgraph.graph import StateGraph, START, END  
from langgraph.prebuilt import ToolNode  
from langgraph.types import Command

\# 1\. Definir o estado compartilhado para a comunicação  
class AgentState(TypedDict):  
    messages: Annotated, operator.add\]

\# 2\. Definir a saída estruturada para o roteador do supervisor  
class Router(TypedDict):  
    next: Literal

\# 3\. Definir o nó supervisor  
llm \= ChatOpenAI(model="gpt-4o")  
supervisor\_prompt \= (  
    "Você é um supervisor encarregado de gerenciar uma conversa entre os"  
    " seguintes trabalhadores: web\_researcher, rag\_expert. Dada a solicitação do usuário,"  
    " responda com o trabalhador que deve agir em seguida. Quando terminar, responda com FINISH."  
)

def supervisor\_node(state: AgentState) \-\> Command\[Literal\["web\_researcher", "rag\_expert", "\_\_end\_\_"\]\]:  
    messages \= \[  
        {"role": "system", "content": supervisor\_prompt},  
    \] \+ state\["messages"\]  
    response \= llm.with\_structured\_output(Router).invoke(messages)  
    goto \= response\["next"\]  
    if goto \== "FINISH":  
        goto \= END  
    return Command(goto=goto)

\# 4\. Criar uma função fábrica para os agentes trabalhadores (subgrafos)  
def create\_agent(llm, tools):  
    llm\_with\_tools \= llm.bind\_tools(tools)  
    def chatbot(state: AgentState):  
        return {"messages": \[llm\_with\_tools.invoke(state\["messages"\])\]}  
      
    def tools\_condition(state):  
        last\_message \= state\["messages"\]\[-1\]  
        return "tools" if hasattr(last\_message, 'tool\_calls') and last\_message.tool\_calls else "agent"

    graph\_builder \= StateGraph(AgentState)  
    graph\_builder.add\_node("agent", chatbot)  
    tool\_node \= ToolNode(tools=tools)  
    graph\_builder.add\_node("tools", tool\_node)  
    graph\_builder.add\_conditional\_edges("agent", tools\_condition)  
    graph\_builder.add\_edge("tools", "agent")  
    graph\_builder.set\_entry\_point("agent")  
    return graph\_builder.compile()

\# 5\. Definir os nós trabalhadores que invocam seus subgrafos  
\# (Supondo que web\_search\_tool e retriever\_tool estejam definidos)  
web\_search\_agent \= create\_agent(llm, \[web\_search\_tool\])  
def web\_research\_node(state: AgentState) \-\> Command\[Literal\["supervisor"\]\]:  
    result \= web\_search\_agent.invoke(state)  
    return Command(  
        update={"messages": \[HumanMessage(content=result\["messages"\]\[-1\].content, name="web\_researcher")\]},  
        goto="supervisor",  
    )

rag\_agent \= create\_agent(llm, \[retriever\_tool\])  
def rag\_node(state: AgentState) \-\> Command\[Literal\["supervisor"\]\]:  
    result \= rag\_agent.invoke(state)  
    return Command(  
        update={"messages": \[HumanMessage(content=result\["messages"\]\[-1\].content, name="rag\_expert")\]},  
        goto="supervisor",  
    )

\# 6\. Montar o grafo principal  
builder \= StateGraph(AgentState)  
builder.add\_node("supervisor", supervisor\_node)  
builder.add\_node("web\_researcher", web\_research\_node)  
builder.add\_node("rag\_expert", rag\_node)

builder.add\_edge(START, "supervisor")  
builder.add\_edge("web\_researcher", "supervisor")  
builder.add\_edge("rag\_expert", "supervisor")

multi\_agent\_graph \= builder.compile()

### **2.2 Redes de Agentes Colaborativos (Agent Swarms)**

Nesta arquitetura, os agentes atuam como pares em uma rede, comunicando-se e transferindo tarefas conforme necessário, sem um supervisor central.21 O fluxo de controle é mais dinâmico e emergente, surgindo das decisões locais de agentes individuais para transferir tarefas.26 Este padrão é ideal para a resolução de problemas complexos onde a sequência de passos não é conhecida a priori, exigindo colaboração dinâmica entre diferentes especialistas — por exemplo, um agente "pesquisador" encontra dados e, em seguida, transfere para um agente "codificador" para gerar um gráfico.30

A escolha entre uma arquitetura de Supervisor e uma de Swarm representa uma decisão fundamental sobre o equilíbrio entre controle e flexibilidade. A arquitetura de Supervisor oferece um controle explícito e de cima para baixo, resultando em um comportamento mais previsível e fácil de depurar, adequado para processos de negócios bem definidos. Em contraste, a arquitetura de Swarm descentraliza o controle, permitindo que um fluxo de trabalho "emergente" surja de interações de baixo para cima. Isso proporciona maior flexibilidade e potencial para resolver problemas novos de maneiras criativas, mas pode tornar o comportamento do sistema mais difícil de prever e depurar.

#### **Implementação Detalhada**

O mecanismo chave em um swarm é a "transferência" (handoff), onde um agente decide passar o controle para outro. Isso é frequentemente implementado através de uma função de roteamento que inspeciona a última mensagem de um agente para decidir o próximo nó.30 Um padrão mais avançado encapsula o próprio mecanismo de transferência dentro de uma ferramenta que um agente pode invocar explicitamente.30 Todos os agentes operam no mesmo

MessagesState, permitindo que vejam o histórico completo do trabalho realizado por seus pares, o que é crucial para o contexto e a colaboração.26

#### **Exemplo de Código: Colaboração entre Pesquisador e Gerador de Gráficos**

O código a seguir, adaptado de 30, demonstra uma colaboração entre um agente de pesquisa e um agente gerador de gráficos.

Python

from langgraph.prebuilt import create\_react\_agent

\# 1\. Definir ferramentas para cada agente  
\# (Supondo que tavily\_tool e python\_repl\_tool estejam definidos)

\# 2\. Criar os agentes como agentes ReAct  
llm \= ChatOpenAI(model="gpt-4o")  
research\_agent \= create\_react\_agent(llm, tools=\[tavily\_tool\], prompt="Você é um assistente de pesquisa.")  
chart\_agent \= create\_react\_agent(llm, tools=\[python\_repl\_tool\], prompt="Você é um especialista em geração de gráficos Python.")

\# 3\. Definir nós que invocam os agentes  
def research\_node(state: AgentState) \-\> dict:  
    result \= research\_agent.invoke(state)  
    return {"messages": \[HumanMessage(content=result\["messages"\]\[-1\].content, name="researcher")\]}

def chart\_node(state: AgentState) \-\> dict:  
    result \= chart\_agent.invoke(state)  
    return {"messages": \[HumanMessage(content=result\["messages"\]\[-1\].content, name="chart\_generator")\]}

\# 4\. Definir a função de roteamento para a transferência  
def router\_function(state: AgentState) \-\> str:  
    last\_message \= state\["messages"\]\[-1\]  
    \# Se o pesquisador encontrar dados, transfere para o gerador de gráficos  
    if last\_message.name \== "researcher":  
        return "chart\_generator"  
    \# Se o gerador de gráficos terminar, finaliza o processo  
    elif last\_message.name \== "chart\_generator":  
        return END  
    return END

\# 5\. Montar o grafo colaborativo  
builder \= StateGraph(AgentState)  
builder.add\_node("researcher", research\_node)  
builder.add\_node("chart\_generator", chart\_node)

builder.add\_edge(START, "researcher")  
builder.add\_conditional\_edges(  
    "researcher",  
    router\_function,  
    {"chart\_generator": "chart\_generator", END: END}  
)  
builder.add\_edge("chart\_generator", END)

collaborative\_graph \= builder.compile()

### **2.3 O Padrão de Reflexão (Agentes Autocorretivos)**

A reflexão é um padrão poderoso onde a saída de um agente é criticada, e essa crítica é realimentada ao agente para melhoria iterativa.9 Isso cria um ciclo "Gerador-Crítico" ou "Gerador-Refletor" que melhora significativamente a qualidade e a confiabilidade da saída final.20 Este padrão é aplicável a qualquer tarefa onde a qualidade é primordial e as saídas iniciais podem ser falhas, como geração de código, redação de ensaios ou raciocínio complexo.35

A geração padrão de LLM é um processo rápido e autorregressivo, análogo ao pensamento intuitivo e reativo do "Sistema 1", que pode ser propenso a erros e alucinações.35 O padrão de reflexão força uma pausa deliberada. A etapa de crítica exige que o sistema pare, avalie sua própria saída em relação a critérios específicos (por exemplo, "este código executa sem erros?", "este ensaio é persuasivo?") e, em seguida, planeje explicitamente uma revisão. Este processo deliberado de autoavaliação e correção é uma característica do pensamento metódico e analítico do "Sistema 2".35 A capacidade do LangGraph de construir facilmente esses ciclos não é apenas um recurso; é uma ferramenta para construir agentes que são fundamentalmente mais robustos, permitindo que os desenvolvedores projetem processos cognitivos que mitigam as fraquezas inerentes da geração "Sistema 1" dos LLMs.

#### **Implementação Detalhada**

O fluxo de trabalho consiste em um nó "Gerador" que tenta resolver a tarefa e um nó "Crítico" que avalia a saída.20 O crítico pode ser outro LLM ou um processo determinístico, como um verificador de código.37 Uma aresta condicional após o nó crítico verifica se uma crítica foi produzida. Se sim, ele retorna ao nó gerador, passando a crítica como nova entrada. Se não, o processo termina.20

#### **Exemplo de Código: Assistente de Codificação Autocorretivo**

O código a seguir, inspirado nos padrões de 37 e 39, descreve a estrutura de um agente de codificação autocorretivo.

Python

import traceback

\# 1\. Definir o estado, incluindo campos para erro e iterações  
class CodeGenerationState(TypedDict):  
    messages: Annotated, operator.add\]  
    code\_solution: str  
    error: str  
    iterations: int

\# 2\. Definir o nó gerador  
def generate\_node(state: CodeGenerationState) \-\> dict:  
    \# Lógica para chamar o LLM para gerar/refinar o código com base nas mensagens (e erros)  
    \#...  
    \# Suponha que o código gerado seja armazenado em \`new\_code\`  
    return {"code\_solution": new\_code, "iterations": state\["iterations"\] \+ 1}

\# 3\. Definir o nó crítico (verificador de código)  
def check\_code\_node(state: CodeGenerationState) \-\> dict:  
    code \= state\["code\_solution"\]  
    try:  
        \# Tenta executar o código em um ambiente seguro  
        exec(code, {})  
        return {"error": "no"}  
    except Exception as e:  
        \# Captura o erro e o adiciona ao estado  
        error\_message \= f"Erro de execução: {traceback.format\_exc()}"  
        return {"error": "yes", "messages": \[HumanMessage(content=error\_message)\]}

\# 4\. Definir a aresta condicional para o ciclo de correção  
MAX\_ITERATIONS \= 3  
def should\_continue\_correction(state: CodeGenerationState) \-\> str:  
    if state\["error"\] \== "no" or state\["iterations"\] \>= MAX\_ITERATIONS:  
        return END  
    else:  
        return "generate" \# Volta para gerar uma nova solução

\# 5\. Montar o grafo de reflexão  
builder \= StateGraph(CodeGenerationState)  
builder.add\_node("generate", generate\_node)  
builder.add\_node("check\_code", check\_code\_node)

builder.add\_edge(START, "generate")  
builder.add\_edge("generate", "check\_code")  
builder.add\_conditional\_edges(  
    "check\_code",  
    should\_continue\_correction,  
    {"generate": "generate", END: END}  
)

self\_correcting\_graph \= builder.compile()

## **Seção 3: Capacidades Essenciais para Sistemas Agênticos Robustos**

Esta seção detalha os componentes de suporte críticos — memória e ferramentas — que transformam um grafo simples em um sistema agêntico capaz e pronto para produção.

### **3.1 Gestão Avançada de Estado e Memória Persistente**

Uma memória eficaz é crucial para que os agentes mantenham o contexto, aprendam com interações passadas e executem tarefas de longa duração.9 LangGraph distingue entre memória de curto prazo (o estado dentro de uma única execução) e memória de longo prazo (persistência entre execuções).

* **Memória de Curto Prazo:** É o próprio objeto State, que armazena o histórico da conversa e dados intermediários durante uma única chamada graph.invoke() ou graph.stream().13  
* **Memória de Longo Prazo e Durabilidade:** A persistência é alcançada através de **Checkpointers**.4 Um checkpointer salva o estado do grafo a cada passo em um backend persistente, como memória, Redis ou Postgres.8 Isso permite a execução durável (retomada após falhas), "viagem no tempo" (reversão para um estado anterior) e, crucialmente, colaboração "human-in-the-loop".8

A persistência via checkpointers transforma a IA de uma ferramenta transacional e efêmera em um colaborador com estado.8 Essa capacidade é o que permite fluxos de trabalho críticos de "human-in-the-loop", onde um agente pode executar uma tarefa, salvar seu estado e aguardar a revisão e aprovação humana antes de prosseguir.9 Essa funcionalidade é essencial para a adoção empresarial em domínios de alto risco, pois permite que os agentes de IA sejam integrados com segurança em processos de negócios existentes que exigem supervisão, revisão e intervenção humana.

#### **Exemplo de Código: Adicionando Memória Persistente**

O código a seguir mostra como adicionar um MemorySaver (um checkpointer em memória) ao compilar o grafo. Para persistir e continuar uma conversa, o grafo é invocado com um thread\_id configurável.

Python

from langgraph.checkpoint.memory import MemorySaver

\# Supondo que \`app\` seja um grafo compilado sem um checkpointer.  
memory \= MemorySaver()  
app\_with\_memory \= app.compile(checkpointer=memory)

\# Invoca o grafo com um ID de thread para persistir o estado.  
thread\_config \= {"configurable": {"thread\_id": "user-123"}}  
app\_with\_memory.invoke({"messages": \[HumanMessage(content="Olá, qual é o meu nome?")\]}, config=thread\_config)

\# Invoca novamente com o mesmo ID de thread para continuar a conversa.  
app\_with\_memory.invoke({"messages": \[HumanMessage(content="Eu disse que meu nome é João.")\]}, config=thread\_config)

### **3.2 Integrando e Utilizando Ferramentas**

As ferramentas são a interface do agente com o mundo exterior, permitindo-lhe realizar ações além da geração de texto, como pesquisar na web, consultar bancos de dados ou chamar APIs.9 O uso de ferramentas é o mecanismo pelo qual os agentes se tornam "aterrados" (grounded) e factuais.

LLMs, por si só, são geradores de texto não aterrados, propensos a alucinações e desconectados de dados em tempo real ou proprietários. As ferramentas fornecem o mecanismo para o aterramento. Quando um agente usa uma ferramenta para consultar uma API 19 ou um banco de dados 22, ele está buscando informações factuais de uma fonte autoritativa. A resposta final do agente é então sintetizada a partir dessas informações aterradas, em vez de ser puramente gerada a partir de seus parâmetros internos. Este é o princípio central da Geração Aumentada por Recuperação (RAG).39 O suporte robusto do LangGraph para ciclos de chamada de ferramentas não é apenas sobre adicionar funcionalidade; é o mecanismo fundamental pelo qual os desenvolvedores podem construir agentes que são confiáveis, factuais e conectados ao mundo real.

#### **Implementação Detalhada**

O processo segue um ciclo no estilo ReAct 9:

1. **Definição da Ferramenta:** Uma ferramenta é uma função Python decorada com @tool. A docstring da função é de importância crítica, pois fornece a descrição que o LLM usa para decidir quando e como chamar a ferramenta.16  
2. Ciclo de Execução da Ferramenta:  
   a. O LLM no nó do agente decide chamar uma ferramenta e gera os argumentos necessários.  
   b. Uma aresta condicional roteia o grafo para um ToolNode, um utilitário pré-construído do LangGraph que executa a função da ferramenta especificada.22

   c. A saída da ferramenta é encapsulada em uma ToolMessage.16

   d. Uma aresta roteia de volta para o nó do agente, passando a ToolMessage para o estado. O LLM agora tem o resultado de sua ação e pode decidir o próximo passo.

#### **Exemplo de Código: Definição e Invocação de uma Ferramenta**

Este exemplo, baseado na lógica de 19 e 19, mostra a definição e o ciclo de uso de uma ferramenta simples.

Python

from langchain\_core.tools import tool

\# 1\. Definir a ferramenta com uma docstring descritiva.  
@tool  
def weather\_tool(city: str) \-\> str:  
    """Retorna o clima atual para uma cidade específica."""  
    \# Lógica para chamar uma API de clima real...  
    if city.lower() \== "são paulo":  
        return "Ensolarado com 25°C."  
    return "Clima não disponível."

\# 2\. Lógica dentro de um nó de agente para decidir e invocar a ferramenta.  
def agent\_node\_logic(state: AgentState):  
    \#... (chama o LLM com ferramentas vinculadas)  
    response \= llm\_with\_tools.invoke(state\["messages"\])  
      
    \# Verifica se o LLM decidiu usar uma ferramenta.  
    if response.tool\_calls:  
        \# A aresta condicional roteará para o ToolNode.  
        \# O ToolNode executará a \`weather\_tool\` com base no \`response.tool\_calls\`.  
        \# O resultado será adicionado ao estado como uma ToolMessage.  
        return {"messages": \[response\]}  
    else:  
        \# O LLM gerou uma resposta final.  
        return {"messages": \[response\]}

## **Seção 4: Conclusão: Rumo a Sistemas Agênticos Confiáveis e Observáveis**

Esta seção final sintetiza as descobertas do relatório, posicionando o LangGraph como um framework fundamental para a próxima geração de aplicações de IA. Também aborda brevemente o papel crítico do ecossistema circundante na transição de sistemas agênticos de protótipos experimentais para serviços de nível de produção.

### **4.1 Síntese das Descobertas**

O argumento central deste relatório é que a natureza com estado e cíclica do LangGraph permite a criação de arquiteturas cognitivas sofisticadas — como Supervisor-Trabalhador, Swarms Colaborativos e Reflexão — que são mais robustas, capazes e confiáveis do que sistemas construídos em frameworks lineares e sem estado. A combinação dessas arquiteturas com memória persistente e uso de ferramentas aterradas permite que os desenvolvedores construam verdadeiros agentes autônomos e colaborativos, capazes de lidar com a complexidade do mundo real.

### **4.2 O Ecossistema Mais Amplo para Agentes em Produção**

LangGraph é uma peça central, mas faz parte de um "Agent Stack" maior.43 Embora o LangGraph forneça a orquestração, ele é projetado para ser combinado com outras ferramentas para uma solução completa.28

* **Observabilidade com LangSmith:** Depurar o comportamento complexo e não determinístico de agentes é extremamente difícil. LangSmith fornece as ferramentas essenciais de rastreamento, visualização e avaliação necessárias para entender os caminhos de execução, inspecionar as transições de estado e identificar a causa raiz das falhas.13  
* **Implantação e Escala com a Plataforma LangGraph:** Mover um agente para produção requer infraestrutura escalável, camadas de persistência e APIs. A Plataforma LangGraph fornece esses recursos prontos para uso, lidando com desafios como execução durável, concorrência e agendamento.8

A construção de um agente poderoso requer mais do que apenas uma biblioteca de orquestração; exige ferramentas para prototipagem, depuração, avaliação, implantação e monitoramento. O ecossistema LangChain fornece uma ferramenta para cada estágio: LangGraph Studio para prototipagem visual 13, LangGraph para orquestração 8, LangSmith para observabilidade e avaliação 43, e a Plataforma LangGraph para implantação e escala.45 Este stack integrado 43 oferece um caminho suave de um protótipo local para uma aplicação escalável de nível empresarial. Portanto, o LangGraph não deve ser visto isoladamente. Seu verdadeiro poder é realizado quando visto como o motor de orquestração central dentro de uma plataforma abrangente, projetada para gerenciar a complexidade de construir, implantar e manter agentes de IA confiáveis em escala.

#### **Referências citadas**

1. LangChain vs. LangGraph: A Comparative Analysis | by Tahir | Medium, acessado em setembro 28, 2025, [https://medium.com/@tahirbalarabe2/%EF%B8%8Flangchain-vs-langgraph-a-comparative-analysis-ce7749a80d9c](https://medium.com/@tahirbalarabe2/%EF%B8%8Flangchain-vs-langgraph-a-comparative-analysis-ce7749a80d9c)  
2. LangChain vs. LangGraph: A Developer's Guide to Choosing Your AI Workflow, acessado em setembro 28, 2025, [https://duplocloud.com/blog/langchain-vs-langgraph/](https://duplocloud.com/blog/langchain-vs-langgraph/)  
3. LangChain vs LangGraph: A Developer's Guide to Choosing Your AI Frameworks \- Milvus, acessado em setembro 28, 2025, [https://milvus.io/blog/langchain-vs-langgraph.md](https://milvus.io/blog/langchain-vs-langgraph.md)  
4. LangChain vs LangGraph vs LangSmith vs LangFlow: Key Differences Explained | DataCamp, acessado em setembro 28, 2025, [https://www.datacamp.com/tutorial/langchain-vs-langgraph-vs-langsmith-vs-langflow](https://www.datacamp.com/tutorial/langchain-vs-langgraph-vs-langsmith-vs-langflow)  
5. LangGraph Tutorial: What Is LangGraph and How to Use It? \- DataCamp, acessado em setembro 28, 2025, [https://www.datacamp.com/tutorial/langgraph-tutorial](https://www.datacamp.com/tutorial/langgraph-tutorial)  
6. LangChain vs LangGraph: Explained \- Peliqan, acessado em setembro 28, 2025, [https://peliqan.io/blog/langchain-vs-langgraph/](https://peliqan.io/blog/langchain-vs-langgraph/)  
7. Building Stateful Applications with LangGraph | by Anoop Maurya | GoPenAI, acessado em setembro 28, 2025, [https://blog.gopenai.com/building-stateful-applications-with-langgraph-860de3c9fa90](https://blog.gopenai.com/building-stateful-applications-with-langgraph-860de3c9fa90)  
8. LangGraph \- LangChain, acessado em setembro 28, 2025, [https://www.langchain.com/langgraph](https://www.langchain.com/langgraph)  
9. Agent architectures \- GitHub Pages, acessado em setembro 28, 2025, [https://langchain-ai.github.io/langgraph/concepts/agentic\_concepts/](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)  
10. How to Build Agentic AI Systems with LangGraph \- ThoughtSpot, acessado em setembro 28, 2025, [https://www.thoughtspot.com/data-trends/data-and-analytics-engineering/agentic-ai](https://www.thoughtspot.com/data-trends/data-and-analytics-engineering/agentic-ai)  
11. state graph node \- GitHub Pages, acessado em setembro 28, 2025, [https://langchain-ai.github.io/langgraph/concepts/low\_level/](https://langchain-ai.github.io/langgraph/concepts/low_level/)  
12. State Management of AI Agents in LangGraph | by Jaydeep Hardikar | Medium, acessado em setembro 28, 2025, [https://medium.com/@jayhardikar/state-management-of-ai-agents-in-langgraph-45f9975f2af2](https://medium.com/@jayhardikar/state-management-of-ai-agents-in-langgraph-45f9975f2af2)  
13. What is LangGraph? \- IBM, acessado em setembro 28, 2025, [https://www.ibm.com/think/topics/langgraph](https://www.ibm.com/think/topics/langgraph)  
14. Understanding State in LangGraph: A Beginners Guide | by Rick ..., acessado em setembro 28, 2025, [https://medium.com/@gitmaxd/understanding-state-in-langgraph-a-comprehensive-guide-191462220997](https://medium.com/@gitmaxd/understanding-state-in-langgraph-a-comprehensive-guide-191462220997)  
15. Beginner's Guide to LangGraph: Create a Multi-Agent Assistant with LLaMA 3 | by Vamsikd, acessado em setembro 28, 2025, [https://medium.com/@vamsikd219/beginners-guide-to-langgraph-create-a-multi-agent-assistant-with-llama-3-ab51c8acd0a1](https://medium.com/@vamsikd219/beginners-guide-to-langgraph-create-a-multi-agent-assistant-with-llama-3-ab51c8acd0a1)  
16. How to Build LangGraph Agents Hands-On Tutorial | DataCamp, acessado em setembro 28, 2025, [https://www.datacamp.com/tutorial/langgraph-agents](https://www.datacamp.com/tutorial/langgraph-agents)  
17. Open Source Observability for LangGraph \- Langfuse, acessado em setembro 28, 2025, [https://langfuse.com/guides/cookbook/integration\_langgraph](https://langfuse.com/guides/cookbook/integration_langgraph)  
18. LangGraph: A Comprehensive Guide to the Agentic Framework | by Yash Paddalwar, acessado em setembro 28, 2025, [https://medium.com/@yashpaddalwar/langgraph-a-comprehensive-guide-to-the-agentic-framework-8625adec2314](https://medium.com/@yashpaddalwar/langgraph-a-comprehensive-guide-to-the-agentic-framework-8625adec2314)  
19. Build a Multi-Agent System with LangGraph and Mistral on AWS ..., acessado em setembro 28, 2025, [https://aws.amazon.com/blogs/machine-learning/build-a-multi-agent-system-with-langgraph-and-mistral-on-aws/](https://aws.amazon.com/blogs/machine-learning/build-a-multi-agent-system-with-langgraph-and-mistral-on-aws/)  
20. A Deep Dive into LangGraph for Self-Correcting AI Agents ..., acessado em setembro 28, 2025, [https://activewizards.com/blog/a-deep-dive-into-langgraph-for-self-correcting-ai-agents](https://activewizards.com/blog/a-deep-dive-into-langgraph-for-self-correcting-ai-agents)  
21. Reference \- GitHub Pages, acessado em setembro 28, 2025, [https://langchain-ai.github.io/langgraph/reference/](https://langchain-ai.github.io/langgraph/reference/)  
22. Multi-Agent System Tutorial with LangGraph \- FutureSmart AI Blog, acessado em setembro 28, 2025, [https://blog.futuresmart.ai/multi-agent-system-with-langgraph](https://blog.futuresmart.ai/multi-agent-system-with-langgraph)  
23. Fully local multi-agent systems with LangGraph \- YouTube, acessado em setembro 28, 2025, [https://www.youtube.com/watch?v=4oC1ZKa9-Hs](https://www.youtube.com/watch?v=4oC1ZKa9-Hs)  
24. Building Agents And Multi Agents With LangGraph- Part 3 \- YouTube, acessado em setembro 28, 2025, [https://www.youtube.com/watch?v=E0fQWFNqGgg](https://www.youtube.com/watch?v=E0fQWFNqGgg)  
25. Multi-Agent Structures (1) | LangChain OpenTutorial \- GitBook, acessado em setembro 28, 2025, [https://langchain-opentutorial.gitbook.io/langchain-opentutorial/17-langgraph/02-structures/08-langgraph-multi-agent-structures-01](https://langchain-opentutorial.gitbook.io/langchain-opentutorial/17-langgraph/02-structures/08-langgraph-multi-agent-structures-01)  
26. LangGraph: Multi-Agent Workflows \- LangChain Blog, acessado em setembro 28, 2025, [https://blog.langchain.com/langgraph-multi-agent-workflows/](https://blog.langchain.com/langgraph-multi-agent-workflows/)  
27. Managing shared state in LangGraph multi-agent system : r/LangChain \- Reddit, acessado em setembro 28, 2025, [https://www.reddit.com/r/LangChain/comments/1n867zq/managing\_shared\_state\_in\_langgraph\_multiagent/](https://www.reddit.com/r/LangChain/comments/1n867zq/managing_shared_state_in_langgraph_multiagent/)  
28. Overview \- Docs by LangChain, acessado em setembro 28, 2025, [https://docs.langchain.com/oss/python/langgraph/overview](https://docs.langchain.com/oss/python/langgraph/overview)  
29. Multi-agent swarms with LangGraph \- YouTube, acessado em setembro 28, 2025, [https://www.youtube.com/watch?v=JeyDrn1dSUQ](https://www.youtube.com/watch?v=JeyDrn1dSUQ)  
30. Multi-agent network \- GitHub Pages, acessado em setembro 28, 2025, [https://langchain-ai.github.io/langgraph/tutorials/multi\_agent/multi-agent-collaboration/](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)  
31. aws-samples/langgraph-multi-agent \- GitHub, acessado em setembro 28, 2025, [https://github.com/aws-samples/langgraph-multi-agent](https://github.com/aws-samples/langgraph-multi-agent)  
32. LangGraph Multi-Agent Systems \- Overview, acessado em setembro 28, 2025, [https://langchain-ai.github.io/langgraph/concepts/multi\_agent/](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)  
33. LangGraph:18 Network or Collaborative Multi-Agent System Implementation \#aiagents \#ai \#genai \#agent \- YouTube, acessado em setembro 28, 2025, [https://www.youtube.com/watch?v=OlxJtmYW5dk](https://www.youtube.com/watch?v=OlxJtmYW5dk)  
34. LangChain/LangGraph: Build Reflection Enabled Agentic | by TeeTracker \- Medium, acessado em setembro 28, 2025, [https://teetracker.medium.com/build-reflection-enabled-agent-9186a35c6581](https://teetracker.medium.com/build-reflection-enabled-agent-9186a35c6581)  
35. Reflection Agents \- LangChain Blog, acessado em setembro 28, 2025, [https://blog.langchain.com/reflection-agents/](https://blog.langchain.com/reflection-agents/)  
36. Enhancing Code Quality with LangGraph Reflection \- Analytics Vidhya, acessado em setembro 28, 2025, [https://www.analyticsvidhya.com/blog/2025/03/enhancing-code-quality-with-langgraph-reflection/](https://www.analyticsvidhya.com/blog/2025/03/enhancing-code-quality-with-langgraph-reflection/)  
37. langchain-ai/langgraph-reflection \- GitHub, acessado em setembro 28, 2025, [https://github.com/langchain-ai/langgraph-reflection](https://github.com/langchain-ai/langgraph-reflection)  
38. Reflection \- GitHub Pages, acessado em setembro 28, 2025, [https://langchain-ai.github.io/langgraph/tutorials/reflection/reflection/](https://langchain-ai.github.io/langgraph/tutorials/reflection/reflection/)  
39. LangGraph: Building Self-Correcting RAG Agent for Code Generation \- LearnOpenCV, acessado em setembro 28, 2025, [https://learnopencv.com/langgraph-self-correcting-agent-code-generation/](https://learnopencv.com/langgraph-self-correcting-agent-code-generation/)  
40. Building a Self-Correcting Coding Assistant with LangChain and LangGraph: A Hands-on Guide | by Anoop Maurya | Medium, acessado em setembro 28, 2025, [https://medium.com/@mauryaanoop3/building-a-self-correcting-coding-assistant-with-langchain-and-langgraph-a-hands-on-guide-3ea7424655be](https://medium.com/@mauryaanoop3/building-a-self-correcting-coding-assistant-with-langchain-and-langgraph-a-hands-on-guide-3ea7424655be)  
41. langchain-ai/langgraph: Build resilient language agents as graphs. \- GitHub, acessado em setembro 28, 2025, [https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph)  
42. Building Multi-Agent Systems with LangGraph: A Step-by-Step Guide | by Sushmita Nandi, acessado em setembro 28, 2025, [https://medium.com/@sushmita2310/building-multi-agent-systems-with-langgraph-a-step-by-step-guide-d14088e90f72](https://medium.com/@sushmita2310/building-multi-agent-systems-with-langgraph-a-step-by-step-guide-d14088e90f72)  
43. LangChain, acessado em setembro 28, 2025, [https://www.langchain.com/](https://www.langchain.com/)  
44. Overview \- Docs by LangChain, acessado em setembro 28, 2025, [https://docs.langchain.com/langgraph-platform/langgraph-studio](https://docs.langchain.com/langgraph-platform/langgraph-studio)  
45. LangGraph Platform \- LangChain, acessado em setembro 28, 2025, [https://www.langchain.com/langgraph-platform](https://www.langchain.com/langgraph-platform)