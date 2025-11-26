from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import TaskSerializer
from scoring import compute_final_score, build_dependency_graph


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

    # return the placeholder scoring results
    return Response({"tasks": scored_tasks})



def suggest_placeholder(request):
    return Response({"status": "ok", "message": "suggest endpoint placeholder"})