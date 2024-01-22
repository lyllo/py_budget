SELECT sq1.meio, sq1.last_transaction, sq1.last_update, sq2.total_transactions

FROM (SELECT meio, MAX(DATA) AS last_transaction, FROM_UNIXTIME(MAX(file_timestamp)) AS last_update
FROM transactions
WHERE DATA <= CURDATE() AND parcela LIKE '1/%' OR parcela = '' OR parcela IS NULL
AND meio IN (SELECT meio FROM sources WHERE fonte IS NOT NULL)
GROUP BY meio) AS sq1

INNER JOIN (SELECT meio, COUNT(1) AS total_transactions
FROM transactions
WHERE meio IN (SELECT meio FROM sources WHERE fonte IS NOT NULL)
GROUP BY meio) AS sq2

ON sq1.meio = sq2.meio
ORDER BY sq1.meio ASC