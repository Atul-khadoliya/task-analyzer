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
    reverse = dependency_graph["reverse"]

    # count direct dependents
    dependents = reverse.get(task_id, [])
    count = len(dependents)

    # find global max dependents for normalization
    all_counts = [len(reverse[tid]) for tid in reverse]
    max_count = max(all_counts) if all_counts else 1

    if max_count == 0:
        return 0.0

    return count / max_count


# Final score combining function


def compute_final_score(task, today, dependency_graph, weights):
     # Extract components
    U = compute_urgency(task.get("due_date"), today)
    I = compute_importance(task.get("importance"))
    E = compute_effort(task.get("estimated_hours"))
    D = compute_dependency_score(task["id"], dependency_graph)

    # Weighted sum
    score = (
        weights["urgency"] * U +
        weights["importance"] * I +
        weights["effort"] * E +
        weights["dependency"] * D
    )

    # clamp to [0, 1]
    score = max(0.0, min(1.0, score))

    return {
        "score": score,
        "components": {
            "urgency": U,
            "importance": I,
            "effort": E,
            "dependency": D
        }
    }


# Dependency graph helper 


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


def detect_cycle(dependency_graph):
    graph = dependency_graph["forward"]

    visited = set()
    in_stack = set()
    parent = {}

    def dfs(node):
        visited.add(node)
        in_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                parent[neighbor] = node
                result = dfs(neighbor)
                if result:
                    return result
            elif neighbor in in_stack:
                # cycle found → reconstruct path
                cycle = [neighbor]
                cur = node
                while cur != neighbor:
                    cycle.append(cur)
                    cur = parent[cur]
                cycle.append(neighbor)
                cycle.reverse()
                return cycle

        in_stack.remove(node)
        return None

    # check all nodes
    for node in graph:
        if node not in visited:
            result = dfs(node)
            if result:
                return result

    return None




def build_explanation(components):
    """
    Build a human-readable explanation for why a task was prioritized.
    """

    parts = []

    # Urgency explanation
    if components['urgency'] == 1.0:
        parts.append("Past due (maximum urgency)")
    elif components['urgency'] > 0.7:
        parts.append("Very urgent")
    elif components['urgency'] > 0.4:
        parts.append("Moderately urgent")

    # Importance explanation
    if components['importance'] > 0.8:
        parts.append("Highly important")
    elif components['importance'] > 0.5:
        parts.append("Important task")

    # Effort explanation
    if components['effort'] > 0.8:
        parts.append("Quick win (low effort)")
    elif components['effort'] < 0.2:
        parts.append("High-effort task")

    # Dependency explanation
    if components['dependency'] > 0.7:
        parts.append("Blocks many other tasks")
    elif components['dependency'] > 0.0:
        parts.append("Blocks some tasks")

    # If nothing stands out
    if not parts:
        return "No strong priority factors."

    return ", ".join(parts) + "."
