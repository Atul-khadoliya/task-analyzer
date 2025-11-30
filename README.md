
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

