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

    # Derive LLM Data
    # llm_resp = resp.get("llm", {})
    # llm_choices = llm_resp.get("choices", [])

    # Derive VDB Data
    # vdb_resp = resp.get("vdb", {})
    # combined_context  = [{
    #         "id": vdb_resp.get("ids")[i],
    #         "distance": vdb_resp.get("distances")[i],
    #         "doc": vdb_resp.get("docs")[i],
    #         "metadata": vdb_resp.get("metadatas")[i],
    # } for i, _ in enumerate(vdb_resp.get("docs", []))]

    # Return Data
    return resp



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

    related_documents = minyma.vdb.get_related(message)
    return related_documents
