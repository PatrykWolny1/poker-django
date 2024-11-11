class TaskManager {
    constructor() {
        this.lastProgress = 0;
        this.progressTimeout = null;
        this.lastDataScript = "";
        this.lastClickedPermsCombs = true;
        this.lastClickedArr = null;
        this.progress = 0;
        this.progressUpdateThreshold = 500; // milliseconds
        this.lastProgressUpdateTime = Date.now() // To track the last progress update
        this.maxAllowedValue = undefined;
        
        this.arrangementLimits = {
            highcardButton: { max_perms: 156304800, max_combs: 1302540 },
            onepairButton: { max_perms: 131788800, max_combs: 1098240 },
            twopairsButton: { max_perms: 14826240, max_combs: 123552 },
            threeofakindButton: { max_perms: 6589440, max_combs: 54912 },
            straightButton: { max_perms: 1224000, max_combs: 10200 },
            colorButton: { max_perms: 612960, max_combs: 5108 },
            fullButton: { max_perms: 449280, max_combs: 3744 },
            carriageButton: { max_perms: 74880, max_combs: 624 },
            straightflushButton: { max_perms: 4320, max_combs: 36 },
            straightroyalflushButton: { max_perms: 480, max_combs: 4 },
        };

        // UI Elements
        this.elements = {
            startTaskButton: document.getElementById("startTaskButton"),
            stopTaskButton: document.getElementById("stopTaskButton"),
            progressBar: document.getElementById('progressBar'),
            dataScriptDiv: document.getElementById('dataScript'),
            downloadButton: document.getElementById("downloadButton"),
            permsButton: document.getElementById('permsButton'),
            combsButton: document.getElementById('combsButton'),

            highcardButton: document.getElementById('highcardButton'),
            onepairButton: document.getElementById('onepairButton'),
            twopairsButton: document.getElementById('twopairsButton'),
            threeofakindButton: document.getElementById('threeofakindButton'),
            straightButton: document.getElementById('straightButton'),
            colorButton: document.getElementById('colorButton'),
            fullButton: document.getElementById('fullButton'),
            carriageButton: document.getElementById('carriageButton'),
            straightflushButton: document.getElementById('straightflushButton'),
            straightroyalflushButton: document.getElementById('straightroyalflushButton'),
        };

        // Task buttons and corresponding URLs
        this.taskButtons = {
            highcardButton: '/high_card_view/',
            onepairButton: '/one_pair_view/',
            twopairsButton: '/two_pairs_view/',
            threeofakindButton: '/three_of_a_kind_view/',
            straightButton: '/straight_view/',
            colorButton: '/color_view/',
            fullButton: '/full_view/',
            carriageButton: '/carriage_view/',
            straightflushButton: '/straight_flush_view/',
            straightroyalflushButton: '/straight_royal_flush_view/',

            permsButton: '/permutacje_view/',
            combsButton: '/kombinacje_view/'
        };

        this.initializeUI();
        this.setupEventListeners();
        this.connectWebSocket();
    }

    initializeUI() {
        this.elements.startTaskButton.disabled = false;
        this.resetProgressBar();

        // Automatically call view for any initially disabled task button
        Object.entries(this.taskButtons).forEach(([buttonKey, url]) => {
            const buttonElement = this.elements[buttonKey];
            if (buttonElement && buttonElement.disabled) {
                this.initiateTask(url);
            }
        });
    }

    setupEventListeners() {
        // Set up click event listeners for task buttons
        Object.entries(this.taskButtons).forEach(([buttonKey, url]) => {
            const buttonElement = this.elements[buttonKey];
            if (buttonElement) {
                buttonElement.addEventListener('click', () => this.handleTaskSelection(buttonElement, url));
            }
        });

        this.elements.carriageButton.disabled = true;
        this.lastClickedArr = this.elements.carriageButton;
        
        this.elements.combsButton.disabled = true;
        this.elements.permsButton.disabled = false;
        this.lastClickedPermsCombs = true;
        
        this.updateMaxAllowedValue()

        this.elements.startTaskButton.addEventListener('click', () => this.showNumberPopup());
        // Start and stop task buttons

        this.elements.stopTaskButton.onclick = () => this.stopTask();
        
        // Download button with confirmation
        this.elements.downloadButton.onclick = () => this.confirmDownload();
        window.addEventListener("visibilitychange", () => {
            if (window.hidden) {
                this.handleBeforeUnload();
            }
        });
        // Stop task on page unload
        // window.addEventListener("beforeunload", () => this.handleBeforeUnload());
    }
    updateMaxAllowedValue() {
        // Check which button is disabled to determine the source of maxAllowedValue
        const isPermsDisabled = this.elements.permsButton.disabled;
        const isCombsDisabled = this.elements.combsButton.disabled;

        // Loop through arrangement buttons to set maxAllowedValue
        for (const [buttonKey, limits] of Object.entries(this.arrangementLimits)) {
            const buttonElement = this.elements[buttonKey];
            
            // Check if the button is the last clicked arrangement button
            if (buttonElement === this.lastClickedArr) {
                // If permsButton is disabled, assign max_perms; if combsButton is disabled, assign max_combs
                this.maxAllowedValue = isPermsDisabled ? limits.max_perms : isCombsDisabled ? limits.max_combs : Infinity;
                break;
            }
        }
    }
    // // Function to get CSRF token from cookies
    // getCookie(name) {
    //     let cookieValue = null;
    //     if (document.cookie && document.cookie !== '') {
    //         const cookies = document.cookie.split(';');
    //         for (let i = 0; i < cookies.length; i++) {
    //             const cookie = cookies[i].trim();
    //             if (cookie.substring(0, name.length + 1) === (name + '=')) {
    //                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
    //                 break;
    //             }
    //         }
    //     }
    //     return cookieValue;
    // }

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

    handleTaskSelection(selectedButton, url) {
        // Enable all arrangement task buttons initially
        for (const [buttonKey] of Object.entries(this.taskButtons)) {
            const buttonElement = this.elements[buttonKey];
            if (buttonElement !== this.elements.permsButton && buttonElement !== this.elements.combsButton) {
                buttonElement.disabled = false;
            }
        }
        
        // Toggle between `permsButton` and `combsButton` clicks
        if (selectedButton === this.elements.permsButton || selectedButton === this.elements.combsButton) {
            // Disable the last clicked arrangement button if it exists
            if (this.lastClickedArr) {
                this.lastClickedArr.disabled = true;
            }
        } else {
            // For an arrangement button click, disable the previously clicked arrangement button if it exists
            if (this.lastClickedArr && this.lastClickedArr !== selectedButton) {
                this.lastClickedArr.disabled = false;
            }
            // Set the newly clicked arrangement button as the last clicked arrangement
            this.lastClickedArr = selectedButton;
        }

        // Toggle between enabling `permsButton` and `combsButton`
        if (selectedButton === this.elements.permsButton) {
            this.elements.permsButton.disabled = true;
            this.elements.combsButton.disabled = false;
            // Set maxAllowedValue based on lastClickedArr's max_perms
            this.maxAllowedValue = this.lastClickedArr ? this.arrangementLimits[this.lastClickedArr.id]?.max_perms : Infinity;
            this.lastClickedPermsCombs = false;
        } else if (selectedButton === this.elements.combsButton) {
            this.elements.combsButton.disabled = true;
            this.elements.permsButton.disabled = false;
            // Set maxAllowedValue based on lastClickedArr's max_combs
            this.maxAllowedValue = this.lastClickedArr ? this.arrangementLimits[this.lastClickedArr.id]?.max_combs : Infinity;
            this.lastClickedPermsCombs = true;
        } else {
            // If an arrangement button is clicked, set maxAllowedValue based on perms/combs status
            this.maxAllowedValue = this.lastClickedPermsCombs
                ? this.arrangementLimits[selectedButton.id]?.max_perms
                : this.arrangementLimits[selectedButton.id]?.max_combs;
        }
        

        selectedButton.disabled = true;

        // Trigger task for selected button's view
        this.initiateTask(url);
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
        fetch('/start_task_view/', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Ensure it's JSON
                'X-CSRFToken': this.getCSRFToken(),  // Include CSRF token
            },
            body: JSON.stringify({ /* add any request data here */ })
        })
        .then(response => response.json())
        .then(() => {
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

            clearTimeout(this.progressTimeout);
            this.progressTimeout = setTimeout(() => this.checkProgressHanging(), 10000);
            this.connectWebSocket();
            this.resetProgressBar();


        })
        .catch(error => console.error('Error starting task:', error));
    }

    stopTask() { 
        fetch('/stop_task_view/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({}),
            credentials: 'same-origin'
        })
        .then(response => response.json())  // Read the JSON data once
        .then(data => {
            console.log(data)

            if (data.status === 'Task stopped successfully') {
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

    confirmDownload() {
        const userConfirmed = confirm("Pobrać plik?");
        if (userConfirmed) {
            window.location.href = '/download_saved_file/';
            this.resetProgressBar();
        } else {
            console.log("Download canceled by user.");
        }
    }

    connectWebSocket() {
        this.socket = new WebSocket('wss://127.0.0.1:8001/ws/');
        
        this.socket.onopen = () => console.log("WebSocket connection opened");
        this.socket.onmessage = (event) => this.handleSocketMessage(event);
        this.socket.onclose = () => {
            console.log("WebSocket connection closed");
            this.socket.close();
        };
    }

    handleSocketMessage(event) {
        const data = JSON.parse(event.data);
        
        // Update progress
        if ('progress' in data) {
            this.updateProgress(data.progress);
            this.lastProgressUpdateTime = Date.now(); // Update the last progress time

            // Clear any existing timeout since we have new progress
            clearTimeout(this.progressTimeout);
            
            // Set a new timeout to check for hanging progress
            this.progressTimeout = setTimeout(() => {
                this.requestLatestDataScript(); // Function to request latest data_script
            }, this.progressUpdateThreshold);
            if (data.action == "request_latest_data_script") {
                this.updateDataScript(data.data_script);
            }
        }
        
        if ('data_script' in data) {
            this.updateDataScript(data.data_script);
        }

        if (data.progress == 100) {
            this.finalizeProgress();
            if ('data_script' in data) {
                this.updateDataScript(data.data_script)
            }
        }
    }

    updateProgress(newProgress) {
        this.progress = newProgress;
        this.lastProgress = this.progress;
        clearTimeout(this.progressTimeout);
        this.progressTimeout = setTimeout(() => this.checkProgressHanging(), 5000);

        // Only disable the start button if the task has not been stopped
        if (!this.isTaskStopped) {
            this.elements.startTaskButton.disabled = (this.progress > 0 && this.progress < 100);
        }
        
        this.elements.progressBar.style.width = this.progress + '%';
        this.elements.progressBar.innerHTML = this.progress + '%';
    }

    updateDataScript(dataScript) {
        this.lastDataScript = dataScript;

        if (this.elements.dataScriptDiv.style.display === "none") {
            this.elements.dataScriptDiv.style.display = "block";
        }
        
        const lines = this.elements.dataScriptDiv.innerHTML.trim().split('<br>');
        const lastEntry = lines[lines.length - 1];

        if (lastEntry !== this.lastDataScript) {
            this.elements.dataScriptDiv.innerHTML += this.lastDataScript + '<br>';
        }
    }

    // Function to request the latest data_script
    requestLatestDataScript() {
        // Your logic to request the latest data_script from the server
        // This could involve sending a message through the WebSocket or making an AJAX call
        console.log("Requesting latest data_script due to hanging progress");
        this.socket.send(JSON.stringify({ action: "request_latest_data_script" }));
    }

    finalizeProgress() {
        this.isTaskStopped = false;
        this.elements.downloadButton.disabled = false;

           // Enable all task buttons except the last clicked button
        for (const buttonKey of Object.keys(this.taskButtons)) {
            const buttonElement = this.elements[buttonKey];
            if (buttonElement !== this.lastClickedArr) {
                buttonElement.disabled = false;
            }
        }
        // Ensure the last clicked button remains disabled
        if (this.lastClickedArr) {
            this.lastClickedArr.disabled = true;
        }
        
        this.elements.startTaskButton.disabled = false
        this.elements.downloadButton.disabled = false;
        
        // Restore state for perms/combs button based on last selection
        if (!this.lastClickedPermsCombs) {
            this.elements.permsButton.disabled = true;
            this.elements.combsButton.disabled = false;
        } else {
            this.elements.combsButton.disabled = true;
            this.elements.permsButton.disabled = false;
        }
    }

    checkProgressHanging() {
        if (this.progress > 0 && this.progress < 100) {
            this.fetchLatestDataScript(); // Fetch the latest data script if progress is hanging
        }
    }

    resetProgressBar() {
        this.elements.progressBar.style.width = 0;
        this.elements.progressBar.innerHTML = '';
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
}

// Initialize the TaskManager class once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const taskManager = new TaskManager();
});