from datetime import date
from dateutil.parser import parse as parse_date


def compute_urgency(due_date, today):
    """
    Returns urgency score (0 to 1).
    Placeholder: returns 0.0 for now.
    """
    return 0.0

def compute_importance(importance):
    """
    Normalize importance (1-10 scale).
    Placeholder: returns 0.0 for now.
    """
    return 0.0

def compute_effort(hours):
    """
    Lower effort = higher score.
    Placeholder: returns 0.0 for now.
    """
    return 0.0

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
    """
    Build a dependency graph and return it.
    Placeholder: returns empty graph.
    """
    return {}
