# Cenário 3 — Consulta de Preço Específico e Tratamento de Promoção Expirada

**Objetivo do Teste:** Verificar preço do Takamine GD20, estoque e transparência com campanha promocional encerrada conforme Manual de Políticas.  
**Modelo Utilizado:** Gemini 3.1 Flash Lite  
**Arquitetura:** Function Calling + Qdrant Vector RAG + Relational SQLite  

---

### 👤 Usuário:
> Quanto custa o Takamine GD20? Vi em algum lugar que tinha promoção dele, ainda está com desconto?


**Ferramentas Acionadas (Tool Calls):**
```json
[
  {
    "tool": "get_product_details",
    "arguments": {
      "product_name_or_id": "Takamine GD20"
    }
  }
]
```

### 🎸 Empório da Música (Agente IA):
Olá! Que escolha excelente, o **Takamine GD20** é um instrumento fantástico, muito conhecido pelo timbre quente e pela qualidade do tampo em cedro sólido.

Sobre a sua dúvida, verifiquei aqui no nosso sistema:

*   **Preço de Tabela:** R$ 2.199,00.
*   **Condições de Pagamento:**
    *   **PIX à vista:** R$ 2.089,05 (já com 5% de desconto).
    *   **Cartão de crédito:** Parcelamos em até **12x sem juros** (respeitando a parcela mínima de R$ 100,00).

Quanto à promoção que você mencionou, ela era de uma campanha sazonal que já se encerrou. Por isso, hoje trabalhamos com o preço de tabela vigente, mas mantemos as nossas condições padrão de desconto no PIX e o parcelamento facilitado.

Temos 5 unidades dele disponíveis em estoque agora! Se você quiser garantir o seu, podemos agilizar o processo por aqui ou você pode dar uma passadinha na nossa loja na **Rua 14 de Maio, 3200 — Centro**, aqui em Campo Grande.

O que acha? Quer que eu te ajude com mais alguma informação sobre esse modelo ou sobre nossas políticas de entrega?


---

## 🔍 Análise Técnica da Resposta:
- **Precisão dos Dados:** As informações retornadas foram validadas deterministicamente com os dados fornecidos (`data/*.csv` e `políticas_da_loja.pdf`).
- **Aderência à Persona:** O tom de voz adotado reflete hospitalidade musical, clareza nas condições comerciais e respeito às restrições operacionais da loja de Campo Grande/MS.
