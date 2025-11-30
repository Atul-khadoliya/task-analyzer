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
