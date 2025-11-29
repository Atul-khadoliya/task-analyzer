// Store tasks in memory
let tasks = [];

// Update task count
function updateTaskCount() {
    document.getElementById("task-count").textContent = `${tasks.length} tasks added.`;
}

// Add task from form inputs
document.getElementById("add-task-btn").addEventListener("click", () => {
    const id = document.getElementById("task-id").value.trim();
    const title = document.getElementById("task-title").value.trim();
    const dueDate = document.getElementById("task-due-date").value.trim();
    const estimatedHours = Number(document.getElementById("task-hours").value);
    const importance = Number(document.getElementById("task-importance").value);
    const dependenciesRaw = document.getElementById("task-dependencies").value.trim();

    // FRONTEND VALIDATION — must match backend rules
    if (!id) {
        alert("ID is required.");
        return;
    }

    if (!title) {
        alert("Title cannot be empty.");
        return;
    }

    if (!dueDate) {
        alert("Due date is required.");
        return;
    }

    if (isNaN(Date.parse(dueDate))) {
        alert("Invalid date format. Use YYYY-MM-DD.");
        return;
    }

    if (isNaN(estimatedHours) || estimatedHours < 0) {
        alert("Estimated hours must be a non-negative number.");
        return;
    }

    if (importance < 1 || importance > 10) {
        alert("Importance must be between 1 and 10.");
        return;
    }

    const dependencies = dependenciesRaw
        ? dependenciesRaw.split(",").map(d => d.trim())
        : [];

    // Only push task AFTER validation
    tasks.push({
        id,
        title,
        due_date: dueDate,
        estimated_hours: estimatedHours,
        importance,
        dependencies
    });

    renderLocalTasks();
    renderDependencyGraph(tasks);

});


// Load tasks from JSON textarea
document.getElementById("load-json-btn").addEventListener("click", () => {
    const raw = document.getElementById("json-input").value.trim();

    let parsed;
    try {
        parsed = JSON.parse(raw);
    } catch (err) {
        alert("Invalid JSON format.");
        return;
    }

    // FRONTEND JSON VALIDATION
    for (let i = 0; i < parsed.length; i++) {
        const t = parsed[i];

        if (!t.id || !String(t.id).trim()) {
            alert(`Task ${i + 1}: ID is required.`);
            return;
        }

        if (!t.title || !t.title.trim()) {
            alert(`Task ${i + 1}: Title cannot be empty.`);
            return;
        }

        if (!t.due_date || isNaN(Date.parse(t.due_date))) {
            alert(`Task ${i + 1}: Invalid due_date.`);
            return;
        }

        if (t.estimated_hours < 0) {
            alert(`Task ${i + 1}: Estimated hours must be >= 0.`);
            return;
        }

        if (t.importance < 1 || t.importance > 10) {
            alert(`Task ${i + 1}: Importance must be 1-10.`);
            return;
        }
    }

    // Only accept JSON AFTER validation
    tasks = parsed;
    renderLocalTasks();
    renderDependencyGraph(tasks);

});


// Send tasks to backend for scoring
document.getElementById("analyze-btn").addEventListener("click", async () => {
    const btn = document.getElementById("analyze-btn");

    // show loading state
    btn.disabled = true;
    btn.innerText = "Analyzing...";
    document.getElementById("error-box").style.display = "none";

    try {
        const strategy = document.getElementById("strategy").value;

        const now = new Date();
        const today = now.getFullYear() + "-" +
                      String(now.getMonth() + 1).padStart(2, "0") + "-" +
                      String(now.getDate()).padStart(2, "0");

        const payload = { today, strategy, tasks };

        const response = await fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            document.getElementById("error-box").style.display = "block";
            document.getElementById("error-box").innerText = JSON.stringify(data, null, 2);
            return;
        }

        // enrich data with original task values
        const enriched = data.tasks.map(t => {
            const raw = tasks.find(x => x.id === t.id);
            return { ...t, ...raw };
        });

        renderResults(enriched);

    } catch (err) {
        document.getElementById("error-box").style.display = "block";
        document.getElementById("error-box").innerText = "Network error.";
    } finally {
        btn.disabled = false;
        btn.innerText = "Analyze Tasks";
    }
});



