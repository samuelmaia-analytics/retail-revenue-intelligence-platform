# Business Metrics

## Scope

This document defines the main business metrics for the Retail Revenue Intelligence Platform using the Brazilian E-Commerce Public Dataset by Olist.

Marketing campaign metrics are not part of the main scope because the Olist dataset does not include campaign, media investment, attribution or customer exposure data.

## Mandatory Interpretation Notes

- Olist does not provide product cost. Real margin must not be calculated without a documented simulation or an external cost source.
- `staging.stg_order_items.item_price` comes from Olist `order_items.price` and represents the item value.
- `staging.stg_order_items.freight_value` represents freight charged at item level.
- `staging.stg_order_payments.payment_value` can have multiple records per order because orders may have split payments.
- Retention metrics must use `customer_unique_id`, not `customer_id`.
- Campaign metrics are excluded from the principal model.

## Metrics

### 1. Gross Revenue

- Technical name: `gross_revenue`
- Business name: Gross Revenue
- Description: Total merchandise value sold, based on item prices.
- Formula: `SUM(fact_order_items.item_price)` or `SUM(fact_orders.gross_revenue)`.
- Source table: `marts.fact_order_items`, `marts.fact_orders`, `marts.fact_revenue_daily`
- Recommended grain: order date, customer state, product category, seller.
- Important notes: This does not include freight unless explicitly added.
- Interpretation pitfalls: Do not compare directly with `payment_value`; payments can include freight and split payments.

### 2. Freight Revenue

- Technical name: `freight_value`
- Business name: Freight Revenue
- Description: Total freight amount associated with sold items.
- Formula: `SUM(fact_order_items.freight_value)` or `SUM(fact_orders.freight_value)`.
- Source table: `marts.fact_order_items`, `marts.fact_orders`, `marts.fact_revenue_daily`
- Recommended grain: order date, customer state, seller state, product category.
- Important notes: Freight is available at item level in Olist.
- Interpretation pitfalls: Freight is not product revenue and should be analyzed separately from merchandise value.

### 3. Total Payment Value

- Technical name: `total_payment_value`
- Business name: Total Payment Value
- Description: Total value paid by customers across all payment records.
- Formula: `SUM(fact_payments.payment_value)` or `SUM(fact_orders.total_payment_value)`.
- Source table: `marts.fact_payments`, `marts.fact_orders`
- Recommended grain: order, payment type, order date.
- Important notes: One order can have multiple payment rows.
- Interpretation pitfalls: Summing payment records without order awareness is valid for total paid value, but counting rows is not the same as counting orders.

### 4. Total Orders

- Technical name: `total_orders`
- Business name: Total Orders
- Description: Number of distinct orders.
- Formula: `COUNT(DISTINCT fact_orders.order_id)`.
- Source table: `marts.fact_orders`, `marts.fact_revenue_daily`
- Recommended grain: order date, customer state, product category, seller.
- Important notes: Use distinct order count when joining to item-level facts.
- Interpretation pitfalls: Counting rows in `fact_order_items` gives item count, not order count.

### 5. Delivered Orders

- Technical name: `delivered_orders`
- Business name: Delivered Orders
- Description: Number of orders marked as delivered.
- Formula: `COUNT(DISTINCT CASE WHEN fact_orders.is_delivered THEN order_id END)`.
- Source table: `marts.fact_orders`, `marts.fact_revenue_daily`
- Recommended grain: order date, customer state, product category.
- Important notes: Based on Olist `order_status = 'delivered'`.
- Interpretation pitfalls: Delivered status should not be inferred only from non-null delivery date.

### 6. Cancelled Orders

- Technical name: `cancelled_orders`
- Business name: Cancelled Orders
- Description: Number of orders marked as canceled.
- Formula: `COUNT(DISTINCT CASE WHEN fact_orders.is_cancelled THEN order_id END)`.
- Source table: `marts.fact_orders`, `marts.fact_revenue_daily`
- Recommended grain: order date, customer state, product category.
- Important notes: Based on Olist `order_status = 'canceled'`.
- Interpretation pitfalls: Canceled orders may still have payment or item records depending on lifecycle timing.

