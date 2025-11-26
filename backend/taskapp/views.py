from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .models import AnalyzedTask
import uuid

from scoring import (
    compute_final_score,
    build_dependency_graph,
    detect_cycle
)


@api_view(['POST'])
def analyze_placeholder(request):
    """
    Step 1: Validate input structure using TaskSerializer
    Step 2: Build dependency graph (currently placeholder)
    Step 3: Compute dummy scores via scoring.py placeholders
    """

    tasks_data = request.data.get("tasks", [])

    # validate tasks one by one
    serializer = TaskSerializer(data=tasks_data, many=True)
    serializer.is_valid(raise_exception=True)

    validated_tasks = serializer.validated_data

    # build dependency graph (empty for now)
    dep_graph = build_dependency_graph(validated_tasks)

    cycle = detect_cycle(dep_graph)
    if cycle:
        return Response(
            {"error": "Circular dependency detected", "cycle": cycle},
            status=status.HTTP_400_BAD_REQUEST
        )

    # default weights until implementing scoring
    weights = {
        "urgency": 0.4,
        "importance": 0.3,
        "effort": 0.2,
        "dependency": 0.1
    }

    today = request.data.get("today", None)

    # compute score for each task
    scored_tasks = []
    for task in validated_tasks:
        result = compute_final_score(task, today, dep_graph, weights)
        scored_tasks.append({
            "id": task.get("id"),
            "title": task.get("title"),
            "score": result["score"],
            "components": result["components"]
        })

        # Create new analysis session
    session_id = uuid.uuid4()

# Save tasks in database
    for st in scored_tasks:
        AnalyzedTask.objects.create(
        session_id=session_id,
        task_id=st["id"],
        title=st["title"],
        score=st["score"],
        urgency=st["components"]["urgency"],
        importance=st["components"]["importance"],
        effort=st["components"]["effort"],
        dependency=st["components"]["dependency"]
    )


    # return the placeholder scoring results
    return Response({
    "session_id": session_id,
    "tasks": scored_tasks
})



def suggest_placeholder(request):
    return Response({"status": "ok", "message": "suggest endpoint placeholder"})