import json
import os

CACHE_FILE = "cache/cache.json"
RAW_CACHE_FILE = "cache/cachemelhorar.json"


def load_cache():

    # Se ainda não existir, devolve cache vazia
    if not os.path.exists(CACHE_FILE):

        return {}

    try:

        with open(
            CACHE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def save_cache(cache):

    # Criar pasta cache caso não exista
    os.makedirs(
        "cache",
        exist_ok=True
    )

    with open(
        CACHE_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cache,
            f,
            indent=4,
            ensure_ascii=False
        )


def get_from_cache(ean):

    cache = load_cache()

    return cache.get(ean)


def add_to_cache(ean, dados):

    # Não guardar dicionários vazios
    if not dados:

        return

    # Remover UNKNOWN, strings vazias e None
    dados_limpos = {

        coluna: valor

        for coluna, valor in dados.items()

        if valor not in [

            "UNKNOWN",
            "N/A",
            "",
            None

        ]

    }

    # Se depois da limpeza não sobrou nada, não guarda
    if not dados_limpos:

        return

    cache = load_cache()

    cache_existente = cache.get(ean, {})

    if not isinstance(cache_existente, dict):
        cache_existente = {}

    cache_existente.update(dados_limpos)
    cache[ean] = cache_existente

    save_cache(cache)


def load_raw_cache():

    if not os.path.exists(RAW_CACHE_FILE):
        return {}

    try:
        with open(RAW_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_raw_cache(cache):

    os.makedirs("cache", exist_ok=True)

    with open(RAW_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)


def get_from_raw_cache(ean):

    cache = load_raw_cache()
    return cache.get(ean)


def add_to_raw_cache(ean, dados):

    if not dados:
        return

    cache = load_raw_cache()
    cache_existente = cache.get(ean, {})

    if not isinstance(cache_existente, dict):
        cache_existente = {}

    cache_existente.update(dados)
    cache[ean] = cache_existente

    save_raw_cache(cache)
