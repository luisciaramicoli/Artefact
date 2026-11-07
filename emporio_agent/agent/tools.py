import json
from typing import Optional, Dict, Any, List, Union
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from emporio_agent.db.database import SessionLocal
from emporio_agent.db.models import Product, Category, Promotion, Order, OrderItem, Customer
from emporio_agent.rag.vector_store import get_vector_store


def search_store_policies(query: str) -> Dict[str, Any]:
    """
    Pesquisa as políticas oficiais e manuais internos da Empório da Música no banco vetorial Qdrant.
    Use sempre que a pergunta envolver regras de trocas, devoluções, direito de arrependimento,
    prazos de frete, garantias, horário de funcionamento, formas de pagamento, regras de parcelamento,
    privacidade/LGPD ou limites de atendimento da loja.

    Args:
        query: Pergunta ou tópicos a pesquisar (ex: "prazo de devolução por arrependimento", "horário de atendimento no sábado", "parcelamento no cartão").
    """
    try:
        vs = get_vector_store()
        results = vs.search(query=query, limit=3, score_threshold=0.35)
        if not results:
            return {
                "found": False,
                "message": "Nenhuma seção específica de políticas encontrada para essa consulta.",
                "results": []
            }

        return {
            "found": True,
            "count": len(results),
            "results": [
                {
                    "section": r["section"],
                    "title": r["title"],
                    "page": r["page"],
                    "content": r["text"]
                }
                for r in results
            ]
        }
    except Exception as e:
        return {"error": f"Erro ao consultar políticas: {str(e)}"}


def query_products(
    category_name: Optional[str] = None,
    max_price: Union[int, float, None] = None,
    min_price: Union[int, float, None] = None,
    search_text: Optional[str] = None,
    in_stock_only: bool = True,
    limit: int = 6
) -> Dict[str, Any]:
    """
    Consulta o catálogo de instrumentos musicais da Empório da Música no banco de dados.
    Permite filtrar por categoria, faixa de preço, texto de busca (marca ou modelo) e disponibilidade.

    Args:
        category_name: Nome ou parte do nome da categoria (ex: "Violões", "Guitarras", "Baixos", "Teclados e Pianos", "Baterias e Percussão", "Sopro").
        max_price: Preço máximo em Reais (BRL).
        min_price: Preço mínimo em Reais (BRL).
        search_text: Palavra-chave para buscar no nome ou descrição do instrumento (ex: "Takamine", "Yamaha", "Fender", "Strinberg", "Nylon").
        in_stock_only: Se True, retorna apenas instrumentos com estoque disponível (> 0) e status ativo.
        limit: Quantidade máxima de produtos a retornar (padrão: 6).
    """
    db: Session = SessionLocal()
    try:
        q = db.query(Product).join(Category)

        # Filters
        if in_stock_only:
            q = q.filter(Product.status == "active", Product.stock_quantity > 0)

        if max_price is not None:
            q = q.filter(Product.price_brl <= float(max_price))

        if min_price is not None:
            q = q.filter(Product.price_brl >= float(min_price))

        if category_name:
            cat_clean = category_name.strip().lower()
            q = q.filter(Category.name.ilike(f"%{cat_clean}%"))

        if search_text:
            text_clean = search_text.strip().lower()
            q = q.filter(
                or_(
                    Product.name.ilike(f"%{text_clean}%"),
                    Product.description.ilike(f"%{text_clean}%")
                )
            )

        products = q.order_by(Product.price_brl.asc()).limit(limit).all()

        if not products:
            return {
                "found": False,
                "message": "Nenhum instrumento musical encontrado com os filtros informados.",
                "products": []
            }

        product_list = []
        for p in products:
            # Check active promotion
            active_promo = db.query(Promotion).filter(
                Promotion.product_id == p.product_id,
                Promotion.is_active == 1
            ).first()

            current_price = p.price_brl
            promo_info = None
            if active_promo:
                discount_val = current_price * (active_promo.discount_percent / 100.0)
                promo_price = current_price - discount_val
                promo_info = {
                    "promotion_name": active_promo.description,
                    "discount_percent": active_promo.discount_percent,
                    "discounted_price_brl": round(promo_price, 2)
                }

            # Parse specs if available
            specs_dict = {}
            if p.specs:
                try:
                    specs_dict = json.loads(p.specs)
                except Exception:
                    specs_dict = {"specs_raw": p.specs}

            product_list.append({
                "product_id": p.product_id,
                "name": p.name,
                "category": p.category.name if p.category else "Instrumentos",
                "price_brl": round(p.price_brl, 2),
                "pix_discount_price_brl": round(p.price_brl * 0.95, 2),
                "stock_quantity": p.stock_quantity,
                "status": p.status,
                "promotion": promo_info,
                "description": p.description,
                "specs": specs_dict
            })

        return {
            "found": True,
            "count": len(product_list),
            "products": product_list
        }
    except Exception as e:
        return {"error": f"Erro ao consultar catálogo: {str(e)}"}
    finally:
        db.close()


