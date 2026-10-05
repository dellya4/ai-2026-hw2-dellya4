import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from jsonschema import validate
from jsonschema.exceptions import ValidationError

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

CHAT_FILE = DATA / "chat_script.json"
SCHEMA_FILE = DATA / "memory_state.schema.json"

MODEL = "gpt-5.6-luna"


SYSTEM_PROMPT = """
You are an assistant for a grant office.

Answer using only information available in the conversation
or in the structured memory state provided to you.

Don't invent facts.
""".strip()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    return OpenAI(api_key=key)


def ask_llm(messages: list[dict]) -> dict:
    client = openai_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return {
        "text": response.choices[0].message.content or "",
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
    }


def compress_history(
        messages: list[dict],
        schema: dict
    ) -> dict:

    schema_text = json.dumps(
        schema,
        ensure_ascii=False,
        indent=2
    )

    compression_prompt = f"""
    Summarize the conversation into exactly one JSON memory object.

    The JSON object MUST satisfy this schema exactly:

    {schema_text}

    Important:
    - Include every required field from the schema.
    - Use exactly the data types required by the schema.
    - Don't add any extra fields.
    - Only output fields listed inside the schema's "properties".
    - Do NOT copy schema metadata into the result.
    - In particular, do NOT output fields such as:
    "$comment", "$schema", "type", "properties",
    "required", or "additionalProperties".
    - Preserve facts that may be needed later.
    - Preserve unresolved questions and user constraints when the schema allows them.
    - If information is unknown, use the value allowed by the schema.
    - Return only the JSON object.
    - Don't use Markdown or ```json fences.
    """.strip()

    compression_messages = messages + [
        {
            "role": "user",
            "content": compression_prompt
        }
    ]

    result = ask_llm(compression_messages)

    try:
        state = json.loads(result["text"])

    except json.JSONDecodeError as e:
        print("\nCOMPRESSION JSON ERROR:")
        print(e)

        print("\nRAW COMPRESSION REPLY:")
        print(result["text"])

        return {
            "ok": False,
            "state": None,
            "raw": result["text"],
            "input_tokens": result["input_tokens"],
        }

    if not validate_state(state, schema):
        print("\nINVALID STATE:")
        print(
            json.dumps(
                state,
                ensure_ascii=False,
                indent=2
            )
        )

        return {
            "ok": False,
            "state": state,
            "raw": result["text"],
            "input_tokens": result["input_tokens"],
        }

    return {
        "ok": True,
        "state": state,
        "raw": result["text"],
        "input_tokens": result["input_tokens"],
    }


def validate_state(state: dict, schema: dict) -> bool:
    try:
        validate(
            instance=state,
            schema=schema
        )
        return True

    except ValidationError as e:
        print("\nSTATE VALIDATION ERROR:")
        print(e.message)
        return False


def run_script(use_compression: bool):
    chat_data = load_json(CHAT_FILE)
    schema = load_json(SCHEMA_FILE)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    token_log = []
    state = None

    turns = chat_data["conversation"]

    for turn in turns:

        if turn == "<compress>":
            if use_compression:
                compressed = compress_history(
                    messages,
                    schema
                )

                token_log.append(
                    compressed["input_tokens"]
                )

                if compressed["ok"]:
                    state = compressed["state"]

                    messages = [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "system",
                            "content": (
                                "Memory state:\n"
                                + json.dumps(
                                    state,
                                    ensure_ascii=False
                                )
                            )
                        }
                    ]

                    print("Compression successful.")

                else:
                    print(
                        "Compression failed. "
                        "Keeping full history."
                    )

            continue

        messages.append({
            "role": "user",
            "content": turn
        })

        result = ask_llm(messages)

        token_log.append(
            result["input_tokens"]
        )

        messages.append({
            "role": "assistant",
            "content": result["text"]
        })

    return {
        "messages": messages,
        "tokens": token_log,
        "state": state,
    }


