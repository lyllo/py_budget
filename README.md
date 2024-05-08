# py_budget

Esta aplicação python tem como objetivo ajudar com a gestão financeira pessoal e é composta basicamente por 3 módulos: Extract, Transform, Load (ETL).

## Extract

Realiza o scraping nos sites das instituições financeiras. Nesta etapa apenas busca os dados no formato em que são disponibilizados (ex: .xls, .xlsx).

### BTG

Não oferece exportação de arquivos, então faz copy paste das transações da timeline em um arquivo .txt que é salvo na pasta `/in`.

Obs: Precisa informar OTP do APP Banking antes da execução do programa.

### Flash

Não oferece exportação de arquivos, então faz copy paste das transações da timeline em um arquivo .txt que é salvo na pasta /in.

Obs: Precisa informar OTP enviado por SMS durante a execução do programa.

### GPA 

Exporta a fatura do cartão GPA pelo site do Itaú no formato .xls (Excel 1997).

Obs: Não precisa informar OTP para consultar dados.

### Itaú

Exporta o extrato da conta corrente no formato .xls (Excel 1997).

Obs: Não precisa informar OTP para consultar dados.

### Pendências

* Contas de Investimento:
    * BTG
    * XP
    * Rico
    * Sofisa
    * Pine

* Cartões de Crédito:
    * XP (Mobile Only)

## Transform

Varre os arquivos de entrada para normalizar as transações financeiras, buscando os seguintes dados:

* [DATE] data: Data no formato aaaa-mm-dd da transação
* [CHAR] item: Texto com histórico da transação (i.e. descrição)
* [CHAR] detalhe: Texto para preenchimento manual com detalhes da transação
* [FLOAT] valor: Valor da transação em R$
* [CHAR] cartao: Texto com o nome do portador do cartão que realizou a transação (aplicável apenas a transações de cartão de crédito)
* [CHAR] parcela: Texto que representa a parcela da transação no formato '1/2'
* [INT] ocorrencia_dia: Geralmente é 1, mas pode ser maior quando há mais de uma transação na mesma data com o mesmo valor (ex: Compra de bebida em uma festa)
* [CHAR] categoria: Texto com o nome da categoria da transação, entre uma lista com cerca de 20 categorias e com cerca de 4 formas de obtenção.
* [CHAR] categoria_fonte: Texto com o nome da forma de obtenção da categoria (exact_match, similar_match, ai_match, manual).
    * exact_match: Quando encontra outra transação com item idêntico.
    * similar_match: Quando encontra outra transação com alto grau de semelhança (usa FuzzyWuzzy).
    * ai_match: Atualmente desativado, mas chama API do GPT passando o item e a lista de categorias, com prompt para solicitar melhor classificação.
* [CHAR] tag: Texto para preenchimento manual para permitir outro tipo de agrupamento de transações (ex: FÉRIAS-2024, que pode conter várias transações de diferentes categorias).
* [CHAR] meio: Nome do meio de pagamento utilizado para realizar a transação (ex: CartãO BTG, Conta Itaú, etc.)
* [CHAR] fonte: Nome do arquivo fonte da transação (ex: btg.txt, history.xlsx, etc)
* [CHAR] hash: Hash da transação, chave primária da tabela, calculado com o algoritmo MD5 em cima da concatenação da tupla {data, item, valor, ocorrencia_dia}.
* [INT] timestamp: Timestamp (epoch) de inserção do registro da transação no banco de dados.
* [INT] file_timestamp: Timestamp (epoch) da última modificação do arquivo fonte da transação.

## Load

Lorem Ipsum

## Organização do projeto

Lorem Ipsum