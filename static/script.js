
document.getElementById("explain-button").addEventListener("click", async () => {
    const book = document.getElementById("book-select").value;
    const chapter = document.getElementById("chapter-input").value;
    const verseFrom = document.getElementById("verse-from-input").value;
    const verseTo = document.getElementById("verse-to-input").value;

    const payload = {
        book: book,
        chapter: chapter,
        verse_from: verseFrom,
        verse_to: verseTo || verseFrom
    };

    document.getElementById("verse").innerText = "⏳ Ładowanie wersetu...";
    document.getElementById("output").innerText = "";

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error("Nie udało się pobrać danych.");
        }

        const data = await response.json();

        document.getElementById("verse").innerText = `Werset:
${data.verse}`;
        document.getElementById("output").innerText = `Wyjaśnienie:
${data.explanation}`;
    } catch (error) {
        document.getElementById("verse").innerText = "❌ Błąd podczas pobierania wersetu.";
        document.getElementById("output").innerText = "";
        console.error(error);
    }
});
