SELECT
    s.meio AS meio,
    MAX(t.data) AS dt_ultima_transacao,
    FROM_UNIXTIME(MAX(t.file_timestamp)) AS dt_ultima_atualizacao,
    FROM_UNIXTIME(f.mtime) AS dt_ultimo_arquivo,
    total_transacoes.Total AS total_transacoes
FROM
    sources s
JOIN
    transactions t ON s.meio = t.meio
JOIN
    files f ON s.fonte = f.nome
JOIN
    (SELECT meio, COUNT(1) AS Total FROM transactions GROUP BY meio) AS total_transacoes
        ON s.meio = total_transacoes.meio
WHERE
	 DATA <= CURDATE() AND 
	 parcela LIKE '1/%' 
	 OR parcela = '' 
	 OR parcela IS NULL
GROUP BY
    s.meio, f.mtime, total_transacoes.Total