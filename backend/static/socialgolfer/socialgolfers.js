let isRunning = false;
let controller = null;

document.getElementById("solveBtn").addEventListener("click", async () => {
    if (isRunning) {
        alert("Solver already running!");
        return;
    }

    const num_players = parseInt(document.getElementById("num_players").value);
    const group_size = parseInt(document.getElementById("group_size").value);
    const algorithm = document.getElementById("algorithm").value;
    const depth_limit = document.getElementById("depth_limit").value;
    const output = document.getElementById("output");

    output.innerText = "Solving... please wait...";
    isRunning = true;
    controller = new AbortController();

    try {
        const response = await fetch("/solve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            signal: controller.signal,
            body: JSON.stringify({
                num_players,
                group_size,
                algorithm,
                depth_limit: depth_limit || null
            })
        });

        const data = await response.json();
        isRunning = false; // ✅ reset when done

        if (!data.success) {
            output.innerText = "No valid schedule found.";
            return;
        }

        let result = `Algorithm Used: ${algorithm}\n`;
        result += `Elapsed Time: ${data.elapsed_time}s\n`;
        result += `Weeks Found: ${data.weeks}\n\n`;

        data.schedule.forEach((week, i) => {
            result += `Week ${i + 1}:\n`;
            week.forEach((group, j) => {
                result += `  Group ${j + 1}: ${group.join(", ")}\n`;
            });
            result += "\n";
        });

        output.innerText = result;

    } catch (err) {
        // --- Solver was manually stopped by user ---
        if (err.name === "AbortError") {
            isRunning = false; // ✅ reset running flag
            output.innerText = "Solver stopped by user.\nShowing progress so far...";

            // Fetch progress from backend
            fetch("/progress")
                .then(res => res.json())
                .then(data => {
                    if (data.schedule) {
                        let result = `Weeks Found So Far: ${data.weeks}\n\n`;
                        data.schedule.forEach((week, i) => {
                            result += `Week ${i + 1}:\n`;
                            week.forEach((group, j) => {
                                result += `  Group ${j + 1}: ${group.join(", ")}\n`;
                            });
                            result += "\n";
                        });
                        output.innerText = result;
                    }
                })
                .catch(e => {
                    output.innerText = "Stopped, but failed to fetch progress.";
                });

        } else {
            // --- Any other error ---
            isRunning = false; // ✅ reset
            output.innerText = "Error: " + err;
        }
    }
});

// ---------------- STOP BUTTON HANDLER ----------------
document.getElementById("stopBtn").addEventListener("click", async () => {
    if (!isRunning) return;

    controller.abort(); // abort fetch call
    await fetch("/stop", { method: "POST" });
    isRunning = false; // ✅ reset immediately on stop

    // Optionally, auto-refresh progress one more time after stopping
    fetch("/progress")
        .then(res => res.json())
        .then(data => {
            const output = document.getElementById("output");
            if (data.schedule && data.schedule.length > 0) {
                let result = `Weeks Found So Far: ${data.weeks}\n\n`;
                data.schedule.forEach((week, i) => {
                    result += `Week ${i + 1}:\n`;
                    week.forEach((group, j) => {
                        result += `  Group ${j + 1}: ${group.join(", ")}\n`;
                    });
                    result += "\n";
                });
                output.innerText = result;
            } else {
                output.innerText = "Solver stopped. No partial results found.";
            }
        });
});