def get_product_details(product_name_or_id: str) -> Dict[str, Any]:
    """
    Obtém a ficha técnica completa, preço exato, histórico de promoções e disponibilidade de um produto específico.

    Args:
        product_name_or_id: ID numérico do produto (ex: '95') ou nome/modelo exato (ex: 'Takamine GD20', 'Yamaha C40').
    """
    db: Session = SessionLocal()
    try:
        clean_input = str(product_name_or_id).strip()

        p = None
        if clean_input.isdigit():
            p = db.query(Product).filter(Product.product_id == int(clean_input)).first()

        if not p:
            p = db.query(Product).filter(Product.name.ilike(f"%{clean_input}%")).first()

        if not p:
            return {
                "found": False,
                "message": f"Instrumento '{clean_input}' não encontrado no catálogo da Empório da Música."
            }

        # Check promotions (both active and inactive to handle customer questions about expired promos)
        promotions = db.query(Promotion).filter(Promotion.product_id == p.product_id).all()
        active_promo = next((pr for pr in promotions if pr.is_active == 1), None)
        expired_promos = [pr for pr in promotions if pr.is_active == 0]

        current_price = p.price_brl
        promo_details = None
        if active_promo:
            discount_val = current_price * (active_promo.discount_percent / 100.0)
            promo_details = {
                "is_active": True,
                "campaign": active_promo.description,
                "discount_percent": active_promo.discount_percent,
                "promotional_price_brl": round(current_price - discount_val, 2)
            }

        expired_details = [
            {
                "campaign": exp.description,
                "discount_percent": exp.discount_percent,
                "status": "expirada/inativa"
            }
            for exp in expired_promos
        ]

        specs_dict = {}
        if p.specs:
            try:
                specs_dict = json.loads(p.specs)
            except Exception:
                specs_dict = {"specs_raw": p.specs}

        return {
            "found": True,
            "product_id": p.product_id,
            "name": p.name,
            "category": p.category.name if p.category else "Instrumentos",
            "table_price_brl": round(p.price_brl, 2),
            "pix_price_5pct_off_brl": round(p.price_brl * 0.95, 2),
            "max_installments_card": "Até 12x sem juros (parcela mínima de R$ 100,00)",
            "stock_quantity": p.stock_quantity,
            "status": p.status,
            "is_discontinued": p.status == "discontinued",
            "active_promotion": promo_details,
            "past_expired_promotions": expired_details,
            "description": p.description,
            "specs": specs_dict
        }
    except Exception as e:
        return {"error": f"Erro ao buscar detalhes do instrumento: {str(e)}"}
    finally:
        db.close()


