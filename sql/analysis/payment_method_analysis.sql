-- Business question: Which payment methods concentrate payment value and how many
-- orders use each method?
SELECT
    payment_type,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS average_payment_value,
    ROUND(AVG(payment_installments), 2) AS average_installments,
    ROUND(
        SUM(payment_value) / NULLIF(SUM(SUM(payment_value)) OVER (), 0),
        4
    ) AS payment_value_share
FROM marts.fact_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;
