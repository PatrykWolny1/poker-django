let lastProgress = 0;
let progressTimeout;
let lastDataScript = ""; // Variable to store the last received data_script
let lastClickedPermsCombs = true;
let progress = 0

document.addEventListener("DOMContentLoaded", function() {

        const pageType = document.body.getAttribute("data-page-type");

        const startTaskButton = document.getElementById("startTaskButton");
        const stopTaskButton = document.getElementById("stopTaskButton");
        const progressBar = document.getElementById('progressBar');
        const dataScriptDiv = document.getElementById('dataScript');
        const downloadButton = document.getElementById("downloadButton");
        const permsButton = document.getElementById('permsButton');
        const combsButton = document.getElementById('combsButton');

        startTaskButton.disabled = false;

        progressBar.style.width = 0;
        progressBar.innerHTML = '';

        if (combsButton.disabled == true) {
            lastClickedPermsCombs = false

            fetch('/kombinacje_view/', { method: 'POST' })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Success:', data);
                })
                .catch(error => console.error('Error starting task:', error));
        } else if (permsButton.disabled == true) {
            lastClickedPermsCombs = true

            fetch('/permutacje_view/', { method: 'POST' })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Success:', data);
                })
                .catch(error => console.error('Error starting task:', error));
        }

        combsButton.addEventListener('click', () => {
            // Toggle the disabled property of button1
            permsButton.disabled = !permsButton.disabled;
            // Optionally, disable button2 after clicking
            combsButton.disabled = true; // Disable button 2 after click
            
            fetch('/kombinacje_view/', { method: 'POST' })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Success:', data);
                })
                .catch(error => console.error('Error starting task:', error));
        });
    
        permsButton.addEventListener('click', () => {
            // Toggle the disabled property of button2
            combsButton.disabled = !combsButton.disabled;
            // Optionally, disable button1 after clicking
            permsButton.disabled = true; // Disable button 1 after click

            fetch('/permutacje_view/', { method: 'POST' })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(text => {
                            throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Success:', data);
                })
                .catch(error => console.error('Error starting task:', error));
        });
        
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
                    downloadButton.disabled = true;

                    if (combsButton.disabled == true) {
                        permsButton.disabled = true;
                        lastClickedPermsCombs = true;
                    } else if (permsButton.disabled == true) {
                        combsButton.disabled = true;
                        lastClickedPermsCombs = false;
                    }

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
                    downloadButton.disabled = false;

                    if (lastClickedPermsCombs == false) {
                        permsButton.disabled = true;
                        combsButton.disabled = false;
                    } else if (lastClickedPermsCombs == true) {
                        combsButton.disabled = true;
                        permsButton.disabled = false;
                    }

                    clearTimeout(progressTimeout);
                })
                .catch(error => console.error('Error stopping task:', error));
        };

        // if (pageType === "initial") {
        //     connectWebSocket(); // Initialize WebSocket for the initial load
        // }

        function connectWebSocket() {
            const socket = new WebSocket('wss://127.0.0.1:8001/ws/');

            socket.onopen = function() {
                console.log("WebSocket connection opened");
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                console.log("Received message:", data.message);  // This should log "WebSocket connection successful!"
                
                if ('progress' in data) {
                    progress = data.progress;
                    console.log("Received progress:", progress);  // Debug log

                    lastProgress = progress;
                    clearTimeout(progressTimeout);
                    progressTimeout = setTimeout(checkProgressHanging, 1000); // Reset for another 5 seconds        

                    if (progress == 0 || progress == 100) {
                        startTaskButton.disabled = false;
                        progressBar.style.width = progress + '%';
                        progressBar.innerHTML = progress + '%'; 
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
                    dataScriptDiv.innerHTML += lastDataScript + '<br>';
                    console.log(dataScriptDiv.innerHTML)
                    const lines = dataScriptDiv.innerHTML.trim().split('<br>');

                    if (lines.length > 1) { 
                        const lastEntry = lines[lines.length-1];

                        if (lastEntry !== lastDataScript) {
                            dataScriptDiv.innerHTML += lastEntry;
                        }
                        console.log(lastEntry)
                    }
                } 
                
                if (progress == 100) {
                    downloadButton.disabled = false;
                    
                    lastDataScript = data.data_script

                    if (lastClickedPermsCombs == false) {
                        permsButton.disabled = true;
                        combsButton.disabled = false;
                    } else if (lastClickedPermsCombs == true) {
                        combsButton.disabled = true;
                        permsButton.disabled = false;
                    }

                    const lines = dataScriptDiv.innerHTML.trim().split('<br>');
                    if (lines.length > 1) { 
                        console.log(lines.length)
                        const lastEntry = lines[lines.length-1];
                        console.log(lastEntry)
                        if (lastEntry !== lastDataScript) {
                            dataScriptDiv.innerHTML += lastEntry;
                        } 
                    }
                }
            };

            socket.onclose = function(event) {
                console.log("WebSocket connection closed");
                socket.close();
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