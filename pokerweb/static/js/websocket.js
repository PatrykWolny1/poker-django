class TaskManager {
    constructor() {
        this.lastProgress = 0;
        this.progressTimeout = null;
        this.lastDataScript = "";
        this.lastClickedPermsCombs = true;
        this.progress = 0;

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

        // Set up permsButton and combsButton to toggle each other
        this.elements.permsButton.addEventListener('click', () => this.handleTaskSelection(this.elements.permsButton, '/permutacje_view/'));
        this.elements.combsButton.addEventListener('click', () => this.handleTaskSelection(this.elements.combsButton, '/kombinacje_view/'));

        this.elements.combsButton.disabled = true;
        this.elements.permsButton.disabled = false;
        
        // Start and stop task buttons
        this.elements.startTaskButton.onclick = () => this.startTask();
        this.elements.stopTaskButton.onclick = () => this.stopTask();
        
        // Download button with confirmation
        this.elements.downloadButton.onclick = () => this.confirmDownload();

        // Stop task on page unload
        window.addEventListener("beforeunload", () => this.handleBeforeUnload());
    }

    handleTaskSelection(selectedButton, url) {
        // Enable all other task buttons
        for (const [buttonKey] of Object.entries(this.taskButtons)) {
            const buttonElement = this.elements[buttonKey];
            if (buttonElement !== selectedButton) {
                buttonElement.disabled = false;
            }
        }

        // Disable the selected button and enable the other one if it's either permsButton or combsButton
        if (selectedButton === this.elements.permsButton) {
            this.elements.combsButton.disabled = false;
        } else if (selectedButton === this.elements.combsButton) {
            this.elements.permsButton.disabled = false;
        }

        // Disable the selected button
        selectedButton.disabled = true;

        // Trigger task for selected button's view
        this.initiateTask(url);
    }

    initiateTask(url) {
        fetch(url, { method: 'POST' })
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
        fetch('/start_task_view/', { method: 'POST' })
            .then(response => response.json())
            .then(() => {
                this.elements.startTaskButton.disabled = true;
                this.elements.downloadButton.disabled = true;

                // Disable all task buttons when starting
                Object.keys(this.taskButtons).forEach(buttonKey => {
                    this.elements[buttonKey].disabled = true;
                });

                clearTimeout(this.progressTimeout);
                this.progressTimeout = setTimeout(() => this.checkProgressHanging(), 1000);
                this.connectWebSocket();
                this.resetProgressBar();

                // Maintain perms/combs button state as per previous functionality
                if (this.elements.combsButton.disabled) {
                    this.elements.permsButton.disabled = true;
                    this.lastClickedPermsCombs = true;
                } else if (this.elements.permsButton.disabled) {
                    this.elements.combsButton.disabled = true;
                    this.lastClickedPermsCombs = false;
                }
            })
            .catch(error => console.error('Error starting task:', error));
    }

    stopTask() {
        fetch('/stop_task_view/', { method: 'POST' })
            .then(response => response.json())
            .then(() => {
                this.elements.startTaskButton.disabled = false;
                this.elements.downloadButton.disabled = false;

                // Re-enable task buttons after stopping
                Object.keys(this.taskButtons).forEach(buttonKey => {
                    this.elements[buttonKey].disabled = false;
                });

                // Restore perms/combs button state based on last selection
                if (!this.lastClickedPermsCombs) {
                    this.elements.permsButton.disabled = true;
                    this.elements.combsButton.disabled = false;
                } else {
                    this.elements.combsButton.disabled = true;
                    this.elements.permsButton.disabled = false;
                }

                clearTimeout(this.progressTimeout);
            })
            .catch(error => console.error('Error stopping task:', error));
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
        
        if ('progress' in data) {
            this.updateProgress(data.progress);
        }
        
        if ('data_script' in data) {
            this.updateDataScript(data.data_script);
        }
        
        if (data.progress == 100) {
            this.finalizeProgress();
        }
    }

    updateProgress(newProgress) {
        this.progress = newProgress;
        this.lastProgress = this.progress;
        clearTimeout(this.progressTimeout);
        this.progressTimeout = setTimeout(() => this.checkProgressHanging(), 1000);
        
        this.elements.startTaskButton.disabled = (this.progress > 0 && this.progress < 100);
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
 //////////////////////////////////////////////Perm on -> finish -> perm on
    finalizeProgress() {
        this.elements.downloadButton.disabled = false;

        // Enable all task buttons
        for (const buttonKey of Object.keys(this.taskButtons)) {
            this.elements[buttonKey].disabled = false;
        }
    
        // Determine if any task buttons are still enabled
        const enabledTaskButtons = Object.keys(this.taskButtons).filter(buttonKey => {
            return !this.elements[buttonKey].disabled;
        });
    
        // If any task button is still enabled, we keep it enabled
        if (enabledTaskButtons.length > 0) {
            this.elements[enabledTaskButtons[0]].disabled = true; // Keep one enabled
        }
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
        if (this.lastProgress === 0 || this.lastProgress > 0) {
            this.elements.startTaskButton.disabled = false;
        }
    }

    resetProgressBar() {
        this.elements.progressBar.style.width = 0;
        this.elements.progressBar.innerHTML = '';
    }

    handleBeforeUnload() {
        fetch('/stop_task_view/', { method: 'POST' })
            .then(() => console.log('Task stopped on refresh.'))
            .catch(error => console.error('Error stopping task:', error));
        this.resetProgressBar();
    }
}

// Initialize the TaskManager class once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const taskManager = new TaskManager();
});