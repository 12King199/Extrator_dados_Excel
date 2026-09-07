from excel_reader import load_excel
from excel_reader import get_missing_columns

from search import search_product
from ai_extractor import extract_attributes

from cache_manager import get_from_cache
from cache_manager import add_to_cache
from cache_manager import get_from_raw_cache
from cache_manager import add_to_raw_cache

from converter import converter_valor
from helper import extrair_campos
from helper import limpar_classe_energetica

import time
import os
import glob
import tempfile


def guardar_excel_com_segurança(dataframe, caminho_final, tentativas=5, espera=2):

    os.makedirs("output", exist_ok=True)

    fd, caminho_temp = tempfile.mkstemp(suffix=".xlsx", dir="output")
    os.close(fd)

    try:
        dataframe.to_excel(caminho_temp, index=False)

        for tentativa in range(1, tentativas + 1):

            try:
                os.replace(caminho_temp, caminho_final)
                return
            except PermissionError:
                if tentativa == tentativas:
                    raise

                print(
                    f"Excel bloqueado. Nova tentativa em {espera} segundos "
                    f"({tentativa}/{tentativas})..."
                )
                time.sleep(espera)
    finally:
        if os.path.exists(caminho_temp):
            try:
                os.remove(caminho_temp)
            except OSError:
                pass


ficheiros = glob.glob("input/*.xlsx")

if not ficheiros:
    print("Nenhum ficheiro Excel encontrado.")
    exit()

INPUT_FILE = ficheiros[0]
nome_ficheiro = os.path.splitext(os.path.basename(INPUT_FILE))[0]
OUTPUT_FILE = f"output/{nome_ficheiro}_preenchido.xlsx"

if os.path.exists(OUTPUT_FILE):
    print("A continuar do Excel já preenchido...")
    df = load_excel(OUTPUT_FILE)
else:
    print("A carregar Excel original...")
    df = load_excel(INPUT_FILE)

df = df.astype(object)

pedidos_gemini = 0
gemini_disponivel = True
usar_api = True

# Modo de teste opcional:
# TEST_START_ROW = 1
# TEST_ROW_COUNT = 5
TEST_START_ROW = 1
TEST_ROW_COUNT = None

total_rows = len(df)
block_ranges = []

if TEST_ROW_COUNT is None or TEST_ROW_COUNT <= 0:
    block_ranges.append((TEST_START_ROW, total_rows))
else:
    current_start = TEST_START_ROW

    while current_start <= total_rows:
        current_end = min(current_start + TEST_ROW_COUNT - 1, total_rows)
        block_ranges.append((current_start, current_end))
        current_start = current_end + 1

