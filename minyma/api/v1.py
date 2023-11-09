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

    resp = minyma.oai.query(message)

    # Return Data
    return resp

"""
TODO - Embeds and loads data into the local ChromaDB.

{
  "input": "string",
  "normalizer": "string",
}
"""
bp.route("/embed", methods=["POST"])
def post_embeddings():
    pass
