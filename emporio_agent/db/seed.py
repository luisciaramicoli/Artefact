import os
import pandas as pd
from pathlib import Path
from sqlalchemy.orm import Session
from emporio_agent.config import settings
from emporio_agent.db.database import SessionLocal, init_db
from emporio_agent.db.models import (
    Category,
    Product,
    Customer,
    Order,
    OrderItem,
    Promotion,
)


def seed_database(force: bool = False):
    """Seed relational database from provided CSV files."""
    init_db()
    db: Session = SessionLocal()

    try:
        data_dir = settings.DATA_DIR

        # Check if already seeded
        if not force and db.query(Product).count() > 0:
            print("Database already populated. Skipping seed.")
            return

        print("Seeding database from CSVs...")

        # 1. Categories
        cat_file = data_dir / "desafio_tecnico_ai_eng - categories.csv"
        if cat_file.exists():
            df_cat = pd.read_csv(cat_file)
            for _, row in df_cat.iterrows():
                cat = Category(
                    category_id=int(row["category_id"]),
                    name=str(row["name"]).strip(),
                    description=str(row["description"]).strip() if pd.notna(row["description"]) else None,
                )
                db.merge(cat)
            db.commit()
            print(f"Loaded {len(df_cat)} categories.")

        # 2. Customers
        cust_file = data_dir / "desafio_tecnico_ai_eng - customers.csv"
        if cust_file.exists():
            df_cust = pd.read_csv(cust_file)
            for _, row in df_cust.iterrows():
                cust = Customer(
                    customer_id=int(row["customer_id"]),
                    name=str(row["name"]).strip(),
                    phone=str(row["phone"]).strip(),
                    email=str(row["email"]).strip(),
                    city=str(row["city"]).strip() if pd.notna(row["city"]) else None,
                )
                db.merge(cust)
            db.commit()
            print(f"Loaded {len(df_cust)} customers.")

        # 3. Products
        prod_file = data_dir / "desafio_tecnico_ai_eng - products.csv"
        if prod_file.exists():
            df_prod = pd.read_csv(prod_file)
            for _, row in df_prod.iterrows():
                prod = Product(
                    product_id=int(row["product_id"]),
                    name=str(row["name"]).strip(),
                    price_brl=float(row["price_brl"]),
                    category_id=int(row["category_id"]),
                    description=str(row["description"]).strip() if pd.notna(row["description"]) else None,
                    stock_quantity=int(row["stock_quantity"]) if pd.notna(row["stock_quantity"]) else 0,
                    status=str(row["status"]).strip() if pd.notna(row["status"]) else "active",
                    specs=str(row["specs"]).strip() if pd.notna(row["specs"]) else None,
                    created_at=str(row["created_at"]).strip() if pd.notna(row["created_at"]) else None,
                )
                db.merge(prod)
            db.commit()
            print(f"Loaded {len(df_prod)} products.")

        # 4. Promotions
        promo_file = data_dir / "desafio_tecnico_ai_eng - promotions.csv"
        if promo_file.exists():
            df_promo = pd.read_csv(promo_file)
            for _, row in df_promo.iterrows():
                promo = Promotion(
                    promotion_id=int(row["promotion_id"]),
                    product_id=int(row["product_id"]),
                    discount_percent=int(row["discount_percent"]),
                    description=str(row["description"]).strip() if pd.notna(row["description"]) else None,
                    is_active=int(row["is_active"]) if pd.notna(row["is_active"]) else 0,
                )
                db.merge(promo)
            db.commit()
            print(f"Loaded {len(df_promo)} promotions.")

        # 5. Orders
        order_file = data_dir / "desafio_tecnico_ai_eng - orders.csv"
        if order_file.exists():
            df_order = pd.read_csv(order_file)
            for _, row in df_order.iterrows():
                ord_obj = Order(
                    order_id=int(row["order_id"]),
                    customer_id=int(row["customer_id"]),
                    order_date=str(row["order_date"]).strip(),
                    status=str(row["status"]).strip(),
                    total_brl=float(row["total_brl"]),
                    payment_method=str(row["payment_method"]).strip(),
                    tracking_code=str(row["tracking_code"]).strip() if pd.notna(row["tracking_code"]) else None,
                    estimated_delivery=str(row["estimated_delivery"]).strip() if pd.notna(row["estimated_delivery"]) else None,
                    notes=str(row["notes"]).strip() if pd.notna(row["notes"]) else None,
                )
                db.merge(ord_obj)
            db.commit()
            print(f"Loaded {len(df_order)} orders.")

        # 6. Order Items
        items_file = data_dir / "desafio_tecnico_ai_eng - order_items.csv"
        if items_file.exists():
            df_items = pd.read_csv(items_file)
            # Remove existing order items if force
            if force:
                db.query(OrderItem).delete()
            for _, row in df_items.iterrows():
                item = OrderItem(
                    order_id=int(row["order_id"]),
                    product_id=int(row["product_id"]),
                    quantity=int(row["quantity"]),
                )
                db.add(item)
            db.commit()
            print(f"Loaded {len(df_items)} order items.")

        print("Database seed completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(force=True)
