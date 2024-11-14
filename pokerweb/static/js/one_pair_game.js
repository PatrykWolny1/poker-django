class OnePairGame {
    constructor() {
        this.progress = 0;
        this.progressUpdateThreshold = 500; // milliseconds
        this.lastProgressUpdateTime = Date.now() // To track the last progress update
        
        // Initialize player names
        this.player1Name = document.getElementById('player1').value;
        this.player2Name = document.getElementById('player2').value;
        
        this.elements = {
            progressBar: document.getElementById('progressBar'),
        }
        progressBar: document.getElementById('progressBar'),
        // Update player names immediately when the object is created
        this.updatePlayerNames();

        // Now connect the WebSocket
        this.connectWebSocket();

        // Attach event listener for the play button
        const playButton = document.getElementById('playButton');
        playButton.addEventListener('click', () => {
            this.updatePlayerNames(); // Update player names when the play button is clicked
            this.startGame(); // Optional: you can start the game logic here
        });

        // Ensure actions before the page is unloaded (on refresh/close)
        window.addEventListener("visibilitychange", () => {
            if (window.hidden) {
                this.handleBeforeUnload();
            }
        });
    }

    connectWebSocket() {
        this.socket = new WebSocket('wss://127.0.0.1:8000/ws/op_game/');

        this.socket.onopen = () => {
            console.log("WebSocket connection opened");
        };

        this.socket.onmessage = (event) => {
            this.handleSocketMessage(event);
        };

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
        }
        if (data.progress == 100) {
            this.finalizeProgress();
        }
    }

    updateProgress(newProgress) {
        this.progress = newProgress;
        this.lastProgress = this.progress;
        clearTimeout(this.progressTimeout);
        this.progressTimeout = setTimeout(() => this.checkProgressHanging(), 5000);

        this.elements.progressBar.style.width = this.progress + '%';
        this.elements.progressBar.innerHTML = this.progress + '%';
    }

    finalizeProgress() {
        // You can add code to finalize the progress or game here
    }

    resetProgressBar() {
        this.elements.progressBar.style.width = 0;
        this.elements.progressBar.innerHTML = '';
    }

    checkProgressHanging() {
        if (this.progress > 0 && this.progress < 100) {
            // Logic for handling progress hanging
        }
    }

    // Method to update player names in the HTML
    updatePlayerNames() {
        // Get player names from input fields (in case they're modified after the constructor)
        this.player1Name = document.getElementById('player1').value;
        this.player2Name = document.getElementById('player2').value;

        // Set the player names in the player area <p> elements
        const player1Area = document.querySelector('.player1-area');
        const player2Area = document.querySelector('.player2-area');

        // Update the text content for the player areas
        player1Area.textContent = this.player1Name;
        player2Area.textContent = this.player2Name;

        // Optionally, update the player titles as well
        const playerTitles = document.querySelectorAll('.player-title');
        playerTitles[0].textContent = this.player1Name;
        playerTitles[1].textContent = this.player2Name;
    }

    // Fetch CSRF Token for making POST requests
    getCSRFToken() {
        let token = document.cookie.split(';').find(row => row.startsWith('csrftoken='));
        return token ? token.split('=')[1] : '';
    }

    startGame() {
        // Add any additional logic here to start the game when the play button is clicked
        console.log("Game Started");
        // Optionally, make a request to initialize the game on the server
        const url = '/start_game/';
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),  // Include CSRF token in the headers
            },
            body: JSON.stringify({ player1Name: this.player1Name, player2Name: this.player2Name })
        })
        .then(response => response.json())
        .then(data => console.log('Game started:', data))
        .catch(error => console.error('Error starting game:', error));
    }

    handleBeforeUnload() {
        const url = '/stop_task_view/';
        // Use fetch to stop the task when the user refreshes or closes the page
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify()
        })
        .then(() => console.log('Task stopped on refresh.'))
        .catch(error => console.error('Error stopping task:', error));
        
        this.finalizeProgress();
        this.resetProgressBar();
    }
}

// Wait until the DOM is fully loaded and then initialize the class
document.addEventListener("DOMContentLoaded", () => {
    const onePairGame = new OnePairGame();
});
