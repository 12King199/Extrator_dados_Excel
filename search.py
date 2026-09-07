from exa_py import Exa
from config import EXA_API_KEY

exa = Exa(EXA_API_KEY)

def search_product(ean, nome, num_results=2):

    query = f"{nome} {ean}" if ean else nome

    try:

        resultado = exa.search_and_contents(
            query,
            num_results=num_results,
            text=True
        )

        paginas = []

        for item in resultado.results:

            paginas.append({
                "title": item.title,
                "url": item.url,
                "text": item.text if item.text else ""
})

        return paginas

    except Exception as e:

        print(f"Erro Exa: {e}")

        return []
