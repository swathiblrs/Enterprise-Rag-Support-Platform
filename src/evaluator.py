import json
from pathlib import Path
from time import time

from src.generator import answer_question


EVAL_FILE = Path("tests/eval_questions.json")


def load_eval_questions():
    with EVAL_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def contains_expected_source(actual_sources, expected_sources):
    return any(source in actual_sources for source in expected_sources)


def run_evaluation():
    questions = load_eval_questions()

    total = len(questions)

    retrieval_correct = 0
    category_correct = 0
    team_correct = 0
    priority_correct = 0
    total_latency = 0

    print("\nRunning evaluation...\n")

    for item in questions:
        question = item["question"]

        start_time = time()
        response = answer_question(question)
        latency_ms = round((time() - start_time) * 1000, 2)

        total_latency += latency_ms

        actual_sources = response["sources"]
        actual_ticket = response["ticket"]

        retrieval_ok = contains_expected_source(
            actual_sources,
            item["expected_sources"],
        )

        category_ok = actual_ticket["category"] == item["expected_category"]
        team_ok = actual_ticket["assigned_team"] == item["expected_team"]
        priority_ok = actual_ticket["priority"] == item["expected_priority"]

        retrieval_correct += int(retrieval_ok)
        category_correct += int(category_ok)
        team_correct += int(team_ok)
        priority_correct += int(priority_ok)

        print(f"Question: {question}")
        print(f"Actual Sources: {actual_sources}")
        print(f"Expected Sources: {item['expected_sources']}")
        print(f"Actual Ticket: {actual_ticket}")
        print(f"Retrieval Correct: {retrieval_ok}")
        print(f"Category Correct: {category_ok}")
        print(f"Team Correct: {team_ok}")
        print(f"Priority Correct: {priority_ok}")
        print(f"Latency: {latency_ms} ms")
        print("-" * 70)

    print("\nEvaluation Summary")
    print("=" * 70)
    print(f"Total Questions: {total}")
    print(f"Retrieval Accuracy: {retrieval_correct / total:.2%}")
    print(f"Category Accuracy: {category_correct / total:.2%}")
    print(f"Team Routing Accuracy: {team_correct / total:.2%}")
    print(f"Priority Accuracy: {priority_correct / total:.2%}")
    print(f"Average Latency: {total_latency / total:.2f} ms")


if __name__ == "__main__":
    run_evaluation()