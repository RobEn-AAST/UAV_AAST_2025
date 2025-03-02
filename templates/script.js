function convertFile(fileType) {
    fetch('/convert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `file_type=${fileType}`
    })
    .then(response => response.json())
    .then(data => {
        updateStatus(data.message, data.status);
    })
    .catch(error => {
        updateStatus('Error: ' + error, 'error');
    });
}

function startMission(missionType) {
    fetch('/mission', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `mission_type=${missionType}`
    })
    .then(response => response.json())
    .then(data => {
        updateStatus(data.message, data.status);
    })
    .catch(error => {
        updateStatus('Error: ' + error, 'error');
    });
}

function updateStatus(message, status) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status-box ${status}`;
}