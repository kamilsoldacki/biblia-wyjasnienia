// 1) Ładowanie struktury Biblii i ustawianie limitów chapter/verse
fetch('/static/bibleStructure_full.json')
  .then(response => response.json())
  .then(bibleStructure => {
    const bookSelect = document.getElementById('book');
    const chapterInput = document.getElementById('chapter');
    const verseFromInput = document.getElementById('verseFrom');
    const verseToInput = document.getElementById('verseTo');

    bookSelect.addEventListener('change', () => {
      const bookData = bibleStructure[bookSelect.value];
      if (bookData) {
        chapterInput.value = 1;
        chapterInput.min = 1;
        chapterInput.max = bookData.chapters;
        updateVerseInputs(bookData, 1);
      }
    });

    chapterInput.addEventListener('change', () => {
      const bookData = bibleStructure[bookSelect.value];
      const ch = parseInt(chapterInput.value, 10);
      if (bookData && bookData.verses[ch]) {
        updateVerseInputs(bookData, ch);
      }
    });

    function updateVerseInputs(bookData, chapter) {
      const maxV = bookData.verses[chapter];
      verseFromInput.value = 1;
      verseFromInput.min = 1;
      verseFromInput.max = maxV;
      verseToInput.value = '';
      verseToInput.min = 1;
      verseToInput.max = maxV;
    }

    // 2) Obsługa formularza – po załadowaniu struktury podpinamy submit:
    const form = document.getElementById('bibleForm');
    const responseDiv = document.getElementById('response');
    const verseTextElem = document.getElementById('selected-verse-text');

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const book = bookSelect.value;
      const chapter = chapterInput.value;
      const verseFrom = verseFromInput.value;
      const verseTo = verseToInput.value;

      // przygotuj prompt i animację „kroków”
      let fragment = `${book} ${chapter}:${verseFrom}`;
      if (verseTo) fragment += `-${verseTo}`;
      const prompt = `Wyjaśnij fragment Biblii ${fragment}.`;

      const steps = [
        "Czytam wybrany fragment...",
        "Sprawdzam języki oryginalne...",
        "Szukam kontekstu historycznego...",
        "Układam wyjaśnienie..."
      ];
      let idx = 0;
      responseDiv.innerHTML = `<p>${steps[idx]}</p>`;
      const loading = setInterval(() => {
        idx++;
        if (idx < steps.length) {
          responseDiv.innerHTML = `<p>${steps[idx]}</p>`;
        }
      }, 2500);

      try {
        const res = await fetch('/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt,
            book,
            chapter,
            verse_start: verseFrom,
            verse_end: verseTo || null
          })
        });
        const data = await res.json();
        clearInterval(loading);

        // 3) Wstawiamy tekst wersetu
        verseTextElem.innerText = data.verse_text;

        // 4) Wstawiamy odpowiedź
        responseDiv.innerHTML =
          `<p><strong>Odpowiedź:</strong></p>
           <div>${marked.parse(data.answer)}</div>`;
      } catch (err) {
        clearInterval(loading);
        responseDiv.innerText = 'Wystąpił błąd. Spróbuj ponownie.';
        console.error(err);
      }
    });

  })
  .catch(error => {
    console.error("Błąd wczytywania struktury Biblii:", error);
  });
