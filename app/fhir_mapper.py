# app/fhir_mapper.py

"""
Mapping from our StructuredNote into simplified FHIR-like JSON.

FHIR resources:
- Patient
- Condition(s)
- MedicationRequest (for each medication)
- Observation (for vitals and labs)
- CarePlan (summarizing plan items)
"""

from typing import Dict, Any, List

from .schemas import StructuredNote


def structured_to_fhir(structured: StructuredNote) -> Dict[str, Any]:
    resources: List[Dict[str, Any]] = []

    # -------------------
    # Patient
    # -------------------
    patient_id = "patient-1"
    patient = {
        "resourceType": "Patient",
        "id": patient_id,
    }

    if structured.patient:
        name_text = structured.patient.name
        if name_text:
            patient["name"] = [{"text": name_text}]

        if structured.patient.sex:
            sex_lower = structured.patient.sex.lower()
            if sex_lower in {"male", "female", "other", "unknown"}:
                patient["gender"] = sex_lower
            else:
                patient["gender"] = "unknown"

        if structured.patient.age:
            # We don't have birthDate, so we use an extension for age
            patient["extension"] = [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                    "valueInteger": structured.patient.age
                }
            ]

    resources.append(patient)

    # -------------------
    # Conditions -> Condition
    # -------------------
    for idx, cond in enumerate(structured.conditions, start=1):
        cond_id = f"condition-{idx}"
        condition_resource: Dict[str, Any] = {
            "resourceType": "Condition",
            "id": cond_id,
            "subject": {"reference": f"Patient/{patient_id}"},
            "clinicalStatus": {"text": "active"},
            "verificationStatus": {"text": "confirmed"},
            "code": {
                "text": cond.name,
            },
        }

        if cond.icd10_code:
            condition_resource["code"]["coding"] = [
                {
                    "system": "http://hl7.org/fhir/sid/icd-10-cm",
                    "code": cond.icd10_code,
                }
            ]

        resources.append(condition_resource)

    # -------------------
    # Medications -> MedicationRequest
    # -------------------
    for idx, med in enumerate(structured.medications, start=1):
        med_id = f"medreq-{idx}"

        med_text_parts = []
        if med.dose:
            med_text_parts.append(med.dose)
        if med.frequency:
            med_text_parts.append(med.frequency)
        dosage_text = " ".join(med_text_parts) if med_text_parts else None

        med_resource: Dict[str, Any] = {
            "resourceType": "MedicationRequest",
            "id": med_id,
            "subject": {"reference": f"Patient/{patient_id}"},
            "status": "active",
            "intent": "order",
            "medicationCodeableConcept": {
                "text": med.name,
            },
        }

        if med.rxnorm_code:
            med_resource["medicationCodeableConcept"]["coding"] = [
                {
                    "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                    "code": med.rxnorm_code,
                }
            ]

        if dosage_text:
            med_resource["dosageInstruction"] = [
                {
                    "text": dosage_text
                }
            ]

        resources.append(med_resource)

    # -------------------
    # Vitals & Labs -> Observation
    # -------------------
    obs_counter = 1

    # Vitals
    for vital in structured.vitals:
        obs_id = f"observation-vital-{obs_counter}"
        obs_counter += 1

        display_text = vital.type
        value_text = vital.value
        if vital.unit:
            value_text = f"{value_text} {vital.unit}"

        obs_resource: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "subject": {"reference": f"Patient/{patient_id}"},
            "code": {
                "text": display_text
            },
            # For simplicity, we store as valueString; in real FHIR you might parse into valueQuantity
            "valueString": value_text,
        }

        resources.append(obs_resource)

    # Labs
    for lab in structured.labs:
        obs_id = f"observation-lab-{obs_counter}"
        obs_counter += 1

        display_text = lab.name
        value_text = lab.value
        if lab.unit:
            value_text = f"{value_text} {lab.unit}"

        obs_resource: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": obs_id,
            "status": "final",
            "subject": {"reference": f"Patient/{patient_id}"},
            "code": {
                "text": display_text
            },
            "valueString": value_text,
        }

        resources.append(obs_resource)

    # -------------------
    # Plan -> CarePlan
    # -------------------
    if structured.plan:
        careplan_id = "careplan-1"
        # Join plan items into a narrative for simplicity
        plan_descriptions = [item.description for item in structured.plan if item.description]
        narrative_text = " | ".join(plan_descriptions) if plan_descriptions else None

        careplan_resource: Dict[str, Any] = {
            "resourceType": "CarePlan",
            "id": careplan_id,
            "subject": {"reference": f"Patient/{patient_id}"},
            "status": "active",
            "intent": "plan",
        }

        if narrative_text:
            careplan_resource["description"] = narrative_text

        resources.append(careplan_resource)

    # -------------------
    # Wrap everything in a Bundle
    # -------------------
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [{"resource": r} for r in resources],
    }

    return bundle
