const checkBtn = document.getElementById("checkBtn");
const userInput = document.getElementById("userInput");
const resultsDiv = document.getElementById("results");
const loadingDiv = document.getElementById("loading");
const actionsDiv = document.getElementById("actions");
const copyBtn = document.getElementById("copyBtn");
const downloadBtn = document.getElementById("downloadBtn");
const themeToggle = document.getElementById("themeToggle");
const shareBtn = document.getElementById("shareBtn");

let lastResult = null;

checkBtn.addEventListener("click", async () => {
  const content = userInput.value.trim();
  if (!content) {
    Swal.fire({
      title: "Error",
      text: "Please paste a link or message first.",
      icon: "error",
      confirmButtonText: "Okay",
    });
    return;
  }

  resultsDiv.className = "results";
  resultsDiv.innerHTML = "";
  loadingDiv.classList.remove("hidden");
  actionsDiv.classList.add("hidden");

  const skeletonOverlay = document.createElement("div");
  skeletonOverlay.className = "full-skeleton";
  document.body.appendChild(skeletonOverlay);

  try {
    const res = await fetch("http://localhost:5000/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content }),
    });

    const data = await res.json();
    lastResult = data;

    loadingDiv.classList.add("hidden");
    document.body.removeChild(skeletonOverlay);

    resultsDiv.classList.add(data.rating);

    const reasonsList = data.reasons
      .map((reason) => `<li>${reason}</li>`)
      .join("");

    resultsDiv.innerHTML = `<h3>${data.rating.toUpperCase()}</h3><ul id="typeList"></ul>`;
    const typeList = document.getElementById("typeList");

    let i = 0;
    function typeNext() {
      if (i < data.reasons.length) {
        const li = document.createElement("li");
        typeList.appendChild(li);
        typeText(li, data.reasons[i], 0, () => {
          i++;
          setTimeout(typeNext, 300); // delay between lines
        });
      }
    }
    typeNext();
    feedback.classList.remove("hidden");

    actionsDiv.classList.remove("hidden");
  } catch (error) {
    loadingDiv.classList.add("hidden");
    document.body.removeChild(skeletonOverlay);
    resultsDiv.innerHTML = `<p style="color:red">❌ Error connecting to server.</p>`;
  }
});

// Copies to clipboard
copyBtn.addEventListener("click", () => {
  if (lastResult) {
    const text = `Rating: ${lastResult.rating.toUpperCase()}\nReasons:\n${lastResult.reasons.join(
      "\n"
    )}`;
    navigator.clipboard.writeText(text);
    alert("Result copied to clipboard!");
  }
});

// Exportss as JSON
downloadBtn.addEventListener("click", () => {
  if (lastResult) {
    const blob = new Blob([JSON.stringify(lastResult, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "scan_result.json";
    a.click();
  }
});

// Theme toggle

// Apply saved theme on load
window.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("themeToggle");
  const iconMoon = document.getElementById("icon-moon");
  const iconSun = document.getElementById("icon-sun");

  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark");
    iconMoon.classList.add("hidden");
    iconSun.classList.remove("hidden");
  } else {
    iconMoon.classList.remove("hidden");
    iconSun.classList.add("hidden");
  }
  // Theme toggle with save hehehehehehe I know you are enjoying these comments
  themeToggle.addEventListener("click", () => {
    const isDark = document.body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");

    iconMoon.classList.toggle("hidden", isDark);
    iconSun.classList.toggle("hidden", !isDark);
  });
});

// Share
shareBtn.addEventListener("click", () => {
  if (lastResult) {
    const text = `Did I Just Get Scammed?\n\nRating: ${lastResult.rating.toUpperCase()}\nReasons:\n${lastResult.reasons.join(
      "\n"
    )}`;
    const encoded = encodeURIComponent(text);
    if (confirm("Open WhatsApp to share?")) {
      window.open(`https://wa.me/?text=${encoded}`, "_blank");
    }
  }
});

function typeText(element, text, index, callback) {
  if (index < text.length) {
    element.innerHTML += text.charAt(index);
    setTimeout(() => typeText(element, text, index + 1, callback), 30); // typing speed
  } else {
    callback();
  }
}

//feedbacks
const feedback = document.getElementById("feedback");
const feedbackResponse = document.getElementById("feedbackResponse");
const thumbsUp = document.getElementById("thumbsUp");
const thumbsDown = document.getElementById("thumbsDown");
const feedbackBox = document.getElementById("feedbackBox");
const submitFeedback = document.getElementById("submitFeedback");
const feedbackText = document.getElementById("feedbackText");

