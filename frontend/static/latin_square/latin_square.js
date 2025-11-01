document.getElementById("generateBtn").addEventListener("click", generateBoard);
document.getElementById("solveBtn").addEventListener("click", solveLatin);
document.getElementById("checkBtn").disabled = true; 

function generateBoard() {
    let size = parseInt(document.getElementById("size").value);
    
    if (size > 15)
    {
        alert("Madhësia e tabelës nuk mund të jetë më e madhe se 15.");
    }
    

    const boardDiv = document.getElementById("board");
    boardDiv.innerHTML = "";

    const board = Array.from({ length: size }, () => Array(size).fill(0));

    function isValid(board, row, col, num) {
        for (let i = 0; i < size; i++) {
            if (board[row][i] === num || board[i][col] === num) return false;
        }
        return true;
    }

    function fillBoard(board, row = 0, col = 0) {
        if (row === size) return true;
        let nextRow = col === size - 1 ? row + 1 : row;
        let nextCol = col === size - 1 ? 0 : col + 1;

        let nums = Array.from({ length: size }, (_, i) => i + 1);
        nums.sort(() => Math.random() - 0.5); 

        for (let num of nums) {
            if (isValid(board, row, col, num)) {
                board[row][col] = num;
                if (fillBoard(board, nextRow, nextCol)) return true;
                board[row][col] = 0;
            }
        }
        return false;
    }

    fillBoard(board);

    const puzzle = board.map(row => row.slice());
    for (let i = 0; i < size; i++) {
        for (let j = 0; j < size; j++) {
            if (Math.random() < 0.3) puzzle[i][j] = 0;
        }
    }

    const table = document.createElement("table");

    for (let i = 0; i < size; i++) {
        const rowEl = document.createElement("tr");
        for (let j = 0; j < size; j++) {
            const cell = document.createElement("td");
            const input = document.createElement("input");
            input.type = "number";
            input.min = 1;
            input.max = size;
            input.classList.add("cell");

            if (puzzle[i][j] !== 0) {
                input.value = puzzle[i][j];
                input.dataset.fixed = "true";
                input.readOnly = true;
                input.classList.add("fixed");
            } else {
                input.value = "";
                input.dataset.fixed = "false";
            }

            input.addEventListener("input", () => {
                if (input.dataset.fixed === "true") {
                    input.value = input.dataset.value || "";
                    return;
                }
                let val = parseInt(input.value, 10);
                if (isNaN(val) || val < 1) val = "";
                if (val > size) val = size;
                input.value = val;
                checkBoardFull();
            });

            cell.appendChild(input);
            rowEl.appendChild(cell);
        }
        table.appendChild(rowEl);
    }

    boardDiv.appendChild(table);

    document.getElementById("solveSection").style.display = "block";

    checkBoardFull();
}

function checkBoardFull() {
    const inputs = document.querySelectorAll("table input");
    const allFilled = Array.from(inputs).every(inp => inp.value !== "" && !isNaN(parseInt(inp.value)));
    document.getElementById("checkBtn").disabled = !allFilled;
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

    const boardCopy = board.map(r => r.slice());

    const algorithm = document.getElementById("algorithm").value;
    const depth_limit = parseInt(document.getElementById("depth_limit").value) || null;

    const res = await fetch("/solve_latin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: boardCopy, algorithm, depth_limit })
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

function toggleDepthInput() {
    const algorithm = document.getElementById("algorithm").value;
    const depthContainer = document.getElementById("depthLimitContainer");

    if (algorithm === "IDDFS") {
        depthContainer.style.display = "block";
    } else {
        depthContainer.style.display = "none";
    }
}
document.getElementById("clearBtn").addEventListener("click", clearBoard);

function clearBoard() {
    const rows = document.querySelectorAll("table tr");
    rows.forEach(row => {
        const cells = row.querySelectorAll("input");
        cells.forEach(cell => {
            if (cell.dataset.fixed === "true") {
                cell.value = cell.dataset.value || cell.value;
            } else {
                cell.value = "";
            }
        });
    });

    const output = document.getElementById("output");
    output.innerHTML = `<p>Board cleared. You can edit or solve again.</p>`;

    document.getElementById("checkBtn").disabled = true;
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

    for (let i = 0; i < n; i++) {
        const seen = new Set();
        for (let j = 0; j < n; j++) {
            if (board[i][j] === 0) continue;
            if (seen.has(board[i][j])) {
                output.innerHTML = `<p>⚠️ Row ${i+1} has duplicates!</p>`;
                return;
            }
            seen.add(board[i][j]);
        }
    }

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
