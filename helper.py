import re
import unicodedata


def normalizar_texto(texto):

    texto = str(texto)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    return texto.lower()


def converter_para_cm(valor, unidade):

    try:
        numero = float(str(valor).replace(",", "."))
    except ValueError:
        return ""

    if unidade == "mm":
        numero /= 10

    if numero.is_integer():
        numero = int(numero)

    return f"{numero} cm"


def eh_exaustor_ou_chamine(texto, nome=""):

    contexto = normalizar_texto(texto) + " " + normalizar_texto(nome)

    termos = [
        "exaust",
        "chamin",
        "coifa",
        "campana",
        "hood",
        "extractor",
        "hotte"
    ]

    return any(termo in contexto for termo in termos)


def limpar_classe_energetica(valor):

    if valor is None:
        return ""

    texto = normalizar_texto(valor).strip()
    texto = re.sub(r"^[\s\|\-:;,\.]+|[\s\|\-:;,\.]+$", "", texto)
    texto = texto.replace("a2plus", "a+")
    texto = texto.replace("a2 plus", "a+")
    texto = texto.replace("a plus", "a+")
    texto = texto.replace("a+++", "a+++")

    match_inicio = re.match(r"^(a\+{0,3}|b|c|d|e|f|g)\b", texto, re.IGNORECASE)

    if match_inicio:
        classe_inicio = match_inicio.group(1).upper().replace(" ", "")
        if classe_inicio in ["A", "A+", "A++", "A+++", "B", "C", "D", "E", "F", "G"]:
            return classe_inicio

    match_exato = re.fullmatch(r"(?:classe(?:\s+energetica)?\s*[:=\-]?\s*)?(a\+{0,3}|b|c|d|e|f|g)", texto, re.IGNORECASE)

    if match_exato:
        classe_exata = match_exato.group(1).upper().replace(" ", "")
        if classe_exata in ["A", "A+", "A++", "A+++", "B", "C", "D", "E", "F", "G"]:
            return classe_exata

    classe_exata = texto.upper().replace(" ", "")

    if classe_exata in ["A", "A+", "A++", "A+++", "B", "C", "D", "E", "F", "G"]:
        return classe_exata

    padroes = [
        r"\bclasse\s*(?:de\s*eficiencia\s*)?energetica\b[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b",
        r"\benergy\s*class\b[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b",
        r"\bclassificacao\s*energetica\b[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b"
    ]

    for padrao in padroes:

        resultado = re.search(padrao, texto, re.IGNORECASE)

        if resultado:

            classe = resultado.group(1).upper().replace(" ", "")
            if classe in ["A", "A+", "A++", "A+++", "B", "C", "D", "E", "F", "G"]:
                return classe

    return ""


def extrair_classe_energetica(texto):

    texto = normalizar_texto(texto)

    padroes = [
        r"\bclasse de eficiencia energetica\b(?:\s*\([^)]+\))?[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b",
        r"\bclasse energetica\b(?:\s*\([^)]+\))?[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b",
        r"\bclassificacao energetica\b(?:\s*\([^)]+\))?[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b",
        r"\benergy class\b(?:\s*\([^)]+\))?[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b",
        r"\benergy efficiency class\b(?:\s*\([^)]+\))?[^a-z0-9]{0,20}(a\+{0,3}|b|c|d|e|f|g)\b"
    ]

    for padrao in padroes:

        resultado = re.search(padrao, texto, re.IGNORECASE)

        if resultado:

            valor = limpar_classe_energetica(resultado.group(1))

            if valor:
                return valor

    return ""


