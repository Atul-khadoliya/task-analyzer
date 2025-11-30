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

# 🏗 How the Dependency Graph Is Built

The system constructs two graphs from the task list:

### **forward graph**
task_id → [tasks it depends on]



### **reverse graph**
task_id → [tasks that depend on it]


### Example
If:
1 depends on 2
3 depends on 1



Then:

**forward**
1 → [2]
3 → [1]

lua


**reverse**
2 → [1]
1 → [3]
3 → []



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

# 🔁 Adaptive Learning (Bonus Feature)

When the user marks a suggestion as:

- 👍 Helpful  
- 👎 Not Helpful  

The system:
1. Increases/decreases weights depending on component values  
2. Normalizes weights  
3. Saves updated weights  
4. Next scoring becomes personalized

### Example:
- User consistently prefers urgent tasks → urgency weight increases  
- User prefers low-effort tasks → effort weight goes up  

---

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
