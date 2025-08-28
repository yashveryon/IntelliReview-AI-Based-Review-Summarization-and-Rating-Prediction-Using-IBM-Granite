window.addEventListener("DOMContentLoaded", () => {
  const textBtn = document.getElementById("textModeBtn");
  const fileBtn = document.getElementById("fileModeBtn");
  const backBtn = document.getElementById("backBtn");

  const textForm = document.getElementById("textForm");
  const fileForm = document.getElementById("fileForm");
  const outputSection = document.getElementById("outputSection");
  const trendSection = document.getElementById("trendSection");
  const chartEl = document.getElementById("sentimentChart");
  const downloadBtn = document.getElementById("downloadBtn");

  const inputReview = document.getElementById("inputReview");
  const summaryOutput = document.getElementById("summaryOutput");
  const ratingOutput = document.getElementById("ratingOutput");
  const sentimentOutput = document.getElementById("sentimentOutput");

  const reviewCardsContainer = document.getElementById("reviewCardsContainer");

  const summarizeBtn = document.getElementById("summarizeBtn");
  const uploadBtn = document.getElementById("uploadBtn");

  const sentimentColors = {
    positive: "#10b981",
    neutral: "#3b82f6",
    negative: "#ef4444"
  };

  function resetAllViews() {
    textForm.style.display = "none";
    fileForm.style.display = "none";
    outputSection.style.display = "none";
    trendSection.classList.add("hidden");
    downloadBtn.classList.add("hidden");
    backBtn.classList.add("hidden");
    document.getElementById("modeButtons").style.display = "flex";
    reviewCardsContainer.innerHTML = "";
    reviewCardsContainer.classList.add("hidden");

    if (window.sentimentChartInstance) {
      window.sentimentChartInstance.destroy();
    }

    inputReview.innerText = "";
    summaryOutput.innerText = "";
    ratingOutput.innerText = "";
    sentimentOutput.innerText = "";
    document.getElementById("reviewInput").value = "";
    document.getElementById("fileUpload").value = "";
  }

  textBtn.addEventListener("click", () => {
    resetAllViews();
    textForm.style.display = "block";
    backBtn.classList.remove("hidden");
    document.getElementById("modeButtons").style.display = "none";
  });

  fileBtn.addEventListener("click", () => {
    resetAllViews();
    fileForm.style.display = "block";
    backBtn.classList.remove("hidden");
    document.getElementById("modeButtons").style.display = "none";
  });

  backBtn.addEventListener("click", () => {
    resetAllViews();
  });

  summarizeBtn.addEventListener("click", async () => {
    const review = document.getElementById("reviewInput").value.trim();
    if (!review) return alert("Please enter a review.");

    const formData = new FormData();
    formData.append("review", review);

    try {
      const res = await fetch("/summarize", {
        method: "POST",
        body: formData
      });

      const data = await res.json();

      inputReview.innerText = data.original_review || "[Review not returned]";
      summaryOutput.innerText = data.summary || "[Summary missing]";
      ratingOutput.innerText = data.predicted_rating ? `⭐ ${data.predicted_rating} / 5` : "Not available";
      sentimentOutput.innerText = data.sentiment || "Not detected";

      outputSection.style.display = "block";

      trendSection.classList.remove("hidden");
      const ctx = chartEl.getContext("2d");
      if (window.sentimentChartInstance) window.sentimentChartInstance.destroy();
      window.sentimentChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: [data.sentiment],
          datasets: [{
            label: "Sentiment",
            data: [1],
            backgroundColor: [sentimentColors[data.sentiment] || "#999"]
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: { display: true, text: "Sentiment (Single Review)" }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, precision: 0 }
            }
          }
        }
      });

      showSuccessToast("Summarization complete!");
    } catch (err) {
      console.error("❌ Error:", err);
      alert("Something went wrong.");
    }
  });

  uploadBtn.addEventListener("click", async () => {
    const file = document.getElementById("fileUpload").files[0];
    if (!file) return alert("Please upload a CSV file.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/upload/summarize_all", {
        method: "POST",
        body: formData
      });

      const json = await res.json();
      const results = json.data || [];

      if (!results.length) return alert("No reviews found.");

      let combinedText = "";
      const dateSentimentMap = {};
      const reviewNumbersMap = {};  // ✅ To track review indexes for each sentiment/date

      reviewCardsContainer.classList.remove("hidden");
      reviewCardsContainer.innerHTML = "";

      results.forEach((item, idx) => {
        const reviewNum = `Review ${idx + 1}`;
        const sentiment = item.sentiment || "unknown";
        const date = item.date || item.timestamp || "Unknown Date";

        // Initialize maps
        if (!dateSentimentMap[date]) {
          dateSentimentMap[date] = { positive: 0, neutral: 0, negative: 0 };
        }
        if (!reviewNumbersMap[date]) {
          reviewNumbersMap[date] = { positive: [], neutral: [], negative: [] };
        }

        if (["positive", "neutral", "negative"].includes(sentiment)) {
          dateSentimentMap[date][sentiment]++;
          reviewNumbersMap[date][sentiment].push(idx + 1);
        }

        const card = document.createElement("div");
        card.className = "bg-white text-black p-4 rounded-xl shadow-md mb-4";
        card.innerHTML = `
          <h3 class="text-lg font-bold mb-2">${reviewNum}</h3>
          <p><strong>Date:</strong> ${date}</p>
          <p><strong>Original:</strong> ${item.original_review || item.review}</p>
          <p><strong>Summary:</strong> ${item.summary}</p>
          <p><strong>Rating:</strong> ⭐ ${item.predicted_rating}</p>
          <p><strong>Sentiment:</strong> <span class="px-2 py-1 rounded text-white text-sm" style="background:${sentimentColors[sentiment] || '#999'}">${sentiment}</span></p>
        `;
        reviewCardsContainer.appendChild(card);

        combinedText += `${reviewNum} (${date})\nOriginal: ${item.original_review || item.review}\nSummary: ${item.summary}\nRating: ${item.predicted_rating}\nSentiment: ${item.sentiment}\n\n`;
      });

      const dates = Object.keys(dateSentimentMap).sort();
      const pos = dates.map(d => dateSentimentMap[d].positive || 0);
      const neu = dates.map(d => dateSentimentMap[d].neutral || 0);
      const neg = dates.map(d => dateSentimentMap[d].negative || 0);

      trendSection.classList.remove("hidden");
      const ctx = chartEl.getContext("2d");
      if (window.sentimentChartInstance) window.sentimentChartInstance.destroy();
      window.sentimentChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
          labels: dates,
          datasets: [
            {
              label: "Positive",
              data: pos,
              backgroundColor: "#10b981"
            },
            {
              label: "Neutral",
              data: neu,
              backgroundColor: "#3b82f6"
            },
            {
              label: "Negative",
              data: neg,
              backgroundColor: "#ef4444"
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            title: {
              display: true,
              text: "Sentiment Trend Over Time"
            },
            tooltip: {
              mode: "index",
              intersect: false,
              callbacks: {
                label: function (context) {
                  const sentiment = context.dataset.label.toLowerCase();
                  const date = context.label;
                  const value = context.raw;
                  const reviews = reviewNumbersMap[date]?.[sentiment]?.join(", ") || "–";
                  return `${context.dataset.label}: ${value} (Review ${reviews})`;
                }
              }
            },
            legend: {
              position: "top"
            }
          },
          interaction: {
            mode: "index",
            intersect: false
          },
          scales: {
            x: {
              stacked: false,
              title: { display: true, text: "Date" }
            },
            y: {
              stacked: false,
              beginAtZero: true,
              title: { display: true, text: "Number of Reviews" }
            }
          }
        }
      });

      downloadBtn.classList.remove("hidden");
      downloadBtn.onclick = () => downloadTextFile(combinedText);

      showSuccessToast("Bulk summarization complete!");
    } catch (err) {
      console.error("❌ Upload Error:", err);
      alert("Error processing file.");
    }
  });

  function downloadTextFile(text) {
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "review_summary.txt";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function showSuccessToast(message) {
    const toast = document.createElement("div");
    toast.innerText = message;
    toast.className = "fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg animate-bounce z-50";
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }
});
