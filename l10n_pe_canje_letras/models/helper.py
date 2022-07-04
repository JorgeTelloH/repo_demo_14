# -*- coding: utf-8 -*-


# Numeros expresado en letras
def number_to_letter(number, mi_moneda=None):
    UNIDADES = (
        '',
        'UN ',
        'DOS ',
        'TRES ',
        'CUATRO ',
        'CINCO ',
        'SEIS ',
        'SIETE ',
        'OCHO ',
        'NUEVE ',
        'DIEZ ',
        'ONCE ',
        'DOCE ',
        'TRECE ',
        'CATORCE ',
        'QUINCE ',
        'DIECISEIS ',
        'DIECISIETE ',
        'DIECIOCHO ',
        'DIECINUEVE ',
        'VEINTE '
    )

    DECENAS = (
        'VENTI',
        'TREINTA ',
        'CUARENTA ',
        'CINCUENTA ',
        'SESENTA ',
        'SETENTA ',
        'OCHENTA ',
        'NOVENTA ',
        'CIEN '
    )

    CENTENAS = (
        'CIENTO ',
        'DOSCIENTOS ',
        'TRESCIENTOS ',
        'CUATROCIENTOS ',
        'QUINIENTOS ',
        'SEISCIENTOS ',
        'SETECIENTOS ',
        'OCHOCIENTOS ',
        'NOVECIENTOS '
    )

    MONEDAS = (
        {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO',
         'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
        {'country': u'Estados Unidos', 'currency': 'USD COMPRA', 'singular': u'DÓLAR',
         'plural': u'DÓLARES', 'symbol': u'US$'},
        {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR',
         'plural': u'DÓLARES', 'symbol': u'US$'},
        {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO',
         'plural': u'EUROS', 'symbol': u'€'},
        {'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO',
         'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
        {'country': u'Perú', 'currency': 'PEN', 'singular': u'SOL',
         'plural': u'SOLES', 'symbol': u'S/.'},
        {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA',
         'plural': u'LIBRAS', 'symbol': u'£'})

    def __convert_group(n):
        """Turn each group of numbers into letters"""
        output = ''

        if n == '100':
            output = "CIEN"
        elif n[0] != '0':
            output = CENTENAS[int(n[0]) - 1]

        k = int(n[1:])
        if k <= 20:
            output += UNIDADES[k]
        else:
            if (k > 30) & (n[2] != '0'):
                output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
            else:
                output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
        return output

    def __convert_decimals(n):
        '''##ALEX##'''
        # if 1 <= n < 21:
        #     return ' CON ' +UNIDADES[int(n)] + ' 00/100 NUEVOS SOLES'
        # elif 21 <= n <= 99:
        #     dizaine, unite =  divmod(n,10)
        #     return ' CON ' +DECENAS[int(dizaine-2)]+'Y ' +UNIDADES[int(unite)] + ' 00/100 NUEVOS SOLES'
        # else:
        #     return ' Y 00/100 NUEVOS SOLES'
        '''##ALEX##'''
        if 1 <= n < 9999999999:
            return 'CON ' + str(n) + '/100 NUEVOS SOLES'
        else:
            return 'CON 00/100 NUEVOS SOLES'

    separate = number.split(".")
    number = int(separate[0])
    if mi_moneda is not None:
        try:
            moneda = list(filter(lambda x: x['currency'] == mi_moneda, MONEDAS))
            if number < 2:
                moneda = moneda[0]['singular']
            else:
                moneda = moneda[0]['plural']
        except:
            return "Tipo de moneda inválida"
    else:
        moneda = ""

    if int(separate[1]) >= 0:
        moneda = __convert_decimals(int(separate[1]))

    """Converts a number into string representation"""
    converted = ''

    if not (0 < number < 999999999):
        return 'CERO CON 00/100 NUEVOS SOLES'

    number_str = str(number).zfill(9)
    millones = number_str[:3]
    miles = number_str[3:6]
    cientos = number_str[6:]

    if millones:
        if millones == '001':
            converted += 'UN MILLON '
        elif int(millones) > 0:
            converted += '%sMILLONES ' % __convert_group(millones)

    if miles:
        if miles == '001':
            converted += 'MIL '
        elif int(miles) > 0:
            converted += '%sMIL ' % __convert_group(miles)

    if cientos:
        if cientos == '001':
            converted += 'UN '
        elif int(cientos) > 0:
            converted += '%s ' % __convert_group(cientos)
    converted += str(moneda)

    return converted.upper()
