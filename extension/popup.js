function analyzeNews() {
    var text = document.getElementById('newsText').value;

    if (text.trim() === '') {
        alert('Please paste a news article first!');
        return;
    }

    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';

    var xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://localhost:8000/predict', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onload = function() {
        if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);

            var resultDiv = document.getElementById('result');
            var resultTitle = document.getElementById('resultTitle');
            var resultConfidence = document.getElementById('resultConfidence');
            var resultMessage = document.getElementById('resultMessage');

            if (data.prediction === 'FAKE') {
                resultDiv.className = 'result fake';
                resultTitle.textContent = 'FAKE NEWS DETECTED!';
            } else {
                resultDiv.className = 'result real';
                resultTitle.textContent = 'REAL NEWS';
            }

            resultConfidence.textContent = 'Confidence: ' + data.confidence + '%';
            resultMessage.textContent = data.message;
            resultDiv.style.display = 'block';
        } else {
            alert('API Error! Status: ' + xhr.status);
        }
        document.getElementById('loading').style.display = 'none';
    };

    xhr.onerror = function() {
        alert('Connection failed! Make sure API is running on port 8000!');
        document.getElementById('loading').style.display = 'none';
    };

    xhr.send(JSON.stringify({ text: text }));
}
