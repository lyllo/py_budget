from dateutil.relativedelta import relativedelta

# Calcula a data quando será debitada uma parcela
def calcula_data_parcela(data_base, parcela):
    data_incrementada = data_base + relativedelta(months=parcela-1)
    return data_incrementada