### 7. Cancellation Rate

- Technical name: `cancellation_rate`
- Business name: Cancellation Rate
- Description: Share of orders that were canceled.
- Formula: `Cancelled Orders / Total Orders`.
- Source table: `marts.fact_orders`
- Recommended grain: order date, customer state.
- Important notes: Use distinct orders in numerator and denominator.
- Interpretation pitfalls: Do not calculate this from item rows without deduplicating orders.

### 8. Late Delivery Rate

- Technical name: `late_delivery_rate`
- Business name: Late Delivery Rate
- Description: Share of delivered orders where delivery happened after the estimated delivery date.
- Formula: `COUNT(DISTINCT late order_id) / COUNT(DISTINCT delivered order_id)`.
- Source table: `marts.fact_orders`, `marts.fact_revenue_daily`, `marts.fact_seller_performance`
- Recommended grain: order date, customer state, seller.
- Important notes: Late delivery is defined as `delivered_customer_date > estimated_delivery_date`.
- Interpretation pitfalls: Orders without delivery date should not be treated as late unless business rules explicitly say so.

### 9. Average Delivery Days

- Technical name: `average_delivery_days`
- Business name: Average Delivery Days
- Description: Average number of days between purchase and customer delivery.
- Formula: `AVG(fact_orders.delivery_days)`.
- Source table: `marts.fact_orders`
- Recommended grain: order date, customer state, seller state.
- Important notes: Use delivered orders with non-null `delivery_days`.
- Interpretation pitfalls: Including undelivered or canceled orders can distort the metric.

### 10. Average Order Value

- Technical name: `average_order_value`
- Business name: Average Order Value
- Description: Average merchandise revenue per order.
- Formula: `Gross Revenue / Total Orders`.
- Source table: `marts.fact_orders`, `marts.fact_revenue_daily`
- Recommended grain: order date, customer state, product category.
- Important notes: In `fact_revenue_daily`, this is calculated at day, state and category grain.
- Interpretation pitfalls: Category-level AOV can double count multi-category orders if rolled up without care.

### 11. Average Review Score

- Technical name: `average_review_score`
- Business name: Average Review Score
- Description: Average customer review score.
- Formula: `AVG(fact_reviews.review_score)`.
- Source table: `marts.fact_reviews`, `marts.fact_seller_performance`
- Recommended grain: order date, customer state, seller.
- Important notes: Olist review scores usually range from 1 to 5.
- Interpretation pitfalls: Reviews are not guaranteed to exist for every order.

### 12. Review Comment Rate

- Technical name: `review_comment_rate`
- Business name: Review Comment Rate
- Description: Share of reviews with a title or message.
- Formula: `COUNT(CASE WHEN has_review_comment THEN review_id END) / COUNT(review_id)`.
- Source table: `marts.fact_reviews`
- Recommended grain: review creation date, customer state, review score.
- Important notes: Uses the staged boolean `has_review_comment`.
- Interpretation pitfalls: A missing comment does not mean a negative review.

### 13. Repeat Customers

- Technical name: `repeat_customers`
- Business name: Repeat Customers
- Description: Number of customers with more than one order.
- Formula: `COUNT(customer_unique_id) WHERE total_orders >= 2`.
- Source table: `marts.fact_customer_retention`
- Recommended grain: customer segment, first order month.
- Important notes: Must use `customer_unique_id`.
- Interpretation pitfalls: `customer_id` is order-specific in Olist and can understate repeat behavior.

### 14. Repeat Purchase Rate

- Technical name: `repeat_purchase_rate`
- Business name: Repeat Purchase Rate
- Description: Share of unique customers who purchased more than once.
- Formula: `Repeat Customers / COUNT(customer_unique_id)`.
- Source table: `marts.fact_customer_retention`
- Recommended grain: customer segment, first order cohort.
- Important notes: Use customer-level retention table to avoid duplicate counting.
- Interpretation pitfalls: Dataset time window limits observed repeat purchases.

