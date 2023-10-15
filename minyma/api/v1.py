import minyma

from flask import Blueprint, request
bp = Blueprint("v1", __name__, url_prefix="/api/v1")

"""
Return OpenAI LLM final response with vector db embedding
context
"""
@bp.route("/query", methods=["POST"])
def get_response():
    data = request.get_json()
    if not data:
        return {"error": "Missing Message"}

    message = str(data.get("message"))
    if message == "":
        return {"error": "Empty Message"}

    oai_response = minyma.oai.query(message)
    return oai_response


"""
Return the raw vector db related response
"""
@bp.route("/related", methods=["POST"])
def get_related():
    data = request.get_json()
    if not data:
        return {"error": "Missing Message"}

    message = str(data.get("message"))
    if message == "":
        return {"error": "Empty Message"}

    related_documents = minyma.cdb.get_related(message)
    return related_documents
