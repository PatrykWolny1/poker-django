class DeepNeuralNetwork {
    static iteration = 0;
    static ifApply = 0;
    static onFirst = true;
    constructor() {
        this.progress = 0;
        this.lastProgress = 0; // Last recorded progress for comparison
        this.progressTimer = null; // Store reference to timeout
        this.maxAllowedValue = 10000;
        this.isMobile = window.innerWidth <= 768; // Determine if the view is mobile or desktop
        this.handleResize = this.handleResize.bind(this);
        this.socket = null;
        this.sessionId = null;
        this.enteredValue = null;
        this.lastClickedChoice = null;
        this.formData = null;

        // UI Elements
        this.elements = {
            startTaskButton: document.getElementById(this.isMobile ? "mobileStartTaskButton" : "startTaskButton"),
            progressBar: document.getElementById(this.isMobile ? "mobileProgressBar" : "progressBar"),
            downloadButton: document.getElementById(this.isMobile ? "mobileDownloadButton" : "downloadButton"),
            winsButton: document.getElementById(this.isMobile ? "mobileWinsButton" : "winsButton"),
            exchangeButton: document.getElementById(this.isMobile ? "mobileExchangeButton" : "exchangeButton"),
            plotButton: document.getElementById(this.isMobile ? "mobilePlotButton" : "plotButton"),
            dataScriptDiv: document.getElementById(this.isMobile ? "mobileDataScript" : "dataScript"),
            applyButton: document.getElementById(this.isMobile ? "mobileApplyButton" : "applyButton"),

        };
        
        this.taskButtons = {
            winsButton: "/wins_view/",
            exchangeButton: "/exchange_view/",
        }

        this.plotsViews = {
            "Loss/Accuracy": "/plot/loss_accuracy",
            "Loss": "/plot/loss_plot",
            "Distributions of wins": "/plot/distribution_of_wins",
            "Distributions of each card": "/plot/distribution_of_each_card",
        }

        this.boundHandleBeforeUnload = this.handleBeforeUnload.bind(this);

        window.addEventListener("resize", this.handleResize);

        this.initializeUI();
        this.setupEventListeners();
        this.connectWebSocket();
    }

    initializeUI() {
        // Automatically call view for any initially disabled task button
        Object.entries(this.taskButtons).forEach(([buttonKey, url]) => {
            const buttonElement = this.elements[buttonKey];
            if (buttonElement && buttonElement.disabled) {
                this.initiateTask(url);
            }
        });
        this.elements.startTaskButton.disabled = false;
        this.elements.downloadButton.disabled = true;
        this.elements.winsButton.disabled = true;
        this.elements.exchangeButton.disabled = false;
        this.elements.plotButton.disabled = true;
        this.lastClickedChoice = this.elements.winsButton;

        this.resetProgressBar();
    }

    setupEventListeners() {
        // Set up click event listeners for task buttons
        Object.entries(this.taskButtons).forEach(([buttonKey, url]) => {
            const buttonElement = this.elements[buttonKey];
            if (buttonElement) {
                buttonElement.addEventListener("click", () => this.handleTaskSelection(buttonElement, url));
            }
        });

        this.elements.plotButton.addEventListener("click", () => this.showPlots());
        this.elements.startTaskButton.addEventListener("click", () => this.showNumberPopup());
        this.elements.applyButton.addEventListener('click', () => this.applyForm());
        this.elements.downloadButton.addEventListener("click", () => this.confirmDownload());
        
        window.addEventListener("beforeunload", this.boundHandleBeforeUnload);
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

    handleTaskSelection(selectedButton, url) {
        // Toggle between `winsButtton` and `exchangeButton` clicks
        if (selectedButton === this.elements.winsButton || selectedButton === this.elements.exchangeButton) {
            if (this.lastClickedChoice !== selectedButton) {
                this.lastClickedChoice.disabled = false;
                this.lastClickedChoice = selectedButton;
                this.lastClickedChoice.disabled = true;
            }
        } 

        // Trigger task for selected button's view
        this.initiateTask(url);
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
            progressBar: document.getElementById(this.isMobile ? "mobileProgressBar" : "progressBar"),
            downloadButton: document.getElementById(this.isMobile ? "mobileDownloadButton" : "downloadButton"),
            winsButton: document.getElementById(this.isMobile ? "mobileWinsButton" : "winsButton"),
            exchangeButton: document.getElementById(this.isMobile ? "mobileExchangeButton" : "exchangeButton"),
        };

        // You can also perform additional updates if necessary, like:
        this.initializeUI(); // Reset UI settings if needed.
        this.setupEventListeners();
        this.connectWebSocket();
    }
    
    gatherFormData() {
        let binaryOutputObject = { binaryOutputValue: "defaultBinaryOutput" };

        if (this.elements.winsButton.disabled) {
            // document.querySelector('select[name="binaryOutput"]').value = "1 - Wygrana/Przegrana";
            binaryOutputObject = {
                binaryOutput: document.querySelector('select[name="binaryOutput"]')?.value || "1 - Wygrana/Przegrana"
            };
        } else if (this.elements.exchangeButton.disabled) {
            // document.querySelector('select[name="binaryOutput"]').value = "3 - Ilosc wymienianych kart";
            binaryOutputObject = {
                binaryOutput: document.querySelector('select[name="binaryOutput"]')?.value || "3 - Ilosc wymienianych kart"
            };
        }

        this.formData = {
            learningRate: document.querySelector('.menu-column input[placeholder="0.0001"]')?.value || "0.0001",
            batchSize: document.querySelector('.menu-column input[placeholder="32"]')?.value || "32",
            optimizer: document.querySelector('select[name="optimizer"]')?.value || "Adam",
            activation: document.querySelector('select[name="activation"]')?.value || "relu",
            activationOutput: document.querySelector('select[name="activationOutput"]')?.value || "sigmoid",
            loss: document.querySelector('select[name="loss"]')?.value || "BinaryCrossentropy",
            layer1: document.querySelector('.menu-column input[placeholder="256"]')?.value || "256",
            layer2: document.querySelector('.menu-column input[placeholder="512"]')?.value || "512",
            layer3: document.querySelector('.menu-column input[placeholder="64"]')?.value || "64",
            binaryOutput: binaryOutputObject.binaryOutput,
        };

        if (this.formData.binaryOutput === "1 - Wygrana/Przegrana") {
            this.elements.winsButton.disabled = true;
            this.elements.exchangeButton.disabled = false;
        } else if (this.formData.binaryOutput === "3 - Ilosc wymienianych kart") {
            this.elements.exchangeButton.disabled = true;
            this.elements.winsButton.disabled = false;
        }
    }

    applyForm() {        
        if (!DeepNeuralNetwork.onFirst && DeepNeuralNetwork.ifApply > 0)   
            this.gatherFormData();

        DeepNeuralNetwork.ifApply += 1;

        if (DeepNeuralNetwork.onFirst)
            this.gatherFormData();

        fetch('/apply_form/', {  
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify(this.formData)
        })
        .then(response => response.json())
        .then(data => console.log('Success:', data))
        .catch((error) => console.error('Error:', error));
    }

    showPlots() {
        Object.entries(this.plotsViews).forEach(([buttonKey, url]) => {
            window.open(url, buttonKey, 'height=600,width=800');
        });
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
                ? `wss://127.0.0.1:8000/ws/deep_neural_network/?session_id=${this.sessionId}`
                : `wss://pokersimulation.onrender.com/ws/deep_neural_network/?session_id=${this.sessionId}`;
    
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
        const key_progress = `epoch_percent_${this.sessionId}`;
        const key_datascript = `fit_output_${this.sessionId}`;
        
        if (key_datascript in data) {
            this.updateDataScript(data, key_datascript);
        }

        if (key_progress in data) {
            this.updateProgress(data, key_progress);
        }
    }
    
    updateDataScript(data, key_datascript) {
        this.lastDataScript = data[key_datascript];

        if (this.elements.dataScriptDiv.style.display === "none") {
            this.elements.dataScriptDiv.style.display = "block";
        }

        const lines = this.elements.dataScriptDiv.innerHTML.trim().split('<br>');
        const lastEntry = lines[lines.length - 1];

        if (lastEntry !== this.lastDataScript) {
            this.elements.dataScriptDiv.innerHTML += this.lastDataScript + '<br>';
        }
    }

    updateProgress(data, key_progress) {
        this.progress = data[key_progress];

        // Only disable the start button if the task has not been stopped
        if (this.progress >= 0 && this.progress < 100) {
            this.elements.downloadButton.disabled = true;
            this.elements.startTaskButton.disabled = true;
            this.elements.exchangeButton.disabled = true;
            this.elements.winsButton.disabled = true;
            this.elements.plotButton.disabled = true;
        }
        
        this.elements.progressBar.style.width = this.progress + '%';
        this.elements.progressBar.innerHTML = this.progress + '%';

        if (this.progress == 100) {
            this.elements.plotButton.disabled = false;
            if (key_progress == `epoch_percent_${this.sessionId}`) {
                this.elements.downloadButton.disabled = false;
                this.elements.startTaskButton.disabled = false;
                if (this.lastClickedChoice === this.elements.winsButton) {
                    this.elements.winsButton.disabled = true;
                    this.elements.exchangeButton.disabled = false;
                } else {
                    this.elements.winsButton.disabled = false;
                    this.elements.exchangeButton.disabled = true;
                }
            }
        }
    }

    resetProgressBar() {
        this.elements.progressBar.style.width = "0";
        this.elements.progressBar.innerHTML = "";
        this.progress = 0;
    }

    getCSRFToken() {
        let token = document.cookie.split(';').find(row => row.startsWith('csrftoken='));
        return token ? token.split('=')[1] : '';
    }

    async showNumberPopup() {  
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

        if (DeepNeuralNetwork.iteration > 0) {
            // Show the loader before execution starts
            await this.stopTask();
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.close();
            }
            await this.connectWebSocket();

            Object.entries(this.taskButtons).forEach(([buttonKey, url]) => {
                const buttonElement = this.elements[buttonKey];
                if (buttonElement && buttonElement.disabled) {
                    this.initiateTask(url);
                }
            });

            this.setupEventListeners();
            
            if (DeepNeuralNetwork.ifApply > 0) {
                this.formData = this.gatherFormData();
                DeepNeuralNetwork.ifApply += 1;
            }

            this.applyForm();

            this.elements.dataScriptDiv.innerHTML = "";
        }
        confirmButton.onclick = async () => {  // Make this function async
            confirmButton.disabled = true;
            this.enteredValue = parseInt(inputField.value, 10);
            
            if (this.enteredValue && !isNaN(this.enteredValue) && this.enteredValue > 0 && this.enteredValue <= this.maxAllowedValue) {
                try {
                    const loaderContainer = document.getElementById('loaderContainer')
                    const content = document.getElementById('content')
                    if (loaderContainer) loaderContainer.style.display = 'flex';
                    if (content) content.style.visibility = 'hidden';

                    const response = await fetch('/submit_number/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.getCSRFToken(),  // Ensure this method correctly retrieves the token
                        },
                        body: JSON.stringify({ value: this.enteredValue })
                    });
        
                    if (!response.ok) {  // Check if response status is not 200-299
                        throw new Error('Network response was not ok: ' + response.statusText);
                    }
        
                    const data = await response.json();  // Await the parsed JSON data
                    console.log("Response from server:", data);
        
                    await this.startTask();
               
                    DeepNeuralNetwork.iteration += 1;  

                    document.body.removeChild(overlay);  // Remove the popup after successful processing
                    if (loaderContainer) loaderContainer.style.display = 'none';
                    if (content) content.style.visibility = 'visible';

                } catch (error) {
                    console.error("Error sending number:", error);
                    alert("Failed to send data. Please try again.");  // Inform the user about the error
                }
            } else {
                alert(`Wpisz właściwą wartość lub mniejszą od: ${this.maxAllowedValue}.`);
            }
            confirmButton.disabled = false;
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
        window.removeEventListener('beforeunload', this.handleBeforeUnload);
        const userConfirmed = confirm("Pobrać plik?");
        if (userConfirmed) {
            window.location.href = `/download_saved_file/?session_id=${this.sessionId}`;
            this.resetProgressBar();
        } else {
            console.log("Download canceled by user.");
        }
        window.addEventListener("beforeunload", this.handleBeforeUnload);
    }
    
    async handleBeforeUnload() {
        console.log('Task stopped on refresh.');
        this.resetProgressBar();
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ action: "close", reason: "on_refresh" }));
            this.socket.close();
        }
        this.stopTask();
        // DeepNeuralNetwork.iteration = 0;
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

    async startTask() {
        try {
            DeepNeuralNetwork.ifApply = 0;
            DeepNeuralNetwork.onFirst = false;
            const startResponse = await fetch('/start_task_deep_neural_network/', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({})
            });
    
            if (!startResponse.ok) {
                throw new Error(`HTTP error, status = ${startResponse.status}`);
            }

            const startData = await startResponse.json();
            console.log('Task started successfully:', startData);
        } catch (error) {
            console.error('Error during task sequence:', error);
            alert('An error occurred while starting the task. Please try again.');
        }
    }
    
    async stopTask() {
        // Ensure buttons are only re-enabled after the fetch operation completes
        try {
            const response = await fetch('/stop_task_deep_neural_network/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ session_id: this.sessionId }),
                credentials: 'same-origin'
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error, status = ${response.status}`);
            }
    
            const data = await response.json();
            console.log('Task stopped successfully:', data);
            
            // Optionally handle data/message received from server
            if (data.message) {
                console.log(data.message);
            }
        } catch (error) {
            console.error('Error stopping task:', error);
            alert('An error occurred while stopping the task. Please try again.');
        } finally {
            // Re-enable buttons regardless of task success or failure
            this.elements.downloadButton.disabled = false;
            this.elements.startTaskButton.disabled = false;
        }
    }
}

// Initialize the DeepNeuralNetwork class once the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
    const deepNeuralNetwork = new DeepNeuralNetwork();
});