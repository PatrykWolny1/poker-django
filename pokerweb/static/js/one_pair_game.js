class OnePairGame {
    constructor() {
        this.cards = "";
        this.progress = 0;
        this.progressUpdateThreshold = 500; // milliseconds
        this.lastProgressUpdateTime = Date.now(); // To track the last progress update
        this.isStopping = false;
        this.iter = 0;
        this.cardsContainer = undefined;
        this.progressGameBorders1 = document.querySelectorAll('.progress-game-border-1');
        this.progressGameBorders2 = document.querySelectorAll('.progress-game-border-2');
        this.progressGameBorders = undefined;
        this.count = 0;
        this.isProgressGameBorders = false;
        this.isChances = true;
        
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
        // window.addEventListener("visibilitychange", () => {
        //     if (window.hidden) {
        //         this.handleBeforeUnload();
        //     }
        // });
        // Ensure actions before the page is unloaded (on refresh/close)
        // Bind the `beforeunload` event listener
        window.addEventListener("beforeunload", this.handleBeforeUnload.bind(this));
    }

    connectWebSocket() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("WebSocket already open");
            this.socket.close();  // Prevent opening a new WebSocket if one is already open
        }

        this.socket = new WebSocket('wss://127.0.0.1:8000/ws/op_game/');

        this.socket.onopen = () => {
            console.log("WebSocket connection opened");
        };

        this.socket.onmessage = (event) => {
            this.handleSocketMessage(event);
        };

        this.socket.onclose = () => {
            console.log("WebSocket connection closed");
        };
    }
    
    updateBorders(progressGames, isFirstSet, data) {
        if (!progressGames) return;
        
        if ('exchange_cards' in data) {
            let exchange_cards = data.exchange_cards;
            console.log(data.exchange_cards)
            if (exchange_cards === 't') {
                exchange_cards = 'TAK'
            } else if (exchange_cards === 'n') {
                exchange_cards = 'NIE'
            }
            if (progressGames[0]) progressGames[0].textContent = `Wymiana kart: ${exchange_cards}`;
        }

        if ('chances' in data) {
            const chances = data.chances;
            if (this.isChances) {
                if (progressGames[1]) progressGames[1].textContent = `Szansa (2 karty): ${chances}%`;
                this.isChances = false;
            } else if (!this.isChances) {
                if (progressGames[2]) progressGames[2].textContent = `Szansa (3 karty): ${chances}%`;
                this.isChances = true;
            }
        }

        if ('amount' in data) {
            const amount = data.amount;
            if (progressGames[3]) progressGames[3].textContent = `Ile kart: ${amount}`;
            // Toggle the flag for the next set
            this.isProgressGameBorders = !isFirstSet;
        }

      
    };

    // Function to dynamically update the text
    updateProgressGameText(data) {
        // Update the appropriate border
        if (this.isProgressGameBorders === false && this.progressGameBorders1) {
            const progressGames = this.progressGameBorders1[0].querySelectorAll('.progress-game');
            console.log("1")
            this.updateBorders(progressGames, false, data);
        } else if (this.isProgressGameBorders === true && this.progressGameBorders2) {
            const progressGames = this.progressGameBorders2[0].querySelectorAll('.progress-game');
            console.log("2")
            this.updateBorders(progressGames, false, data);
        }
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

        this.updateProgressGameText(data);
   

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
        console.log("beforeunload triggered");
        console.log(this.socket)
     
        console.log("Stopping background task.....");
        this.stopTask();
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("Closing WebSocket...");
            this.socket.close();
        }   
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
