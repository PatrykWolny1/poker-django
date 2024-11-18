class OnePairGame {
    constructor() {
        this.cards = "";
        this.progress = 0;
        this.progressUpdateThreshold = 500; // milliseconds
        this.lastProgressUpdateTime = Date.now(); // To track the last progress update
        this.isStopping = false;
        this.iter = 0;
        this.cardsContainer = undefined;
        this.type_arrangement = undefined;
        this.amount = undefined;
        this.exchange_cards = undefined;
        this.chance = undefined
        
        // Initialize player names
        this.player1Name = document.getElementById('player1').value;
        this.player2Name = document.getElementById('player2').value;
        
        this.elements = {
            progressBar: document.getElementById('progressBar'),
            playButton: document.getElementById('playButton'),
            nextButton1: document.getElementById('nextButton1'),
            nextButton2: document.getElementById('nextButton2'),
        }

        // Update player names immediately when the object is created
        this.updatePlayerNames();

        // Now connect the WebSocket
        this.connectWebSocket();

        // Attach event listener for the play button
        
        this.elements.playButton.disabled = true;

        this.elements.nextButton1.addEventListener('click', () => {
            this.fetchRedisValue('wait_buffer')

        });
        
        this.elements.nextButton2.addEventListener('click', () => {
            this.fetchRedisValue('wait_buffer')
        });

        this.elements.playButton.addEventListener('click', () => {
           
        });

        // Ensure actions before the page is unloaded (on refresh/close)
        window.addEventListener("beforeunload", () => {
            this.handleBeforeUnload();
            // Optionally inform the user the task is stopping
            console.log("Stopping background task...");
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

        if ('cards' in data) {
            console.log(data.cards); // Debugging: check the card names
            // Assuming you have 5 cards to display
            if (this.iter === 0) {
                this.cardsContainer = document.querySelectorAll('.cards-1 .card');
            }
            if (this.iter === 1) {
                this.cardsContainer = document.querySelectorAll('.cards-2 .card');
            }
            this.iter += 1;
            // Loop through the card names and set the corresponding image
            data.cards.forEach((card, index) => {
                if (this.cardsContainer[index]) {
                    // Set the background image for each card element
                    this.cardsContainer[index].style.backgroundImage = `url("/static/css/img/${card}.png")`;
                }
            });
        }  

        if ('type_arrangement' in data) {
            console.log(data.type_arrangement)
        }
        if ('exchange_cards' in data) {
            console.log(data.exchange_cards)
        }
        if ('amount' in data) {
            console.log(data.amount)
            if ('chance' in data) {
                console.log(data.chance)
            }
        }

        // Update progress
        if ('progress' in data) {
            console.log("IN PROGRESS")
            this.updateProgress(data.progress);
            // this.lastProgressUpdateTime = Date.now(); // Update the last progress time

            // Clear any existing timeout since we have new progress
            // clearTimeout(this.progressTimeout);

            if (data.progress > 0 && data.progress < 100) {
                this.elements.playButton.disabled = true;
            }
        }
        if (data.progress == 100) {
            this.elements.playButton.disabled = false;
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
        // Disable the play button after it's clicked
        // this.elements.playButton.disabled = true;
        
        console.log("Game Started");
        
        this.updatePlayerNames(); // Update player names when the play button is clicked

        // Send a request to initialize the game on the server
        const url = '/start_game/';
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({ player1Name: this.player1Name, player2Name: this.player2Name })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Game started:', data);
        })
        .catch(error => {
            console.error('Error starting game:', error);
            playButton.disabled = false; // Re-enable the button if there's an error
        });
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
            }
        })
        .catch(error => {
            console.error('Error stopping task:', error);
            alert('An error occurred while stopping the task. Please try again.');
        });
    }
    
    handleBeforeUnload() {
        if (this.isStopping) return;
        this.isStopping = true;
    
        const url = '/stop_task_view/';
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', this.getCSRFToken()); // Ensure `getCSRFToken()` returns the correct token.
    
        // Convert FormData to a Blob for sendBeacon
        const body = new URLSearchParams(formData).toString();
        const blob = new Blob([body], { type: 'application/x-www-form-urlencoded' });
    
        const result = navigator.sendBeacon(url, blob);
    
        if (!result) {
            console.error("sendBeacon failed.");
        }
        console.log("Stop task request sent.");
    }
    // }
    // handleBeforeUnload() {
    //     console.log("Attempting to stop task on page unload...");
    //     this.stopTask();
    // }
    
    fetchRedisValue(key) {
        // Send a POST request with the value in the body

        fetch("/get_redis_value/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.getCSRFToken(), // Include CSRF token for POST
            },
            body: JSON.stringify({ key: key }), // Send the key in the request body
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Response from the server:", data);
            })
            .catch(error => console.error("Error sending value to the view:", error));
    }
}

// Wait until the DOM is fully loaded and then initialize the class
document.addEventListener("DOMContentLoaded", () => {
    const onePairGame = new OnePairGame();
});