def extrair_dimensao(texto, coluna):

    texto = normalizar_texto(texto)
    coluna = normalizar_texto(coluna)

    rotulos = {
        "profundidade": ["profundidade", "fundo"],
        "altura": ["altura", "alto"],
        "largura": ["largura", "largo"]
    }

    def encontrar_valor(label_patterns):

        for padrao in label_patterns:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if resultado:

                valor = resultado.group(1)
                unidade = resultado.group(2).lower() if resultado.lastindex and resultado.lastindex >= 2 and resultado.group(2) else ""
                return converter_para_cm(valor, unidade)

        return ""

    if coluna == "altura":

        padroes_altura_intervalo = [
            r"\baltura\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\s*(?:/|a|e|entre)\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\b",
            r"\baltura\b(?:\s*\([^)]+\))?.*?\bentre\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\s*(?:e|a|-)\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\b",
        ]

        for padrao in padroes_altura_intervalo:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if resultado:

                valor1 = resultado.group(1)
                unidade1 = resultado.group(2).lower() if resultado.group(2) else ""
                valor2 = resultado.group(3)
                unidade2 = resultado.group(4).lower() if resultado.lastindex and resultado.lastindex >= 4 and resultado.group(4) else unidade1

                valor1_cm = converter_para_cm(valor1, unidade1)
                valor2_cm = converter_para_cm(valor2, unidade2)

                if valor1_cm and valor2_cm:
                    return f"{valor1_cm.replace(' cm', '')}-{valor2_cm}"

        return encontrar_valor([
            r"\baltura\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\b",
            r"\b(\d+(?:[.,]\d+)?)\s*(mm|cm)\b\s*(?:de\s*)?\baltura\b",
            r"\baltura\b(?:\s*\([^)]+\))?.*?\b(\d+(?:[.,]\d+)?)\s*(mm|cm)\b"
        ])

    if coluna in ["profundidade", "largura"]:

        labels = rotulos.get(coluna, [coluna])

        padroes = []

        for rotulo in labels:

            padroes.extend([
                rf"\b{rotulo}\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\b",
                rf"\b(\d+(?:[.,]\d+)?)\s*(mm|cm)\b\s*(?:de\s*)?\b{rotulo}\b",
                rf"\b{rotulo}\b(?:\s*\([^)]+\))?.*?\b(\d+(?:[.,]\d+)?)\s*(mm|cm)\b"
            ])

        return encontrar_valor(padroes)

    return ""


