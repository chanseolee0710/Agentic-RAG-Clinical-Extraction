# app/agent.py

"""
Agent for structured data extraction from medical notes.

Pipeline:
1. Use LLM to extract structured fields (patient, conditions, meds, vitals, labs, plan)
   in a strict JSON format.
2. Enrich conditions with ICD-10 codes.
3. Enrich medications with RxNorm codes.
"""

import json
from typing import Dict, Any, Optional, Tuple

import requests
from openai import OpenAI

from .config import settings
from .schemas import StructuredNote, Condition, Medication


# Create an OpenAI client
# Create an OpenAI client
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

# ---------- Helpers: external code lookup (public APIs) ----------

def lookup_icd10(condition_name: str) -> Optional[str]:
    """
    Best-effort ICD-10 lookup using the NLM clinicaltables API.

    Docs: https://clinicaltables.nlm.nih.gov/apidoc/icd10cm/v3/doc.html

    If the API fails or no result, returns None.
    """
    try:
        resp = requests.get(
            "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search",
            params={
                "sf": "code,name",
                "terms": condition_name,
                "maxList": 1,
            },
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        # data[3] is list of [code, name] pairs
        results = data[3]
        if results:
            code = results[0][0]
            return code
    except Exception:
        # Fail silently and return None
        return None
    return None


def lookup_rxnorm(med_name: str) -> Optional[str]:
    """
    Best-effort RxNorm lookup using the RxNav API.

    Docs: https://rxnav.nlm.nih.gov/REST/rxcui.html

    If the API fails or no result, returns None.
    """
    try:
        resp = requests.get(
            "https://rxnav.nlm.nih.gov/REST/rxcui.json",
            params={"name": med_name},
            timeout=5,
        )
        resp.raise_for_status()
        data = resp.json()
        id_group = data.get("idGroup", {})
        rxcui = id_group.get("rxnormId")
        if rxcui and len(rxcui) > 0:
            return rxcui[0]
    except Exception:
        return None
    return None


# ---------- Core Agent Logic ----------

def _call_llm_for_structure(note: str) -> Tuple[Dict[str, Any], Any]:
    """
    Calls the LLM to turn a raw note into structured JSON matching StructuredNote.

    Returns a Python dict (not a Pydantic model yet).
    """
    system_prompt = (
        "You are an assistant that extracts structured data from clinical notes. "
        "You MUST respond with valid JSON ONLY, with this exact structure:\n\n"
        "{\n"
        '  "patient": {\n'
        '    "name": string or null,\n'
        '    "age": integer or null,\n'
        '    "sex": string or null\n'
        "  },\n"
        '  "conditions": [ {"name": string} ],\n'
        '  "medications": [ {"name": string, "dose": string or null, "route": string or null, "frequency": string or null} ],\n'
        '  "vitals": [ {"type": string, "value": string, "unit": string or null} ],\n'
        '  "labs": [ {"name": string, "value": string, "unit": string or null} ],\n'
        '  "plan": [ {"description": string} ]\n'
        "}\n\n"
        "If some sections are not present in the note, return empty lists or nulls for those fields. "
        "Do NOT include any extra keys or comments."
    )

    user_prompt = f"Clinical note:\n\n{note}\n\nExtract the structured data now."

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()

    # The model might wrap JSON in ```json ... ```; strip that if present.
    if raw.startswith("```"):
        raw = raw.strip("`")
        # remove leading 'json\n' if present
        if raw.lower().startswith("json"):
            raw = raw[4:].lstrip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        # For robustness, wrap in a basic structure if parsing fails
        # In a real system, you'd retry or log this.
        raise RuntimeError(f"Failed to parse LLM JSON: {e}\nRaw content:\n{raw}")

    return data, response.usage


def _enrich_with_codes(struct_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes the raw dict from the LLM and enriches conditions and medications
    with ICD-10 and RxNorm codes.
    """
    # Enrich conditions
    conditions = struct_dict.get("conditions") or []
    for cond in conditions:
        name = cond.get("name")
        if name:
            icd_code = lookup_icd10(name)
            cond["icd10_code"] = icd_code

    # Enrich medications
    meds = struct_dict.get("medications") or []
    for med in meds:
        name = med.get("name")
        if name:
            rx_code = lookup_rxnorm(name)
            med["rxnorm_code"] = rx_code

    struct_dict["conditions"] = conditions
    struct_dict["medications"] = meds
    return struct_dict


def extract_structured_note(note: str) -> Tuple[StructuredNote, Any]:
    """
    Main entry point: given a raw text note, return a StructuredNote Pydantic model.
    """
    struct_dict, usage = _call_llm_for_structure(note)
    struct_dict = _enrich_with_codes(struct_dict)

    # Use Pydantic to validate & coerce into the StructuredNote model
    structured = StructuredNote(**struct_dict)
    return structured, usage
