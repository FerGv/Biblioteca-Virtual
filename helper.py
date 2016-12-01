def date_format(fecha):
    meses = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    mes = meses[fecha.month - 1]

    return "{} de {} del {}".format(fecha.day, mes, fecha.year)