function showFeedback(text, color) {
  feedbackResponse.textContent = text;
  feedbackResponse.style.color = color;
  feedbackResponse.classList.remove("show");
  void feedbackResponse.offsetWidth; // for force reflow to restart animation
  feedbackResponse.classList.add("show");
}

function sparkleBurst(btn, emoji = "👍") {
  for (let i = 0; i < 6; i++) {
    const sparkle = document.createElement("span");
    sparkle.className = "sparkle";
    sparkle.textContent = emoji;

    const offsetX = (Math.random() - 0.5) * 20;
    const offsetY = Math.random() * -30 - 10;

    const rect = btn.getBoundingClientRect();
    sparkle.style.left = `${rect.left + rect.width / 2 + offsetX}px`;
    sparkle.style.top = `${rect.top + offsetY}px`;

    document.body.appendChild(sparkle);

    setTimeout(() => {
      sparkle.remove();
    }, 800);
  }
}

function burstEmoji(button, emoji = "👎") {
  const burst = document.createElement("span");
  burst.className = "burst";
  burst.textContent = emoji;

  const rect = button.getBoundingClientRect();
  burst.style.left = `${rect.left + rect.width / 2}px`;
  burst.style.top = `${rect.top - 20}px`;

  document.body.appendChild(burst);

  setTimeout(() => burst.remove(), 1000);
}

thumbsUp.addEventListener("click", () => {
  showFeedback("🎉 Thanks for your feedback!", "#28a745");
  sparkleBurst(thumbsUp, "👍");
  feedbackBox.classList.remove("hidden");
});

thumbsDown.addEventListener("click", () => {
  showFeedback("🙏 Sorry about that. We'll try to improve.", "#dc3545");
  sparkleBurst(thumbsDown, "👎");
  feedbackBox.classList.remove("hidden");
});

submitFeedback.addEventListener("click", () => {
  const name = document.getElementById("feedbackName").value.trim();
  const email = document.getElementById("feedbackEmail").value.trim();
  const feedback = document.getElementById("feedbackText").value.trim();

  if (!name || !email || !feedback) {
    Swal.fire({
      icon: "info",
      title: "Missing Info",
      text: "Please fill in all the fields before submitting.",
    });
    return;
  }

  emailjs.init("service_56109gg", "template_a16aqem", {
    name: name,
    email: email,
    feedback: feedback,
  })
  .then(() => {
    Swal.fire({
      icon: "success",
      title: "Thank you!",
      text: "Your feedback has been sent successfully.",
    });
    document.getElementById("feedbackName").value = "";
    document.getElementById("feedbackEmail").value = "";
    document.getElementById("feedbackText").value = "";
    feedbackBox.classList.add("hidden");
  })
  .catch((error) => {
    Swal.fire({
      icon: "error",
      title: "Sending failed",
      text: "Could not send your feedback. Try again later.",
    });
    console.error("EmailJS Error:", error);
  });
});


const scamIcons = [
  `
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="orangered" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M16 18c0 2-2 4-4 4s-4-2-4-4V5a4 4 0 018 0v2" />
    <circle cx="16" cy="2" r="2" fill="orangered"/>
  </svg>
  `,
  `
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="crimson" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="2" y="5" width="20" height="14" rx="2" ry="2" />
    <line x1="2" y1="10" x2="22" y2="10" />
    <line x1="8" y1="15" x2="10" y2="15" />
    <line x1="14" y1="15" x2="18" y2="15" />
  </svg>
  `,
  `
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#e63946" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10 14a4 4 0 000-8h-2a4 4 0 000 8h2zm4-4h2a4 4 0 010 8h-2a4 4 0 010-8z" />
    <line x1="8" y1="12" x2="16" y2="12" />
  </svg>
  `,
  `
  <svg xmlns="http://www.w3.org/2000/svg" fill="#43aa8b" viewBox="0 0 24 24" stroke="none">
    <path d="M12 2l9 4v6c0 5.25-3.75 10-9 12C6.75 22 3 17.25 3 12V6l9-4z"/>
    <path d="M9.5 11.5l2 2 3.5-3.5" fill="none" stroke="#fff" stroke-width="2"/>
  </svg>
  `,
];

//Randomization in its peak, thanks to python I sorta understand this to the full
const scamIconContainer = document.getElementById("scamIcon");
if (scamIconContainer) {
  const randomIndex = Math.floor(Math.random() * scamIcons.length);
  scamIconContainer.innerHTML = scamIcons[randomIndex];
}
