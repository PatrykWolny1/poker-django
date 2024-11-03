let lastProgress = 0;
let progressTimeout;
let lastDataScript = ""; // Variable to store the last received data_script

document.addEventListener("DOMContentLoaded", function() {

        const pageType = document.body.getAttribute("data-page-type");

        const startTaskButton = document.getElementById("startTaskButton");
        const stopTaskButton = document.getElementById("stopTaskButton");
        const progressBar = document.getElementById('progressBar');
        const dataScriptDiv = document.getElementById('dataScript');
        const downloadButton = document.getElementById("downloadButton");

        startTaskButton.disabled = false;

        progressBar.style.width = 0;
        progressBar.innerHTML = '';

        downloadButton.onclick = function () {
            const userConfirmed = confirm("Pobrać plik?");
        
            if (userConfirmed) {
                // Redirect to the download view URL
                window.location.href = '/download_saved_file/';
                resetProgressBar()
            } else {
                console.log("Download canceled by user.");
            }
        };

        // Function to check if progress is "hanging"
        function checkProgressHanging() {
            if (lastProgress === 0 && startTaskButton.disabled) {
                console.log("Progress is hanging at 0%. Enabling startTaskButton.");
                startTaskButton.disabled = false;
            } else if (lastProgress > 0 && startTaskButton.disabled) {
                console.log("Progress is hanging above 0%. Enabling startTaskButton.");
                startTaskButton.disabled = false;
            }
        }

        startTaskButton.onclick = function () {
            // First, call stop_task_view to ensure any running tasks are stopped
            fetch('/start_task_view/', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log("Previous task stopped:", data);
                    // Now, start the new task
                    startTaskButton.disabled = true;
                    clearTimeout(progressTimeout)
                    progressTimeout = setTimeout(checkProgressHanging, 1000); // 5 seconds (adjust as needed)
                    connectWebSocket();
                    resetProgressBar();
                })
                .catch(error => console.error('Error starting task:', error));
        };

        stopTaskButton.onclick = function () {
            fetch('/stop_task_view/', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    console.log("Task stopped:", data);
                    // Reset progress bar
                    // resetProgressBar()
                    startTaskButton.disabled = false;

                    clearTimeout(progressTimeout);
                })
                .catch(error => console.error('Error stopping task:', error));
        };

        // if (pageType === "initial") {
        //     connectWebSocket(); // Initialize WebSocket for the initial load
        // }

        function connectWebSocket() {
            const socket = new WebSocket('wss://127.0.0.1:8001/ws/progress/');

            socket.onopen = function() {
                console.log("WebSocket connection opened");
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                console.log("Received message:", data.message);  // This should log "WebSocket connection successful!"
                


                if ('progress' in data) {
                    const progress = data.progress;
                    console.log("Received progress:", progress);  // Debug log

                    lastProgress = progress;
                    clearTimeout(progressTimeout);
                    progressTimeout = setTimeout(checkProgressHanging, 1000); // Reset for another 5 seconds        

                    if (progress == 0 || progress == 100) {
                        startTaskButton.disabled = false;
                        if (progress == 100) {
                            progressBar.style.width = progress + '%';
                            progressBar.innerHTML = progress + '%';        
                        }
                    }
                    if (progress > 0 && progress < 100) {
                        startTaskButton.disabled = true;
                        progressBar.style.width = progress + '%';
                        progressBar.innerHTML = progress + '%';    
                    }
                }
                if ('data_script' in data) {
                    const data_script = data.data_script;
                    
                    lastDataScript = data_script; // Store the latest data_script

                    console.log("Received data_script:", data_script);  // Debug log
                    if (dataScriptDiv.style.display === "none") {
                        dataScriptDiv.style.display = "block"; // Show data-script container
                    }
                    dataScriptDiv.innerHTML += data_script + "<br>";  
                }

                if (data.progress > 100) {
                    const data_script = data.data_script;
                    dataScriptDiv.innerHTML += data_script + "<br>";  
                    socket.close();
                }
            };

            socket.onclose = function(event) {
                console.log("WebSocket connection closed");
            }
        };

        function resetProgressBar() {
            const progressBar = document.getElementById('progressBar');
            progressBar.style.width = 0;
            progressBar.innerHTML = '';
        }
        
        connectWebSocket();

        window.addEventListener("beforeunload", function() {
            fetch('/stop_task_view/', { method: 'POST' })  // Make a POST request to stop the task
                .then(response => console.log('Task stopped on refresh.'))
                .then(data => {
                    console.log("Restarting progress bar:", data);
                    // Reset progress bar
                    resetProgressBar();
                })
                .catch(error => console.error('Error stopping task:', error));
        });
});