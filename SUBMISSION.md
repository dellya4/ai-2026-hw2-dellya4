# HW2 submission

**Name: Abdrakhmanova Adel**

**Student ID: S23067852**

**Group: CSS4007-ENG-10**

**Repository:** https://github.com/dellya4/ai-2026-hw2-dellya4

## AI tool disclosure

State which AI tools you used and for what. Expected and fine; undisclosed use
is not. If you used a model to help you draft a prompt, say which prompt.

>Use ChanGPT for understanding, helpfully and debugging. 

---

## Sublab Easy — one task, four roles

### Decisions per role

One row per enquiry. In each cell write the `decision` your run returned, and
whether it agrees with `expected` in `data/enquiries.json`:

| Enquiry | policy_officer | front_desk | auditor   | bilingual_clerk |
|---|----------------|------------|-----------|-----------------|
| E-01 | granted        | granted    | more_info | granted         |
| E-02 | more_info      | more_info  | more_info | more_info       |
| E-03 | refused        | more_info  | refused   | refused         |
| E-04 | refused        | more_info  | refused   | refused         |
| E-05 | granted        | granted    | more_info | granted         |
| E-06 | granted        | granted    | more_info | granted         |
| E-07 | granted        | granted    | more_info | granted         |
| E-08 | not_found      | not_found  | not_found | not_found       |
| E-09 | refused        | more_info  | refused   | refused         |
| E-10 | more_info      | more_info  | refused   | refused         |
| **agrees with `expected`** | 10/10          | 7/10       | 4/10      | 9/10            |
| **parsed** | 10/10          | 10/10        | 10/10       | 10/10             |
| **schema-valid** | 10/10            | 10/10        | 10/10       | 10/10             |

### Which field moved, on which enquiry, under which role

| Field               | Enquiries that moved                                                                                                                                            | Role(s) that moved it                |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------|
| `found`             | None                                                                                                                                                            | None                                 |
| `decision`          | E-03 (front_desk), E-04 (front_desk), E-09 (front_desk), E-01 (auditor), E-05 (auditor), E-06 (auditor), E-07 (auditor), E-10 (auditor), E-10 (bilingual_clerk) | front_desk, auditor, bilingual_clerk |
| `amount`            | E-02 (auditor)                                                                                                                                                  | auditor                              |
| `missing_documents` | None                                                                                                                                                            | None                                 |

Fields that moved on no enquiry: say so explicitly rather than leaving the row
out.

### Raw replies

Paste the full reply for **one enquiry where a role changed the decision** away
from the policy officer's:

```
"applicant_id": "A-203",
  "found": true,
  "decision": "more_info",
  "amount": 0,
  "missing_documents": [],
  "reason": "The official record shows a GPA of 2.4, below the required minimum of 2.67. 
  The applicant would need a qualifying GPA of at least 2.67 for the application to be granted."
```

Paste the full reply for **E-07 (the Kazakh enquiry)** from the bilingual
clerk, so the `reason` language is visible:

```
"applicant_id": "A-201",
  "found": true,
  "decision": "granted",
  "amount": 250000,
  "missing_documents": [],
  "reason": "Сіз грантқа сайсыз: GPA 3.4, кіріс санаты 1, транскрипт пен жеке куәлік құжаттары бар. 
  Грант мөлшері — 250 000 теңге."
```

### Written answers

**1. Which fields are role-sensitive and which are not?** Point at rows in your
tables.

> The most sensitive fields is decision, because every role follows his rules. For example, 
> front-desk change refused to more_info, because this role don't give direct refusal. 
> Auditor change granted to more info, because this role don't give accept after first reading
> The amount fields is a less sensitive for role because change only 1 time. 

**2. Which enquiries are most sensitive to the role, and why those?** Say what
E-03, E-04, E-07 and E-10 are each testing.

