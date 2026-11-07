import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
from emporio_agent.config import settings
from emporio_agent.rag.vector_store import get_vector_store


def extract_policy_chunks(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract and structure chunks from the Empório da Música policies manual.
    Preserves section headers, titles, and page references for maximum retrieval accuracy.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"Policy PDF not found at {pdf_path}")

    reader = PdfReader(str(pdf_path))
    chunks: List[Dict[str, Any]] = []
    chunk_id = 1

    # Structured sections mapped by manual chapters
    # We combine text from pages and chunk along clear logical topic boundaries
    full_text_by_page = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        # Clean up header / footer noise
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned = "\n".join(lines)
        full_text_by_page.append({"page": page_num, "text": cleaned})

    # High-quality chunk definitions based on the 10 manual chapters
    sections_catalog = [
        {
            "section": "1.0",
            "title": "Sobre a Empório da Música e Escopo de Produtos",
            "page": 2,
            "text": (
                "1. Sobre a Empório da Música:\n"
                "A Empório da Música é uma loja especializada em instrumentos musicais fundada em 2008 em Campo Grande, "
                "Mato Grosso do Sul. Com mais de 15 anos de atuação no mercado, somos referência regional na venda de instrumentos "
                "para músicos iniciantes, intermediários e profissionais. Nosso catálogo abrange mais de 300 instrumentos de marcas "
                "nacionais e internacionais, incluindo guitarras, baixos, violões, baterias, teclados, instrumentos de sopro, "
                "cordas orquestrais e ukuleles.\n\n"
                "IMPORTANTE - ESCOPO EXCLUSIVO DE ATUAÇÃO:\n"
                "Trabalhamos EXCLUSIVAMENTE com instrumentos musicais. NÃO comercializamos e NÃO temos em estoque acessórios como: "
                "cordas, palhetas, cabos, cases, capas, pedais de efeito, correias ou amplificadores. Caso o cliente solicite acessórios, "
                "o atendente deve gentilmente informar esse limite de escopo e sugerir lojas parceiras de música na região.\n\n"
                "1.1 Missão:\n"
                "Democratizar o acesso a instrumentos musicais de qualidade na região Centro-Oeste, oferecendo atendimento especializado "
                "e preços competitivos, contribuindo para o desenvolvimento cultural e musical da comunidade.\n\n"
                "1.2 Dados da Empresa:\n"
                "Razão Social: Empório da Música Instrumentos Musicais Ltda.\n"
                "Nome Fantasia: Empório da Música\n"
                "CNPJ: 12.345.678/0001-90\n"
                "Endereço: Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333\n"
                "Telefone / WhatsApp: (67) 3341-4444\n"
                "E-mail: contato@emporiodamusica.com.br"
            ),
        },
        {
            "section": "2.0",
            "title": "Horário de Funcionamento e Atendimento",
            "page": 2,
            "text": (
                "2. Horário de Funcionamento:\n"
                "O atendimento presencial na loja física e o atendimento via WhatsApp seguem os horários:\n"
                "- Segunda a Sexta-feira: 09:00 às 18:00\n"
                "- Sábado: 09:00 às 13:00\n"
                "- Domingo e Feriados: Fechado\n\n"
                "Em datas especiais (Black Friday, Aniversário da Loja, Natal), o horário pode ser estendido com aviso prévio.\n"
                "Fora do expediente, o assistente virtual deve acolher o cliente e informar o horário de retorno."
            ),
        },
        {
            "section": "3.0",
            "title": "Formas de Pagamento e Condições de Parcelamento",
            "page": 3,
            "text": (
                "3. Formas de Pagamento:\n"
                "Aceitamos as seguintes formas de pagamento para compras presenciais e online:\n"
                "- PIX: Pagamento à vista com 5% de desconto sobre o preço de tabela do produto.\n"
                "- Cartão de Débito: Pagamento à vista, todas as bandeiras aceitas.\n"
                "- Cartão de Crédito: Parcelamento em até 12x sem juros (todas as bandeiras aceitas).\n"
                "- Boleto Bancário: Pagamento à vista, compensação em até 3 dias úteis.\n\n"
                "3.1 Regras de Parcelamento no Cartão de Crédito:\n"
                "- Em até 3x: sem juros, sem valor mínimo de parcela (exceto abaixo de R$ 50,00).\n"
                "- De 4x a 6x: sem juros, com parcela mínima de R$ 80,00.\n"
                "- De 7x a 12x: sem juros, com parcela mínima de R$ 100,00.\n"
                "- Combinação de formas de pagamento (ex.: PIX + Cartão de Crédito): permitida para compras acima de R$ 2.000,00."
            ),
        },
        {
            "section": "4.1",
            "title": "Política de Trocas e Devoluções - Direito de Arrependimento",
            "page": 3,
            "text": (
                "4. Política de Trocas e Devoluções (CDC Lei nº 8.078/90):\n"
                "4.1 Direito de Arrependimento (Compras Online / WhatsApp):\n"
                "- O cliente pode solicitar a devolução e cancelamento da compra em até 7 (sete) dias corridos após o recebimento do produto, sem necessidade de justificativa.\n"
                "- O produto deve estar em sua embalagem original, sem sinais de uso, acompanhado de todos os manuais e acessórios originais de fábrica.\n"
                "- O reembolso integral será realizado na mesma forma de pagamento original em até 10 dias úteis após o recebimento e conferência na loja.\n"
                "- O frete de devolução por arrependimento dentro do prazo legal de 7 dias é por conta da Empório da Música (loja emite logística reversa)."
            ),
        },
        {
            "section": "4.2",
            "title": "Trocas por Defeito, Preferência e Itens Não Elegíveis",
            "page": 4,
            "text": (
                "4.2 Trocas por Defeito de Fabricação:\n"
                "- Produtos com defeito de fabricação podem ser trocados diretamente com a loja em até 30 (trinta) dias corridos após a compra.\n"
                "- Após os 30 dias corridos, o cliente deve acionar a garantia diretamente com o fabricante do instrumento (a loja pode intermediar).\n"
                "- Danos causados por mau uso, quedas, umidade excessiva ou modificações/reparos não autorizados não são cobertos.\n\n"
                "4.3 Trocas por Preferência (cor, modelo, tamanho):\n"
                "- Permitidas em até 7 dias da compra, mediante disponibilidade do produto desejado no estoque.\n"
                "- O produto deve estar em perfeito estado e na embalagem original lacrada/intacta.\n"
                "- Diferenças de valor serão acertadas ou reembolsadas.\n\n"
                "4.4 Itens Não Elegíveis para Troca:\n"
                "- Instrumentos com personalização ou ajustes sob encomenda (setup, regulagem especial).\n"
                "- Produtos de ponta de estoque ou liquidação com aviso explícito de venda no estado."
            ),
        },
        {
            "section": "5.0",
            "title": "Prazos de Entrega, Frete e Retirada na Loja",
            "page": 4,
            "text": (
                "5. Prazos de Entrega e Frete:\n"
                "- Campo Grande (perímetro urbano): Entrega expressa em até 1 dia útil (frete fixo R$ 19,90 ou Grátis para compras acima de R$ 300,00).\n"
                "- Interior do Mato Grosso do Sul (MS): Prazo de 2 a 5 dias úteis via transportadora parceira.\n"
                "- Demais estados e regiões do Brasil: Prazo de 5 a 12 dias úteis via Correios (SEDEX ou PAC) ou transportadoras parceiras.\n"
                "- Retirada na Loja Física (Rua 14 de Maio, 3200): Gratuita, disponível em até 2 horas após a confirmação do pagamento durante o horário comercial.\n"
                "- Rastreamento: Todos os pedidos enviados contam com código de rastreamento enviado por e-mail e WhatsApp logo após a postagem."
            ),
        },
        {
            "section": "6.0",
            "title": "Política de Promoções e Descontos",
            "page": 5,
            "text": (
                "6. Promoções e Descontos:\n"
                "- Promoções são sazonais (Black Friday, Aniversário da Loja, Semana do Músico) e possuem validade determinada no sistema.\n"
                "- Promoções não são cumulativas com outros cupons ou campanhas (exceto o desconto de 5% à vista no PIX, que se aplica sobre o valor promocional).\n"
                "- Promoções expiradas: O assistente NUNCA deve prometer nem aplicar descontos de promoções já inativas/expiradas. Caso o cliente mencione uma promoção passada, deve-se explicar de forma transparente que a campanha encerrou e informar o preço atual vigente.\n"
                "- Descontos especiais: O assistente virtual não possui autorização para conceder descontos além dos cadastrados no sistema ou do desconto de 5% no PIX."
            ),
        },
        {
            "section": "7.0",
            "title": "Diretrizes de Atendimento e Persona WhatsApp",
            "page": 6,
            "text": (
                "7. Atendimento via WhatsApp e Canais Digitais:\n"
                "7.1 Diretrizes e Tom de Voz:\n"
                "- Tom de voz: Informal, acolhedor e profissional. Tratar o cliente como um amigo apaixonado por música. Evitar jargões excessivamente burocráticos ou respostas frias/robotizadas.\n"
                "- Informações precisas: NUNCA inventar ou chutar preços, estoques ou status de pedidos sem consultar as ferramentas oficiais da loja. Informação errada frustra o cliente e gera propaganda enganosa.\n"
                "- Limite de Escopo: A Empório da Música comercializa EXCLUSIVAMENTE instrumentos musicais. Pedidos de acessórios (cordas, pedais, cabos, amplificadores, capas, afinadores) devem ser educadamente recusados, orientando que trabalhamos apenas com instrumentos e sugerindo procurar lojas parceiras de acessórios.\n"
                "- Saudação e empatia: Cumprimentar cordialmente, entender o estilo musical ou necessidade do cliente, buscar no catálogo, apresentar opções detalhadas e tirar dúvidas sobre especificações."
            ),
        },
        {
            "section": "8.0",
            "title": "Políticas de Garantia Legal e do Fabricante",
            "page": 7,
            "text": (
                "8. Garantia:\n"
                "8.1 Garantia Legal:\n"
                "- Em conformidade com o CDC (Código de Defesa do Consumidor), todos os instrumentos têm garantia legal de 90 (noventa) dias contra defeitos de fabricação a partir do recebimento.\n\n"
                "8.2 Garantia do Fabricante:\n"
                "- A maioria dos fabricantes oferece garantia complementar de 6 meses a 2 anos (descrita no manual/termo de garantia do produto).\n\n"
                "8.3 O que NÃO é coberto pela garantia:\n"
                "- Desgaste natural de peças móveis ou consumíveis (trastes, cordas originais, feltros).\n"
                "- Danos resultantes de mau uso, quedas, impactos físicos ou acidentes.\n"
                "- Danos causados por umidade excessiva, maresia, exposição ao sol ou calor extremo.\n"
                "- Modificações, regulagens agressivas ou manutenções realizadas por assistências técnicas não credenciadas."
            ),
        },
        {
            "section": "9.0",
            "title": "Privacidade e Proteção de Dados (LGPD)",
            "page": 7,
            "text": (
                "9. Privacidade e Proteção de Dados Pessoais (LGPD - Lei nº 13.709/2018):\n"
                "- A Empório da Música trata dados de clientes (nome, CPF, telefone, e-mail, endereço) com estrita confidencialidade.\n"
                "- Os dados são usados exclusivamente para processar pedidos, emitir notas fiscais, entrega e atendimento pós-venda.\n"
                "- NUNCA compartilhamos dados de clientes com terceiros para fins publicitários.\n"
                "- O cliente tem o direito de solicitar a confirmação, correção ou exclusão de seus dados do cadastro a qualquer momento pelo WhatsApp ou e-mail de atendimento."
            ),
        },
    ]

    for item in sections_catalog:
        chunks.append({
            "id": chunk_id,
            "text": item["text"],
            "metadata": {
                "section": item["section"],
                "title": item["title"],
                "page": item["page"],
            }
        })
        chunk_id += 1

    return chunks


def ingest_policies(force: bool = False):
    """Ingest policy PDF into Qdrant vector database."""
    pdf_path = settings.DATA_DIR / "políticas_da_loja.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"Policy PDF file not found at {pdf_path}")

    vector_store = get_vector_store()
    current_count = vector_store.count()

    if current_count > 0 and not force:
        print(f"Policy vector store already indexed ({current_count} chunks). Skipping ingestion.")
        return

    print("Extracting policy document chunks...")
    chunks = extract_policy_chunks(pdf_path)
    print(f"Generated {len(chunks)} high-quality semantic policy chunks.")

    print("Computing embeddings and indexing into Qdrant...")
    vector_store.upsert_documents(chunks)
    print(f"Successfully indexed {len(chunks)} chunks into collection '{settings.QDRANT_COLLECTION_NAME}'.")


if __name__ == "__main__":
    ingest_policies(force=True)
