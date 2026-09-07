def converter_valor(valor):

    if valor is None:
        return valor

    valor = str(valor).strip()

    mapa = {

        # Cores
        "Blanco": "White",
        "Blanc": "White",
        "Bianco": "White",
        "WeiÃŸ": "White",
        "Wit": "White",
        "Branco": "White",

        "Negro": "Black",
        "Noir": "Black",
        "Nero": "Black",
        "Schwarz": "Black",
        "Preto": "Black",

        "Gris": "Grey",
        "Gray": "Grey",
        "Grau": "Grey",
        "Cinzento": "Grey",

        "Plata": "Silver",
        "Argent": "Silver",
        "Silber": "Silver",
        "Prata": "Silver",

        "Rojo": "Red",
        "Rouge": "Red",
        "Rot": "Red",
        "Vermelho": "Red",

        "Azul": "Blue",
        "Bleu": "Blue",
        "Blau": "Blue",

        "Verde": "Green",
        "Vert": "Green",
        "GrÃ¼n": "Green",

        "Cromo": "Cromado",
        "Cromada": "Cromado",
        "Cromado": "Cromado",

        # Sim / NÃ£o
        "SÃ­": "Yes",
        "Si": "Yes",
        "Oui": "Yes",
        "Ja": "Yes",
        "Sim": "Yes",

        "No": "No",
        "Nein": "No",
        "Non": "No",
        "NÃ£o": "No",

        # Vidro Temperado
        "Tempered Glass": "Yes",
        "Vidrio templado": "Yes",
        "Verre trempÃ©": "Yes",
        "Hartglas": "Yes",

        "Sin vidrio templado": "No",
        "Sans verre trempÃ©": "No",

        # Valores desconhecidos
        "N/A": "N/A",
        "NA": "UNKNOWN",
        "None": "UNKNOWN",
        "null": "UNKNOWN",
        "": "UNKNOWN"

    }

    return mapa.get(valor, valor)
