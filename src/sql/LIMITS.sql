SELECT
    l.categoria AS categoria,
    ROUND(l.limite,2) AS plan,
    COALESCE(ROUND(SUM(t.valor), 2), 0) AS actual,
    ROUND(l.limite,2) - COALESCE(ROUND(SUM(t.valor), 2), 0) AS gap
FROM
    limits l
LEFT JOIN
    transactions t ON l.categoria = t.categoria
    AND YEAR(t.data) = YEAR(CURRENT_DATE)
    AND MONTH(t.data) = MONTH(CURRENT_DATE)
GROUP BY
    l.categoria, l.limite;