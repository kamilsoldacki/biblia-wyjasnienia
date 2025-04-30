fetch('/static/bibleStructure_full.json')
  .then(response => response.json())
  .then(bibleStructure => {
    const bookSelect = document.getElementById('book');
    const chapterInput = document.getElementById('chapter');
    const verseFromInput = document.getElementById('verseFrom');
    const verseToInput = document.getElementById('verseTo');

    // 1. Aktualizuj listę ksiąg tylko jeśli chcesz generować ją dynamicznie
    // (Jeśli masz <optgroup> w HTML, to pomiń ten fragment):
    // Object.keys(bibleStructure).forEach(book => {
    //   const option = document.createElement('option');
    //   option.value = book;
    //   option.textContent = book;
    //   bookSelect.appendChild(option);
    // });

    // 2. Po zmianie księgi ustaw max rozdział
    bookSelect.addEventListener('change', () => {
      const selectedBook = bookSelect.value;
      const bookData = bibleStructure[selectedBook];

      if (bookData) {
        const maxChapter = bookData.chapters;
        chapterInput.value = 1;
        chapterInput.min = 1;
        chapterInput.max = maxChapter;
        updateVerseInputs(bookData, 1);
      }
    });

    // 3. Po zmianie rozdziału ustaw max werset
    chapterInput.addEventListener('change', () => {
      const selectedBook = bookSelect.value;
      const selectedChapter = parseInt(chapterInput.value);
      const bookData = bibleStructure[selectedBook];

      if (bookData && bookData.verses[selectedChapter]) {
        updateVerseInputs(bookData, selectedChapter);
      }
    });

    function updateVerseInputs(bookData, chapter) {
      const maxVerse = bookData.verses[chapter];
      verseFromInput.value = 1;
      verseFromInput.min = 1;
      verseFromInput.max = maxVerse;
      verseToInput.value = '';
      verseToInput.min = 1;
      verseToInput.max = maxVerse;
    }
  })
  .catch(error => {
    console.error("Błąd wczytywania struktury Biblii:", error);
  });