def procurar_valor(texto, coluna, nome=""):

    texto_original = str(texto)
    texto = normalizar_texto(texto_original)
    nome = normalizar_texto(nome)
    coluna = normalizar_texto(coluna)

    if coluna == "temperatura maxima":

        padroes_temperatura = [
            r"\btemperatura maxima\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(?:°\s*c|º\s*c|c)?\b",
            r"\btemp\.?\s*m[ae]x\.?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(?:°\s*c|º\s*c|c)?\b",
            r"\btemp(?:eratura)?\s*max(?:ima)?\.?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(?:°\s*c|º\s*c|c)?\b",
            r"\bmax\.?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(?:°\s*c|º\s*c|c)?\b",
            r"\b(\d+(?:[.,]\d+)?)\s*(?:°\s*c|º\s*c|c)\b"
        ]

        for padrao in padroes_temperatura:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if resultado:

                return f"{resultado.group(1)} °C"

    if coluna == "diametro":

        padroes_diametro = [
            r"\bdiametro\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\b",
            r"\bdiam\.?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\b",
            r"\bdiam(?:etro)?\s*de\s*(?:placa\s*)?[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)\b",
            r"\bø\s*(\d+(?:[.,]\d+)?)\s*(?:mm|cm)?\b",
            r"\b(\d+(?:[.,]\d+)?)\s*mm\b",
            r"\b(\d+(?:[.,]\d+)?)\s*cm\b"
        ]

        for padrao in padroes_diametro:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if resultado:

                valor = resultado.group(1)
                if "cm" in resultado.group(0):
                    try:
                        valor_mm = float(valor.replace(",", ".")) * 10
                        if valor_mm.is_integer():
                            valor_mm = int(valor_mm)
                        return f"{valor_mm} mm"
                    except ValueError:
                        return ""

                return f"{valor} mm"

    if coluna in ["profundidade", "altura", "largura"]:
        return extrair_dimensao(texto, coluna)

    if coluna == "potencia":
        if eh_exaustor_ou_chamine(texto, nome):
            padroes_extracao = [
                r"\bcap\.\s*extra[cç][aã]o.*?(?:intensiv[ao]|m[3³]/h)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b",
                r"\bpot[eê]ncia\s*intensiv[ao].*?\b(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b",
                r"\bextra[cç][aã]o\s*m[aá]x(?:ima)?(?:/min)?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b",
                r"\b(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b"
            ]

            for padrao in padroes_extracao:

                resultado = re.search(padrao, texto, re.IGNORECASE)

                if resultado:

                    valor = resultado.group(1).replace(",", ".")
                    unidade = resultado.group(2)

                    if valor:
                        if float(valor).is_integer():
                            valor = str(int(float(valor)))
                        return f"{valor} {unidade}"

        return ""

        padroes_potencia = [
            r"\bpotencia\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"\bpot(?:encia)?\.?\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"\bpower\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"\bmotor\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"\bconsumo\b(?:\s*\([^)]+\))?\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"\b(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b"
        ]

        for padrao in padroes_potencia:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if not resultado:
                continue

            valor = resultado.group(1).replace(",", ".")
            unidade = resultado.group(2).lower() if resultado.lastindex and resultado.lastindex >= 2 and resultado.group(2) else ""

            try:
                valor_numero = float(valor)
            except ValueError:
                continue

            if unidade == "kw":
                valor_numero *= 1000
            elif unidade in ["w", "watt", "watts"] and not valor_numero.is_integer():
                continue

            if valor_numero < 100 and unidade in ["w", "watt", "watts"] and "potencia" not in texto and "power" not in texto and "motor" not in texto and "consumo" not in texto:
                continue

            if valor_numero.is_integer():
                valor_numero = int(valor_numero)

            return f"{valor_numero} W"

    if coluna == "cor":

        cores = [

            "preto",
            "black",
            "branco",
            "white",
            "inox",
            "cromado",
            "cromada",
            "cromo",
            "grafite",
            "antracite",
            "cinza",
            "titanium",
            "bege"
        ]

        acabamentos = [
            "mate",
            "matte",
            "fosco"
        ]

        cortes = [
            "caracteristicas",
            "informacoes",
            "numero de",
            "pesos e dimensoes",
            "dimensoes",
            "tamanho",
            "tamanhos",
            "medidas",
            "medida",
            "capacidade",
            "capacidades",
            "garantia"
        ]

        for cor in cores:

            padroes_cor = [
                rf"\bcor\s*:\s*{cor}\b",
                rf"\bcor\s*-\s*{cor}\b",
                rf"\bcor\s*=\s*{cor}\b"
            ]

            for padrao in padroes_cor:

                if re.search(padrao, texto, re.IGNORECASE):

                    return cor.capitalize()

        for cor in cores:

            if cor in texto:

                trecho = texto.split(cor, 1)[1]

                for corte in cortes:

                    trecho = trecho.split(corte, 1)[0]

                for acabamento in acabamentos:

                    trecho = trecho.split(acabamento, 1)[0]

                if cor in ["cromado", "cromada", "cromo"]:
                    return "Cromado"

                if cor in ["preto", "black"]:
                    return "Black"

                if cor in ["branco", "white"]:
                    return "White"

                if cor in ["cinza", "grey", "gray"]:
                    return "Grey"

                if cor == "titanium":
                    return "Titanium"

                if cor == "bege":
                    return "Bege"

                return cor.capitalize()

    padroes = [

        rf"{coluna}\s*:\s*(.+)",
        rf"{coluna}\s*-\s*(.+)",
        rf"{coluna}\s*=\s*(.+)"

    ]

    for padrao in padroes:

        resultado = re.search(
            padrao,
            texto,
            re.IGNORECASE
        )

        if resultado:

            valor = resultado.group(1)
            valor = valor.split("\n")[0]
            valor = valor.split(",")[0]
            valor = valor.split(";")[0]
            valor = valor.split("caracteristicas")[0]
            valor = valor.split("informacoes")[0]
            valor = valor.split("numero de")[0]
            valor = valor.split("pesos e dimensoes")[0]
            valor = valor.split("dimensoes")[0]
            valor = valor.split("garantia")[0]

            valor = valor.strip()

            if valor:

                return valor

    return ""


def extrair_do_nome(nome, coluna):

    if not nome or not coluna:
        return ""

    texto = normalizar_texto(nome)
    coluna = normalizar_texto(coluna)

    if coluna == "cor":

        cores = [

            "preto",
            "black",
            "branco",
            "white",
            "inox",
            "cromado",
            "cromada",
            "cromo",
            "grafite",
            "antracite",
            "cinza",
            "titanium",
            "bege"
        ]

        for cor in cores:

            if cor in texto:

                if cor in ["cromado", "cromada", "cromo"]:
                    return "Cromado"

                if cor in ["preto", "black"]:
                    return "Black"

                if cor in ["branco", "white"]:
                    return "White"

                if cor in ["cinza", "grey", "gray"]:
                    return "Grey"

                if cor == "titanium":
                    return "Titanium"

                if cor == "bege":
                    return "Bege"

                return cor.capitalize()

        return ""

    if coluna == "temperatura maxima":

        padroes_temperatura = [
            r"(\d+(?:[.,]\d+)?)\s*(?:°\s*c|º\s*c|c)",
            r"temp\.?\s*m[ae]x\.?\s*(\d+(?:[.,]\d+)?)",
            r"temperatura\s*m[ae]x\.?\s*(\d+(?:[.,]\d+)?)"
        ]

        for padrao in padroes_temperatura:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if resultado:

                return f"{resultado.group(1)} °C"

        return ""

    if coluna == "classe energetica":

        texto_limpo = normalizar_texto(nome)

        padroes_classe = [
            r"\b(a\+{0,3}|b|c|d|e|f|g)\b",
            r"\b(a\s*plus)\b",
            r"\b(a2\s*plus)\b",
            r"\b(a2plus)\b"
        ]

        for padrao in padroes_classe:

            resultado = re.search(padrao, texto_limpo, re.IGNORECASE)

            if resultado:

                valor = resultado.group(1).upper().replace(" ", "")
                valor = valor.replace("A2PLUS", "A+")
                valor = valor.replace("APLUS", "A+")
                valor = valor.replace("A2", "A+")
                return limpar_classe_energetica(valor)

        return ""

    if coluna in ["profundidade", "altura", "largura"]:
        return extrair_dimensao(texto, coluna)

    if coluna == "potencia":
        if eh_exaustor_ou_chamine(texto, nome):
            padroes_potencia = [
                r"potencia\s*(?:intensiva\s*)?(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b",
                r"pot\.?\s*(?:intensiva\s*)?(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b",
                r"cap\.\s*extracao\s*(?:intensiva\s*)?(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b",
                r"extracao\s*m[aá]x(?:ima)?(?:/min)?\s*(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b",
                r"(\d+(?:[.,]\d+)?)\s*(m3/h|m³/h)\b"
            ]

            for padrao in padroes_potencia:

                resultado = re.search(padrao, texto, re.IGNORECASE)

                if resultado:

                    valor = resultado.group(1).replace(",", ".")
                    unidade = resultado.group(2)

                    if float(valor).is_integer():
                        valor = str(int(float(valor)))

                    return f"{valor} {unidade}"

            return ""

        padroes_potencia = [
            r"potencia\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"pot\.?\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"power\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"motor\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"consumo\s*(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b",
            r"(\d+(?:[.,]\d+)?)\s*(kw|w|watt|watts)\b"
        ]

        for padrao in padroes_potencia:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if resultado:

                valor = resultado.group(1).replace(",", ".")
                unidade = resultado.group(2).lower() if resultado.lastindex and resultado.lastindex >= 2 and resultado.group(2) else ""

                try:
                    valor_numero = float(valor)
                except ValueError:
                    continue

                if unidade == "kw":
                    valor_numero *= 1000
                elif unidade in ["w", "watt", "watts"] and not valor_numero.is_integer():
                    continue
                elif unidade == "" and ("." in valor or "," in valor) and valor_numero < 20:
                    valor_numero *= 1000

                if any(medida in texto for medida in ["m3/h", "m³/h", "m3h", "m³h"]):
                    if not any(contexto in texto for contexto in ["potencia", "power", "motor", "consumo"]):
                        continue

                if unidade in ["w", "watt", "watts"] and valor_numero < 100:
                    continue

                if valor_numero.is_integer():
                    valor_numero = int(valor_numero)

                return f"{valor_numero} W"

        return ""

    if coluna == "classe energetica":
        valor = extrair_classe_energetica(texto)

        if valor:
            return valor

        resultado = re.search(r"\b(a\+{0,3}|b|c|d|e|f|g)\b", texto, re.IGNORECASE)

        if resultado:
            return resultado.group(1).upper().replace(" ", "")

        return ""

    if coluna == "diametro":

        padroes_diametro = [
            r"ø\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)?",
            r"diam\.?\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)?",
            r"diametro\s*(\d+(?:[.,]\d+)?)\s*(mm|cm)?",
            r"(\d+(?:[.,]\d+)?)\s*mm",
            r"(\d+(?:[.,]\d+)?)\s*cm"
        ]

        for padrao in padroes_diametro:

            resultado = re.search(padrao, texto, re.IGNORECASE)

            if resultado:

                valor = resultado.group(1)
                unidade = resultado.group(2) if len(resultado.groups()) > 1 else ""

                if unidade == "cm":
                    try:
                        valor_mm = float(valor.replace(",", ".")) * 10
                        if valor_mm.is_integer():
                            valor_mm = int(valor_mm)
                        return f"{valor_mm} mm"
                    except ValueError:
                        return ""

                if unidade == "mm" or "mm" in resultado.group(0):
                    return f"{valor} mm"

                return ""

    return ""


def extrair_campos(texto, colunas, nome=""):

    dados = {}

    for coluna in colunas:

        valor = procurar_valor(
            texto,
            coluna,
            nome
        )

        if valor == "":

            valor = extrair_do_nome(
                nome,
                coluna
            )

        if coluna == "classe energetica":
            valor = limpar_classe_energetica(valor)

        dados[coluna] = valor

    return dados
