from datetime import datetime
from dateutil.parser import parse as parse_date


def compute_urgency(due_date, today,horizon=30):
     if not due_date:
        return 0.1  # missing due date → low urgency

    # convert strings to date objects
     if isinstance(due_date, str):
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
     if isinstance(today, str):
        today = datetime.strptime(today, "%Y-%m-%d").date()

     days_left = (due_date - today).days

    # past due → maximum urgency
     if days_left < 0:
        return 1.0

    # normalize relative to horizon
     urgency = 1 - (days_left / horizon)

    # clamp between 0 and 1
     urgency = max(0.0, min(1.0, urgency))
     return urgency

def compute_importance(importance):
      if importance is None:
        importance = 5

    # Ensure valid range
      importance = max(1, min(10, importance))

    # normalize: convert 1–10 range to 0–1
      return (importance - 1) / 9
    

def compute_effort(hours,max_effort=8):
    if hours is None:
        hours = 4  # default medium effort

    # ensure hours is non-negative
    hours = max(0, hours)

    # cap hours at max_effort
    effective = min(hours, max_effort)

    # invert (0 hours = 1.0, max_effort = 0.0)
    score = 1 - (effective / max_effort)

    # clamp to 0–1
    return max(0.0, min(1.0, score))

def compute_dependency_score(task_id, dependency_graph):
    """
    Score based on how many tasks depend on this task.
    Placeholder: returns 0.0 for now.
    """
    return 0.0


# Final score combining function


def compute_final_score(task, today, dependency_graph, weights):
    """
    Combines all factors into a final priority score.
    Placeholder returns {
        'score': 0.0,
        'components': {}
    }
    """
    return {
        "score": 0.0,
        "components": {
            "urgency": 0.0,
            "importance": 0.0,
            "effort": 0.0,
            "dependency": 0.0
        }
    }


# Dependency graph helper (placeholder)


def build_dependency_graph(tasks):
    forward = {}
    reverse = {}

    # initialize all task ids
    for task in tasks:
        tid = task["id"]
        forward[tid] = []
        reverse[tid] = []

    # fill edges
    for task in tasks:
        tid = task["id"]
        deps = task.get("dependencies", [])

        forward[tid] = deps

        for dep in deps:
            if dep in reverse:
                reverse[dep].append(tid)

    return {
        "forward": forward,
        "reverse": reverse
    }
