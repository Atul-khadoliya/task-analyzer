# Smart Task Analyzer

Smart Task Analyzer is a full-stack intelligent task-prioritization system built using **Django REST Framework** and **Vanilla JavaScript**.  
It analyzes tasks, computes priority scores, visualizes dependencies, draws an Eisenhower Matrix, learns from user feedback, includes weekend-aware urgency, and features complete unit tests.

All bonus tasks are fully implemented.

---

## 🚀 Setup Instructions

### 1. Clone the repository
git clone https://github.com/Atul-khadoliya/task-analyzer

cd task-analyzer



### 2. Backend setup

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

cd backend


### 3. Run migrations

python manage.py migrate


### 4. Start backend
python manage.py runserver



### 5. Start frontend  
Open `frontend/index.html` using **Live Server**.

---

## 🔗 API Overview

### **POST `/api/tasks/analyze/`**
Takes a list of tasks and returns:
- Computed priority score (0–1)
- Breakdown of urgency, importance, effort, dependency
- Human-readable explanation
- Dependency graph structure
- Cycle detection (if any)
- Sorted list of tasks by priority

### **GET `/api/tasks/suggest/`**
Returns the **top 3 tasks** the user should work on today, with explanations.

---

# 🧠 How the Algorithm Works

The system assigns every task a **priority score between 0 and 1** using **four components**:

---

# 1️⃣ Urgency (deadline proximity)

### ✔ **Data Used**
- `due_date` (deadline)
- `today` (current date from API)

### ✔ **How It Works**
- If past due → `urgency = 1.0`
- If due today → `1.0`
- Fewer working days left → higher urgency
- Weekends are ignored (Mon–Fri only)
- Horizon (default 30 days) limits long-term deadlines

### **Formula**
urgency = 1 - (working_days_left / horizon)



### **Examples**
- Due tomorrow → ~0.96  
- Due in 20 working days → 0.33  
- Due in 100 days → 0.0  

---

# 2️⃣ Importance (1–10 rating)

### ✔ **Data Used**
- `importance` (1–10) provided by user

### ✔ **How It Works**
Importance is normalized to a 0–1 scale.

### **Formula**
importance = (importance_raw - 1) / 9



### **Examples**
- Importance 10 → 1.0  
- Importance 5 → 0.44  
- Importance 1 → 0.0  

---

# 3️⃣ Effort (estimated hours)

### ✔ **Data Used**
- `estimated_hours`

### ✔ **How It Works**
- Smaller tasks → higher score  
- Large tasks → lower score  
- Hours capped at 8

### **Formula**
effort = 1 - (min(hours, 8) / 8)



### **Examples**
- 1 hour → 0.875  
- 4 hours → 0.5  
- 10 hours → 0.0  

---

# 4️⃣ Dependency Impact

### ✔ **Data Used**
- Task ID  
- Automatically built **dependency graph** (reverse graph)

### ✔ **What It Means**
> “How many tasks get unblocked if I do this task?”

More direct dependents → higher score.

