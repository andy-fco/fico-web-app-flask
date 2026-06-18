from flask import request, jsonify, session
from controllers import login_required
from services.chatbot_service import generate_chatbot_response


def register_routes(app):

    @app.route("/api/chatbot", methods=["POST"])
    @login_required
    def chatbot_api():
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()

        if not message:
            return jsonify({"error": "El mensaje no puede estar vacío."}), 400

        id_usuario = session.get("id_usuario")

        if not id_usuario:
            return jsonify({"error": "Sesión no válida."}), 401

        chat_history = session.get("chat_history", [])

        try:
            response_text = generate_chatbot_response(
                id_usuario=id_usuario,
                user_message=message,
                chat_history=chat_history,
            )
        except RuntimeError as error:
            return jsonify({"error": str(error)}), 500
        except Exception as error:
            print(f"Error en chatbot: {error}")
            return jsonify({
                "error": "No se pudo generar una respuesta del asistente."
            }), 500

        chat_history.append({
            "role": "user",
            "content": message
        })

        chat_history.append({
            "role": "assistant",
            "content": response_text
        })

        session["chat_history"] = chat_history[-10:]
        session.modified = True

        return jsonify({
            "response": response_text
        })

    @app.route("/api/chatbot/history", methods=["GET"])
    @login_required
    def chatbot_history():
        return jsonify({
            "history": session.get("chat_history", [])
        })

    @app.route("/api/chatbot/clear", methods=["POST"])
    @login_required
    def chatbot_clear():
        session.pop("chat_history", None)
        session.modified = True

        return jsonify({
            "success": True
        })