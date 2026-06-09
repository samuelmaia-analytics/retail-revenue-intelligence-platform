# Initial Data Quality Report

Date: 2026-06-07

## Scope

The requested path `data/raw/` is currently empty, except for `.gitkeep`.

This report therefore analyzes the available generated CSV files in `data/sample/`:

- `customers.csv`
- `products.csv`
- `orders.csv`
- `order_items.csv`
- `shipments.csv`

## Executive Summary

The generated sample data is suitable as an initial Brazilian retail/e-commerce case. It includes customers, products, orders, order items and shipments with plausible channels, payment methods, Brazilian states, carriers and commercial metrics.

The main quality issue is monetary reconciliation: some order-level fields do not exactly match item-level aggregations due to rounding at different grains. This is expected in synthetic data generated from floating point arithmetic, but should be corrected before using the dataset as a reliable analytics layer.

## File Volumes

| File | Rows | Assessment |
| --- | ---: | --- |
| `customers.csv` | 250 | Good for sample cohort and customer analysis |
| `products.csv` | 12 | Small but enough for category/product examples |
| `orders.csv` | 600 | Good for initial revenue and operations analysis |
| `order_items.csv` | 1,524 | Consistent with 1 to 4 products per order |
| `shipments.csv` | 600 | One shipment per order |

## Columns

### `customers.csv`

| Column | Expected Type | Notes |
| --- | --- | --- |
| `customer_id` | string | Unique customer key |
| `customer_name` | string | Synthetic customer name |
| `state` | string | Brazilian state abbreviation |
| `acquisition_channel` | string | Acquisition source |
| `signup_date` | date | Customer registration date |

### `products.csv`

| Column | Expected Type | Notes |
| --- | --- | --- |
| `product_id` | string | Unique product key |
| `product_name` | string | Product description |
| `category` | string | Product category |
| `unit_price` | decimal | Sale price |
| `unit_cost` | decimal | Unit cost |

### `orders.csv`

| Column | Expected Type | Notes |
| --- | --- | --- |
| `order_id` | string | Unique order key |
| `customer_id` | string | Customer foreign key |
| `order_datetime` | timestamp | Order timestamp |
| `channel` | string | Sales channel |
| `payment_method` | string | Payment method |
| `status` | string | Order status |
| `gross_revenue` | decimal | Gross order amount |
| `discount_amount` | decimal | Order discount |
| `freight_amount` | decimal | Freight charged |
| `cancellation_amount` | decimal | Cancelled amount |
| `return_amount` | decimal | Returned amount |
| `net_revenue` | decimal | Net revenue after discount, cancellation and return |
| `cost_amount` | decimal | Total cost |
| `gross_margin` | decimal | Net revenue minus cost when revenue is positive |

### `order_items.csv`

| Column | Expected Type | Notes |
| --- | --- | --- |
| `order_item_id` | string | Unique order item key |
| `order_id` | string | Order foreign key |
| `product_id` | string | Product foreign key |
| `quantity` | integer | Units sold |
| `unit_price` | decimal | Unit sale price |
| `unit_cost` | decimal | Unit cost |
| `gross_revenue` | decimal | Item gross amount |
| `discount_amount` | decimal | Item discount |
| `cost_amount` | decimal | Item cost |

### `shipments.csv`

| Column | Expected Type | Notes |
| --- | --- | --- |
| `shipment_id` | string | Unique shipment key |
| `order_id` | string | Order foreign key |
| `carrier` | string | Logistics provider |
| `promised_date` | date | Promised delivery date |
| `delivered_date` | date, nullable | Blank for cancelled orders |
| `is_late` | boolean | Whether delivery happened after promised date |

## Nulls and Blank Values

| File | Finding |
| --- | --- |
| `customers.csv` | No blank values found |
| `products.csv` | No blank values found |
| `orders.csv` | No blank values found |
| `order_items.csv` | No blank values found |
| `shipments.csv` | `delivered_date` has 92 blanks |

The 92 blank `delivered_date` values are consistent with the 92 cancelled orders.

## Key Uniqueness

| Key | Duplicates |
| --- | ---: |
| `customers.customer_id` | 0 |
| `products.product_id` | 0 |
| `orders.order_id` | 0 |
| `order_items.order_item_id` | 0 |
| `shipments.shipment_id` | 0 |

## Brazilian Retail Fit

The data is broadly coherent for a Brazilian retail/e-commerce case.

Positive points:

- Customer states use Brazilian UF abbreviations: `SP`, `RJ`, `MG`, `PR`, `RS`, `SC`, `BA`, `PE`, `GO`, `DF`.
- Payment methods include `pix`, `credit_card` and `boleto`, which are relevant for Brazil.
- Sales channels include `site`, `app` and `marketplace`.
- Logistics providers include `Correios`, `Jadlog`, `Loggi` and `Total Express`.
- Product categories are plausible for retail: fashion, footwear, electronics, home, beauty and accessories.

Potential improvement:

- Customer names are synthetic and simple, which is acceptable for a portfolio case.
- Product catalog is intentionally small. For a richer BI dashboard, consider expanding to 50 to 200 SKUs.
- Geographic distribution is fairly uniform across states. A more realistic Brazilian case would usually have higher concentration in `SP`, `RJ` and `MG`.

## Categorical Distributions

### Order Status

| Status | Rows |
| --- | ---: |
| `delivered` | 403 |
| `returned` | 105 |
| `cancelled` | 92 |

The return and cancellation rates are high but useful for demonstrating operational and margin analysis.

