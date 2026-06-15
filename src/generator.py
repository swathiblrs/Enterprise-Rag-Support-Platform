from typing import List, Dict

from src.retriever import retrieve_relevant_chunks
from src.ticket_classifier import classify_ticket


def generate_answer(question: str, retrieved_chunks: List[Dict]) -> Dict:
    if not retrieved_chunks:
        return {
            "answer": "I could not find enough information in the knowledge base to answer this.",
            "sources": [],
            "fallback_triggered": True,
        }

    sources = []
    context_parts = []

    for chunk in retrieved_chunks:
        source = chunk["source"]

        if source not in sources:
            sources.append(source)

        context_parts.append(chunk["text"])

    combined_context = "\n\n".join(context_parts)

    answer = build_simple_answer(question, combined_context, sources)

    return {
        "answer": answer,
        "sources": sources,
        "fallback_triggered": False,
    }


def build_simple_answer(question: str, context: str, sources: List[str]) -> str:
    question_lower = question.lower()

    if "vpn" in question_lower:
        answer = (
            "Based on the knowledge base, first confirm that you can log in to the "
            "Single Sign-On portal. Then restart the VPN client, verify Duo MFA approval, "
            "clear saved VPN credentials, confirm you are using the latest VPN client version, "
            "and reconnect using the new password if it was recently changed."
        )

    elif "password" in question_lower or "account" in question_lower or "locked" in question_lower:
        answer = (
            "Based on the knowledge base, visit the Single Sign-On password reset portal, "
            "verify your identity using the approved recovery method, reset the password, "
            "wait 5 to 10 minutes for synchronization, sign out of active sessions, and log in again."
        )

    elif "duo" in question_lower or "mfa" in question_lower:
        answer = (
            "Based on the knowledge base, verify network connectivity on the mobile device, "
            "open the Duo Mobile app manually, check push notification settings, and re-register "
            "the device if the phone was changed."
        )

    else:
        answer = (
            "I found related knowledge-base information, but I could not generate a specific "
            "answer for this issue yet."
        )

    answer += "\n\nSources:\n"
    for source in sources:
        answer += f"- {source}\n"

    return answer


def answer_question(question: str) -> Dict:
    retrieved_chunks = retrieve_relevant_chunks(question)
    rag_response = generate_answer(question, retrieved_chunks)
    ticket = classify_ticket(question)

    return {
        "question": question,
        "answer": rag_response["answer"],
        "sources": rag_response["sources"],
        "ticket": ticket,
        "fallback_triggered": rag_response["fallback_triggered"],
    }


if __name__ == "__main__":
    question = "My VPN is not working after I reset my password"

    response = answer_question(question)

    print("\nQuestion:")
    print(response["question"])

    print("\nAnswer:")
    print(response["answer"])

    print("\nTicket Recommendation:")
    print(response["ticket"])