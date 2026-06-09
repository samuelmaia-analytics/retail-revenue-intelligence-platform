-- Business question: How is payment value distributed by installment count and
-- which installment profiles are most common?
SELECT
    payment_installments,
    COUNT(*) AS payment_records,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS average_payment_value,
    ROUND(
        COUNT(*)::DOUBLE / NULLIF(SUM(COUNT(*)) OVER (), 0),
        4
    ) AS payment_record_share,
    ROUND(
        SUM(payment_value) / NULLIF(SUM(SUM(payment_value)) OVER (), 0),
        4
    ) AS payment_value_share
FROM marts.fact_payments
GROUP BY payment_installments
ORDER BY payment_installments;
