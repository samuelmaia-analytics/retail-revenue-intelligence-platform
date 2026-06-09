"""Generate synthetic retail sample data for local development."""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
RANDOM_SEED = 42


@dataclass(frozen=True)
class Product:
    product_id: str
    product_name: str
    category: str
    unit_price: float
    unit_cost: float


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write dictionaries to CSV using stable column order."""
    if not rows:
        raise ValueError(f"No rows to write for {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def money(value: float) -> float:
    return round(value, 2)


def generate_customers(total: int = 250) -> list[dict[str, object]]:
    states = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "PE", "GO", "DF"]
    channels = ["organic", "paid_search", "marketplace", "social", "email"]
    first_names = [
        "Ana",
        "Bruno",
        "Carla",
        "Diego",
        "Fernanda",
        "Gustavo",
        "Juliana",
        "Lucas",
        "Mariana",
        "Rafael",
    ]
    last_names = [
        "Silva",
        "Santos",
        "Oliveira",
        "Souza",
        "Pereira",
        "Costa",
        "Rodrigues",
        "Almeida",
    ]

    customers = []
    start_date = date(2024, 1, 1)

    for index in range(1, total + 1):
        signup_date = start_date + timedelta(days=random.randint(0, 540))
        customers.append(
            {
                "customer_id": f"CUST-{index:05d}",
                "customer_name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "state": random.choice(states),
                "acquisition_channel": random.choice(channels),
                "signup_date": signup_date.isoformat(),
            }
        )

    return customers


def generate_products() -> list[Product]:
    product_specs = [
        ("Camiseta Basica", "Moda", 59.9, 24.5),
        ("Calca Jeans", "Moda", 149.9, 72.0),
        ("Tenis Casual", "Calcados", 229.9, 118.0),
        ("Sandalia Urbana", "Calcados", 99.9, 43.0),
        ("Smart Speaker", "Eletronicos", 349.9, 221.0),
        ("Fone Bluetooth", "Eletronicos", 189.9, 91.0),
        ("Cafeteira Inox", "Casa", 279.9, 154.0),
        ("Jogo de Panelas", "Casa", 399.9, 238.0),
        ("Creme Hidratante", "Beleza", 44.9, 17.0),
        ("Perfume 100ml", "Beleza", 219.9, 93.0),
        ("Mochila Executiva", "Acessorios", 179.9, 82.0),
        ("Relogio Digital", "Acessorios", 259.9, 137.0),
    ]

    return [
        Product(
            product_id=f"PROD-{index:04d}",
            product_name=name,
            category=category,
            unit_price=price,
            unit_cost=cost,
        )
        for index, (name, category, price, cost) in enumerate(product_specs, start=1)
    ]


def generate_orders(
    customers: list[dict[str, object]],
    products: list[Product],
    total_orders: int = 600,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    channels = ["site", "app", "marketplace"]
    payment_methods = ["credit_card", "pix", "boleto"]
    statuses = ["delivered", "delivered", "delivered", "delivered", "cancelled", "returned"]
    start_date = datetime(2025, 1, 1, 8, 0, 0)

    orders = []
    order_items = []
    shipments = []

    for order_index in range(1, total_orders + 1):
        customer = random.choice(customers)
        order_datetime = start_date + timedelta(
            days=random.randint(0, 364),
            hours=random.randint(0, 12),
            minutes=random.randint(0, 59),
        )
        status = random.choice(statuses)
        discount_rate = random.choice([0, 0, 0, 0.05, 0.1, 0.15])
        freight_amount = money(random.uniform(9.9, 39.9))
        order_id = f"ORD-{order_index:06d}"

        selected_products = random.sample(products, k=random.randint(1, 4))
        gross_revenue = 0.0
        discount_amount = 0.0
        cost_amount = 0.0

        for item_index, product in enumerate(selected_products, start=1):
            quantity = random.randint(1, 3)
            item_gross = product.unit_price * quantity
            item_discount = item_gross * discount_rate
            item_cost = product.unit_cost * quantity

            gross_revenue += item_gross
            discount_amount += item_discount
            cost_amount += item_cost

            order_items.append(
                {
                    "order_item_id": f"{order_id}-{item_index:02d}",
                    "order_id": order_id,
                    "product_id": product.product_id,
                    "quantity": quantity,
                    "unit_price": money(product.unit_price),
                    "unit_cost": money(product.unit_cost),
                    "gross_revenue": money(item_gross),
                    "discount_amount": money(item_discount),
                    "cost_amount": money(item_cost),
                }
            )

        cancellation_amount = gross_revenue - discount_amount if status == "cancelled" else 0.0
        return_amount = gross_revenue - discount_amount if status == "returned" else 0.0
        net_revenue = gross_revenue - discount_amount - cancellation_amount - return_amount

        orders.append(
            {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "order_datetime": order_datetime.isoformat(sep=" "),
                "channel": random.choice(channels),
                "payment_method": random.choice(payment_methods),
                "status": status,
                "gross_revenue": money(gross_revenue),
                "discount_amount": money(discount_amount),
                "freight_amount": freight_amount,
                "cancellation_amount": money(cancellation_amount),
                "return_amount": money(return_amount),
                "net_revenue": money(net_revenue),
                "cost_amount": money(cost_amount),
                "gross_margin": money(net_revenue - cost_amount if net_revenue > 0 else 0),
            }
        )

        promised_date = order_datetime.date() + timedelta(days=random.randint(3, 8))
        delivered_date = None
        if status in {"delivered", "returned"}:
            delivered_date = promised_date + timedelta(days=random.choice([-1, 0, 0, 1, 2]))

        shipments.append(
            {
                "shipment_id": f"SHP-{order_index:06d}",
                "order_id": order_id,
                "carrier": random.choice(["Correios", "Jadlog", "Loggi", "Total Express"]),
                "promised_date": promised_date.isoformat(),
                "delivered_date": delivered_date.isoformat() if delivered_date else "",
                "is_late": bool(delivered_date and delivered_date > promised_date),
            }
        )

    return orders, order_items, shipments


def main() -> None:
    random.seed(RANDOM_SEED)

    customers = generate_customers()
    products = generate_products()
    orders, order_items, shipments = generate_orders(customers, products)

    product_rows = [
        {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "category": product.category,
            "unit_price": money(product.unit_price),
            "unit_cost": money(product.unit_cost),
        }
        for product in products
    ]

    outputs = {
        "customers.csv": customers,
        "products.csv": product_rows,
        "orders.csv": orders,
        "order_items.csv": order_items,
        "shipments.csv": shipments,
    }

    for filename, rows in outputs.items():
        write_csv(SAMPLE_DIR / filename, rows)

    print(f"Generated sample data in {SAMPLE_DIR}")
    for filename, rows in outputs.items():
        print(f"- {filename}: {len(rows)} rows")


if __name__ == "__main__":
    main()