def check_order_status(
    order_id: Union[int, str, None] = None,
    tracking_code: Optional[str] = None,
    customer_identifier: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consulta o status, código de rastreamento, previsão de entrega e itens de um pedido de cliente.

    Args:
        order_id: Número/ID do pedido (ex: 1, 2, 15).
        tracking_code: Código de rastreamento (ex: 'BRAB1234567BR').
        customer_identifier: Nome, e-mail ou telefone do cliente para localizar seus pedidos.
    """
    db: Session = SessionLocal()
    try:
        q = db.query(Order).join(Customer)

        found_order = None
        if order_id is not None:
            try:
                numeric_order_id = int(order_id)
                found_order = q.filter(Order.order_id == numeric_order_id).first()
            except (ValueError, TypeError):
                pass

        if not found_order and tracking_code:
            found_order = q.filter(Order.tracking_code.ilike(tracking_code.strip())).first()

        if not found_order and customer_identifier:
            c_clean = customer_identifier.strip()
            found_order = q.filter(
                or_(
                    Customer.name.ilike(f"%{c_clean}%"),
                    Customer.email.ilike(f"%{c_clean}%"),
                    Customer.phone.ilike(f"%{c_clean}%")
                )
            ).order_by(Order.order_id.desc()).first()

        if not found_order:
            return {
                "found": False,
                "message": "Nenhum pedido localizado com os dados informados. Solicite ao cliente o número do pedido ou CPF/e-mail cadastrado."
            }

        # Fetch items
        items = db.query(OrderItem).filter(OrderItem.order_id == found_order.order_id).all()
        order_items_list = []
        for it in items:
            p = db.query(Product).filter(Product.product_id == it.product_id).first()
            order_items_list.append({
                "product_id": it.product_id,
                "product_name": p.name if p else "Produto não identificado",
                "quantity": it.quantity,
                "unit_price_brl": round(p.price_brl, 2) if p else None
            })

        status_pt_map = {
            "delivered": "Entregue",
            "in_transit": "Em trânsito / A caminho",
            "processing": "Em processamento / Preparando envio",
            "cancelled": "Cancelado"
        }

        return {
            "found": True,
            "order_id": found_order.order_id,
            "customer_name": found_order.customer.name if found_order.customer else None,
            "order_date": found_order.order_date,
            "status_code": found_order.status,
            "status_label": status_pt_map.get(found_order.status, found_order.status),
            "tracking_code": found_order.tracking_code or "Aguardando geração do código de postagem",
            "estimated_delivery": found_order.estimated_delivery or "Sob consulta com a transportadora",
            "total_brl": round(found_order.total_brl, 2),
            "payment_method": found_order.payment_method,
            "notes": found_order.notes,
            "items": order_items_list
        }
    except Exception as e:
        return {"error": f"Erro ao consultar pedido: {str(e)}"}
    finally:
        db.close()


def get_categories() -> Dict[str, Any]:
    """
    Retorna a lista completa de todas as categorias e departamentos de instrumentos musicais comercializados pela Empório da Música.
    Use sempre que o cliente perguntar de forma ampla quais produtos a loja oferece, quais instrumentos vende,
    quais categorias existem no catálogo ou quando quiser uma visão geral dos departamentos.
    """
    db: Session = SessionLocal()
    try:
        categories = db.query(Category).order_by(Category.category_id.asc()).all()
        cat_list = []
        for cat in categories:
            prod_count = db.query(Product).filter(
                Product.category_id == cat.category_id,
                Product.status == "active"
            ).count()
            cat_list.append({
                "category_id": cat.category_id,
                "name": cat.name,
                "description": cat.description,
                "active_products_in_stock": prod_count
            })

        return {
            "found": True,
            "total_categories": len(cat_list),
            "categories": cat_list,
            "scope_reminder": "Trabalhamos exclusivamente com instrumentos musicais nessas categorias. Não vendemos acessórios (cordas, palhetas, cabos, cases, etc.)."
        }
    except Exception as e:
        return {"error": f"Erro ao listar categorias: {str(e)}"}
    finally:
        db.close()


def get_store_info() -> Dict[str, Any]:
    """
    Retorna informações essenciais e gerais sobre a Empório da Música:
    endereço, telefone/WhatsApp, horários, localização e regras de escopo.
    """
    return {
        "store_name": "Empório da Música",
        "founded": 2008,
        "address": "Rua 14 de Maio, 3200 — Centro, Campo Grande - MS, CEP 79202-333",
        "phone_whatsapp": "(67) 3341-4444",
        "email": "contato@emporiodamusica.com.br",
        "opening_hours": {
            "monday_to_friday": "09:00 às 18:00",
            "saturday": "09:00 às 13:00",
            "sunday_and_holidays": "Fechado"
        },
        "instrument_categories": [
            "Guitarras",
            "Baixos",
            "Baterias e Percussão",
            "Teclados e Pianos",
            "Violões",
            "Instrumentos de Sopro (Madeiras)",
            "Instrumentos de Sopro (Metais)",
            "Cordas Orquestrais",
            "Ukuleles"
        ],
        "payment_options": "PIX (5% de desconto à vista), Débito, Cartão de Crédito em até 12x sem juros (parcela mínima R$ 100), Boleto Bancário",
        "shipping": "Frete Grátis para Campo Grande acima de R$ 300 (ou fixo R$ 19,90). Retirada gratuita na loja em até 2h após confirmação do pagamento.",
        "scope_restriction": "A Empório da Música vende EXCLUSIVAMENTE instrumentos musicais. NÃO comercializa acessórios como cabos, cordas, palhetas, cases ou amplificadores."
    }

