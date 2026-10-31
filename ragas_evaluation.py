
import json
import csv
from pathlib import Path

import ollama
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import Faithfulness
from ragas.llms import LangchainLLMWrapper
from langchain_ollama import ChatOllama

from workflow import build_workflow
from ragas.run_config import RunConfig

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"
QUESTIONS_FILE = ROOT / "tests" / "test_questions.json"

RESULTS_DIR.mkdir(exist_ok=True)


def load_questions():
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    return [
        item for item in questions
        if item["expected_behavior"] == "answer"
    ]


def generate_evaluation_data():
    """Run the real RAG workflow and collect its answers and contexts."""

    app = build_workflow()
    questions = load_questions()

    evaluation_data = []

    for item in questions:
        print(f"Evaluating {item['id']}: {item['question']}")

        result = app.invoke({
            "question": item["question"]
        })

        output = result["result"]

        if not output["is_sufficient"]:
            print(f"WARNING: {item['id']} was refused.")
            continue

        contexts = [
            chunk["text"]
            for chunk in result["evidence"]["chunks"]
            if chunk.get("text")
        ]

        evaluation_data.append({
            "user_input": item["question"],
            "response": output["answer"],
            "retrieved_contexts": contexts,
        })

    if not evaluation_data:
        raise RuntimeError(
            "No answerable questions produced answers. "
            "Check retrieval and evidence thresholds."
        )

    return evaluation_data



def run_ragas():
    data = generate_evaluation_data()

    print("\n========== EVALUATION DATA ==========")

    for i, item in enumerate(data):
        print(f"\nQuestion {i + 1}:")
        print("Question:", item["user_input"])
        print("Answer:", item["response"])
        print("Number of contexts:", len(item["retrieved_contexts"]))
        print("Context preview:", item["retrieved_contexts"][:1])

    dataset = Dataset.from_list(data)

    local_llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0,
    )

    evaluator_llm = LangchainLLMWrapper(local_llm)

    metrics = [Faithfulness(llm=evaluator_llm)]

    print("\nRunning Ragas evaluation...")

    results = evaluate(
      dataset=dataset,
      metrics=metrics,
      raise_exceptions=True,
      run_config=RunConfig(
          timeout=600,
          max_workers=1,
          max_retries=2,
          max_wait=30,
      ),
    )

    df = results.to_pandas()

    print("\n========== INDIVIDUAL SCORES ==========")
    print(df[["faithfulness"]])

    valid_scores = df["faithfulness"].dropna()

    if valid_scores.empty:
        average_score = None
        print("No valid Faithfulness scores were generated.")
    else:
        average_score = float(valid_scores.mean())
        print(f"Average Faithfulness: {average_score:.4f}")

    csv_path = RESULTS_DIR / "ragas-baseline.csv"
    df.to_csv(csv_path, index=False)

    summary = {
        "model": "qwen2.5:3b",
        "metric": "faithfulness",
        "number_of_questions": len(data),
        "valid_scores": len(valid_scores),
        "scores": {
            "faithfulness": average_score
        },
    }

    json_path = RESULTS_DIR / "ragas-baseline.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=4)

    print("\nRagas baseline:")
    print(json.dumps(summary, indent=4))

    print(f"\nSaved CSV: {csv_path}")
    print(f"Saved JSON: {json_path}")



if __name__ == "__main__":
    run_ragas()
