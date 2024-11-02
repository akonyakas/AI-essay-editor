function submitText() {
    const text = document.getElementById('essayInput').value;
    const resultsContainer = document.getElementById('resultsContainer');

    fetch('/ai-essay-editor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        resultsContainer.innerHTML = ''; // Clear previous results
        data.forEach(item => {
            const sentenceBox = document.createElement('div');
            sentenceBox.classList.add('sentence-box');

            const originalSentence = document.createElement('p');
            originalSentence.classList.add('original-sentence');
            originalSentence.textContent = `Original: ${item.original_sentence}`;
            
            sentenceBox.appendChild(originalSentence);

            if (item.revised_sentence) {
                const revisedSentence = document.createElement('p');
                revisedSentence.classList.add('revised-sentence');
                revisedSentence.textContent = `Revised: ${item.revised_sentence}`;
                sentenceBox.appendChild(revisedSentence);
            }

            const explanation = document.createElement('p');
            explanation.classList.add('explanation');
            explanation.textContent = `Explanation: ${item.explanation}`;
            sentenceBox.appendChild(explanation);

            resultsContainer.appendChild(sentenceBox);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