try:
    for block_start, block_end in block_ranges:
        print(f"\n=== A iniciar bloco {block_start}-{block_end} ===")

        for row_number in range(block_start, block_end + 1):
            index = row_number - 1
            row = df.iloc[index]

            ean = str(row["EAN"]).strip()
            nome = str(row["Nome"]).strip()

            print("\n--------------------------------")
            print(f"Linha {row_number}")
            print(f"EAN: {ean}")
            print(f"Nome: {nome}")

            missing = get_missing_columns(row)

            if "EAN" in missing:
                missing.remove("EAN")

            if "Nome" in missing:
                missing.remove("Nome")

            missing = [
                campo
                for campo in missing
                if str(row[campo]).strip().upper() in ["", "NAN", "NONE", "N/A", "NA"]
            ]

            if len(missing) == 0:
                print("Linha já preenchida.")
                continue

            print("Campos em falta:")
            print(missing)

            dados = {}
            missing_ia = []

            dados_cache = get_from_cache(ean)
            if dados_cache:
                print("Produto encontrado na cache.")
                dados.update(dados_cache)

                missing = [
                    coluna
                    for coluna in missing
                    if str(dados.get(coluna, "")).strip().upper() in ["", "N/A", "NA", "NONE", "NAN"]
                ]

            raw_cache = get_from_raw_cache(ean)
            if len(missing) > 0 and raw_cache:
                texto_guardado = str(raw_cache.get("texto_total", "")).strip()

                if texto_guardado:
                    dados_reanalise = extrair_campos(texto_guardado, missing, nome)

                    for coluna, valor in dados_reanalise.items():
                        if dados.get(coluna, "") == "" and str(valor).strip().upper() not in ["", "NAN", "NONE", "N/A", "NA"]:
                            dados[coluna] = valor

                    missing = [
                        coluna
                        for coluna in missing
                        if str(dados.get(coluna, "")).strip().upper() in ["", "NAN", "NONE", "N/A", "NA"]
                    ]

                    if len(dados_reanalise) > 0:
                        print("Reanalisado com a cache melhorada.")

            if len(missing) > 0 and usar_api:
                num_resultados = 5 if "Classe Energetica" in missing else 2
                resultados = search_product(ean, nome, num_results=num_resultados)

                texto_total = ""
                dados_search = {coluna: "" for coluna in missing}

                for resultado in resultados:
                    texto = resultado["text"]
                    texto_total += texto + "\n"

                    dados_resultado = extrair_campos(texto, missing, nome)

                    for coluna, valor in dados_resultado.items():
                        if dados_search.get(coluna, "") == "" and valor != "":
                            dados_search[coluna] = valor

                missing_ia = [
                    coluna
                    for coluna, valor in dados_search.items()
                    if str(valor).strip().upper() in ["", "N/A", "NA", "NONE", "NAN"]
                ]

                dados_ia = {}

                if len(missing_ia) > 0 and gemini_disponivel:
                    pedidos_gemini += 1
                    dados_ia = extract_attributes(texto_total, missing_ia)

                if dados_ia is None:
                    print("\nGemini indisponível.")
                    print("Continuando apenas com o helper...")
                    gemini_disponivel = False
                    dados_ia = {}

                dados_search.update(dados_ia)
                dados.update(dados_search)
                add_to_raw_cache(
                    ean,
                    {
                        "texto_total": texto_total,
                        "nome": nome
                    }
                )
            elif len(missing) > 0 and not usar_api:
                dados_search = {coluna: "" for coluna in missing}
                dados.update(dados_search)

            if "Classe Energetica" in dados:
                classe_original = dados.get("Classe Energetica", "")
                classe_limpa = limpar_classe_energetica(classe_original)
                if classe_limpa:
                    dados["Classe Energetica"] = classe_limpa
                elif str(classe_original).strip() != "":
                    dados["Classe Energetica"] = "N/A"

            if len(missing) > 0 and not usar_api:
                print("API desativada. Continuando apenas com o helper e as caches...")

            if len(missing_ia) == 0:
                print("Tudo encontrado sem IA.")

            if not usar_api:
                pass
            elif gemini_disponivel:
                for coluna in missing:
                    if coluna == "Classe Energetica":
                        continue
                    if str(dados.get(coluna, "")).strip().upper() in ["", "NAN", "NONE", "N/A", "NA"]:
                        dados[coluna] = "N/A"
            else:
                for coluna in missing:
                    if coluna == "Classe Energetica":
                        continue
                    if str(dados.get(coluna, "")).strip().upper() in ["", "NAN", "NONE", "N/A", "NA"]:
                        dados[coluna] = "N/A"

            if dados and any(valor not in ["", "UNKNOWN", None] for valor in dados.values()):
                add_to_cache(ean, dados)

            print("Resposta final:")
            print(dados)

            for coluna, valor in dados.items():
                valor = converter_valor(valor)
                if valor not in ["", "UNKNOWN", None]:
                    df.at[index, coluna] = valor

            guardar_excel_com_segurança(df, OUTPUT_FILE)
            print("Progresso guardado.")

            if len(missing_ia) > 0 and gemini_disponivel:
                time.sleep(30)

        print(f"\n=== Bloco {block_start}-{block_end} concluído ===")

        if TEST_ROW_COUNT is not None and TEST_ROW_COUNT > 0:
            continuar = input("Queres continuar para o próximo teste? (sim/não): ").strip().lower()
            if continuar not in ["sim", "s", "yes", "y"]:
                break

    df["EAN"] = df["EAN"].astype(str)
    guardar_excel_com_segurança(df, OUTPUT_FILE)
    print("\nExcel preenchido com sucesso.")

except KeyboardInterrupt:
    print("\nInterrompido pelo utilizador. A guardar progresso com segurança...")
    df["EAN"] = df["EAN"].astype(str)
    guardar_excel_com_segurança(df, OUTPUT_FILE)
    print("Progresso guardado com segurança.")
