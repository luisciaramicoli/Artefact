# Cenário 6 — Limite de Escopo da Loja (Recusa Educada de Acessórios)

**Objetivo do Teste:** Garantir respeito à regra de ouro do manual interno: a Empório da Música comercializa EXCLUSIVAMENTE instrumentos musicais, recusando gentilmente pedidos de cordas/palhetas.  
**Modelo Utilizado:** Gemini 3.1 Flash Lite  
**Arquitetura:** Function Calling + Qdrant Vector RAG + Relational SQLite  

---

### 👤 Usuário:
> Vocês vendem encordoamento de aço para violão e palhetas avulsas?


*Nenhuma ferramenta externa necessária (resposta direta com base no prompt do sistema ou conhecimento estático).*

### 🎸 Empório da Música (Agente IA):
Olá! Que bom receber seu contato aqui na Empório da Música.

Sobre a sua pergunta, preciso ser bem sincero com você: aqui na nossa loja, somos **especializados exclusivamente em instrumentos musicais** (como violões, guitarras, baixos, teclados, baterias, entre outros).

Por conta dessa nossa especialização, **não trabalhamos com a venda de acessórios**, o que inclui encordoamentos, palhetas, cabos, amplificadores ou cases. 

Como queremos que você continue sua jornada musical da melhor forma, sugiro que procure uma das lojas parceiras aqui da região de Campo Grande que trabalham com acessórios; com certeza eles poderão te atender prontamente com essas peças!

Se você estiver pensando em trocar de instrumento ou quiser conhecer algum modelo novo de violão, aí sim conte comigo! Será um prazer te ajudar a encontrar o seu próximo companheiro de som. 😊

Precisa de ajuda com mais alguma coisa?


---

## 🔍 Análise Técnica da Resposta:
- **Precisão dos Dados:** As informações retornadas foram validadas deterministicamente com os dados fornecidos (`data/*.csv` e `políticas_da_loja.pdf`).
- **Aderência à Persona:** O tom de voz adotado reflete hospitalidade musical, clareza nas condições comerciais e respeito às restrições operacionais da loja de Campo Grande/MS.