>E-03 is more sensitive to the role because different role give different result, and it depends on rules 
> which we write. For example, where applicant don't have some requirements for grant, the policy give only refuse,
> but front give more_info, because this role afraid of refuses
> 
> E-04 is sensitive too. Majority roles give refuse, but front again give more_info for applicant who don't 
> follows some requirements
> 
> E-07 is more interesting case. This enquiry give information in different language and bilingual_clerk give grant and
> write reason in this language (kazakh). A different role, officer give grant too. Auditor for this case give only more_info,
> because it can't give accept in first reading
> 
> E-10 shows moment, where official documents is differed with applicant words. Officer don't believe him and give more_info,
> but auditor and clerk were some strong and give only refused

**3. Where does discretion belong — the role paragraph, or code that reads
`decision` afterwards?** Say what a downstream program can and cannot tell
about which role produced a record.

>The most important rules must check in code after receiving the response. The role can change model behavior and some 
> habits (which we write), but the important things can lose in this text. 
> 
> And if we didn't save role manually, program can't understand who give this decision, 
> because it doesn't look this data. And it more interesting, how different role can give a similar decision
> more_info in different situations

**4. Is a role a boundary?** Say in Week 2 terms what the role paragraph is
made of, and what you would put in code — not in the prompt — if a wrong
`decision` were expensive.

>No, role is some tools for setting up models behavior and some mood in messages. But this property doesn't give security,
> because it doesn't mean that the result will be correct always. If mistakes will cost expensive, I will write some 
> helpful code, which will check the result of program before giving a final decision. Some time model can forget about 
> some rules, or I don't be able to describe specific situations where the model should give a specific rejection.

---

## Sublab Medium — memory you choose

### Tokens per call

| Call | A — never compressed | B — compressed at the `compress` turn |
|---|----------------------|---------------------------------------|
| 1 | 63                   | 63                                    |
| 2 | 128                  | 118                                   |
| 3 | 201                  | 193                                   |
| 4 | 279                  | 279                                   |
| 5 | 355                  | 349                                   |
| 6 | 460                  | 467                                   |
| 7 | 553                  | 553                                   |
| 8 | 649                  | 665                                   |
| 9 | 736                  | 749                                   |
| 10 | 822                  | 1358                                  |
| 11 | 944                  | 267                                   |
| 12 | -                    | 373                                   |
| **peak** | 944                  | 1358                                  |
| **total for the run** | 5190                 | 5434                                  |

### Probes after the conversation

| Probe                 | Tests     | A retrieved? | A answer                                                                                                                                                                                                                                                                                | B retrieved? | B answer                                                                                                                                                       |
|-----------------------|-----------|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Q-1 identity          | turn 1    | Yes          | You are Daniyar Qoshan, applicant **A-202**.                                                                                                                                                                                                                                            | Yes          | You are **Daniyar Qoshan**, and your applicant ID is **A-202**.                                                                                                |
| Q-2 missing document  | turn 5    | Yes          | The only document you have explicitly said is missing is your **ID card**. You said you plan to bring it to the office on Thursday. The status of your transcript, family income certificate, and employer letter is not confirmed.                                                     | Yes          | The missing document is a copy or scan of your ID card                                                                                                         |
| Q-3 band and amount   | turns 3–4 | No           | Your income band is **2**, based on your family’s certificate. However, the grant amount associated with band 2 has not been provided, so I can’t calculate or confirm the payment. Please ask the grant office for the applicable amount.                                              | No           | Your family’s certificate places you in **income band 2**. The corresponding grant amount is not provided in the available information, so I can’t confirm it. |
| Q-4 the constraint    | turn 6    | Yes          | You said you can come to the office on **Thursdays**, since you have lab all week otherwise                                                                                                                                                                                             | Yes          | You can come to the office on **Thursdays**.                                                                                                                   |
| Q-5 the open question | turn 7    | Yes          | You asked whether a **scanned letter from your employer** would be accepted, or whether you must provide the **original**. I said I didn’t have the grant office’s document-submission policy and recommended asking whether they accept a scan, clear photo, or digitally signed copy. | Yes          | You asked whether a scanned letter from your employer would count, or whether the original letter is required.                                                 |
| **retrieved**         |           | 4/5          |                                                                                                                                                                                                                                                                                         | 4/5          |                                                                                                                                                                |

### The state my compression produced

