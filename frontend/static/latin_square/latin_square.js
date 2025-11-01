document.getElementById("generateBtn").addEventListener("click", generateBoard);
document.getElementById("solveBtn").addEventListener("click", solveLatin);

function generateBoard() {
    const size = parseInt(document.getElementById("size").value);
    const boardDiv = document.getElementById("board");
    boardDiv.innerHTML = "";

    const table = document.createElement("table");
    for (let i = 0; i < size; i++) {
        const row = document.createElement("tr");
        for (let j = 0; j < size; j++) {
            const cell = document.createElement("td");
            const input = document.createElement("input");
            input.type = "number";
            input.min = 0;
            input.max = size;
            input.value = 0;
            input.classList.add("cell");

            // 🔒 Prevent invalid numbers
            input.addEventListener("input", () => {
            let val = parseInt(input.value, 10);

            if (isNaN(val) || val < 0) val = 0;
            if (val > size) val = size;

            input.value = val; // Force the value to be an integer
            });


            cell.appendChild(input);
            row.appendChild(cell);
        }
        table.appendChild(row);
    }
    boardDiv.appendChild(table);

    // 👇 Show algorithm, depth limit, and solve button after table is generated
    document.getElementById("solveSection").style.display = "block";
}

async function solveLatin() {
    const board = [];
    const rows = document.querySelectorAll("table tr");
    rows.forEach(row => {
        const cells = row.querySelectorAll("input");
        const rowData = [];
        cells.forEach(cell => rowData.push(parseInt(cell.value) || 0));
        board.push(rowData);
    });

    const algorithm = document.getElementById("algorithm").value;
    const depth_limit = parseInt(document.getElementById("depth_limit").value) || null;

    const res = await fetch("/solve_latin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board, algorithm, depth_limit })
    });

    const data = await res.json();
    const output = document.getElementById("output");
    if (data.success) {
        output.innerHTML = `<p>✅ Solved in ${data.elapsed_time}s using ${algorithm}!</p>`;
        renderSolution(data.solution);
    } else {
        output.innerHTML = `<p>⚠️ ${data.message}</p>`;
    }
}

function renderSolution(solution) {
    const table = document.querySelector("table");
    for (let i = 0; i < solution.length; i++) {
        const row = table.rows[i];
        for (let j = 0; j < solution[i].length; j++) {
            row.cells[j].firstChild.value = solution[i][j];
        }
    }
}

// ✅ Corrected toggleDepthInput() function
function toggleDepthInput() {
    const algorithm = document.getElementById("algorithm").value;
    const depthContainer = document.getElementById("depthLimitContainer");

    if (algorithm === "IDDFS") {
        depthContainer.style.display = "block";
    } else {
        depthContainer.style.display = "none";
    }
}

document.getElementById("checkBtn").addEventListener("click", checkBoard);

function checkBoard() {
    const board = [];
    const rows = document.querySelectorAll("table tr");
    const n = rows.length;

    rows.forEach(row => {
        const cells = row.querySelectorAll("input");
        const rowData = [];
        cells.forEach(cell => rowData.push(parseInt(cell.value) || 0));
        board.push(rowData);
    });

    const output = document.getElementById("output");

    // Check rows
    for (let i = 0; i < n; i++) {
        const seen = new Set();
        for (let j = 0; j < n; j++) {
            if (board[i][j] === 0) continue; // skip empty cells
            if (seen.has(board[i][j])) {
                output.innerHTML = `<p>⚠️ Row ${i+1} has duplicates!</p>`;
                return;
            }
            seen.add(board[i][j]);
        }
    }

    // Check columns
    for (let j = 0; j < n; j++) {
        const seen = new Set();
        for (let i = 0; i < n; i++) {
            if (board[i][j] === 0) continue;
            if (seen.has(board[i][j])) {
                output.innerHTML = `<p>⚠️ Column ${j+1} has duplicates!</p>`;
                return;
            }
            seen.add(board[i][j]);
        }
    }

    output.innerHTML = `<p>✅ So far, your board is valid!</p>`;
}
