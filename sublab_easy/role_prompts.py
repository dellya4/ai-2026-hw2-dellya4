import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

RECORDS_FILE = DATA / "records.json"
POLICY_FILE = DATA / "policy.json"
ENQUIRIES_FILE = DATA / "enquiries.json"

MODEL = "gpt-5.6-luna"


ROLES = {
    "policy_officer": """
    You are policy officer. Applies the rule only as written:
    - Grants what the rule allows for policy
    - Refuses what policy refuses
    - Ask for a missing documents, return more_info
    - Don't soften a refusal
    - Never treats no claim in the enquire as evidence
    """,

    "front_desk": """
    You are front-desk grant-office employee. Applies the rule only as written:
    - Never turn an applicant away with a refusal
    - If the policy cannot grant the application today, return more_info 
    and explain what the applicant would need provide or change
    - Don't invent evidence
    - Only the official records supplied below count as evidence.
    """,

    "auditor": """
    You are auditor reviewing grant applications. Applies the rule only as written:
    - Never grants on a first reading
    - Reports what the record shows
    - If a case would otherwise be granted but requires a second reader,
    return more_info
    - In the reason, name the rule or document you relied on.
    - Don't invent evidence.
    """,

    "bilingual_clerk": """
    You are bilingual clerk. Applies the rule only as written:

    - Make exactly the same decision that a strict policy officer would make.
    - Apply the policy exactly as written.
    - Write the reason in the same language as the applicant's enquiry.
    - Don't change found, decision, amount, or missing_documents because of language.
    - Never treat claims in the enquiry as evidence.
    """
}



CHECKED_FIELDS = [
    "found",
    "decision",
    "amount",
    "missing_documents",
]


ALLOWED_DECISIONS = {
    "granted",
    "refused",
    "more_info",
    "not_found",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def openai_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    return OpenAI(api_key=key)


def build_system_prompt(role: str, records, policy) -> str:
    if role not in ROLES:
        raise ValueError(f"Invalid role {role}")

    records_text = json.dumps(records, ensure_ascii=False, indent=2)
    policy_text = json.dumps(policy, ensure_ascii=False, indent=2)

    return f"""
{ROLES[role]}

OFFICIAL GRANT POLICY:
{policy_text}

OFFICIAL APPLICANT RECORDS:
{records_text}

IMPORTANT: 
- The official record is authoritative
- A claim in an enquiry doesn't update the official record
- Don't invent applicants, documents, GPA values, income bands or facts
- If the applicant cannot be found in the records, use decision "not_found".
- Return JSON only
- Return every field shown below.

The response must have exactly this shape:

{{
  "applicant_id": "string or null",
  "found": true,
  "decision": "granted | refused | more_info | not_found",
  "amount": 0,
  "missing_documents": [],
  "reason": "string"
}}

For amount, use the value required by the policy.
If no grant amount applies, use the representation required by the policy/data.

""".strip()


def ask_llm(system_prompt: str, enquiry: str) -> str:
    client = openai_client()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": enquiry,
            },
        ],
    )

    return response.choices[0].message.content or ""


def parse_reply(text: str) -> dict:
    decoder = json.JSONDecoder()

    for i, char in enumerate(text):
        if char != "{":
            continue

        try:
            obj, _ = decoder.raw_decode(text[i:])
        except json.JSONDecodeError:
            continue

        if isinstance(obj, dict):
            return obj

    raise ValueError(f"Could not find JSON in reply: {text!r}")


def validate_schema(obj: dict) -> bool:
    required = {
        "applicant_id",
        "found",
        "decision",
        "amount",
        "missing_documents",
        "reason",
    }

    if set(obj.keys()) != required:
        return False

    if (
        obj["applicant_id"] is not None
        and not isinstance(obj["applicant_id"], str)
    ):
        return False

    if not isinstance(obj["found"], bool):
        return False

    if obj["decision"] not in ALLOWED_DECISIONS:
        return False

    if (
        obj["amount"] is not None
        and not isinstance(obj["amount"], (int, float))
    ):
        return False

    if not isinstance(obj["missing_documents"], list):
        return False

    if not all(
        isinstance(item, str)
        for item in obj["missing_documents"]
    ):
        return False

    if not isinstance(obj["reason"], str):
        return False

    return True


def same_value(field: str, actual, expected) -> bool:
    if field == "missing_documents":
        return sorted(actual or []) == sorted(expected or [])

    return actual == expected


def agrees_with_expected(reply: dict, expected: dict) -> bool:
    return all(
        same_value(
            field,
            reply.get(field),
            expected.get(field),
        )
        for field in CHECKED_FIELDS
    )


