
document.getElementById('bibleForm').addEventListener('submit', async function (e) {
  e.preventDefault();

  const book = document.getElementById('book').value;
  const chapter = document.getElementById('chapter').value;
  const verseFrom = document.getElementById('verseFrom').value;
  const verseTo = document.getElementById('verseTo').value;

  if (!book || !chapter || !verseFrom) {
    alert('Uzupełnij księgę, rozdział i początkowy werset.');
    return;
  }

  let reference = `${book} ${chapter}:${verseFrom}`;
  if (verseTo) {
    reference += `-${verseTo}`;
  }

  const responseDiv = document.getElementById('response');
  responseDiv.innerHTML = '⏳ Trwa pobieranie wersetu i generowanie wyjaśnienia...';

  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: reference })
    });

    const data = await res.json();

    if (res.ok) {
      responseDiv.innerHTML = `
        <h3>Werset:</h3>
        <p>${data.verse}</p>
        <h3>Wyjaśnienie:</h3>
        <p>${data.answer}</p>
      `;
    } else {
      responseDiv.innerHTML = `<p><strong>Błąd:</strong> ${data.answer}</p>`;
    }
  } catch (err) {
    responseDiv.innerHTML = '<p><strong>Błąd połączenia z serwerem.</strong></p>';
  }
});
