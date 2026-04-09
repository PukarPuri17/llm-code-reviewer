// app.js — Frontend JavaScript Logic
// Handles form submission, calls the backend API, and renders results.

const API_URL = "http://localhost:5000/api/review";
const MAX_CHARS = 10000;

// Update character counter as user types
document.getElementById("code-input").addEventListener("input", function () {
  const len = this.value.length;
  const counter = document.getElementById("char-count");
  counter.textContent = `${len.toLocaleString()} / 10,000 characters`;
  counter.classList.toggle("warning", len > 8000);
});


async function analyzeCode() {
  const code = document.getElementById("code-input").value.trim();
  const language = document.getElementById("language").value;

  hideElement("validation-error");
  hideElement("api-error");

  // Client-side validation before sending to server
  if (!language) {
    showError("validation-error", "Please select a programming language.");
    return;
  }

  if (!code) {
    showError("validation-error", "Please paste some code before analyzing.");
    return;
  }

  if (code.length > MAX_CHARS) {
    showError("validation-error", `Code exceeds the 10,000 character limit (yours is ${code.length.toLocaleString()} chars).`);
    return;
  }

  // Show loading state
  showElement("loading");
  hideElement("results");
  document.getElementById("analyze-btn").disabled = true;

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unknown server error.");
    }

    renderResults(data);

  } catch (err) {
    hideElement("loading");
    showError("api-error", `Error: ${err.message}. Make sure the backend server is running at localhost:5000.`);
    document.getElementById("analyze-btn").disabled = false;
  }
}


function renderResults(data) {
  hideElement("loading");

  renderList("bugs-list", data.bugs);
  renderList("security-list", data.security);
  renderList("quality-list", data.quality);

  showElement("results");
  document.getElementById("results").scrollIntoView({ behavior: "smooth" });
}


function renderList(elementId, items) {
  const ul = document.getElementById(elementId);
  ul.innerHTML = "";

  if (!items || items.length === 0) {
    ul.innerHTML = '<li class="empty">No issues found.</li>';
    return;
  }

  items.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    ul.appendChild(li);
  });
}


function resetForm() {
  document.getElementById("code-input").value = "";
  document.getElementById("language").value = "";
  document.getElementById("char-count").textContent = "0 / 10,000 characters";
  document.getElementById("analyze-btn").disabled = false;
  hideElement("results");
  hideElement("validation-error");
  hideElement("api-error");
  window.scrollTo({ top: 0, behavior: "smooth" });
}


function showElement(id) {
  document.getElementById(id).classList.remove("hidden");
}

function hideElement(id) {
  document.getElementById(id).classList.add("hidden");
}

function showError(id, message) {
  const el = document.getElementById(id);
  el.textContent = message;
  el.classList.remove("hidden");
}