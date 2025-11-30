import pytest
from datetime import date

from ..scoring import(
    compute_urgency,
    compute_importance,
    compute_effort,
    compute_dependency_score,
    compute_final_score,
    build_dependency_graph,
    detect_cycle,
    count_working_days,
)



# compute_urgency tests


def test_urgency_past_due():
    assert compute_urgency("2024-01-01", "2024-01-05") == 1.0


def test_urgency_same_day():
    today = "2024-01-10"
    assert compute_urgency(today, today) == 1.0


def test_urgency_far_future_low():
    urgency = compute_urgency("2024-02-20", "2024-01-01")
    assert 0 <= urgency < 0.2


def test_urgency_weekend_skip():
    friday = date(2024, 1, 5)
    monday = date(2024, 1, 8)

    working = count_working_days(friday, monday)
    assert working == 1

    urgency = compute_urgency("2024-01-08", "2024-01-05")
    assert 0.9 <= urgency <= 1.0


# compute_importance tests


def test_importance_min_max():
    assert compute_importance(10) == 1.0
    assert compute_importance(1) == 0.0


def test_importance_out_of_range_clamped():
    assert compute_importance(99) == 1.0
    assert compute_importance(-5) == 0.0


# compute_effort tests


def test_effort_zero_hours():
    assert compute_effort(0) == 1.0


def test_effort_max_effort():
    assert compute_effort(8) == 0.0


def test_effort_above_max_clamped():
    assert compute_effort(20) == 0.0


def test_effort_negative_clamped():
    assert compute_effort(-5) == 1.0



# build_dependency_graph tests


def test_build_dependency_graph():
    tasks = [
        {"id": "A", "dependencies": ["B"]},
        {"id": "B", "dependencies": []},
    ]

    graph = build_dependency_graph(tasks)

    assert graph["forward"]["A"] == ["B"]
    assert graph["forward"]["B"] == []
    assert graph["reverse"]["B"] == ["A"]
    assert graph["reverse"]["A"] == []



# detect_cycle tests


def test_detect_cycle_present():
    tasks = [
        {"id": "A", "dependencies": ["B"]},
        {"id": "B", "dependencies": ["A"]},
    ]

    graph = build_dependency_graph(tasks)
    cycle = detect_cycle(graph)

    assert cycle is not None
    assert cycle[0] == cycle[-1]


def test_detect_cycle_none():
    tasks = [
        {"id": "A", "dependencies": ["B"]},
        {"id": "B", "dependencies": []},
    ]

    graph = build_dependency_graph(tasks)
    cycle = detect_cycle(graph)

    assert cycle is None


# dependency score tests


def test_dependency_score():
    tasks = [
        {"id": "A", "dependencies": []},
        {"id": "B", "dependencies": ["A"]},
        {"id": "C", "dependencies": ["A"]},
        {"id": "D", "dependencies": ["A"]},
    ]

    graph = build_dependency_graph(tasks)

    score_A = compute_dependency_score("A", graph)
    score_B = compute_dependency_score("B", graph)

    assert score_A > 0  # A is depended on by many
    assert score_B == 0



# final score tests


def test_final_score_respects_weights():
    task = {
        "id": "A",
        "due_date": "2024-01-15",
        "importance": 9,
        "estimated_hours": 2,
        "dependencies": []
    }

    graph = build_dependency_graph([task])

    weights = {
        "urgency": 1.0,
        "importance": 0.0,
        "effort": 0.0,
        "dependency": 0.0
    }

    result = compute_final_score(task, "2024-01-10", graph, weights)

    assert result["score"] == result["components"]["urgency"]


# working day counter tests

def test_working_day_count():
    d1 = date(2024, 1, 1)  # Monday
    d2 = date(2024, 1, 3)  # Wednesday

    assert count_working_days(d1, d2) == 2





# 1. Test urgency weekend skip + horizon effect

def test_urgency_horizon_behavior():
    # Due far in future, urgency should be near zero
    urgency = compute_urgency("2025-06-01", "2025-01-01", horizon=30)
    assert 0.0 <= urgency <= 0.2



