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


cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


### 3. Run migrations


python manage.py migrate


### 4. Start backend


python manage.py runserver


### 5. Start frontend  
Open `frontend/index.html` using **Live Server**.

---

## 🧠 How the Algorithm Works

The system assigns every task a **priority score from 0 to 1** using four weighted factors:

### **1. Urgency (deadline proximity)**
- Uses **working days only** (skips Saturday/Sunday).
- Closer deadlines → higher urgency.
- Past-due tasks automatically get **urgency = 1.0**.

### **2. Importance (1–10 rating)**
Normalized to a 0–1 scale.

### **3. Effort (estimated hours)**
Effort is inverted — tasks requiring fewer hours score higher.
This encourages “quick wins” and productivity momentum.

### **4. Dependency Impact**
If a task unblocks many others, it gets a higher dependency score.

### **Final Score Formula**


score =
(urgency * w_urgency) +
(importance * w_importance) +
(effort * w_effort) +
(dependency * w_dependency)

Each component is returned along with a human-readable explanation.

---

## 🎚 Default Weights & Learning System

The default weights for the **Smart Balance** strategy are:

| Component   | Weight |
|------------|--------|
| Urgency    | 0.4    |
| Importance | 0.3    |
| Effort     | 0.2    |
| Dependency | 0.1    |

These weights are stored in a singleton model so they persist across sessions.

### Why these weights?

### ✔ **Urgency = 0.4 (Highest)**  
Deadlines have immediate consequences. The system must always prioritize time-critical tasks.

### ✔ **Importance = 0.3**  
Importance matters, but not at the cost of missing deadlines.

### ✔ **Effort = 0.2**  
Low-effort tasks boost productivity momentum, but shouldn’t outrank important or urgent tasks.

### ✔ **Dependency = 0.1**  
Useful but situational; a small weight ensures it influences the ranking without dominating it.

---

## 🔁 Adaptive Learning (Bonus Feature)

When the user clicks **“Helpful”** or **“Not Helpful”**, the system adjusts weights:

- If helpful → increase weights for factors that were high for that task.
- If not helpful → decrease them.

After adjustments, weights are normalized so they always sum to 1.

Over time, the system adapts to the user's real behavior:
- Prefers urgent tasks → urgency weight grows  
- Prefers high-impact tasks → importance weight grows  
- Prefers quick wins → effort weight grows  
- Prefers unblockers → dependency weight grows  

This makes the scoring algorithm **personalized**.

---

## 🧩 Bonus Features Implemented

All major bonus challenges completed:

- ✔ Dependency Graph Visualization  
- ✔ Eisenhower Matrix  
- ✔ Weekend-Aware Date Intelligence  
- ✔ Learning System with persistent weights  
- ✔ Full Unit Tests for scoring logic  

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

With more time, I would add:

- Modern interactive UI (React + D3.js)
- Global holiday calendars in urgency calculation
- Drag-and-drop dependency editing
- User accounts with personalized profiles
- Machine-learned priority predictions
- Kanban + Gantt visualizations
- Multi-day focus planning based on constraints

---


