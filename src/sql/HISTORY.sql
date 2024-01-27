-- Gera todas as combinações possíveis de categoria e período para o mês atual e últimos 5 meses
WITH categorias_periodos AS (
    SELECT DISTINCT
        c.categoria,
        p.periodo
    FROM
        (SELECT DISTINCT categoria FROM limits) c
    CROSS JOIN
        (SELECT DISTINCT DATE_FORMAT(DATA, '%Y-%m') AS periodo FROM transactions WHERE data >= DATE_SUB(CURDATE(), INTERVAL 5 MONTH) AND data <= CURDATE()) p
)

-- Faz um LEFT JOIN com a tabela transactions para obter a soma de gastos
SELECT
    cp.categoria,
    cp.periodo,
    COALESCE(ROUND(SUM(t.valor), 2), 0) AS total
FROM
    categorias_periodos cp
LEFT JOIN
    transactions t ON cp.categoria = t.categoria AND cp.periodo = DATE_FORMAT(t.DATA, '%Y-%m')
GROUP BY
    cp.categoria,
    cp.periodo
ORDER BY
    cp.categoria,
    cp.periodo;
