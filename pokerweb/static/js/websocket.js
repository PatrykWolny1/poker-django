document.addEventListener("DOMContentLoaded", function() {

        const pageType = document.body.getAttribute("data-page-type");

        const progressBar = document.getElementById('progressBar');
        const dataScriptDiv = document.getElementById('dataScript');
        const downloadButton = document.getElementById("downloadButton");

        downloadButton.onclick = function () {
            const userConfirmed = confirm("Are you sure you want to download the file?");
        
            if (userConfirmed) {
                // Redirect to the download view URL
                window.location.href = '/download_saved_file/';
            } else {
                console.log("Download canceled by user.");
            }
        };
        if (pageType === "initial") {
            connectWebSocket(); // Initialize WebSocket for the initial load
        }
        function connectWebSocket() {
            const socket = new WebSocket('wss://127.0.0.1:8001/ws/progress/');

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                console.log("Received message:", data.message);  // This should log "WebSocket connection successful!"

                if ('progress' in data) {
                    const progress = data.progress;
                    console.log("Received progress:", progress);  // Debug log
                    progressBar.style.width = progress + '%';
                    progressBar.innerHTML = progress + '%';
                }
                if ('data_script' in data) {
                    const data_script = data.data_script;
                    console.log("Received data_script:", data_script);  // Debug log
                    if (dataScriptDiv.style.display === "none") {
                        dataScriptDiv.style.display = "block"; // Show data-script container
                    }
                    dataScriptDiv.innerHTML += data_script + "<br>";
                }

                if (progress >= 100) {
                    socket.close();
                }
            };

            socket.onclose = function(event) {
                console.log("WebSocket connection closed");
            };
        }   

});

window.addEventListener("beforeunload", function() {
    fetch('/stop_task_view/', { method: 'POST' })  // Make a POST request to stop the task
        .then(response => console.log('Task stopped on refresh.'))
        .catch(error => console.error('Error stopping task:', error));
});

