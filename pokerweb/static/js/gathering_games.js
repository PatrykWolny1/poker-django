class GatheringGames {
    constructor() {
        this.lastProgress = 0;
        this.lastDataScript = "";
        this.lastClickedPermsCombs = true;
        this.lastClickedArr = null;
        this.progressTimeout = 0;
        this.progress = 0;
        this.progressUpdateThreshold = 500; // milliseconds
        this.lastProgressUpdateTime = Date.now(); // To track the last progress update
        this.maxAllowedValue = undefined;
        this.isMobile = window.innerWidth <= 768; // Determine if the view is mobile or desktop
        this.handleResize = this.handleResize.bind(this);
        this.socket = null;
        this.sessionId = null;
        this.enableStartTask = false;

        // UI Elements
        this.elements = {
            startTaskButton: document.getElementById(this.isMobile ? "mobileStartTaskButton" : "startTaskButton"),
            stopTaskButton: document.getElementById(this.isMobile ? "mobileStopTaskButton" : "stopTaskButton"),
            progressBar: document.getElementById(this.isMobile ? "mobileProgressBar" : "progressBar"),
            downloadButton: document.getElementById(this.isMobile ? "mobileDownloadButton" : "downloadButton"),
        };

        window.addEventListener("resize", this.handleResize);

        this.initializeUI();
        this.setupEventListeners();
        this.connectWebSocket();
    }

    initializeUI() {
        this.elements.startTaskButton.disabled = false;
        this.resetProgressBar();
    }

    setupEventListeners() {
        this.lastClickedArr = this.elements.carriageButton;

        this.lastClickedPermsCombs = true;

        this.elements.startTaskButton.addEventListener("click", () => this.showNumberPopup());
        // Start and stop task buttons

        this.elements.stopTaskButton.onclick = () => this.stopTask();

        // Download button with confirmation
        this.elements.downloadButton.onclick = () => this.confirmDownload();

        window.addEventListener("visibilitychange", () => {
            if (window.hidden) {
                this.handleBeforeUnload();
            }
        });

    }

    handleResize() {
        // Determine if the view is now mobile or desktop
        const isNowMobile = window.innerWidth <= 768;

        // Only execute if the view state (mobile/desktop) has changed
        if (isNowMobile !== this.isMobile) {
            this.isMobile = isNowMobile;
            console.log("Window resized, mobile view:", this.isMobile);
            this.updateElementsForResize();

            // Update the UI elements for mobile or desktop accordingly
        }
    }

    updateElementsForResize() {
        this.lastDataScript = "";

        // Reassign elements based on current view (mobile/desktop)

        this.elements = {
            startTaskButton: document.getElementById(this.isMobile ? "mobileStartTaskButton" : "startTaskButton"),
            stopTaskButton: document.getElementById(this.isMobile ? "mobileStopTaskButton" : "stopTaskButton"),
            progressBar: document.getElementById(this.isMobile ? "mobileProgressBar" : "progressBar"),
            downloadButton: document.getElementById(this.isMobile ? "mobileDownloadButton" : "downloadButton"),
        };
    
        // You can also perform additional updates if necessary, like:
        this.initializeUI(); // Reset UI settings if needed.
        this.setupEventListeners();
        this.connectWebSocket();
    }

    async fetchSessionId() {
        try {
            const response = await fetch('/api/fetch_session_id/');
            const data = await response.json();
            const sessionId = data.session_id;
            console.log("Session ID:", sessionId);
            return sessionId;
        } catch (error) {
            console.error("Error fetching session ID:", error);
        }
    }

    async connectWebSocket() {
        console.log(window.env.IS_DEV)
        
        try {
            // Fetch the session ID
            const response = await fetch('/get_session_id/');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.sessionId = await this.fetchSessionId(); 
            console.log("Session ID in connectWebSocket:", this.sessionId);
            // Construct the WebSocket URL
            const webSocketUrl = window.env.IS_DEV.includes("yes")
                ? `wss://127.0.0.1:8000/ws/gathering_games/?session_id=${this.sessionId}`
                : `wss://pokersimulation.onrender.com/ws/gathering_games/?session_id=${this.sessionId}`;
    
            console.log("Connecting to WebSocket:", webSocketUrl);
    
            // Create and return the WebSocket instance
            this.socket = new WebSocket(webSocketUrl);

        } catch (error) {
            console.error("Error creating WebSocket:", error);
            throw error; // Propagate the error for further handling
        }

        this.socket.onopen = () => console.log("WebSocket connection opened", this.socket);
        this.socket.onmessage = (event) => this.handleSocketMessage(event);
        this.socket.onclose = () => {
            console.log("WebSocket connection closed");
            this.socket.close();
        };
    }

    handleSocketMessage(event) {
        const data = JSON.parse(event.data);
        
        // Update progress
        const key_progress = `progress_${this.sessionId}`;
        if (key_progress in data) {
            this.updateProgress(data[key_progress]);
        }
        if (data[key_progress] == 100) {
            this.finalizeProgress();
        }
    }

    updateProgress(newProgress) {
        this.progress = newProgress;
        this.lastProgress = this.progress;

        // Only disable the start button if the task has not been stopped
        if (!this.isTaskStopped) {
            this.elements.startTaskButton.disabled = (this.progress > 0 && this.progress < 100);
        }

        this.elements.progressBar.style.width = this.progress + '%';
        this.elements.progressBar.innerHTML = this.progress + '%';
    }

    finalizeProgress() {
        this.isTaskStopped = false;
        this.elements.downloadButton.disabled = false;

        // Ensure the last clicked button remains disabled
        if (this.lastClickedArr) {
            this.lastClickedArr.disabled = true;
        }

        this.elements.startTaskButton.disabled = false;
        this.elements.downloadButton.disabled = false;
    }

    resetProgressBar() {
        this.elements.progressBar.style.width = "0";
        this.elements.progressBar.innerHTML = "";
    }

    getCSRFToken() {
        let token = document.cookie.split(';').find(row => row.startsWith('csrftoken='));
        return token ? token.split('=')[1] : '';
    }

    showNumberPopup() {
        this.updateMaxAllowedValue();
    
        // Create the overlay
        const overlay = document.createElement("div");
        overlay.className = "popup-overlay";
        
        const popup = document.createElement("div");
        popup.className = "popup";
    
        const message = document.createElement("p");
        message.innerText = `Podaj ilość układów do wygenerowania (maksimum: ${this.maxAllowedValue})`;
        popup.appendChild(message);
    
        const inputField = document.createElement("input");
        inputField.type = "number";
        inputField.max = this.maxAllowedValue;
        inputField.placeholder = `Wpisz ilość ≤ ${this.maxAllowedValue}`;
        popup.appendChild(inputField);
    
        const confirmButton = document.createElement("button");
        confirmButton.innerText = "OK";
        confirmButton.className = "popup-button";
        confirmButton.onclick = () => {
            const enteredValue = parseInt(inputField.value, 10);
            if (enteredValue && !isNaN(enteredValue) && enteredValue > 0 && enteredValue <= this.maxAllowedValue) {
                document.body.removeChild(overlay);
    
                // Send the entered value to Django
                fetch('/submit_number/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify({ value: enteredValue })
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Response from server:", data);
                    if (data.message) {
                        alert(data.message);  // Optionally display server response in an alert
                    }
                    this.startTask();  // Start the task with the entered value
                })
                .catch(error => {
                    console.error("Error sending number:", error);
                    alert("Błąd przy wysyłaniu danych. Spróbuj ponownie.");
                });
            } else {
                alert(`Wpisz właściwą wartość lub mniejszą od: ${this.maxAllowedValue}.`);
            }
        };
        popup.appendChild(confirmButton);
    
        const cancelButton = document.createElement("button");
        cancelButton.innerText = "Anuluj";
        cancelButton.className = "popup-button";
        cancelButton.onclick = () => {
            document.body.removeChild(overlay);
        };
        popup.appendChild(cancelButton);
    
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
    
        // Optional: Close popup with escape key
        document.addEventListener('keydown', function onKeydown(event) {
            if (event.key === "Escape") {
                document.body.removeChild(overlay);
                document.removeEventListener('keydown', onKeydown);
            }
        });
    }


    confirmDownload() {
        const userConfirmed = confirm("Pobrać plik?");
        if (userConfirmed) {
            window.location.href = `/download_saved_file/?session_id=${this.sessionId}`;
            this.resetProgressBar();
        } else {
            console.log("Download canceled by user.");
        }
    }
    
    handleBeforeUnload() {
        const url = '/stop_task_view/';
        // Use fetch instead of sendBeacon to allow custom headers
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',  // Ensure it's JSON
                'X-CSRFToken': this.getCSRFToken(),  // Include CSRF token in the headers
            },
            body: JSON.stringify(),  // Send any data you need in the body
        })
        .then(() => console.log('Task stopped on refresh.'))
        .catch(error => console.error('Error stopping task:', error));
        this.finalizeProgress();
        this.resetProgressBar();
    }

    initiateTask(url) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Ensure it's JSON
                'X-CSRFToken': this.getCSRFToken(),  // Include CSRF token
            },
            body: JSON.stringify({})
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => console.log('Task initiated:', data))
        .catch(error => console.error('Error starting task:', error));
    }

    startTask() {
        fetch('/start_task_combs_perms/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Ensure it's JSON
                'X-CSRFToken': this.getCSRFToken(),  // Include CSRF token
            },
            body: JSON.stringify({ /* add any request data here */ })
        })
        .then(response => response.json())
        .then(async () => {
            this.elements.startTaskButton.disabled = true;
            this.elements.downloadButton.disabled = true;
            
            // Maintain perms/combs button state as per previous functionality
            if (this.elements.combsButton.disabled) {
                this.elements.permsButton.disabled = true;
                this.lastClickedPermsCombs = true;
            } else if (this.elements.permsButton.disabled) {
                this.elements.combsButton.disabled = true;
                this.lastClickedPermsCombs = false;
            }

            // Disable all task buttons when starting
            Object.keys(this.taskButtons).forEach(buttonKey => {
                this.elements[buttonKey].disabled = true;
            });
            this.enableStartTask = true;
            this.connectWebSocket();
            this.resetProgressBar();


        })
        .catch(error => console.error('Error starting task:', error));
    }

    stopTask() { 
        fetch('/stop_task_combs_perms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({session_id : this.sessionId}),
            credentials: 'same-origin'
        })
        .then(response => response.json())  // Read the JSON data once
        .then(data => {
            console.log(data)

            if (data.message === `Task stopped for session ${this.sessionId}`) {
                console.log('Task stopped successfully');
                this.finalizeProgress();
                this.resetProgressBar();
                this.isTaskStopped = true;
                this.elements.startTaskButton.disabled = false
            }
        })
        .catch(error => {
            console.error('Error stopping task:', error);
            alert('An error occurred while stopping the task. Please try again.');
        });
 
    }
}

// Initialize the GatheringGames class once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const gatheringGames = new GatheringGames();
});