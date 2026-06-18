import os
from google import genai
from services.chatbot_context import build_chatbot_context


MODEL_NAME = "gemini-2.5-flash-lite"


def generate_chatbot_response(id_usuario: int, user_message: str, chat_history: list[dict]) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta configurar GEMINI_API_KEY en el archivo .env")

    client = genai.Client(api_key=api_key)

    contexto = build_chatbot_context(id_usuario)

    historial_texto = ""

    for item in chat_history[-6:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        historial_texto += f"{role}: {content}\n"

    prompt = f"""
Sos el asistente financiero de FiCo, una aplicación web de finanzas personales.

Reglas:
- Respondé en español rioplatense claro y directo.
- Usá el contexto financiero real del usuario cuando sea relevante.
- No inventes datos que no estén en el contexto.
- Si faltan datos, aclaralo.
- No des asesoramiento financiero profesional como certeza.
- No prometas ejecutar acciones. Por ahora solo podés analizar, explicar y sugerir.
- Sé breve, útil y concreto.

{contexto}

Historial reciente:
{historial_texto}

Mensaje actual:
{user_message}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text or "No pude generar una respuesta en este momento."