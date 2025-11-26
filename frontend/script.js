// Store tasks in memory
let tasks = [];

// Update task count
function updateTaskCount() {
    document.getElementById("task-count").textContent = `${tasks.length} tasks added.`;
}

// Add task from form inputs
document.getElementById("add-task-btn").addEventListener("click", () => {
    const title = document.getElementById("title").value.trim();
    const due_date = document.getElementById("due_date").value;
    const hours = document.getElementById("hours").value;
    const importance = document.getElementById("importance").value;
    const dependencies = document.getElementById("dependencies").value;

    if (!title) {
        alert("Title is required!");
        return;
    }

    const task = {
        id: "t" + (tasks.length + 1),
        title,
        due_date: due_date || null,
        estimated_hours: hours ? parseFloat(hours) : null,
        importance: importance ? parseInt(importance) : null,
        dependencies: dependencies
            ? dependencies.split(",").map(d => d.trim())
            : []
    };

    tasks.push(task);
    updateTaskCount();

    // Clear inputs
    document.getElementById("title").value = "";
    document.getElementById("hours").value = "";
    document.getElementById("importance").value = "";
    document.getElementById("dependencies").value = "";
});

// Load tasks from JSON textarea
document.getElementById("load-json-btn").addEventListener("click", () => {
    const text = document.getElementById("json-input").value.trim();

    if (!text) {
        alert("Please paste valid JSON.");
        return;
    }

    try {
        const jsonTasks = JSON.parse(text);

        if (!Array.isArray(jsonTasks)) {
            alert("JSON must be an array of tasks.");
            return;
        }

        jsonTasks.forEach((t, index) => {
            tasks.push({
                id: t.id || "t" + (tasks.length + 1),
                title: t.title || "Untitled Task",
                due_date: t.due_date || null,
                estimated_hours: t.estimated_hours ?? null,
                importance: t.importance ?? null,
                dependencies: t.dependencies || []
            });
        });

        updateTaskCount();
        alert("Tasks loaded!");
    } catch (error) {
        alert("Invalid JSON!");
    }
});

// Send tasks to backend for scoring
document.getElementById("analyze-btn").addEventListener("click", async () => {

    if (tasks.length === 0) {
        alert("Please add at least one task before analyzing.");
        return;
    }

    const now = new Date();
const today = now.getFullYear() + "-" +
              String(now.getMonth() + 1).padStart(2, "0") + "-" +
              String(now.getDate()).padStart(2, "0");
    const strategy = document.getElementById("strategy").value;

    const payload = {
        today,
        strategy,
        tasks: tasks
    };

    try {
        document.getElementById("results").innerHTML = "<p>Analyzing...</p>";

        const response = await fetch("http://127.0.0.1:8000/api/tasks/analyze/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            document.getElementById("results").innerHTML =
                `<p style="color:red;">Error: ${data.error || "Unknown error"}</p>`;
            return;
        }

        renderResults(data.tasks);

    } catch (err) {
        document.getElementById("results").innerHTML =
            `<p style="color:red;">Network error.</p>`;
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
            <h3>${t.title}</h3>
            <p><b>Score:</b> ${t.score.toFixed(3)}</p>
            <p><b>Urgency:</b> ${t.components.urgency.toFixed(3)}</p>
            <p><b>Importance:</b> ${t.components.importance.toFixed(3)}</p>
            <p><b>Effort:</b> ${t.components.effort.toFixed(3)}</p>
            <p><b>Dependency:</b> ${t.components.dependency.toFixed(3)}</p>
        `;

        container.appendChild(card);
    });
}
// Fetch the top 3 suggested tasks from backend
document.getElementById("get-suggestions-btn").addEventListener("click", async () => {
    try {
        document.getElementById("suggestions").innerHTML = "<p>Loading suggestions...</p>";

        const response = await fetch("http://127.0.0.1:8000/api/tasks/suggest/", {
            method: "GET"
        });

        const data = await response.json();

        if (!response.ok) {
            document.getElementById("suggestions").innerHTML =
                `<p style="color:red;">Error: ${data.error || "Unknown error"}</p>`;
            return;
        }

        renderSuggestions(data.suggestions);

    } catch (err) {
        document.getElementById("suggestions").innerHTML =
            `<p style="color:red;">Network error.</p>`;
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
        card.className = `task-card ${priorityClass}`;

        card.innerHTML = `
            <h3>${s.title}</h3>
            <p><b>Score:</b> ${s.score.toFixed(3)}</p>
            <p><b>Why:</b> ${s.why}</p>
        `;

        container.appendChild(card);
    });
}


