from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import uuid

from .serializers import TaskSerializer
from .models import AnalyzedTask, GlobalSettings, Feedback

from scoring import (
    build_explanation,
    compute_final_score,
    build_dependency_graph,
    detect_cycle
)



# ANALYZE ENDPOINT


@api_view(['POST'])
def analyze_placeholder(request):
    """
    Analyze tasks, compute scores using either strategy weights
    or learned weights, and save the results in the DB.
    """

    tasks_data = request.data.get("tasks", [])

    # Validate structure
    serializer = TaskSerializer(data=tasks_data, many=True)
    serializer.is_valid(raise_exception=True)
    validated_tasks = serializer.validated_data

    # Build dependency graph
    dep_graph = build_dependency_graph(validated_tasks)

    # Check circular
    cycle = detect_cycle(dep_graph)
    if cycle:
        return Response(
            {"error": "Circular dependency detected", "cycle": cycle},
            status=status.HTTP_400_BAD_REQUEST
        )

    # User-selected strategy
    strategy = (request.data.get("strategy") or "smart").lower()

    # Static profiles
    WEIGHT_PROFILES = {
        "smart":     {"urgency": 0.4, "importance": 0.3, "effort": 0.2, "dependency": 0.1},
        "fast":      {"urgency": 0.0, "importance": 0.0, "effort": 1.0, "dependency": 0.0},
        "impact":    {"urgency": 0.0, "importance": 1.0, "effort": 0.0, "dependency": 0.0},
        "deadline":  {"urgency": 1.0, "importance": 0.0, "effort": 0.0, "dependency": 0.0},
    }

    # Resolve weights (learned only for "smart")
    if strategy in ["fast", "impact", "deadline"]:
        weights = WEIGHT_PROFILES[strategy]
    else:
        settings = GlobalSettings.objects.first()

        if settings is None:
            settings = GlobalSettings.objects.create(
                weight_urgency=0.4,
                weight_importance=0.3,
                weight_effort=0.2,
                weight_dependency=0.1
            )

        weights = {
            "urgency": settings.weight_urgency,
            "importance": settings.weight_importance,
            "effort": settings.weight_effort,
            "dependency": settings.weight_dependency
        }

    today = request.data.get("today")

    # Score tasks
    scored_tasks = []
    for task in validated_tasks:
        result = compute_final_score(task, today, dep_graph, weights)
        explanation = build_explanation(result["components"])

        scored_tasks.append({
            "id": task.get("id"),
            "title": task.get("title"),
            "due_date": task.get("due_date"),
            "estimated_hours": task.get("estimated_hours"),
            "importance": task.get("importance"),
            "dependencies": task.get("dependencies"),
            "score": result["score"],
            "components": result["components"],
            "explanation": explanation
        })

    # Create session
    session_id = uuid.uuid4()

    # Save results in DB
    for st in scored_tasks:
        AnalyzedTask.objects.create(
            session_id=session_id,
            task_id=st["id"],
            title=st["title"],
            score=st["score"],
            urgency=st["components"]["urgency"],
            importance=st["components"]["importance"],
            effort=st["components"]["effort"],
            dependency=st["components"]["dependency"],
            due_date=st.get("due_date")
        )

    return Response({
        "session_id": session_id,
        "tasks": scored_tasks
    })



# SUGGEST ENDPOINT


@api_view(['GET'])
def suggest_placeholder(request):
    """
    Return top 3 tasks from latest session.
    """

    latest_task = AnalyzedTask.objects.order_by('-created_at').first()
    if not latest_task:
        return Response(
            {"error": "No analyzed tasks found. Run /api/tasks/analyze/ first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    latest_session_id = latest_task.session_id

    top_three = (
        AnalyzedTask.objects
        .filter(session_id=latest_session_id)
        .order_by('-score')[:3]
    )

    suggestions = []
    for t in top_three:
        components = {
            "urgency": t.urgency,
            "importance": t.importance,
            "effort": t.effort,
            "dependency": t.dependency
        }

        suggestions.append({
            "id": t.task_id,
            "title": t.title,
            "score": t.score,
            "due_date": t.due_date,
            "why": build_explanation(components)
        })

    return Response({
        "session_id": str(latest_session_id),
        "suggestions": suggestions
    })



# FEEDBACK ENDPOINT (LEARNING SYSTEM)


@api_view(['POST'])
def submit_feedback(request):
    """
    User marks a suggestion as helpful or not.
    We update global weights accordingly.
    """

    task_id = request.data.get("task_id")
    was_helpful = request.data.get("was_helpful")

    if task_id is None or was_helpful is None:
        return Response(
            {"error": "task_id and was_helpful are required"},
            status=400
        )

    # Get the latest analyzed values for this task
    analyzed = AnalyzedTask.objects.filter(task_id=task_id).order_by('-created_at').first()
    if not analyzed:
        return Response({"error": "Task not found in analysis history"}, status=404)

    # Save feedback
    Feedback.objects.create(
        task_id=task_id,
        was_helpful=bool(was_helpful)
    )

    # Get or init weight settings
    settings = GlobalSettings.objects.first()
    if not settings:
        settings = GlobalSettings.objects.create(
            weight_urgency=0.4,
            weight_importance=0.3,
            weight_effort=0.2,
            weight_dependency=0.1
        )

    lr = 0.05  # learning rate

    # Extract actual component scores
    U = analyzed.urgency
    I = analyzed.importance
    E = analyzed.effort
    D = analyzed.dependency

    # Update weights
    if was_helpful:
        settings.weight_urgency += lr * U
        settings.weight_importance += lr * I
        settings.weight_effort += lr * E
        settings.weight_dependency += lr * D
    else:
        settings.weight_urgency -= lr * U
        settings.weight_importance -= lr * I
        settings.weight_effort -= lr * E
        settings.weight_dependency -= lr * D

    # Normalize to sum to 1
    S = (
        settings.weight_urgency +
        settings.weight_importance +
        settings.weight_effort +
        settings.weight_dependency
    )

    settings.weight_urgency /= S
    settings.weight_importance /= S
    settings.weight_effort /= S
    settings.weight_dependency /= S

    settings.save()

    return Response({
        "message": "Feedback saved. Weights updated.",
        "weights": {
            "urgency": settings.weight_urgency,
            "importance": settings.weight_importance,
            "effort": settings.weight_effort,
            "dependency": settings.weight_dependency
        }
    })
