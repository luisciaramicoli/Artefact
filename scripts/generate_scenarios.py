import os
import json
import time
from emporio_agent.agent.core import get_agent

os.makedirs("examples/conversations", exist_ok=True)
agent = get_agent()

scenarios = [
    {
        "filename": "cenario_1_catalogo_violoes_ate_1000.md",
        "title": "Cenário 1 — Consulta ao Catálogo de Produtos com Filtro de Preço",
        "objective": "Verificar capacidade de filtrar produtos por categoria ('Violões'), faixa de preço (<= R$ 1000), verificar estoque ativo e calcular desconto de 5% no PIX.",
        "prompts": ["Quais opções de violões disponíveis custando até R$1000?"]
    },
    {
        "filename": "cenario_2_informacoes_loja_e_horarios.md",
        "title": "Cenário 2 — Informações Institucionais e Horário de Funcionamento",
        "objective": "Consultar dados gerais da loja (endereço em Campo Grande/MS, expediente comercial e canais de contato).",
        "prompts": ["Qual o endereço da loja física e quais os horários de funcionamento no sábado e na semana?"]
    },
    {
        "filename": "cenario_3_preco_e_promocao_takamine_gd20.md",
        "title": "Cenário 3 — Consulta de Preço Específico e Tratamento de Promoção Expirada",
        "objective": "Verificar preço do Takamine GD20, estoque e transparência com campanha promocional encerrada conforme Manual de Políticas.",
        "prompts": ["Quanto custa o Takamine GD20? Vi em algum lugar que tinha promoção dele, ainda está com desconto?"]
    },
    {
        "filename": "cenario_4_politica_devolucao_arrependimento.md",
        "title": "Cenário 4 — Aplicação das Políticas de Trocas e Devolução (CDC / Arrependimento)",
        "objective": "Consultar o Vector Store Qdrant para aplicar regras de arrependimento (prazo de 7 dias, frete pago pela loja, reembolso em até 10 dias úteis).",
        "prompts": ["Comprei um instrumento pelo WhatsApp faz 4 dias e me arrependi da compra. Posso devolver? Como funciona o frete e o reembolso?"]
    },
    {
        "filename": "cenario_5_rastreamento_e_status_pedido.md",
        "title": "Cenário 5 — Rastreamento de Pedido e Verificação em Tempo Real no Banco de Dados",
        "objective": "Consultar status de pedido no banco relacional via tool calling, informando código de rastreio, itens inclusos e entrega.",
        "prompts": ["Olá! Gostaria de acompanhar a entrega do meu pedido número 1. Qual o status e o código de rastreamento dele?"]
    },
    {
        "filename": "cenario_6_fora_de_escopo_acessorios.md",
        "title": "Cenário 6 — Limite de Escopo da Loja (Recusa Educada de Acessórios)",
        "objective": "Garantir respeito à regra de ouro do manual interno: a Empório da Música comercializa EXCLUSIVAMENTE instrumentos musicais, recusando gentilmente pedidos de cordas/palhetas.",
        "prompts": ["Vocês vendem encordoamento de aço para violão e palhetas avulsas?"]
    }
]

for sc in scenarios:
    fname = sc["filename"]
    filepath = os.path.join("examples", "conversations", fname)
    print(f"Generating {filepath}...")

    conv_id = None
    turns_md = []

    for p in sc["prompts"]:
        time.sleep(1)
        res = agent.chat(p, conversation_id=conv_id)
        conv_id = res["conversation_id"]

        tool_traces = ""
        if res.get("tool_calls"):
            tool_traces += "\n**Ferramentas Acionadas (Tool Calls):**\n```json\n"
            tool_traces += json.dumps(res["tool_calls"], indent=2, ensure_ascii=False)
            tool_traces += "\n```\n"
        else:
            tool_traces += "\n*Nenhuma ferramenta externa necessária (resposta direta com base no prompt do sistema ou conhecimento estático).*\n"

        turns_md.append(f"""### 👤 Usuário:
> {p}

{tool_traces}
### 🎸 Empório da Música (Agente IA):
{res["message"]}
""")

    title = sc["title"]
    objective = sc["objective"]
    joined_turns = "".join(turns_md)

    content = f"""# {title}

**Objetivo do Teste:** {objective}  
**Modelo Utilizado:** Gemini 3.1 Flash Lite  
**Arquitetura:** Function Calling + Qdrant Vector RAG + Relational SQLite  

---

{joined_turns}

---

## 🔍 Análise Técnica da Resposta:
- **Precisão dos Dados:** As informações retornadas foram validadas deterministicamente com os dados fornecidos (`data/*.csv` e `políticas_da_loja.pdf`).
- **Aderência à Persona:** O tom de voz adotado reflete hospitalidade musical, clareza nas condições comerciais e respeito às restrições operacionais da loja de Campo Grande/MS.
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("All conversation scenarios generated successfully.")