### Sales Channel

| Channel | Rows |
| --- | ---: |
| `site` | 217 |
| `marketplace` | 199 |
| `app` | 184 |

### Payment Method

| Payment Method | Rows |
| --- | ---: |
| `pix` | 203 |
| `credit_card` | 200 |
| `boleto` | 197 |

## Date Checks

| Field | Min | Max | Invalid Dates |
| --- | --- | --- | ---: |
| `customers.signup_date` | 2024-01-07 | 2025-06-19 | 0 |
| `orders.order_datetime` | 2025-01-02 10:49:00 | 2025-12-31 17:40:00 | 0 |
| `shipments.promised_date` | 2025-01-05 | 2026-01-07 | 0 |
| `shipments.delivered_date` | 2025-01-07 | 2026-01-07 | 0 |

Assessment:

- Order dates cover calendar year 2025, which is good for time-series analysis.
- Shipment dates extending into early 2026 are plausible because late-December orders can be delivered in January.
- Customer signup dates start before the order period, which supports retention and cohort analysis.

## Negative and Zero Values

No negative numeric values were found.

Expected zero values:

| Field | Zero Count | Assessment |
| --- | ---: | --- |
| `orders.discount_amount` | 296 | Orders without discount |
| `orders.cancellation_amount` | 508 | Non-cancelled orders |
| `orders.return_amount` | 495 | Non-returned orders |
| `orders.net_revenue` | 197 | Cancelled or returned orders |
| `orders.gross_margin` | 197 | Cancelled or returned orders |
| `order_items.discount_amount` | 767 | Items without discount |

## Numeric Ranges

| Field | Min | Max | Assessment |
| --- | ---: | ---: | --- |
| `orders.gross_revenue` | 44.90 | 3,189.00 | Plausible for multi-item retail orders |
| `orders.discount_amount` | 0.00 | 478.35 | Plausible |
| `orders.freight_amount` | 9.94 | 39.82 | Plausible for Brazilian e-commerce |
| `orders.net_revenue` | 0.00 | 2,819.00 | Plausible |
| `orders.cost_amount` | 17.00 | 1,810.00 | Plausible |
| `orders.gross_margin` | 0.00 | 1,328.00 | Plausible |
| `order_items.quantity` | 1 | 3 | Plausible |
| `products.unit_price` | 44.90 | 399.90 | Plausible |
| `products.unit_cost` | 17.00 | 238.00 | Plausible |

## Referential Integrity

| Check | Issues |
| --- | ---: |
| Orders with missing customer | 0 |
| Order items with missing order | 0 |
| Order items with missing product | 0 |
| Shipments with missing order | 0 |
| Orders without items | 0 |
| Orders without shipment | 0 |

Assessment: referential integrity is good.

## Consistency Between `orders` and `order_items`

Item-level aggregation was compared against order-level totals for:

- `gross_revenue`
- `discount_amount`
- `cost_amount`

Findings:

| Check | Result |
| --- | ---: |
| Total mismatches | 88 |
| Affected field | Mostly `discount_amount` |
| Typical difference | 0.01 to 0.02 |

Example mismatches:

| Order | Field | Order Value | Item Sum |
| --- | --- | ---: | ---: |
| `ORD-000003` | `discount_amount` | 72.97 | 72.98 |
| `ORD-000006` | `discount_amount` | 51.71 | 51.70 |
| `ORD-000010` | `discount_amount` | 151.43 | 151.42 |
| `ORD-000024` | `discount_amount` | 168.62 | 168.60 |

Assessment:

This is a data quality issue caused by rounding discount values independently at item and order grains. For analytics engineering, this should be resolved before building dbt marts. The recommended approach is to calculate financial facts from the same grain consistently, preferably from `order_items`, and then aggregate to order level.

## Business Rule Checks

| Rule | Issues |
| --- | ---: |
| `net_revenue = gross_revenue - discount_amount - cancellation_amount - return_amount` | 76 |
| `gross_margin = net_revenue - cost_amount` when net revenue is positive | 0 |
| Cancelled orders have cancellation amount | 0 |
| Non-cancelled orders do not have cancellation amount | 0 |
| Returned orders have return amount | 0 |
| Non-returned orders do not have return amount | 0 |

The 76 `net_revenue` formula mismatches are also consistent with rounding differences.

## Shipment Consistency

| Check | Issues |
| --- | ---: |
| Delivered or returned order without `delivered_date` | 0 |
| Cancelled order with `delivered_date` | 0 |
| Invalid `is_late` values | 0 |

Late deliveries:

| Metric | Value |
| --- | ---: |
| Late shipments | 203 |

Assessment:

Shipment data is internally consistent. The late delivery rate is high enough to support operational analysis.

## Recommendations

1. Populate `data/raw/` or update documentation to clarify that generated CSVs are stored in `data/sample/`.
2. Fix monetary generation logic to avoid floating point rounding drift between `orders` and `order_items`.
3. Use `Decimal` or integer cents for financial calculations in the data generator.
4. Decide whether returned orders should have `net_revenue = 0` or whether revenue should remain and returns should be modeled as a separate negative event.
5. Consider increasing product catalog size and making state distribution more realistic for Brazil.
6. Add automated tests for uniqueness, referential integrity, non-negative financials and revenue reconciliation.

## Overall Assessment

The dataset is strong enough for the first version of a portfolio project and already supports meaningful BI and analytics engineering examples. Before using it as the trusted analytical layer, the monetary reconciliation issue should be fixed or explicitly handled in dbt transformations.
