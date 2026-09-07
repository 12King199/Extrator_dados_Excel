import json
import re

from google import genai
from config import GEMINI_API_KEY


# Criar cliente
client = genai.Client(
    api_key=GEMINI_API_KEY
)


def extract_attributes(texto, colunas):

    prompt = f"""
Com base no texto abaixo, extrai APENAS os seguintes atributos:

{colunas}

Regras:

- Devolve apenas JSON válido.
- Se não estiver presente, usa "UNKNOWN".
- Não inventes valores.
- Não expliques nada.

Texto:

{texto}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        resposta = response.text

        resposta = resposta.replace(
            "```json",
            ""
        )

        resposta = resposta.replace(
            "```",
            ""
        )

        return json.loads(
            resposta
        )

    except Exception as e:

        print("\nErro Gemini:")
        print(e)

        texto_erro = str(e)

        match = re.search(
            r"Please retry in ([0-9.]+)s",
            texto_erro
        )

        if match:

            segundos = float(
                match.group(1)
            )

            print(
                f"\nGemini disponível novamente em aproximadamente {segundos:.0f} segundos."
            )

        return None