# py_budget

Esta aplicação python é uma solução de gestão financeira pessoal composta por basicamente 3 módulos: Extract, Transform, Load (ETL).

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

## Transform

Lorem Ipsum

## Load

Lorem Ipsum

## Organização do projeto

Lorem Ipsum