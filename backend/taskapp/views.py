from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .models import AnalyzedTask
import uuid

from scoring import (
    build_explanation,
    compute_final_score,
    build_dependency_graph,
    detect_cycle
)


@api_view(['POST'])
def analyze_placeholder(request):
    """
    Step 1: Validate input structure using TaskSerializer
    Step 2: Build dependency graph
    Step 3: Compute scores and store in DB
    """

    tasks_data = request.data.get("tasks", [])

    # Validate tasks
    serializer = TaskSerializer(data=tasks_data, many=True)
    serializer.is_valid(raise_exception=True)
    validated_tasks = serializer.validated_data

    # Build dependency graph
    dep_graph = build_dependency_graph(validated_tasks)

    # Detect circular dependency
    cycle = detect_cycle(dep_graph)
    if cycle:
        return Response(
            {"error": "Circular dependency detected", "cycle": cycle},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Determine strategy (default = smart)
    strategy = (request.data.get("strategy") or "smart").lower()

    # Weight distributions based on strategy
    WEIGHT_PROFILES = {
        "smart": {       # Balanced
            "urgency": 0.4,
            "importance": 0.3,
            "effort": 0.2,
            "dependency": 0.1
        },
        "fast": {        # Fastest Wins — effort only
            "urgency": 0.0,
            "importance": 0.0,
            "effort": 1.0,
            "dependency": 0.0
        },
        "impact": {      # High Impact — importance only
            "urgency": 0.0,
            "importance": 1.0,
            "effort": 0.0,
            "dependency": 0.0
        },
        "deadline": {    # Deadline Driven — urgency only
            "urgency": 1.0,
            "importance": 0.0,
            "effort": 0.0,
            "dependency": 0.0
        }
    }

    weights = WEIGHT_PROFILES.get(strategy, WEIGHT_PROFILES["smart"])
    


    today = request.data.get("today", None)

    # Compute scores
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


    # THIS IS THE CORRECT PLACE TO CREATE SESSION
    session_id = uuid.uuid4()

    # Save tasks for this session in DB
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

    # Return results
    return Response({
        "session_id": session_id,
        "tasks": scored_tasks
    })




@api_view(['GET'])
def suggest_placeholder(request):
    """
    Return top 3 tasks from the latest analysis session.
    """

    # 1. Find latest session
    latest_task = AnalyzedTask.objects.order_by('-created_at').first()

    if not latest_task:
        return Response(
            {"error": "No analyzed tasks found. Run /api/tasks/analyze/ first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    latest_session_id = latest_task.session_id

    # 2. Fetch all tasks from this session
    tasks = AnalyzedTask.objects.filter(session_id=latest_session_id).order_by('-score')

    # 3. Take top 3
    top_three = tasks[:3]

    # 4. Build suggestions list
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