# 2. Test missing fields (importance defaults, hours defaults)

def test_missing_fields_default_behavior():
    task = {"id": 1, "due_date": "2025-01-20"}  # missing importance + hours
    graph = build_dependency_graph([task])
    weights = {"urgency": 1, "importance": 1, "effort": 1, "dependency": 1}

    result = compute_final_score(task, "2025-01-10", graph, weights)
    comps = result["components"]

    assert comps["importance"] == (5 - 1) / 9     # default importance = 5
    assert comps["effort"] == 1 - (4 / 8)         # default hours = 4



# 3. Test invalid importance gets clamped

def test_importance_clamping():
    assert compute_importance(50) == 1.0
    assert compute_importance(-10) == 0.0



# 4. Test effort edge behavior (negative, >8)

def test_effort_edge_cases():
    assert compute_effort(-5) == 1.0   # negative → treated as 0
    assert compute_effort(20) == 0.0   # >8 → clamped to 8



# 5. Test heavy dependency network (A blocks all)

def test_dependency_score_heavy_network():
    tasks = [
        {"id": 1, "dependencies": []},
        {"id": 2, "dependencies": [1]},
        {"id": 3, "dependencies": [1]},
        {"id": 4, "dependencies": [1]},
    ]
    graph = build_dependency_graph(tasks)

    score_A = compute_dependency_score(1, graph)
    score_B = compute_dependency_score(2, graph)

    assert score_A == 1.0   # A is the max blocker
    assert score_B == 0.0   # B blocks no other tasks



# 6. Test deep dependency chain (A → B → C → D)

def test_dependency_chain_depth():
    tasks = [
        {"id": 1, "dependencies": []},
        {"id": 2, "dependencies": [1]},
        {"id": 3, "dependencies": [2]},
        {"id": 4, "dependencies": [3]},
    ]
    graph = build_dependency_graph(tasks)

    # Direct dependents only matter
    assert compute_dependency_score(1, graph) == 1.0  # only task with dependents
    assert compute_dependency_score(4, graph) == 0.0



# 7. Test cycle detection (A → B → A)

def test_cycle_detection_simple():
    tasks = [
        {"id": "A", "dependencies": ["B"]},
        {"id": "B", "dependencies": ["A"]},
    ]
    graph = build_dependency_graph(tasks)
    cycle = detect_cycle(graph)

    assert cycle is not None
    assert cycle[0] == cycle[-1]



# 8. Test final score respects single weight dominance

def test_final_score_single_weight_priority():
    task = {
        "id": "X",
        "due_date": "2025-01-15",
        "importance": 10,
        "estimated_hours": 1,
        "dependencies": []
    }
    graph = build_dependency_graph([task])

    # Only importance matters
    weights = {"urgency": 0, "importance": 1, "effort": 0, "dependency": 0}

    result = compute_final_score(task, "2025-01-01", graph, weights)

    assert result["score"] == result["components"]["importance"]



# 9. Test urgency: due today vs due far future

def test_urgency_today_vs_future():
    today = "2025-01-10"
    urgent = compute_urgency(today, today)
    future = compute_urgency("2025-12-31", today)

    assert urgent == 1.0
    assert future < 0.2



# 10. Test tie-breaking: equal scores sorted by score only (logic leaves ties stable)

def test_equal_score_behavior():
    tasks = [
        {"id": 1, "due_date": "2025-01-10", "importance": 5, "estimated_hours": 4, "dependencies": []},
        {"id": 2, "due_date": "2025-01-10", "importance": 5, "estimated_hours": 4, "dependencies": []},
        {"id": 3, "due_date": "2025-01-10", "importance": 5, "estimated_hours": 4, "dependencies": []},
    ]

    graph = build_dependency_graph(tasks)
    weights = {"urgency": 1, "importance": 1, "effort": 1, "dependency": 1}

    scores = [compute_final_score(t, "2025-01-10", graph, weights)["score"] for t in tasks]

    assert scores[0] == scores[1] == scores[2]