### **Formula**
dependency = (# of direct dependents) / (max dependents in graph)


### **Examples**
- Blocks 5 tasks → 1.0  
- Blocks 2 tasks → 0.4  
- Blocks none → 0.0  

---

## 🔗 Dependency Graph Visualization

The system builds a directed graph to understand how tasks depend on one another and to visually show which tasks block others.

### Data Used

Each input task includes:

    {
        "id": int,
        "dependencies": [list of task IDs]
    }

From this, two graphs are built:

    forward[id]  = tasks this task depends on
    reverse[id]  = tasks that depend on this task

---

### Graph Construction

Pseudocode:

    initialize forward and reverse maps for all task IDs

    for each task in tasks:
        forward[task.id] = task.dependencies
        for dep in task.dependencies:
            reverse[dep].append(task.id)

Example:

    Task 1 depends on [2]
    Task 3 depends on [1]

Produces:

    forward:
        1 → [2]
        2 → []
        3 → [1]

    reverse:
        1 → [3]
        2 → [1]
        3 → []

---

### How the Visualization Uses This Data

The frontend receives the graph and renders:

- arrows showing dependency direction
- highlighting of tasks that unblock others
- visual warning if a cycle is detected
- task nodes sized or colored based on dependency score

---

### Why This Matters

- Users can see bottlenecks (tasks many others depend on)
- Helps identify the “best leverage points” to work on first
- Makes the system more intuitive and transparent

### What it's used for:


- Dependency score  
- Cycle detection  
- Eisenhower matrix insights  
- Explanations like “Blocks many tasks”  

---

# 🔄 Cycle Detection

The system finds loops such as:
A → B → C → A



If detected, response includes:
"cycle_detected": true,
"cycle": [A, B, C, A]


---

# 🧮 Final Score Formula

All components are combined using weights:

score =
(urgency * w_urgency) +
(importance * w_importance) +
(effort * w_effort) +
(dependency * w_dependency)



Each score is returned with:
- Component breakdown
- Human-readable explanation

---

# 🎚 Default Weights & Learning System

| Component   | Weight |
|------------|--------|
| Urgency    | 0.4 |
| Importance | 0.3 |
| Effort     | 0.2 |
| Dependency | 0.1 |

Weights are stored in a **singleton model**.

### ✔ Why these weights?
- Urgency matters most (deadlines)
- Importance next
- Effort encourages quick wins
- Dependency is situational but helpful

---

## 🔁 Adaptive Learning (Bonus Feature)

When the user marks a suggested task as “Helpful” or “Not Helpful”, the system adjusts future scoring based on the actual component values of that task.

### Data Used

components = {

    "urgency": <float 0–1>,
    
    "importance": <float 0–1>,
    
    "effort": <float 0–1>,
    
    "dependency": <float 0–1>
}

weights = {

    "urgency": <float>,
    
    "importance": <float>,
    
    "effort": <float>,
    
    "dependency": <float>
}

These two data structures drive the learning update.

---

### How the System Reacts

#### Helpful (👍):
- Increase weights of components that were strong in the suggested task.
- Example:
    - If urgency = 0.92 and effort = 0.80, both weights receive a boost.

#### Not Helpful (👎):
- Decrease weights of components that were strong in the suggested task.
- Example:
    - If urgency is high but the user marks the task as not helpful, urgency weight decreases.

---

### Weight Adjustment Logic (Core Formula)

For each component:

    new_weight = old_weight ± (component_value * learning_rate)

- Use “+” for Helpful
- Use “–” for Not Helpful
- learning_rate is small (e.g., 0.05)

Components with higher values have a stronger effect on weight updates.

---

### Normalization (Required Step)

After modification, weights may no longer sum to 1.  
We normalize them:

    total = sum(all_weights)
    weight[x] = weight[x] / total

Example:
    Temporary weights:
        urgency:    0.45
        importance: 0.30
        effort:     0.23
        dependency: 0.12

    After normalization:
        urgency:    0.41
        importance: 0.27
        effort:     0.21
        dependency: 0.11

---

### Persistence

The updated weights are saved into a **singleton model** in the database:

- Updates persist across runs
- All future scoring uses updated weights
- System becomes personalized over time

---

### Personalization Effects

- If user prefers urgent tasks → urgency weight increases
- If user prefers quick wins → effort weight increases
- If user likes high-impact tasks → importance weight increases
- If user prefers tasks that unblock others → dependency weight increases

Over repeated feedback, the system becomes a personalized task recommender.

# 🧩 Bonus Features Implemented
- ✔ Dependency Graph Visualization  
- ✔ Eisenhower Matrix  
- ✔ Weekend-Aware Urgency  
- ✔ Adaptive Learning System  
- ✔ Cycle Detection  
- ✔ Persistent Weight Model  
- ✔ Full Unit Tests  

---

## ⏱ Time Breakdown

| Feature | Time |
|--------|------|
| Backend API | 1.5 hours |
| Scoring Algorithm | 1 hour |
| Frontend UI + Styling | 1 hour |
| Dependency Graph | 45 min |
| Eisenhower Matrix | 45 min |
| Date Intelligence | 30 min |
| Learning System | 1 hour |
| Unit Tests | 45 min |
| Debugging + Polishing | 1 hour |
| **Total** | **8–9 hours** |

---

## 🔮 Future Improvements

- React + D3.js interactive UI  
- Holiday-aware urgency  
- Drag-and-drop dependency editing  
- User accounts with personalized profiles  
- ML-based task predictions  
- Gantt + Kanban views  
- Multi-day planning  
