const API_BASE = ""; 

document.addEventListener("DOMContentLoaded", () => {
  const boardDiv    = document.getElementById("board");
  const generateBtn = document.getElementById("generateBtn");
  const solveBtn    = document.getElementById("solveBtn");
  const clearBtn    = document.getElementById("clearBtn");
  const finishBtn   = document.getElementById("finishBtn"); 
  const levelSelect = document.getElementById("level");
  const statusDiv   = document.getElementById("status");
  const congratsDiv = document.getElementById("congrats");


  function setStatus(msg, type = "") {
    statusDiv.classList.remove("error", "ok");
    if (type) statusDiv.classList.add(type);
    statusDiv.textContent = msg || "";
  }

  function clearHighlights() {
    boardDiv.querySelectorAll("input").forEach(inp => inp.classList.remove("input-error"));
  }

  function highlightCells(cells) {
    const inputs = boardDiv.querySelectorAll("input");
    cells.forEach(({ r, c }) => {
      const idx = r * 9 + c;
      if (inputs[idx]) inputs[idx].classList.add("input-error");
    });
  }

  function setButtonsOnlyGenerate() {
    generateBtn.disabled = false;
    levelSelect.disabled = false;

    solveBtn.disabled  = true;
    clearBtn.disabled  = true;
    finishBtn.disabled = true;
  }

  function setButtonsDefault() {
    generateBtn.disabled = false;
    levelSelect.disabled = false;

    solveBtn.disabled  = false;
    clearBtn.disabled  = false;
    updateFinishState(); 
  }


  function boardComplete(board) {
    return board.every(row => row.every(v => Number.isInteger(v) && v >= 1 && v <= 9));
  }

  function validateBoard(board) {
    const errors = [];
    const inRange = v => Number.isInteger(v) && v >= 1 && v <= 9;

    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        if (!inRange(board[r][c])) errors.push({ r, c, reason: "empty_or_invalid" });
      }
    }

    for (let r = 0; r < 9; r++) {
      const pos = new Map();
      for (let c = 0; c < 9; c++) {
        const v = board[r][c];
        if (!inRange(v)) continue;
        if (pos.has(v)) {
          const prevC = pos.get(v);
          errors.push({ r, c, reason: "row_duplicate" }, { r, c: prevC, reason: "row_duplicate" });
        } else pos.set(v, c);
      }
    }

    for (let c = 0; c < 9; c++) {
      const pos = new Map();
      for (let r = 0; r < 9; r++) {
        const v = board[r][c];
        if (!inRange(v)) continue;
        if (pos.has(v)) {
          const prevR = pos.get(v);
          errors.push({ r, c, reason: "col_duplicate" }, { r: prevR, c, reason: "col_duplicate" });
        } else pos.set(v, r);
      }
    }

    for (let br = 0; br < 3; br++) {
      for (let bc = 0; bc < 3; bc++) {
        const pos = new Map();
        for (let r = br * 3; r < br * 3 + 3; r++) {
          for (let c = bc * 3; c < bc * 3 + 3; c++) {
            const v = board[r][c];
            if (!inRange(v)) continue;
            if (pos.has(v)) {
              const { r: pr, c: pc } = pos.get(v);
              errors.push({ r, c, reason: "box_duplicate" }, { r: pr, c: pc, reason: "box_duplicate" });
            } else pos.set(v, { r, c });
          }
        }
      }
    }

    return { ok: errors.length === 0 && boardComplete(board), errors };
  }

  function updateFinishState() {
    if (!finishBtn) return;
    const board = readBoardFromUI();
    const allFilled = board.every(row => row.every(v => Number.isInteger(v) && v >= 1 && v <= 9));
    finishBtn.disabled = !allFilled;
  }

  function createGrid() {
    boardDiv.innerHTML = "";
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const cell = document.createElement("div");
        cell.className = "cell";
        if ((r + 1) % 3 === 0 && r !== 8) cell.style.borderBottom = "2px solid #000";
        if ((c + 1) % 3 === 0 && c !== 8) cell.style.borderRight = "2px solid #000";

        const input = document.createElement("input");
        input.type = "text";
        input.maxLength = 1;
        input.dataset.r = r;
        input.dataset.c = c;
        input.dataset.fixed = "false";

        input.addEventListener("input", (e) => {
          if (e.target.dataset.fixed === "true") {
            e.target.value = e.target.dataset.value || "";
            return;
          }
          const val = e.target.value.replace(/[^1-9]/g, "");
          e.target.value = val;

          e.target.classList.remove("input-error");
          setStatus("");
          if (congratsDiv) congratsDiv.style.display = "none";

          updateFinishState();
        });

        cell.appendChild(input);
        boardDiv.appendChild(cell);
      }
    }
  }

  function readBoardFromUI() {
    const rows = [];
    const inputs = boardDiv.querySelectorAll("input");
    for (let r = 0; r < 9; r++) {
      const row = [];
      for (let c = 0; c < 9; c++) {
        const idx = r * 9 + c;
        const val = inputs[idx].value;
        row.push(val === "" ? 0 : parseInt(val));
      }
      rows.push(row);
    }
    return rows;
  }

  function setBoardToUI(board, markFixed = false) {
    const inputs = boardDiv.querySelectorAll("input");
    for (let r = 0; r < 9; r++) {
      for (let c = 0; c < 9; c++) {
        const idx = r * 9 + c;
        const input = inputs[idx];
        const val = board[r][c];

        input.value = val === 0 ? "" : val;
        input.classList.remove("input-error");

        if (markFixed) {
          if (val !== 0) {
            input.dataset.fixed = "true";
            input.dataset.value = String(val);
            input.readOnly = true;
            input.classList.add("fixed");
          } else {
            input.dataset.fixed = "false";
            input.dataset.value = "";
            input.readOnly = false;
            input.classList.remove("fixed");
          }
        }
      }
    }
    updateFinishState();
  }

  async function generatePuzzle() {
    const level = levelSelect.value;
    setStatus("Generating puzzle...");
    clearHighlights();
    if (congratsDiv) congratsDiv.style.display = "none";
    setButtonsDefault(); 

    try {
      const res = await fetch(`${API_BASE}/generate?level=${level}`);
      const data = await res.json();
      if (data.status === "ok") {
        setBoardToUI(data.puzzle, true); 
        setStatus(`Puzzle generated (${data.level})`);
      } else {
        setStatus("Error generating puzzle", "error");
      }
    } catch (err) {
      setStatus("Could not reach backend. Make sure Flask is running.", "error");
      console.error(err);
    }
  }

  async function solvePuzzle() {
    const puzzle = readBoardFromUI();
    clearHighlights();
    setStatus("Solving...");
    finishBtn.disabled = true;

    try {

      const res = await fetch(`${API_BASE}/solve_sudoku`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ puzzle })
      });
      const data = await res.json();

      if (data.status === "unique" || data.status === "multiple") {
        setBoardToUI(data.solution, false);
        setStatus(
          data.status === "unique" ? "Solved (unique)" : "Solved (multiple)",
          "ok"
        );
        if (congratsDiv) congratsDiv.style.display = "block";
        setButtonsOnlyGenerate();
      } else if (data.status === "unsolvable") {
        setStatus("Unsolvable: 0 solutions.", "error");
        setButtonsDefault();
      } else if (data.status === "invalid") {
        setStatus("Invalid puzzle: row/column/box conflicts.", "error");
        setButtonsDefault();
      } else {
        setStatus(`Error: ${data.message || "backend error"}`, "error");
        setButtonsDefault();
      }
    } catch (err) {
      setStatus("Error communicating with backend.", "error");
      console.error(err);
      setButtonsDefault();
    }
  }


  generateBtn.addEventListener("click", generatePuzzle);
  solveBtn.addEventListener("click", solvePuzzle);


  clearBtn.addEventListener("click", () => {
    if (clearBtn.disabled) return;
    const inputs = boardDiv.querySelectorAll("input");
    inputs.forEach(i => {
      if (i.dataset.fixed !== "true") {
        i.value = "";
        i.classList.remove("input-error");
      }
    });
    setStatus("");
    if (congratsDiv) congratsDiv.style.display = "none";
    updateFinishState();
  });


  if (finishBtn) {
    finishBtn.disabled = true;
    finishBtn.addEventListener("click", () => {
      if (finishBtn.disabled) return;

      clearHighlights();
      if (congratsDiv) congratsDiv.style.display = "none";

      const board = readBoardFromUI();
      const result = validateBoard(board);

      if (result.ok) {
        setStatus("U zgjidh saktë! Bravo!", "ok");
        if (congratsDiv) congratsDiv.style.display = "block";
        setButtonsOnlyGenerate();
      } else {
        const cells = result.errors.map(e => ({ r: e.r, c: e.c }));
        highlightCells(cells);
        setStatus("Ka gabime – korrigjo qelizat e theksuara dhe shtyp ‘Perfundo’.", "error");
      }
    });
  }

  createGrid();
  updateFinishState();
});