```json
{
  "applicant_id": "A-202",
  "topic": "Study grant application and document submission",
  "facts": [
    "Applicant's name is Daniyar Qoshan.",
    "Applicant sent a transcript last week.",
    "Applicant's family's certificate places them in income band 2.",
    "Applicant could not upload their ID card because their home scanner broke.",
    "Applicant's sister, Aruzhan, applied last year and is on file."
  ],
  "decisions": [],
  "constraints": [
    "Applicant can come to the office only on Thursdays because they have lab all week otherwise."
  ],
  "open_questions": [
    "Does the applicant qualify for the study grant?",
    "How much would the grant award be if approved?",
    "Does a scanned letter from the applicant's employer count, or is the original required?",
    "If the applicant brings the ID card on Thursday, will the decision be made the same day?",
    "Does the sister's previous application affect the applicant's eligibility or award?"
  ],
  "language": "English with some Kazakh"
}
```

### Written answers

**1. What did compression buy?** Peak tokens both ways, probes retrieved both
ways, and — if a probe was lost — which one and which turn it came from.

>Peak in uncompressed version is 944 tokens and 1358 in compressed version, it was moment when we compressed history.
>But after compression my calls take a fewer tokens, for example, in uncompressed version it was 944 tokens and in compressed
>version it was 267 tokens. Different was 677 tokens (it can depend on model, because some answers in first model may be a biggest,
> bit we can compare it how example)

>Each model retrieved 4 of 5 probes. They lost question with count of grant, it was Q-3.   

**2. Why must the state be structured rather than a paragraph?** You could have
asked for "a summary". Say what changes when the summary is an object with
named fields.

>Structure data it some easier for model, because it save the most important moment and find it faster 
>that unstructured data, for example, paragraph or some text

**3. What is missing from your state that you would add?** Name what you would
add and what you would drop to pay for it.

>The most important add fields for amount, that model save it and show after. I want drop field with decision,
> because model doesn't add some information in this place.

**4. When is compression the wrong choice?** Name a conversation where it would
lose something that cannot be recovered, and say whether your program would
notice.

>Compression is a bad idea for topics with a lot of important information, some numbers,
> name and another. Summery can drop a really necessary details. For example, my program doesn't remember info 
> with count of grant. 

> And the wrong idea using compression is a small conversation after compression. If looked on my result, compressed program cost 
> more expensive than uncompressed. It was because function "compressed" cost a lot of tokens, because we send history, some description 
> and JSON structure. 

---

## Sublab Hard — stories in, CVs out, the best candidate by code

### Part 1 — extraction

