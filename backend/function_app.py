# function_app.py
import json
import logging

import azure.functions as func

from app.agent_client import chat_with_agent


# Nivel de auth: FUNCTION (podemos cambiarlo a ANONYMOUS si querés)
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# ===============================
#  HTTP → CHAT CON AGENTE
# ===============================
@app.route(route="http_chat", methods=["POST"])
def http_chat(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("📨 /http_chat invocado")

    # Intentamos leer JSON
    try:
        body = req.get_json()
    except:
        return func.HttpResponse(
            json.dumps({"error": "Body debe ser JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    # Obtenemos campos
    message = body.get("message")
    thread_id = body.get("threadId")
    comuna_id = body.get("comunaId")
    canal = body.get("channel")
    idioma = body.get("language")

    if not message:
        return func.HttpResponse(
            json.dumps({"error": "Campo 'message' es requerido"}),
            status_code=400,
            mimetype="application/json",
        )

    # Construimos contexto opcional
    extra_context = {
        "comunaId": comuna_id,
        "channel": canal,
        "language": idioma,
    }
    extra_context = {k: v for k, v in extra_context.items() if v is not None}

    # Llamamos al agente (Escenario 2)
    try:
        result = chat_with_agent(
            user_message=message,
            thread_id=thread_id,
            extra_context=extra_context if extra_context else None,
        )

        return func.HttpResponse(
            json.dumps(result, ensure_ascii=False),
            mimetype="application/json",
            status_code=200,
        )

    except Exception as e:
        logging.exception("❌ Error en http_chat")
        return func.HttpResponse(
            json.dumps(
                {"error": "Error interno llamando al agente", "detail": str(e)},
                ensure_ascii=False,
            ),
            status_code=500,
            mimetype="application/json",
        )
