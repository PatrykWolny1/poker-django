class CardsPermutations {
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
            startTaskButton: document.getElementById(this.isMobile ? "mobileStartTaskButton" : "startTaskButton"),
            stopTaskButton: document.getElementById(this.isMobile ? "mobileStopTaskButton" : "stopTaskButton"),
            progressBar: document.getElementById(this.isMobile ? "mobileProgressBar" : "progressBar"),
            dataScriptDiv: document.getElementById(this.isMobile ? "mobileDataScript" : "dataScript"),
            downloadButton: document.getElementById(this.isMobile ? "mobileDownloadButton" : "downloadButton"),
            permsButton: document.getElementById(this.isMobile ? "mobilePermsButton" : "permsButton"),
            combsButton: document.getElementById(this.isMobile ? "mobileCombsButton" : "combsButton"),

            highcardButton: document.getElementById(this.isMobile ? "mobileHighcardButton" : "highcardButton"),
            onepairButton: document.getElementById(this.isMobile ? "mobileOnepairButton" : "onepairButton"),
            twopairsButton: document.getElementById(this.isMobile ? "mobileTwopairsButton" : "twopairsButton"),
            threeofakindButton: document.getElementById(this.isMobile ? "mobileThreeofakindButton" : "threeofakindButton"),
            straightButton: document.getElementById(this.isMobile ? "mobileStraightButton" : "straightButton"),
            colorButton: document.getElementById(this.isMobile ? "mobileColorButton" : "colorButton"),
            fullButton: document.getElementById(this.isMobile ? "mobileFullButton" : "fullButton"),
            carriageButton: document.getElementById(this.isMobile ? "mobileCarriageButton" : "carriageButton"),
            straightflushButton: document.getElementById(this.isMobile ? "mobileStraightflushButton" : "straightflushButton"),
            straightroyalflushButton: document.getElementById(this.isMobile ? "mobileStraightroyalflushButton" : "straightroyalflushButton"),
        };

        // Task buttons and corresponding URLs
        this.taskButtons = {
            highcardButton: "/high_card_view/",
            onepairButton: "/one_pair_view/",
            twopairsButton: "/two_pairs_view/",
            threeofakindButton: "/three_of_a_kind_view/",
            straightButton: "/straight_view/",
            colorButton: "/color_view/",
            fullButton: "/full_view/",
            carriageButton: "/carriage_view/",
            straightflushButton: "/straight_flush_view/",
            straightroyalflushButton: "/straight_royal_flush_view/",

            permsButton: "/permutacje_view/",
            combsButton: "/kombinacje_view/",
        };
        window.addEventListener("resize", this.handleResize);

        this.initializeUI();
        this.setupEventListeners();
        // this.connectWebSocket();
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
                buttonElement.addEventListener("click", () => this.handleTaskSelection(buttonElement, url));
            }
        });

        this.elements.carriageButton.disabled = true;
        this.lastClickedArr = this.elements.carriageButton;

        this.elements.combsButton.disabled = true;
        this.elements.permsButton.disabled = false;
        this.lastClickedPermsCombs = true;

        this.updateMaxAllowedValue();

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

        this.elements = {
            startTaskButton: document.getElementById(this.isMobile ? "mobileStartTaskButton" : "startTaskButton"),
            stopTaskButton: document.getElementById(this.isMobile ? "mobileStopTaskButton" : "stopTaskButton"),
            progressBar: document.getElementById(this.isMobile ? "mobileProgressBar" : "progressBar"),
            dataScriptDiv: document.getElementById(this.isMobile ? "mobileDataScript" : "dataScript"),
            downloadButton: document.getElementById(this.isMobile ? "mobileDownloadButton" : "downloadButton"),
            permsButton: document.getElementById(this.isMobile ? "mobilePermsButton" : "permsButton"),
            combsButton: document.getElementById(this.isMobile ? "mobileCombsButton" : "combsButton"),
            highcardButton: document.getElementById(this.isMobile ? "mobileHighcardButton" : "highcardButton"),
            onepairButton: document.getElementById(this.isMobile ? "mobileOnepairButton" : "onepairButton"),
            twopairsButton: document.getElementById(this.isMobile ? "mobileTwopairsButton" : "twopairsButton"),
            threeofakindButton: document.getElementById(this.isMobile ? "mobileThreeofakindButton" : "threeofakindButton"),
            straightButton: document.getElementById(this.isMobile ? "mobileStraightButton" : "straightButton"),
            colorButton: document.getElementById(this.isMobile ? "mobileColorButton" : "colorButton"),
            fullButton: document.getElementById(this.isMobile ? "mobileFullButton" : "fullButton"),
            carriageButton: document.getElementById(this.isMobile ? "mobileCarriageButton" : "carriageButton"),
            straightflushButton: document.getElementById(this.isMobile ? "mobileStraightflushButton" : "straightflushButton"),
            straightroyalflushButton: document.getElementById(this.isMobile ? "mobileStraightroyalflushButton" : "straightroyalflushButton"),
        };
        
        // Task buttons and corresponding URLs
        this.taskButtons = {
            highcardButton: "/high_card_view/",
            onepairButton: "/one_pair_view/",
            twopairsButton: "/two_pairs_view/",
            threeofakindButton: "/three_of_a_kind_view/",
            straightButton: "/straight_view/",
            colorButton: "/color_view/",
            fullButton: "/full_view/",
            carriageButton: "/carriage_view/",
            straightflushButton: "/straight_flush_view/",
            straightroyalflushButton: "/straight_royal_flush_view/",

            permsButton: "/permutacje_view/",
            combsButton: "/kombinacje_view/",
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
        
        // if (window.env.IS_DEV.includes('yes')) {
        //     this.socket = new WebSocket('wss://127.0.0.1:8000/ws/perms_combs/');    
        // } else if (window.env.IS_DEV.includes('no')) {
        //     this.socket = new WebSocket('wss://pokersimulation.onrender.com/ws/perms_combs/');    //'wss://127.0.0.1:8000/ws/perms_combs/'
        // }
        try {
            if (this.enableStartTask) {
                // Fetch the session ID
                const response = await fetch('/get_session_id/');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.sessionId = await this.fetchSessionId(); 
                console.log("Session ID in connectWebSocket:", this.sessionId);
                // Construct the WebSocket URL
                const webSocketUrl = window.env.IS_DEV.includes("yes")
                    ? `wss://127.0.0.1:8000/ws/perms_combs/?session_id=${this.sessionId}`
                    : `wss://pokersimulation.onrender.com/ws/perms_combs/?session_id=${this.sessionId}`;
        
                console.log("Connecting to WebSocket:", webSocketUrl);
        
                // Create and return the WebSocket instance
                this.socket = new WebSocket(webSocketUrl);
            } else {
                console.log("Click Start button!");
                return;
            }
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
        const key_data_script = `data_script_${this.sessionId}`
        if (key_progress in data) {
            this.updateProgress(data[key_progress]);
            // this.lastProgressUpdateTime = Date.now(); // Update the last progress time

            // //Clear any existing timeout since we have new progress
            // clearTimeout(this.progressTimeout);
            
            // // Set a new timeout to check for hanging progress
            // this.progressTimeout = setTimeout(() => {
            //     this.requestLatestDataScript(); // Function to request latest data_script
            // }, this.progressUpdateThreshold);
            if (data.action == key_data_script) {
                this.updateDataScript(data[key_data_script]);
            }
        }
        if (key_data_script in data) {
            console.log(data[key_data_script])
            this.updateDataScript(data[key_data_script]);
        }

        if (data[key_progress] == 100) {
            this.finalizeProgress();
            if (key_data_script in data) {
                this.updateDataScript(data[key_data_script])
            }
        }
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

        this.elements.startTaskButton.disabled = false;
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

// Initialize the CardsPermutations class once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const cardsPermutations = new CardsPermutations();
});