| Story    | Parsed? | Valid? | Fields that came back `null`                                   | Traps hit                                                          |
|----------|---------|--------|----------------------------------------------------------------|--------------------------------------------------------------------|
| story-01 | Yes     | Yes    | -                                                              | No                                                                 |
| story-02 | Yes     | Yes    | graduation_year, gpa_original, gpa_original_scale, gpa_4_scale | Contradiction (the graduation isn't numerical), missing data (GPA) |
| story-03 | Yes     | Yes    | -                                                              | GPA scale is 5, a second paper is under review                     |
| story-04 | Yes     | Yes    | -                                                              | 1 published book, 1 under review and 2 in preparation              |
| story-05 | Yes     | Yes    | -                                                              | CV in kazakh language                                              |
| story-06 | Yes     | Yes    | graduation_year, gpa_original, gpa_original_scale, gpa_4_scale | Contradiction (graduation and GPA)                                 |

The four traps, for reference: no GPA stated · a GPA on another scale · a paper
that is not published · a story that contradicts itself.

Paste the extraction for **story-06**, the one that contradicts itself:

```json

{
  "candidate_id": "story-06",
  "full_name": "Nurzhan Abilov",
  "degree": "BSc in Statistics",
  "graduation_year": null,
  "gpa_original": null,
  "gpa_original_scale": null,
  "gpa_4_scale": null,
  "languages": [
    "Kazakh",
    "Russian",
    "English"
  ],
  "published_peer_reviewed_outputs": 1,
  "other_research_outputs": [
    "One poster at a local event"
  ],
  "relevant_experience_months": 40,
  "contradictions": [
    {
      "field": "gpa",
      "values": [
        "3.2",
        "3.5"
      ],
      "note": "The story gives both values and explicitly states the GPA is not cleanly known."
    },
    {
      "field": "graduation_year",
      "values": [
        "2024",
        "2026"
      ],
      "note": "The story says the candidate graduated in 2024 and is currently a final-year student graduating in 2026."
    }
  ],
  "evidence": {
    "full_name": "\"# Nurzhan Abilov\"",
    "degree": "\"I graduated in 2024 with a BSc in Statistics.\"",
    "graduation_year": null,
    "gpa": null,
    "language": [
      "\"Languages: Kazakh, Russian, English.\""
    ],
    "published_peer_reviewed_output": [
      "\"one paper published, in a peer-reviewed proceedings, on survey weighting.\""
    ],
    "relevant_experience_months": [
      "\"I have been at an insurance analytics team since February 2023, which is about forty months.\""
    ]
  }
}

```

### Part 2 — scores and the winner

| Candidate | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) |
|---|----------------|----------------|------------------|-----------------------|
| story-01 | 5              | 5              | 2                | 4.40                  |
| story-02 | 0              | 2.5            | 5                | 1.75                  |
| story-03 | 4              | 2.5            | 2.92             | 3.33                  |
| story-04 | 4              | 3              | 5                | 3.90                  |
| story-05 | 5              | 2.5            | 1.25             | 3.50                  |
| story-06 | 2              | 3              | 5                | 2.90                  |

**Winner, computed by my code:** story-01 total=4.40

**The model's prose answer, asked separately ("who should win?"):**

> **Candidate ID: story-01 — Aziza Bekova. Aziza has a strong 3.8/4.0 GPA, two published peer-reviewed outputs, and eight months of relevant experience. Although some candidates have more experience, her superior academic record and two publications give her the strongest weighted profile overall.**
```

### Part 3 — written answers

**1. Which rule did you have to add, and what broke without it?** Name the
story that forced it.

>The most important rule was - "If the story contains contradictory value for a fields,
    don't choose one and don't average them
    Return null for that field and record the contradiction". This criteria goos work in 6 story, when 
    person said different years and GPA.

**2. Where did the model guess, and where did your code have to decide?** One
example of each, from your run.

>The model rated according to criteria, so there could be an interpretation of it. For example, for story-06, 
>with a contradictory GPA, the model still set academic = 2.
>The code, in turn, didn't interpret the candidates, but calculated the final score using a formula from rubric. 
>For example, for story-01, the code calculated a weighted total of 4.40 and selected this candidate as the winner based on the final scores.

**3. Did your prose ranking and your computed ranking agree?** Say which one
you trust and why — and if they agreed, what you would need to see before
trusting the prose one alone.

>Yes, the results matched. Both my code and the model's separate prose response chose story-01 as the winner.
>I trust the ranking calculated by the code more because it uses an explicit formula and the result can be verified. 
>To trust only the prose response of the model, it would be better to see transparent ratings for each criterion and 
>confirmation that the model is neutral to all candidates.

**4. The rubric has no anchor for a contradicted field.** The stories say 3.2
and then 3.5; the rubric defines a 0 and a 5 and nothing in between for this
case. Say what you did and what the rule should be.

>The GPA fields for story-06 were set to null, and the contradiction itself was saved in contradictions.
>When scoring, the model still gave the candidate academic = 2, because rubric does not define the exact behavior for such a case. 
>The best outcome is if rubric requires you to send conflicting academic data for manual verification, 
>since a person could either get confused or deliberately lie.

**5. How close were your top two candidates?** If they were within 0.05, say
what you would tell the committee and what you would change in the extraction
to make that call defensible.

>story-01 — 4.40
>story-04 — 3.90
>The difference was 0.50, so the candidate's victory is fully justified and logical.

---

## Reflection (optional, one short paragraph)

Having now written a role prompt, compressed a conversation, and ranked six
extractions — what will you do differently the next time you build something
that has to get reliable structured output out of a model?

>