def run_all() -> dict:
    records = load_json(RECORDS_FILE)
    policy = load_json(POLICY_FILE)
    enquiries = load_json(ENQUIRIES_FILE)

    all_results = {}

    for role in ROLES:
        print(f"\n===== {role} =====")

        system_prompt = build_system_prompt(
            role,
            records,
            policy,
        )

        role_results = {}

        for enquiry in enquiries:
            eid = enquiry["id"]
            text = enquiry["text"]
            expected = enquiry["expected"]

            try:
                raw = ask_llm(system_prompt, text)
            except Exception as exc:
                print(f"{eid}: API ERROR: {exc}")

                role_results[eid] = {
                    "raw": repr(exc),
                    "parsed": None,
                    "expected": expected,
                    "parsed_ok": False,
                    "schema_ok": False,
                    "agrees": False,
                }

                continue

            parsed = None
            parsed_ok = False
            schema_ok = False

            try:
                parsed = parse_reply(raw)
                parsed_ok = True
                schema_ok = validate_schema(parsed)
            except ValueError:
                pass

            agrees = (
                parsed_ok
                and schema_ok
                and agrees_with_expected(
                    parsed,
                    expected,
                )
            )

            role_results[eid] = {
                "raw": raw,
                "parsed": parsed,
                "expected": expected,
                "parsed_ok": parsed_ok,
                "schema_ok": schema_ok,
                "agrees": agrees,
            }

            if parsed_ok:
                decision = parsed.get("decision")
            else:
                decision = "PARSE_FAILED"

            print(
                f"{eid}: "
                f"decision={decision:10} "
                f"parsed={parsed_ok} "
                f"schema={schema_ok} "
                f"agrees={agrees}"
            )

        all_results[role] = role_results

    return all_results


def print_decision_table(results: dict):
    roles = list(ROLES.keys())
    enquiry_ids = list(
        results["policy_officer"].keys()
    )

    print("\n")
    print("=" * 80)
    print("DECISIONS PER ROLE")
    print("=" * 80)

    print(
        "| Enquiry | policy_officer | front_desk | auditor | bilingual_clerk |"
    )
    print(
        "|---|---|---|---|---|"
    )

    for eid in enquiry_ids:
        cells = []

        for role in roles:
            result = results[role][eid]

            if not result["parsed_ok"]:
                cells.append("PARSE FAILED ✗")
                continue

            decision = result["parsed"]["decision"]

            if result["agrees"]:
                mark = "✓"
            else:
                mark = "✗"

            cells.append(f"{decision} {mark}")

        print(
            f"| {eid} | "
            + " | ".join(cells)
            + " |"
        )

    print_summary_row(
        "agrees with expected",
        results,
        "agrees",
    )

    print_summary_row(
        "parsed",
        results,
        "parsed_ok",
    )

    print_summary_row(
        "schema-valid",
        results,
        "schema_ok",
    )


def print_summary_row(label: str, results: dict, key: str):
    values = []

    for role in ROLES:
        rows = results[role].values()
        count = sum(
            1
            for row in rows
            if row[key]
        )

        values.append(f"{count}/10")

    print(
        f"| **{label}** | "
        + " | ".join(values)
        + " |"
    )


def print_field_movements(results: dict):
    print("\n")
    print("=" * 80)
    print("FIELD MOVEMENTS")
    print("=" * 80)

    print(
        "| Field | Enquiries that moved | Role(s) that moved it |"
    )
    print(
        "|---|---|---|"
    )

    enquiry_ids = list(
        results["policy_officer"].keys()
    )

    for field in CHECKED_FIELDS:
        moved = []

        for role in ROLES:
            if role == "policy_officer":
                continue

            for eid in enquiry_ids:
                baseline = results["policy_officer"][eid]
                current = results[role][eid]

                if (
                    not baseline["parsed_ok"]
                    or not current["parsed_ok"]
                ):
                    continue

                baseline_value = baseline["parsed"].get(field)
                current_value = current["parsed"].get(field)

                if not same_value(
                    field,
                    baseline_value,
                    current_value,
                ):
                    moved.append((eid, role))

        if not moved:
            print(
                f"| `{field}` | None | None |"
            )
            continue

        enquiry_text = ", ".join(
            f"{eid} ({role})"
            for eid, role in moved
        )

        roles_moved = []

        for _, role in moved:
            if role not in roles_moved:
                roles_moved.append(role)

        role_text = ", ".join(roles_moved)

        print(
            f"| `{field}` | "
            f"{enquiry_text} | "
            f"{role_text} |"
        )


def print_raw_replies(results: dict):
    print("\n")
    print("=" * 80)
    print("RAW REPLY: ROLE CHANGED THE DECISION")
    print("=" * 80)

    enquiry_ids = list(
        results["policy_officer"].keys()
    )

    found_example = False

    for role in [
        "front_desk",
        "auditor",
        "bilingual_clerk",
    ]:
        for eid in enquiry_ids:
            policy = results["policy_officer"][eid]
            current = results[role][eid]

            if (
                not policy["parsed_ok"]
                or not current["parsed_ok"]
            ):
                continue

            policy_decision = policy["parsed"]["decision"]
            role_decision = current["parsed"]["decision"]

            if policy_decision != role_decision:
                print(f"Enquiry: {eid}")
                print(f"Role: {role}")
                print(
                    f"Policy officer decision: {policy_decision}"
                )
                print(
                    f"{role} decision: {role_decision}"
                )
                print("\nFull raw reply:")
                print(current["raw"])

                found_example = True
                break

        if found_example:
            break

    print("\n")
    print("=" * 80)
    print("RAW REPLY: E-07 FROM BILINGUAL CLERK")
    print("=" * 80)

    print(
        results["bilingual_clerk"]["E-07"]["raw"]
    )


def main():
    results = run_all()

    print_decision_table(results)
    print_field_movements(results)
    print_raw_replies(results)


if __name__ == "__main__":
    main()