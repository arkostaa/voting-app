async function sendVote(tech) {
    const alertBox = document.getElementById('alert-box');
    
    const spanA = document.getElementById('count-a');
    const spanB = document.getElementById('count-b');

    // Get option names from the data-key attribute
    const keyA = spanA.getAttribute('data-key');
    const keyB = spanB.getAttribute('data-key');

    try {
        const response = await fetch('/api/vote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vote: tech })
        });

        const result = await response.json();

        if (response.ok) {
            // Update counts from the response's `results` key
            if (result.results) {
                spanA.innerText = result.results[keyA] || 0;
                spanB.innerText = result.results[keyB] || 0;
            }

            alertBox.className = 'alert alert-success';
            alertBox.innerText = result.message;
            alertBox.classList.remove('d-none');
        } else {
            alertBox.className = 'alert alert-danger';
            alertBox.innerText = "Error: " + result.message;
            alertBox.classList.remove('d-none');
        }

    } catch (error) {
        console.error('Error:', error);
        alertBox.className = 'alert alert-danger';
        alertBox.innerText = "Network error!";
        alertBox.classList.remove('d-none');
    }
}