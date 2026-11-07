# Cenário 5 — Rastreamento de Pedido e Verificação em Tempo Real no Banco de Dados

**Objetivo do Teste:** Consultar status de pedido no banco relacional via tool calling, informando código de rastreio, itens inclusos e entrega.  
**Modelo Utilizado:** Gemini 3.1 Flash Lite  
**Arquitetura:** Function Calling + Qdrant Vector RAG + Relational SQLite  

---

### 👤 Usuário:
> Olá! Gostaria de acompanhar a entrega do meu pedido número 1. Qual o status e o código de rastreamento dele?


**Ferramentas Acionadas (Tool Calls):**
```json
[
  {
    "tool": "check_order_status",
    "arguments": {
      "order_id": 1
    }
  }
]
```

### 🎸 Empório da Música (Agente IA):
Olá, Pedro! Tudo bem?

Verifiquei aqui no nosso sistema e tenho ótimas notícias sobre o seu pedido número 1!

O status dele consta como **Entregue**. O código de rastreamento é **BRAB1234567BR**.

O item entregue foi o seu **Martin D-28 Dreadnought Natural**. Espero que esteja aproveitando muito esse instrumento incrível!

Caso precise de qualquer outra informação ou tenha alguma dúvida, estou à disposição. Conte sempre com a Empório da Música para acompanhar sua jornada musical! 🎸


---

## 🔍 Análise Técnica da Resposta:
- **Precisão dos Dados:** As informações retornadas foram validadas deterministicamente com os dados fornecidos (`data/*.csv` e `políticas_da_loja.pdf`).
- **Aderência à Persona:** O tom de voz adotado reflete hospitalidade musical, clareza nas condições comerciais e respeito às restrições operacionais da loja de Campo Grande/MS.
