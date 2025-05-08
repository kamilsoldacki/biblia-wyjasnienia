document.getElementById("storyForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    const form = e.target;

    const data = {
        q1: form.q1.value,
        q2: form.q2.value,
        q3: form.q3.value,
        q4: form.q4.value,
        q5: form.q5.value
    };

    // Ukryj formularz i pokaż pasek ładowania
    form.style.display = "none";
    const loadingBarContainer = document.getElementById("loadingBarContainer");
    const loadingBar = document.getElementById("loadingBar");
    const loadingPercent = document.getElementById("loadingPercent");
    loadingBarContainer.style.display = "block";

    let current = 0;
    const max = 96;
    const duration = 240000; // 4 minuty = 240 000 ms
    const interval = duration / max;

    const progressInterval = setInterval(() => {
        if (current < max) {
            current++;
            loadingBar.style.width = `${current}%`;
            loadingPercent.textContent = `${current}%`;
        } else {
            clearInterval(progressInterval);
        }
    }, interval);

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        const timeRemaining = Math.max(0, duration - current * interval);

        setTimeout(() => {
            loadingBarContainer.style.display = "none";

            if (result.audio_base64) {
                const audio = document.getElementById("audio");
                audio.src = "data:audio/mpeg;base64," + result.audio_base64;
                showPlayer();
            } else {
                alert("Wystąpił problem z generowaniem audio.");
                console.error(result);
            }
        }, timeRemaining);

    } catch (error) {
        console.error("Błąd podczas wysyłania żądania:", error);
        alert("Coś poszło nie tak.");
        form.style.display = "block";
        loadingBarContainer.style.display = "none";
    }
});

document.addEventListener("DOMContentLoaded", () => {
  const steps = document.querySelectorAll(".step");
  const prevBtn = document.getElementById("prevBtn");
  const nextBtn = document.getElementById("nextBtn");
  const submitBtn = document.getElementById("submitBtn");
  const stepIndicator = document.getElementById("step-indicator");
  let currentStep = 0;

  function showStep(index) {
    steps.forEach((step, i) => {
      step.classList.toggle("hidden", i !== index);
    });
    prevBtn.classList.toggle("hidden", index === 0);
    nextBtn.classList.toggle("hidden", index === steps.length - 1);
    submitBtn.classList.toggle("hidden", index !== steps.length - 1);
    if (stepIndicator) {
      stepIndicator.textContent = `Krok ${index + 1} z ${steps.length}`;
    }
  }

  if (prevBtn && nextBtn && submitBtn && steps.length > 0) {
    prevBtn.addEventListener("click", () => {
      if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
      }
    });

    nextBtn.addEventListener("click", () => {
      const textarea = steps[currentStep].querySelector("textarea");
      if (textarea && textarea.checkValidity()) {
        currentStep++;
        showStep(currentStep);
      } else {
        textarea.reportValidity();
      }
    });

    showStep(currentStep);
  }
});
