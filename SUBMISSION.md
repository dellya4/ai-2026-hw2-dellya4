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
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
| 9 | | |
| 10 | | |
| 11 | | |
| 12 | | |
| **peak** | | |
| **total for the run** | | |

### Probes after the conversation

| Probe | Tests | A retrieved? | A answer | B retrieved? | B answer |
|---|---|---|---|---|---|
| Q-1 identity | turn 1 | | | | |
| Q-2 missing document | turn 5 | | | | |
| Q-3 band and amount | turns 3–4 | | | | |
| Q-4 the constraint | turn 6 | | | | |
| Q-5 the open question | turn 7 | | | | |
| **retrieved** | | /5 | | /5 | |

### The state my compression produced

```json
```

### Written answers

**1. What did compression buy?** Peak tokens both ways, probes retrieved both
ways, and — if a probe was lost — which one and which turn it came from.

>

**2. Why must the state be structured rather than a paragraph?** You could have
asked for "a summary". Say what changes when the summary is an object with
named fields.

>

**3. What is missing from your state that you would add?** Name what you would
add and what you would drop to pay for it.

>

**4. When is compression the wrong choice?** Name a conversation where it would
lose something that cannot be recovered, and say whether your program would
notice.

>

---

## Sublab Hard — stories in, CVs out, the best candidate by code

### Part 1 — extraction

| Story | Parsed? | Valid? | Fields that came back `null` | Traps hit |
|---|---|---|---|---|
| story-01 | | | | |
| story-02 | | | | |
| story-03 | | | | |
| story-04 | | | | |
| story-05 | | | | |
| story-06 | | | | |

The four traps, for reference: no GPA stated · a GPA on another scale · a paper
that is not published · a story that contradicts itself.

Paste the extraction for **story-06**, the one that contradicts itself:

```json
```

### Part 2 — scores and the winner

| Candidate | academic (0–5) | research (0–5) | experience (0–5) | weighted total (code) |
|---|---|---|---|---|
| story-01 | | | | |
| story-02 | | | | |
| story-03 | | | | |
| story-04 | | | | |
| story-05 | | | | |
| story-06 | | | | |

**Winner, computed by my code:**

**The model's prose answer, asked separately ("who should win?"):**

>
```

### Part 3 — written answers

**1. Which rule did you have to add, and what broke without it?** Name the
story that forced it.

>

**2. Where did the model guess, and where did your code have to decide?** One
example of each, from your run.

>

**3. Did your prose ranking and your computed ranking agree?** Say which one
you trust and why — and if they agreed, what you would need to see before
trusting the prose one alone.

>

**4. The rubric has no anchor for a contradicted field.** The stories say 3.2
and then 3.5; the rubric defines a 0 and a 5 and nothing in between for this
case. Say what you did and what the rule should be.

>

**5. How close were your top two candidates?** If they were within 0.05, say
what you would tell the committee and what you would change in the extraction
to make that call defensible.

>

---

## Reflection (optional, one short paragraph)

Having now written a role prompt, compressed a conversation, and ranked six
extractions — what will you do differently the next time you build something
that has to get reliable structured output out of a model?

>
