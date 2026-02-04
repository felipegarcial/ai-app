"""
Chain-of-Thought (CoT) Pattern Implementation.

Forces the model to reason step-by-step before generating content.
This improves accuracy and consistency by making the reasoning process explicit.

Usage:
    from prompts.patterns.chain_of_thought import get_cot_prompt, COT_LEGAL_DOCUMENT

    # Get CoT prompt for legal documents
    cot_section = get_cot_prompt("legal_document")

    # Or use directly
    prompt = f"{COT_LEGAL_DOCUMENT}\n\nNow generate the document."
"""

# Chain-of-Thought prompt for legal document generation
COT_LEGAL_DOCUMENT = """
## Chain-of-Thought: Reason Before Generating

**IMPORTANT**: Before generating any content, you MUST complete the following analysis.
Think through each step carefully and write your reasoning.

<thinking>
### Step 1: Analyze the Parties
- Who is the disclosing party and what is their role?
- Who is the receiving party and what is their role?
- Is this a mutual or unilateral agreement?

### Step 2: Evaluate Confidential Information Scope
- What specific types of information need protection?
- Are there any exclusions that should apply?
- How broad or narrow should the definition be?

### Step 3: Consider Duration and Jurisdiction
- What is the appropriate term for this agreement?
- What jurisdiction's laws will govern?
- Are there any jurisdiction-specific requirements?

### Step 4: Identify Required Clauses
- Which standard clauses are essential for this NDA?
- Are there any special circumstances requiring additional clauses?
- What remedies should be specified for breach?

### Step 5: Plan Document Structure
- Outline the sections in logical order
- Note any dependencies between sections
- Identify defined terms to use consistently
</thinking>

After completing your analysis above, generate the document.

---

## Few-Shot Example: Correct Reasoning

Here is an example of proper Chain-of-Thought reasoning for an NDA:

<example>
**Input Data:**
- party_a_name: TechCorp Inc.
- party_b_name: InnovateLab LLC
- confidential_info_type: AI algorithms and training data
- duration: 3 years
- governing_law: Delaware

<thinking>
### Step 1: Analyze the Parties
- TechCorp Inc. appears to be the disclosing party sharing proprietary technology
- InnovateLab LLC is the receiving party, likely a partner or contractor
- Since only one party is sharing confidential info, this is a UNILATERAL NDA
- Both are companies (not individuals), so corporate signature blocks needed

### Step 2: Evaluate Confidential Information Scope
- "AI algorithms" requires protection of: source code, model architectures, hyperparameters
- "Training data" includes: datasets, data processing methods, annotations
- Exclusions should include: publicly available AI research, independently developed algorithms
- Scope should be SPECIFIC to AI/ML domain, not overly broad

### Step 3: Consider Duration and Jurisdiction
- 3-year term is reasonable for technology that evolves quickly
- Delaware law is favorable for corporate agreements
- Delaware allows injunctive relief without proving irreparable harm
- No specific Delaware NDA statute requirements

### Step 4: Identify Required Clauses
- Standard clauses: definitions, obligations, exclusions, term, remedies
- Special considerations for AI: prohibition on reverse engineering models
- Remedies: injunctive relief essential for trade secrets, monetary damages
- Add: return/destruction of data clause for training datasets

### Step 5: Plan Document Structure
1. Header with parties and effective date
2. Recitals explaining purpose
3. Definitions (Confidential Information, Disclosing Party, Receiving Party)
4. Obligations of Receiving Party
5. Exclusions from Confidential Information
6. Term and Termination
7. Remedies
8. General Provisions
9. Signatures
</thinking>
</example>

Now apply this same rigorous analysis to the current request.
""".strip()