function renderResults(tasks) {
    const container = document.getElementById("results");
    container.innerHTML = "";

    tasks.forEach(t => {
        const priorityClass =
            t.score > 0.7 ? "priority-high" :
            t.score > 0.4 ? "priority-medium" :
            "priority-low";

        const card = document.createElement("div");
        card.className = `task-card ${priorityClass}`;

        card.innerHTML = `
            <div class="card-title">${t.title}</div>

            <div class="card-grid">
                <p><b>Priority:</b> ${t.score > 0.7 ? "High 🔥" : t.score >= 0.4 ? "Medium ⚠️" : "Low 🟢"}</p>
                <p><b>Score:</b> ${t.score.toFixed(3)}</p>

                <p><b>Urgency:</b> ${t.components.urgency.toFixed(3)}</p>
                <p><b>Importance:</b> ${t.components.importance.toFixed(3)}</p>

                <p><b>Effort:</b> ${t.components.effort.toFixed(3)}</p>
                <p><b>Dependency:</b> ${t.components.dependency.toFixed(3)}</p>

                <p><b>Due Date:</b> ${t.due_date}</p>
                <p><b>Estimated Hours:</b> ${t.estimated_hours}</p>

                <p><b>Importance Level:</b> ${t.importance}</p>
            </div>

            <div class="explanation-box">
                <b>Explanation:</b> ${t.explanation}
            </div>
        `;

        container.appendChild(card);
    });
    renderEisenhowerMatrix(tasks);

}

// Fetch the top 3 suggested tasks from backend
document.getElementById("get-suggestions-btn").addEventListener("click", async () => {
    const btn = document.getElementById("get-suggestions-btn");

    btn.disabled = true;
    btn.innerText = "Loading...";
    document.getElementById("error-box").style.display = "none";

    try {
        const response = await fetch("http://127.0.0.1:8000/api/tasks/suggest/");

        const data = await response.json();

        if (!response.ok) {
            document.getElementById("error-box").style.display = "block";
            document.getElementById("error-box").innerText = data.error || "Error fetching suggestions.";
            return;
        }

        renderSuggestions(data.suggestions);

    } catch (err) {
        document.getElementById("error-box").style.display = "block";
        document.getElementById("error-box").innerText = "Network error.";
    } finally {
        btn.disabled = false;
        btn.innerText = "Get Suggestions";
    }
});


function renderSuggestions(suggestions) {
    const container = document.getElementById("suggestions");
    container.innerHTML = "";

    suggestions.forEach(s => {
        const priorityClass =
            s.score > 0.7 ? "priority-high" :
            s.score > 0.4 ? "priority-medium" :
            "priority-low";

        const card = document.createElement("div");
        card.className = `suggestion-card ${priorityClass}`;

        card.innerHTML = `
            <div class="card-title">${s.title}</div>

            <div class="card-grid">
                <p><b>Score:</b> ${s.score.toFixed(3)}</p>
                <p><b>Due Date:</b> ${s.due_date || "Not provided"}</p>
            </div>

            <div class="explanation-box">
                <b>Why this task:</b> ${s.why}
            </div>
        `;

        container.appendChild(card);
    });
}

document.getElementById("clear-tasks-btn").addEventListener("click", () => {
    tasks = []; // empty task list

    document.getElementById("results").innerHTML = "";
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("error-box").style.display = "none";
    
    // HIDE MATRIX AGAIN
    document.getElementById("matrix-grid").style.display = "none";
    // also clear any local display of tasks
    const taskContainer = document.getElementById("task-list");
    if (taskContainer) taskContainer.innerHTML = "";

    alert("All tasks cleared.");
});

function renderDependencyGraph(tasks) {
    const container = document.getElementById("dependency-graph");
    container.innerHTML = "";

    if (!tasks || tasks.length === 0) {
        container.innerHTML = "<p>No task dependencies.</p>";
        return;
    }

    tasks.forEach(task => {
        if (!task.dependencies || task.dependencies.length === 0) {
            container.innerHTML += `
                <div>
                    <span class="dep-node">${task.id}</span>
                </div>
            `;
        } else {
            task.dependencies.forEach(dep => {
                container.innerHTML += `
                    <div>
                        <span class="dep-node">${task.id}</span>
                        <span class="dep-arrow">→</span>
                        <span class="dep-node">${dep}</span>
                    </div>
                `;
            });
        }
    });
}

function renderEisenhowerMatrix(tasks) {

    document.getElementById("matrix-grid").style.display = "grid";
    ["q1", "q2", "q3", "q4"].forEach(q => {
        document.querySelector(`#${q} .matrix-content`).innerHTML = "";
    });

    tasks.forEach(t => {
        const u = t.components.urgency;
        const imp = t.components.importance;

        let quadrant;
        if (u >= 0.5 && imp >= 0.5) quadrant = "q1";      // Urgent + Important
        else if (u < 0.5 && imp >= 0.5) quadrant = "q2"; // Not Urgent + Important
        else if (u >= 0.5 && imp < 0.5) quadrant = "q3"; // Urgent + Not Important
        else quadrant = "q4";                             // Not Urgent + Not Important

        const div = document.createElement("div");
        div.className = "matrix-item";
        div.innerHTML = `
            <b>${t.title}</b><br>
            <small>U: ${u.toFixed(2)} | I: ${imp.toFixed(2)}</small>
        `;

        document.querySelector(`#${quadrant} .matrix-content`).appendChild(div);
    });
}

