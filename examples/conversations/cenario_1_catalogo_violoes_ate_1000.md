# Cenário 1 — Consulta ao Catálogo de Produtos com Filtro de Preço

**Objetivo do Teste:** Verificar capacidade de filtrar produtos por categoria ('Violões'), faixa de preço (<= R$ 1000), verificar estoque ativo e calcular desconto de 5% no PIX.  
**Modelo Utilizado:** Gemini 3.1 Flash Lite  
**Arquitetura:** Function Calling + Qdrant Vector RAG + Relational SQLite  

---

### 👤 Usuário:
> Quais opções de violões disponíveis custando até R$1000?


**Ferramentas Acionadas (Tool Calls):**
```json
[
  {
    "tool": "query_products",
    "arguments": {
      "category_name": "Violões",
      "max_price": 1000
    }
  }
]
```

### 🎸 Empório da Música (Agente IA):
Olá! Que alegria ver você buscando um novo instrumento. Aqui na **Empório da Música**, temos ótimas opções de violões para quem está começando ou para quem busca um custo-benefício excelente, todos dentro da sua faixa de até R$ 1.000,00.

Confira os modelos que temos disponíveis em estoque agora:

| Modelo | Tipo de Corda | Preço (Tabela) | Preço no PIX (5% desc.) |
| :--- | :--- | :--- | :--- |
| **Tagima Memphis AC-39** | Nylon | R$ 429,90 | **R$ 408,40** |
| **Rozini RC-104 Estudante** | Nylon | R$ 459,90 | **R$ 436,90** |
| **Shelby SN-100 Folk** | Aço | R$ 549,00 | **R$ 521,55** |
| **Giannini GF-1R Folk** | Aço | R$ 579,90 | **R$ 550,90** |
| **Yamaha C40** | Nylon | R$ 599,90 | **R$ 569,90** |
| **Giannini GN-15** | Nylon | R$ 689,00 | **R$ 654,55** |

### 💡 Dicas importantes:
*   **Condições de Pagamento**: Além do desconto no PIX, você pode parcelar qualquer um desses modelos em até **12x sem juros** no cartão de crédito (parcela mínima de R$ 100,00).
*   **Visite a gente**: Estamos na Rua 14 de Maio, 3200, no Centro de Campo Grande. Será um prazer receber você para testar esses instrumentos e sentir qual deles combina mais com a sua pegada!
*   **Lembrete**: Como somos uma loja especializada exclusivamente em instrumentos musicais, não trabalhamos com acessórios (como capas, cordas extras ou afinadores).

Algum desses modelos chamou mais a sua atenção? Se quiser saber mais detalhes técnicos de algum deles, é só me perguntar! Estou aqui para ajudar você a escolher o seu próximo companheiro de música. 🎶


---

## 🔍 Análise Técnica da Resposta:
- **Precisão dos Dados:** As informações retornadas foram validadas deterministicamente com os dados fornecidos (`data/*.csv` e `políticas_da_loja.pdf`).
- **Aderência à Persona:** O tom de voz adotado reflete hospitalidade musical, clareza nas condições comerciais e respeito às restrições operacionais da loja de Campo Grande/MS.