# Chain-of-Thought prompt for document revision
COT_REVISION = """
## Chain-of-Thought: Analyze Before Revising

**IMPORTANT**: Before making any changes, analyze the revision request carefully.

<thinking>
### Step 1: Understand the Request
- What specific change is being requested?
- Which section(s) are affected?

### Step 2: Assess Impact
- Will this change affect other sections?
- Are there any dependencies to consider?
- Could this create inconsistencies?

### Step 3: Plan the Revision
- What is the minimal change needed?
- How to maintain document consistency?
- Are defined terms affected?
</thinking>

After completing your analysis, apply the revision.

---

## Few-Shot Example: Correct Revision Analysis

<example>
**Current Document Excerpt:**
"...The term of this Agreement shall be two (2) years from the Effective Date..."

**Revision Request:**
"Change the duration to 5 years and add an auto-renewal clause"

<thinking>
### Step 1: Understand the Request
- Two changes requested: (1) duration change, (2) new clause addition
- Affects Section 5: Term and Termination
- Auto-renewal is a new feature, not just a modification

### Step 2: Assess Impact
- Duration change: straightforward text replacement
- Auto-renewal clause: need to add termination notice requirement
- Must update any references to "two (2) years" elsewhere
- Remedies section may reference term - check for consistency

### Step 3: Plan the Revision
1. Replace "two (2) years" with "five (5) years" in Term section
2. Add auto-renewal language: "shall automatically renew for successive one (1) year periods"
3. Add termination notice: "unless either party provides written notice of non-renewal at least thirty (30) days prior"
4. Scan document for any other duration references
5. No defined terms affected
</thinking>

**Revised Section:**
"The term of this Agreement shall be five (5) years from the Effective Date and shall automatically renew for successive one (1) year periods unless either party provides written notice of non-renewal at least thirty (30) days prior to the end of the then-current term."
</example>

Now apply this same careful analysis to the current revision request.
""".strip()

# Chain-of-Thought prompt for data extraction
COT_EXTRACTION = """
## Chain-of-Thought: Analyze Before Extracting

<thinking>
### Step 1: Identify Entities
- What parties are mentioned?
- What roles do they have?

### Step 2: Extract Key Terms
- Duration mentioned?
- Jurisdiction specified?
- Type of information to protect?

### Step 3: Validate Completeness
- What information is present?
- What is still missing?
</thinking>

Now extract the structured data.
""".strip()

# Registry of available CoT prompts
COT_PROMPTS = {
    "legal_document": COT_LEGAL_DOCUMENT,
    "revision": COT_REVISION,
    "extraction": COT_EXTRACTION,
}


def get_cot_prompt(prompt_type: str = "legal_document") -> str:
    """
    Get a Chain-of-Thought prompt by type.

    Args:
        prompt_type: Type of CoT prompt to retrieve.
                    Options: "legal_document", "revision", "extraction"

    Returns:
        The CoT prompt string

    Raises:
        ValueError: If prompt_type is not recognized
    """
    if prompt_type not in COT_PROMPTS:
        available = ", ".join(COT_PROMPTS.keys())
        raise ValueError(f"Unknown CoT prompt type: {prompt_type}. Available: {available}")

    return COT_PROMPTS[prompt_type]


def build_cot_prompt(
    steps: list[dict],
    intro: str = "Before proceeding, analyze the situation:",
    outro: str = "After completing your analysis, proceed."
) -> str:
    """
    Build a custom Chain-of-Thought prompt from steps.

    Args:
        steps: List of dicts with 'title' and 'questions' keys
        intro: Introduction text before the thinking section
        outro: Text after the thinking section

    Returns:
        Formatted CoT prompt string

    Example:
        steps = [
            {"title": "Understand Context", "questions": ["What is the goal?", "Who is involved?"]},
            {"title": "Plan Approach", "questions": ["What steps are needed?", "What could go wrong?"]}
        ]
        prompt = build_cot_prompt(steps)
    """
    lines = [
        "## Chain-of-Thought Analysis",
        "",
        f"**IMPORTANT**: {intro}",
        "",
        "<thinking>"
    ]

    for i, step in enumerate(steps, 1):
        lines.append(f"### Step {i}: {step['title']}")
        for question in step.get("questions", []):
            lines.append(f"- {question}")
        lines.append("")

    lines.append("</thinking>")
    lines.append("")
    lines.append(outro)

    return "\n".join(lines)
