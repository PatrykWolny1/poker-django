class OnePairGame {
    constructor() {
        this.cards = "";
        this.progress = 0;
        this.progressUpdateThreshold = 500; // milliseconds
        this.lastProgressUpdateTime = Date.now(); // To track the last progress update
        this.isStopping = false;
        this.iter = 0;
        this.iter1 = 0;
        this.iter2 = 0;
        this.iter3 = 0;
        this.iter4 = 0;
        this.arrayTemp = new Array();
        this.arrayRouteBinTree1 = new Array()
        this.arrayRouteBinTree2 = new Array()
        this.cardsContainer = undefined;
        this.progressGameBorders1 = document.querySelectorAll('.progress-game-border-1');
        this.progressGameBorders2 = document.querySelectorAll('.progress-game-border-2');
        this.progressGameBorders = undefined;
        this.count = 0;
        this.isProgressGameBorders = false;
        this.isChances = true;
        this.socket = undefined;
        this.isResult = false;
        this.isName = true;
        
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

        this.elements.nextButton1.disabled = true;
        this.elements.nextButton2.disabled = true;
  
        this.elements.nextButton1.addEventListener('click', () => {
            this.fetchRedisValue('wait_buffer')
            this.elements.nextButton1.disabled = true;
            this.elements.nextButton2.disabled = true;
            setTimeout(() => {
                this.elements.nextButton1.disabled = true;
                this.elements.nextButton2.disabled = false;            
            }, 4500);  
         });
        
        this.elements.nextButton2.addEventListener('click', () => {
            this.fetchRedisValue('wait_buffer')
            this.elements.nextButton1.disabled = true;
            this.elements.nextButton2.disabled = false;
        });

        this.elements.playButton.addEventListener('click', () => {
           
        });

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
            const exchangeCardsText = data.exchange_cards === 't' ? 'TAK' : 'NIE';
            if (progressGames[0]) progressGames[0].textContent = `Wymiana kart: ${exchangeCardsText}`;
        }

        this.waitForChances(data, progressGames)

        if ('amount' in data) {
            const amount = data.amount;
            if (progressGames[3]) progressGames[3].textContent = `Ile kart: ${amount}`;
            // Toggle the flag for the next set
            this.isProgressGameBorders = !isFirstSet;
        }
        
        if ('type_arrangement_result' in data) {
            const typeArrangementResult = data.type_arrangement_result;
        
            if (this.iter4 === 0) {
                const arrangement_result_1 = document.querySelector('.arrangement-result-1');
                arrangement_result_1.textContent = typeArrangementResult;
                this.iter4 = 1;
            } else if (this.iter4 === 1) {
                const arrangement_result_2 = document.querySelector('.arrangement-result-2');
                arrangement_result_2.textContent = typeArrangementResult;
                this.iter4 = 0;
            }
        }

        if ('first_second' in data) {
            const firstSecond = data.first_second;
            if (firstSecond === '0') {
                this.toggleClass("result-info-1", "active", 'result');

            } else if (firstSecond === '1') {
                this.toggleClass("result-info-2", "active", 'result');
            }
        }

        // Handle strategies
        if ('strategy_one' in data || 'strategy_two' in data) {
            console.log(data.strategy_one || data.strategy_two);
            this.processStrategyData(data);
        }

        if (this.hasRequiredKeys(data)) {
            // If data contains one of the required keys, process it
            // console.log("Valid data:", data);
            this.processStrategyData(data);
        } 

        if (this.iter1 === 2) {
            this.animateBinaryTree();
        }
        

    };

    animateBinaryTree() {
        const delay = 500; // Delay between steps in milliseconds
        const animationContainer = [
            { array: this.arrayRouteBinTree1, label: "Tree 1" },
            { array: this.arrayRouteBinTree2, label: "Tree 2" },
        ];

        const processArray = (array, callback) => {        
            array.forEach((element, index) => {
                setTimeout(() => {
                    // Reset all active classes before starting
                    this.resetClasses();
                    console.log(element)
                    if (element.includes("main")) {
                        this.toggleClass("main", "active", "diagram-container");
                    } else if (element.startsWith("Yes")) {
                        this.toggleClass("top-left", "active", "diagram-container");
                        this.toggleClass("line-top-left", "active", "diagram-container");
                    } else if (element.includes("No")) {
                        this.toggleClass("top-right", "active", "diagram-container");
                        this.toggleClass("line-top-right", "active", "diagram-container");
                    } else if (element.startsWith("Two")) {
                        this.toggleClass("bottom-left", "active", "diagram-container");
                        this.toggleClass("line-bottom-left", "active", "diagram-container");
                    } else if (element.startsWith("Three")) {
                        this.toggleClass("bottom-right", "active", "diagram-container");
                        this.toggleClass("line-bottom-right", "active", "diagram-container");
                    }


                    // After the last element, invoke the callback
                    if (index === array.length - 1 && callback) {
                        setTimeout(callback, delay);
                    }
                }, index * delay);
            });
        };
        const playerName = document.querySelector('.player-name-text');
        
        if (this.iter2 === 0) {
            playerName.textContent = this.player1Name;
            this.iter2 = 1;
        }
        processArray(animationContainer[0].array, () => {
            if (this.iter2 === 1) {
                playerName.textContent = this.player2Name;
                this.iter2 = 0;
            }
            processArray(animationContainer[1].array, () => {
             
                this.animateBinaryTree();
            });
        });

    }
    
    // Helper function to reset all classes
    resetClasses() {
        const container = document.querySelector(".diagram-container");
        const allClasses = [
            "main",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
            "line-top-left",
            "line-top-right",
            "line-bottom-left",
            "line-bottom-right",
        ];
        allClasses.forEach((className) => {
            const element = container.querySelector(`.${className}`);

            element.classList.remove("active");
        });
    }

    toggleClass(elementClass, className, whichQuery) {
        const element = document.querySelector(`.${whichQuery} .${elementClass}`);
        console.log(element)
        if (element) {
            element.classList.add(className);
        } else {
            console.warn(`Element with class "${elementClass}" not found.`);
        }
    }
    
    // Function to check if required keys are in the data
    hasRequiredKeys(data) {
        // Define the keys you're expecting in `data`
        const requiredKeys = ['p1_2x_1', 'p1_2x_0', 'p2x', 'p1x', 'yes_no', 'cards_2_3'];
        return requiredKeys.some(key => key in data);  // Returns true if any of the required keys exist in `data`
    }

    //TODO: wykonac poprawke dla odpowiedzi 'NIE' - dla jednego i drugiego gracza zachowuje sie inaczej; animacja dla drzewa decyzyjnego 
    processStrategyData(data) {
        const keysToUpdate = {
            p1_2x_1: 'top-left-text',
            p1_2x_0: 'top-right-text',
            p2x: 'bottom-left-text',
            p1x: 'bottom-right-text',
        };

        // this.toggleClass('main', 'active');
        for (const [key, value] of Object.entries(data)) {
            if (key.includes('yes_no') || key.includes('cards_2_3')) {
                console.log(data)
                if (value.startsWith('Yes')) {
                    this.arrayTemp.push(value)
                    console.log(value)
                } else if (value.includes('No')) {
                    this.arrayTemp.push(value)
                    console.log(value)
                } else if (value.startsWith('Two')) {
                    this.arrayTemp.push(value)
                    console.log(value)
                } else if (value.startsWith('Three')) {
                    this.arrayTemp.push(value)
                    console.log(value)
                }

                if (this.iter1 === 0 && (this.arrayTemp.length === 2 || this.arrayTemp[0] === 'No')) {
                    this.arrayTemp.unshift("main")
                    this.arrayRouteBinTree1 = this.arrayTemp;
                    console.log(this.arrayTemp, "1")
                    this.arrayTemp = [];
                    this.iter1 += 1;
                } else if (this.iter1 === 1 && (this.arrayTemp.length === 2 || this.arrayTemp[0] === 'No')) {
                    this.arrayTemp.unshift("main")
                    console.log(this.arrayTemp, "2")
                    this.arrayRouteBinTree2 = this.arrayTemp;
                    this.iter1 += 1;
                }
            }

            if (key in keysToUpdate) {
                const extractedText = this.extractText(value);
                const rounded = (parseFloat(extractedText) * 100).toFixed(1);
                this.updatePercentage(keysToUpdate[key], rounded);
            } else {
                this.logStrategyKey(key, value);
            }
        }
    }
    
    logStrategyKey(key, value) {
        const strategyKeys = ['yes_no', 'strategy_one', 'strategy_two'];
        if (strategyKeys.includes(key)) {
            console.log(`Received ${key}: ${value}`);
        }
    }
    
    updatePercentage(id, newValue) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = `${newValue}%`;
        }
    }

    waitForChances(data, progressGames) {
        const interval = setInterval(() => {
            if ('chances' in data) {
                const chances = data.chances;
    
                if (this.isChances) {
                    if (progressGames[1]) {
                        progressGames[1].textContent = `Szansa (2 karty): ${chances}%`;
                    }
                    this.isChances = false;
                } else {
                    if (progressGames[2]) {
                        progressGames[2].textContent = `Szansa (3 karty): ${chances}%`;
                    }
                    this.isChances = true;
                }
    
                // Check if both elements have been updated
                const chances_2 = progressGames[1]?.textContent.includes("Szansa (2 karty)");
                const chances_3 = progressGames[2]?.textContent.includes("Szansa (3 karty)");
                if (chances_2 && chances_3) {
                    clearInterval(interval); // Stop checking when both conditions are met
                }
            }
        }, 100); // Check every 100 milliseconds
    }

    // Function to dynamically update the text
    updateProgressGameText(data) {
        // Update the appropriate border
        if (this.isProgressGameBorders === false && this.progressGameBorders1) {
            const progressGames = this.progressGameBorders1[0].querySelectorAll('.progress-game');
            this.updateBorders(progressGames, false, data);
        } else if (this.isProgressGameBorders === true && this.progressGameBorders2) {
            const progressGames = this.progressGameBorders2[0].querySelectorAll('.progress-game');
            this.updateBorders(progressGames, false, data);
        }
    }

    handleSocketMessage(event) {
        const data = JSON.parse(event.data);

        if ('cards' in data) {
            console.log(data.cards); // Debugging: check the card names
            // Assuming you have 5 cards to display
            if (this.iter === 0) {
                if (this.isResult) {
                    this.cardsContainer = document.querySelectorAll('.cards-3 .card');
                } else {
                    this.cardsContainer = document.querySelectorAll('.cards-1 .card');
                }
            }
            if (this.iter === 1) {
                if (this.isResult) {
                    this.cardsContainer = document.querySelectorAll('.cards-4 .card');
                } else {
                    this.cardsContainer = document.querySelectorAll('.cards-2 .card');
                }
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
            const typeArrangement = data.type_arrangement;
        
            if (this.iter3 === 0) {
                const arrangement1 = document.querySelector('.arrangement-1');
                arrangement1.textContent = typeArrangement;
                this.iter3 = 1;
            } else if (this.iter3 === 1) {
                const arrangement2 = document.querySelector('.arrangement-2');
                arrangement2.textContent = typeArrangement;
                this.iter3 = 0;
            }
        }

        if (this.iter == 2) {
            setTimeout(() => {
                this.elements.nextButton1.disabled = false;
                this.elements.nextButton2.disabled = true;            
            }, 6500);  
            this.iter = 0;
            this.isResult = true;
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

    extractText(input) {
        const match = input.match(/^\d+\((.*?)\)$/);
        return match ? match[1] : ''; // Return the captured group or an empty string if no match
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
        console.log("Stopping background task.....");
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("Closing WebSocket...");
            this.socket.close();
        }
        this.stopTask();

    }
    
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
