import json
import concurrent.futures
from datetime import datetime, timedelta, date
from typing import Any, Dict, List

from .utils import get_nested_value

BASELINE_CACHE = {}

def evaluate_condition(submission: dict, condition: dict) -> bool:
    field_value = get_nested_value(submission, condition.get('field', ''))
    operator = condition.get('operator')
    guideline_value = condition.get('value')
    
    if operator == "equals":
        return field_value == guideline_value
    elif operator == ">=":
        if isinstance(guideline_value, list):
            lower, upper = guideline_value
            return lower <= field_value <= upper
        return field_value >= guideline_value
    elif operator == "in":
        if isinstance(guideline_value, list):
            return field_value in guideline_value
        return field_value == guideline_value
    elif operator == "contains_at_least":
        if not isinstance(field_value, list):
            return False
        items = guideline_value.get("items", [])
        threshold = guideline_value.get("threshold", 1)
        count = sum(1 for item in items if item in field_value)
        return count >= threshold
    return False

def evaluate_guideline(submission: dict, guideline: dict) -> bool:
    conditions = guideline.get('conditions', {})
    logic = conditions.get('logic', 'all').lower()
    condition_list = conditions.get('conditions', [])
    if not condition_list:
        return False
    results = [evaluate_condition(submission, cond) for cond in condition_list]
    return any(results) if logic == 'any' else all(results)

def evaluate_near_miss(submission: dict, guideline: dict, margin: float = 0.1) -> bool:
    for cond in guideline.get('conditions', {}).get('conditions', []):
        if cond.get('operator') == ">=":
            field_value = get_nested_value(submission, cond.get('field'))
            if field_value is None:
                continue
            if isinstance(cond.get('value'), list):
                lower, _ = cond.get('value')
                if (lower - field_value) / lower <= margin:
                    return True
            else:
                threshold = cond.get('value')
                if (threshold - field_value) / threshold <= margin:
                    return True
    return False

def get_baseline_results(baseline: dict, submissions: List[dict]) -> List[bool]:
    if not baseline or not baseline.get("conditions", {}).get("conditions"):
        return [False] * len(submissions)
    
    baseline_id = baseline.get('id')
    if baseline_id in BASELINE_CACHE:
        return BASELINE_CACHE[baseline_id]
    
    results = [evaluate_guideline(submission, baseline) for submission in submissions]
    BASELINE_CACHE[baseline_id] = results
    return results

def analyze_impact_advanced(submissions: List[dict],
                            baseline: dict,
                            modified: dict) -> Dict[str, Any]:
    total_submissions = len(submissions)
    outcome_changes = 0
    breakdown_by_industry = {}
    breakdown_by_risk_factor = {}
    breakdown_by_company_size = {}
    breakdown_by_location = {}
    time_impact = {"immediate": 0, "gradual": 0}
    financial_impact = 0.0
    near_miss_submissions = []

    immediate_cutoff = datetime.now() - timedelta(days=180)

    baseline_results = get_baseline_results(baseline, submissions)

    def process_submission(index: int, submission: dict) -> Dict[str, Any]:
        baseline_result = baseline_results[index]
        modified_result = evaluate_guideline(submission, modified)
        near_miss = evaluate_near_miss(submission, modified)
        return {
            "baseline": baseline_result,
            "modified": modified_result,
            "near_miss": near_miss,
            "submission": submission
        }

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_submission, idx, sub): idx for idx, sub in enumerate(submissions)}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    for res in results:
        sub = res["submission"]
        if res["baseline"] != res["modified"]:
            outcome_changes += 1

            industry = sub.get("company_data", {}).get("industry", "unknown")
            breakdown_by_industry[industry] = breakdown_by_industry.get(industry, 0) + 1

            for factor in sub.get("risk_profile", {}).get("risk_factors", []):
                breakdown_by_risk_factor[factor] = breakdown_by_risk_factor.get(factor, 0) + 1

            employees = sub.get("company_data", {}).get("employees", 0)
            if employees < 50:
                size = "small"
            elif employees < 250:
                size = "medium"
            else:
                size = "large"
            breakdown_by_company_size[size] = breakdown_by_company_size.get(size, 0) + 1

            location = sub.get("company_data", {}).get("location", "unknown")
            breakdown_by_location[location] = breakdown_by_location.get(location, 0) + 1

            try:
                sub_date = datetime.strptime(sub.get("submission_date"), "%Y-%m-%d")
                if sub_date >= immediate_cutoff:
                    time_impact["immediate"] += 1
                else:
                    time_impact["gradual"] += 1
            except Exception:
                pass

            revenue = sub.get("financials", {}).get("revenue", 0)
            if res["modified"] and not res["baseline"]:
                financial_impact += revenue
            elif res["baseline"] and not res["modified"]:
                financial_impact -= revenue

        if res["near_miss"]:
            near_miss_submissions.append(sub.get("submission_id"))

    outcome_change_percentage = (outcome_changes / total_submissions * 100) if total_submissions else 0.0

    return {
        "total_submissions": total_submissions,
        "outcome_changes": outcome_changes,
        "outcome_change_percentage": outcome_change_percentage,
        "breakdown_by_industry": breakdown_by_industry,
        "breakdown_by_risk_factor": breakdown_by_risk_factor,
        "breakdown_by_company_size": breakdown_by_company_size,
        "breakdown_by_location": breakdown_by_location,
        "time_impact": time_impact,
        "financial_impact": financial_impact,
        "near_miss_submissions": near_miss_submissions,
    }