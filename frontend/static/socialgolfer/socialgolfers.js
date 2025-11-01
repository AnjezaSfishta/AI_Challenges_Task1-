document.getElementById("solveBtn").addEventListener("click", async () => {
    const num_players = parseInt(document.getElementById("num_players").value);
    const group_size = parseInt(document.getElementById("group_size").value);
    const algorithm = document.getElementById("algorithm").value;
    const depth_limit = document.getElementById("depth_limit").value;
    const output = document.getElementById("output");

    if (isNaN(num_players) || num_players <= 0) {
        output.innerText = "Error: Please enter a valid number of players.";
        return;
    }

    if (isNaN(group_size) || group_size <= 1) {
        output.innerText = "Error: Please enter a valid group size (≥2).";
        return;
    }

    if (num_players % group_size !== 0) {
        output.innerText = `Error: ${num_players} players cannot be evenly divided into groups of ${group_size}.`;
        return;
    }

    if (algorithm === "Depth-Limited Search (DLS)" && (depth_limit === "" || isNaN(parseInt(depth_limit)))) {
        output.innerText = "Error: Please enter a depth limit when using DLS.";
        return;
    }

    output.innerText = "Solving... please wait...";

    try {
        const response = await fetch("/solve", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                num_players,
                group_size,
                algorithm,
                depth_limit: depth_limit || null
            })
        });

        const data = await response.json();

        if (!data.success) {
            output.innerText = "No valid schedule found.";
            return;
        }

        let result = `Maximum Weeks Found: ${data.weeks}\n\n`;

        data.schedule.forEach((week, i) => {
            result += `Week ${i + 1}:\n`;
            week.forEach((group, j) => {
                result += `  Group ${j + 1}: ${group.join(", ")}\n`;
            });
            result += "\n";
        });

        output.innerText = result;
    } catch (err) {
        output.innerText = "Error connecting to backend: " + err;
    }
});
