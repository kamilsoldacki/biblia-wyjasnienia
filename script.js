fetch('bibleStructure_full.json')
  .then(response => response.json())
  .then(bibleStructure => {
    const bookSelect = document.getElementById('book');
    const chapterInput = document.getElementById('chapter');
    const verseFromInput = document.getElementById('verseFrom');
    const verseToInput = document.getElementById('verseTo');

    // 1. Wypełnij select z księgami
    Object.keys(bibleStructure).forEach(book => {
      const option = document.createElement('option');
      option.value = book;
      option.textContent = book;
      bookSelect.appendChild(option);
    });

    // 2. Ogranicz rozdziały
    bookSelect.addEventListener('change', () => {
      const selectedBook = bookSelect.value;
      const maxChapter = bibleStructure[selectedBook]?.chapters || 1;
      chapterInput.value = 1;
      chapterInput.max = maxChapter;
    });

    // 3. Ogranicz wersety
    chapterInput.addEventListener('change', () => {
      const selectedBook = bookSelect.value;
      const selectedChapter = chapterInput.value;
      const maxVerse = bibleStructure[selectedBook]?.verses[selectedChapter] || 1;
      verseFromInput.value = 1;
      verseFromInput.max = maxVerse;
      verseToInput.value = '';
      verseToInput.max = maxVerse;
    });
  })
  .catch(error => {
    console.error("Błąd wczytywania struktury Biblii:", error);
  });
