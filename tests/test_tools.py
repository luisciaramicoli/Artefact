import pytest
from emporio_agent.db.seed import seed_database
from emporio_agent.agent.tools import (
    get_categories,
    query_products,
    get_product_details,
    check_order_status,
    get_store_info,
)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    seed_database()


def test_get_categories():
    res = get_categories()
    assert res["found"] is True
    assert res["total_categories"] == 9
    cat_names = [c["name"] for c in res["categories"]]
    assert "Guitarras" in cat_names
    assert "Violões" in cat_names
    assert "Teclados e Pianos" in cat_names
    assert "Baterias e Percussão" in cat_names
    assert "Ukuleles" in cat_names


def test_query_violoes_under_1000():
    res = query_products(category_name="Violões", max_price=1000.0, in_stock_only=True)
    assert res["found"] is True
    assert len(res["products"]) > 0
    for p in res["products"]:
        assert p["price_brl"] <= 1000.0
        assert p["stock_quantity"] > 0
        assert p["category"] == "Violões"
        assert "pix_discount_price_brl" in p


def test_get_takamine_gd20_details():
    res = get_product_details("Takamine GD20")
    assert res["found"] is True
    assert res["name"] == "Takamine GD20 Dreadnought Natural"
    assert res["table_price_brl"] == 2199.0
    assert res["pix_price_5pct_off_brl"] == round(2199.0 * 0.95, 2)
    assert res["stock_quantity"] == 5
    assert len(res["past_expired_promotions"]) >= 1


def test_check_order_status_delivered():
    res = check_order_status(order_id=1)
    assert res["found"] is True
    assert res["order_id"] == 1
    assert res["status_code"] == "delivered"
    assert res["tracking_code"] == "BRAB1234567BR"
    assert len(res["items"]) > 0


def test_get_store_info_scope():
    info = get_store_info()
    assert "Campo Grande" in info["address"]
    assert "(67) 3341-4444" in info["phone_whatsapp"]
    assert "EXCLUSIVAMENTE instrumentos musicais" in info["scope_restriction"]