def run_probes(messages, probes):
    results = []

    for probe in probes:
        probe_messages = messages + [
            {
                "role": "user",
                "content": probe["question"]
            }
        ]

        result = ask_llm(probe_messages)

        answer = result["text"]

        retrieved = any(
            expected.lower() in answer.lower()
            for expected in probe["expect_contains"]
        )

        print(f"\n{probe['id']}")
        print("Question:", probe["question"])
        print("Tests:", probe["tests"])
        print("Answer:", answer)
        print("Retrieved:", retrieved)

        results.append({
            "id": probe["id"],
            "question": probe["question"],
            "answer": answer,
            "retrieved": retrieved,
        })

    return results


def print_tokens(label: str, tokens: list[int]):
    print(f"\n{label}")

    for i, count in enumerate(tokens, start=1):
        print(
            f"Call {i}: {count} input tokens"
        )

    print(
        f"Peak: {max(tokens)} input tokens"
    )

    print(
        f"Total for the run: {sum(tokens)} input tokens"
    )


def run_experiment():
    chat_data = load_json(CHAT_FILE)

    probes = chat_data["probes"]

    print("\n===== UNCOMPRESSED =====")

    uncompressed = run_script(
        use_compression=False
    )

    print("\n===== COMPRESSED =====")

    compressed = run_script(
        use_compression=True
    )

    print("\n===== TOKEN COUNTS =====")

    print_tokens(
        "UNCOMPRESSED",
        uncompressed["tokens"]
    )

    print_tokens(
        "COMPRESSED",
        compressed["tokens"]
    )

    print("\n===== COMPRESSED STATE =====")

    if compressed["state"] is not None:
        print(
            json.dumps(
                compressed["state"],
                ensure_ascii=False,
                indent=2
            )
        )
    else:
        print("No valid compressed state was created.")

    print("\n===== PROBES: UNCOMPRESSED =====")

    uncompressed_probe_results = run_probes(
        uncompressed["messages"],
        probes
    )

    print("\n===== PROBES: COMPRESSED =====")

    compressed_probe_results = run_probes(
        compressed["messages"],
        probes
    )

    return {
        "uncompressed": uncompressed,
        "compressed": compressed,
        "uncompressed_probes": uncompressed_probe_results,
        "compressed_probes": compressed_probe_results,
    }


def interactive():
    schema = load_json(SCHEMA_FILE)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    last_tokens = 0
    total_tokens = 0

    while True:
        user_text = input("\nYou: ").strip()

        if not user_text:
            continue

        if user_text.lower() in {
            "exit",
            "quit"
        }:
            print(
                f"\nTotal input tokens used: "
                f"{total_tokens}"
            )
            break

        if user_text.lower() == "tokens":
            print(
                f"Last input tokens: "
                f"{last_tokens}"
            )

            print(
                f"Total input tokens: "
                f"{total_tokens}"
            )

            continue

        if user_text.lower() in {
            "compress",
            "<compress>"
        }:
            compressed = compress_history(
                messages,
                schema
            )

            compression_tokens = compressed.get(
                "input_tokens",
                0
            )

            last_tokens = compression_tokens
            total_tokens += compression_tokens

            if compressed["ok"]:
                state = compressed["state"]

                messages = [
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "system",
                        "content": (
                            "Memory state:\n"
                            + json.dumps(
                                state,
                                ensure_ascii=False
                            )
                        )
                    }
                ]

                print(
                    "\nCompression successful."
                )

                print(
                    json.dumps(
                        state,
                        ensure_ascii=False,
                        indent=2
                    )
                )

                print(
                    f"\nCompression input tokens: "
                    f"{compression_tokens}"
                )

                print(
                    f"Total input tokens: "
                    f"{total_tokens}"
                )

            else:
                print(
                    "Compression failed. "
                    "History was kept."
                )

                print(
                    f"Compression input tokens: "
                    f"{compression_tokens}"
                )

            continue

        messages.append({
            "role": "user",
            "content": user_text
        })

        result = ask_llm(messages)

        last_tokens = result["input_tokens"]
        total_tokens += last_tokens

        print(
            "\nAssistant:",
            result["text"]
        )

        print(
            f"\nInput tokens this call: "
            f"{last_tokens}"
        )

        print(
            f"Total input tokens: "
            f"{total_tokens}"
        )

        messages.append({
            "role": "assistant",
            "content": result["text"]
        })


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--interactive",
        action="store_true"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive()
    else:
        run_experiment()


if __name__ == "__main__":
    main()