### 15. Customer Lifetime Revenue

- Technical name: `customer_lifetime_revenue`
- Business name: Customer Lifetime Revenue
- Description: Total merchandise revenue generated by a unique customer within the dataset period.
- Formula: `SUM(gross_revenue) BY customer_unique_id`.
- Source table: `marts.fact_customer_retention`
- Recommended grain: `customer_unique_id`, customer segment.
- Important notes: This is lifetime revenue inside the dataset window, not all-time real customer lifetime value.
- Interpretation pitfalls: Do not call this LTV unless acquisition cost and margin assumptions are defined.

### 16. Days Since Last Purchase

- Technical name: `days_since_last_purchase`
- Business name: Days Since Last Purchase
- Description: Days between a customer's last order and the maximum order date in the dataset.
- Formula: `DATE_DIFF('day', last_order_date, dataset_max_order_date)`.
- Source table: `marts.fact_customer_retention`
- Recommended grain: `customer_unique_id`, customer segment.
- Important notes: Uses dataset maximum order date as reference, not current system date.
- Interpretation pitfalls: Using current date would make the metric stale and misleading for historical data.

### 17. Revenue by State

- Technical name: `revenue_by_state`
- Business name: Revenue by State
- Description: Gross revenue grouped by customer state.
- Formula: `SUM(gross_revenue) GROUP BY customer_state`.
- Source table: `marts.fact_orders`, `marts.fact_revenue_daily`
- Recommended grain: customer state, order date.
- Important notes: This uses customer state, not seller state.
- Interpretation pitfalls: Clarify whether the state dimension refers to customer, seller or geolocation.

### 18. Revenue by Product Category

- Technical name: `revenue_by_product_category`
- Business name: Revenue by Product Category
- Description: Gross revenue grouped by translated product category.
- Formula: `SUM(item_price) GROUP BY product_category_name_english`.
- Source table: `marts.fact_order_items`, `marts.fact_revenue_daily`
- Recommended grain: product category, order date, customer state.
- Important notes: If translation is missing, the original category is retained.
- Interpretation pitfalls: Multi-category orders can appear in multiple categories.

### 19. Revenue by Seller State

- Technical name: `revenue_by_seller_state`
- Business name: Revenue by Seller State
- Description: Gross revenue grouped by seller state.
- Formula: `SUM(gross_revenue) GROUP BY seller_state`.
- Source table: `marts.fact_seller_performance`, `marts.fact_order_items`
- Recommended grain: seller state, seller, order date.
- Important notes: This describes seller location, not customer demand location.
- Interpretation pitfalls: Do not mix seller state with customer state without explicit labeling.

### 20. Seller Late Delivery Rate

- Technical name: `seller_late_delivery_rate`
- Business name: Seller Late Delivery Rate
- Description: Share of a seller's orders delivered after the estimated delivery date.
- Formula: `late_deliveries / total_orders`.
- Source table: `marts.fact_seller_performance`
- Recommended grain: seller, seller state.
- Important notes: Uses distinct late orders per seller.
- Interpretation pitfalls: Sellers with few orders can have volatile rates.

### 21. Payment Method Share

- Technical name: `payment_method_share`
- Business name: Payment Method Share
- Description: Share of payment value or payment records by payment method.
- Formula: `SUM(payment_value) BY payment_type / SUM(payment_value)` or `COUNT(*) BY payment_type / COUNT(*)`.
- Source table: `marts.fact_payments`
- Recommended grain: payment type, order date if joined to orders.
- Important notes: State clearly whether share is value-based or count-based.
- Interpretation pitfalls: Multiple payment rows per order can inflate count-based shares.

### 22. Average Installments

- Technical name: `average_installments`
- Business name: Average Installments
- Description: Average number of installments used in payments.
- Formula: `AVG(payment_installments)`.
- Source table: `marts.fact_payments`
- Recommended grain: payment type, order date if joined to orders.
- Important notes: Most useful when filtered to installment-compatible payment methods.
- Interpretation pitfalls: Some payment methods may have zero or one installment by definition.
