class OnePairGame {
    constructor(executeFunction, isMobile) {   
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
        this.iter5 = 0;
        this.iter6 = 0;
        this.iter7 = 0;
        this.arrayTemp = new Array();
        this.arrayRouteBinTree1 = new Array();
        this.arrayRouteBinTree2 = new Array();
        this.cardsContainer = null;
        this.isMobile = isMobile;
        
        this.progressGameBorders1 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-1') 
            : document.querySelectorAll('.progress-game-border-1');

        this.progressGameBorders2 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-2') 
            : document.querySelectorAll('.progress-game-border-2');
        this.progressGameBorders = null;
        this.isProgressGameBorders = false;
        this.isChances = true;
        this.isResult = false;
        this.isName = true;
        this.noAnimateBT = false;
        this.timeoutIds = [];
        this.socket = null;
        this.executeFunction = executeFunction;
        this.arrangement_result_off = null
        
        // Initialize player names
        this.player1Name = document.getElementById('player1').value;
        this.player2Name = document.getElementById('player2').value;
        
        this.elements = {
            progressBar: document.getElementById('progressBar'),
            playButton: document.getElementById('playButton'),
            nextButton1: this.isMobile 
                ? document.getElementById('nextButton1Mobile')
                : document.getElementById('nextButton1'),
            nextButton2: this.isMobile 
                ? document.getElementById('nextButton2Mobile')
                : document.getElementById('nextButton2'),
        }
        
   
        // Update player names immediately when the object is created
        this.updatePlayerNames();
        
            // Now connect the WebSocket
        this.initializeWebSocket();

        // Attach event listener for the play button
        this.elements.playButton.disabled = true;
        
        this.elements.nextButton1.disabled = true;
        this.elements.nextButton2.disabled = true;
        
        this.elements.playButton.addEventListener('click', () => {
            this.elements.playButton.disabled = true;
            this.startGame();
            this.elements.playButton.disabled = false;
        });

        this.elements.nextButton1.addEventListener('click', () => {
            this.fetchRedisValue('wait_buffer')
            this.elements.nextButton1.disabled = true;
            this.elements.nextButton2.disabled = false;            
         });
        
        this.elements.nextButton2.addEventListener('click', () => {
            this.fetchRedisValue('wait_buffer')
            this.elements.nextButton1.disabled = true;
            this.elements.nextButton2.disabled = true;
            
            if (this.arrangement_result_off) {
                this.elements.nextButton1.disabled = true;
                this.elements.nextButton2.disabled = true;
            } else {
                setTimeout(() => {
                    this.elements.nextButton1.disabled = true;
                    this.elements.nextButton2.disabled = false;            
                }, 1500);
            } 
     
        });

        window.addEventListener("beforeunload", this.handleBeforeUnload.bind(this));

        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth <= 768;
            console.log('Viewport resized. Is mobile:', this.isMobile);
        });
    }
    
    // Method to initialize WebSocket
    async initializeWebSocket() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("Closing previous WebSocket...");
            this.socket.close();
        }
        this.socket = null;

        console.log(window.env.IS_DEV);

        if (window.env.IS_DEV.includes('yes')) {
            this.socket = new WebSocket('wss://127.0.0.1:8000/ws/op_game/');    
        } else if (window.env.IS_DEV.includes('no')) {
            this.socket = new WebSocket('wss://pokersimulation.onrender.com/ws/op_game/');    //'wss://127.0.0.1:8000/ws/op_game/'
        }
        console.log("WebSocket instance created:", this.socket);

        this.socket.onopen = () => {
            console.log("WebSocket connection opened");
        };

        this.socket.onmessage = (event) => {
            this.handleSocketMessage(event);
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.socket.onclose = () => {
            console.log('WebSocket connection closed');
        };
    }

    // Method to reset instance variables
    resetInstanceVariables() {
        this.cards = "";
        this.progress = 0;
        this.progressUpdateThreshold = 500;
        this.lastProgressUpdateTime = Date.now();
        this.isStopping = false;
        this.iter = 0;
        this.iter1 = 0;
        this.iter2 = 0;
        this.iter3 = 0;
        this.iter4 = 0;
        this.iter5 = 0;
        this.arrayTemp = [];
        this.arrayRouteBinTree1 = [];
        this.arrayRouteBinTree2 = [];
        this.cardsContainer = null;
        this.progressGameBorders1 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-1') 
            : document.querySelectorAll('.progress-game-border-1');

        this.progressGameBorders2 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-2') 
            : document.querySelectorAll('.progress-game-border-2');
        this.progressGameBorders = null;
        this.isProgressGameBorders = false;
        this.isChances = true;
        this.isResult = false;
        this.isName = true;
        this.player1Name = document.getElementById('player1').value;
        this.player2Name = document.getElementById('player2').value;
        this.socket = null;
        this.executeFunction = false;
        
        const progressGames1 = this.isMobile
            ? this.progressGameBorders1[0].querySelectorAll('.mobile-only .progress-game')
            : this.progressGameBorders1[0].querySelectorAll('.progress-game');
        progressGames1[0].textContent = null;
        progressGames1[1].textContent = null;
        progressGames1[2].textContent = null;
        progressGames1[3].textContent = null;

        const progressGames2 = this.isMobile
            ? this.progressGameBorders2[0].querySelectorAll('.mobile-only .progress-game')
            : this.progressGameBorders2[0].querySelectorAll('.progress-game');
        progressGames2[0].textContent = null;
        progressGames2[1].textContent = null;
        progressGames2[2].textContent = null;
        progressGames2[3].textContent = null;

        const arrangement_result_1 = this.isMobile
            ? document.querySelector('.mobile-only .arrangement-result-1')
            : document.querySelector('.arrangement-result-1')
        arrangement_result_1.textContent = null;

        const arrangement_result_2 = this.isMobile
            ? document.querySelector('.mobile-only .arrangement-result-2')
            : document.querySelector('.arrangement-result-2')
        arrangement_result_2.textContent = null;

        this.arrangement_result_off = null

        // Select all the containers for the cards
        const cardContainers = [
            ...document.querySelectorAll('.cards-3'),
            ...document.querySelectorAll('.cards-1'),
            ...document.querySelectorAll('.cards-4'),
            ...document.querySelectorAll('.cards-2')
        ];

        // Loop through each container
        cardContainers.forEach(container => {
            // Find all the individual card elements within the container
            const cards = container.querySelectorAll('.card');
            
            // Loop over each card and reset the background image
            cards.forEach(card => {
                card.style.backgroundImage = null;  // Remove any background image
            });
        });

        const container = this.isMobile
            ? document.querySelector(".result", "mobile-only")
            : document.querySelector(".result");
        const allClasses = [
            "result-info-1",
            "result-info-2",
        ];
        allClasses.forEach((className) => {
            const element = container.querySelector(`.${className}`);
            element.classList.remove("active");
        })

        this.elements.playButton.disabled = false;
    }

    // Method to reinitialize the instance
    reinitializeInstance() {
        console.log("Reinitializing instance...");
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.close();
        }

        this.resetInstanceVariables();
        this.initializeWebSocket();
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
                const arrangement_result_1 = this.isMobile
                ? document.querySelector('.mobile-only .arrangement-result-1')
                : document.querySelector('.arrangement-result-1');
                arrangement_result_1.textContent = typeArrangementResult;
                this.iter4 = 1;
            } else if (this.iter4 === 1) {
                const arrangement_result_2 = this.isMobile
                ? document.querySelector('.mobile-only .arrangement-result-2')
                : document.querySelector('.arrangement-result-2');
                arrangement_result_2.textContent = typeArrangementResult;
                
                this.arrangement_result_off = true;
                this.iter4 = 0;
            }
        }

        if ('first_second' in data) {
            this.firstSecond = data.first_second;
            if (this.firstSecond === '0') {
                this.toggleClass("result-info-1", "active", 'result');

            } else if (this.firstSecond === '1') {
                this.toggleClass("result-info-2", "active", 'result');
            }
            this.elements.nextButton1.disabled = true;
            this.elements.nextButton2.disabled = true; 
        }

        // Handle strategies
        if ('strategy_one' in data || 'strategy_two' in data) {
            // console.log(data.strategy_one || data.strategy_two);
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
            this.timeoutIds = [];

            array.forEach((element, index) => {
                const timeoutId = setTimeout(() => {
                    // Reset all active classes before starting
                    this.resetClasses();
        
                    // console.log(element)
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

                this.timeoutIds.push(timeoutId);
            });
            this.resetClasses();
        };
        const playerName = this.isMobile 
            ? document.getElementById('player-name-text-mobile')
            : document.querySelector('.player-name-text');

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
        const container = this.isMobile 
            ? document.querySelector(".mobile-only .diagram-container")
            : document.querySelector(".diagram-container");

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
        let element = null;

        if (whichQuery === 'diagram-container') {
            element = this.isMobile
                ? document.querySelector(`.mobile-only .${whichQuery} .${elementClass}`)
                : document.querySelector(`.${whichQuery} .${elementClass}`);
        } else {
            element = this.isMobile
                ? document.querySelector(`.mobile-only .${elementClass}`)
                : document.querySelector(`.${whichQuery} .${elementClass}`);
            // console.log(element)
        }
        if (element && className) {
            element.classList.add(className);
        } else {
            console.log(`Element with class "${elementClass}" not found.`);
        }
    }
    
    // Function to check if required keys are in the data
    hasRequiredKeys(data) {
        // Define the keys you're expecting in `data`
        const requiredKeys = ['p1_2x_1', 'p1_2x_0', 'p2x', 'p1x', 'yes_no', 'cards_2_3'];
        return requiredKeys.some(key => key in data);  // Returns true if any of the required keys exist in `data`
    }

    processStrategyData(data) {
        let keysToUpdate;

        if (this.isMobile) {
            keysToUpdate = {
                p1_2x_1: 'top-left-text-mobile',
                p1_2x_0: 'top-right-text-mobile',
                p2x: 'bottom-left-text-mobile',
                p1x: 'bottom-right-text-mobile'
            };
        } else {
            keysToUpdate = {
                p1_2x_1: 'top-left-text',
                p1_2x_0: 'top-right-text',
                p2x: 'bottom-left-text',
                p1x: 'bottom-right-text'
            };
        }

        // this.toggleClass('main', 'active');
        for (const [key, value] of Object.entries(data)) {
            if (key.includes('yes_no') || key.includes('cards_2_3')) {
                if (value.startsWith('Yes')) {
                    this.arrayTemp.push(value)
                } else if (value.includes('No')) {
                    this.arrayTemp.push(value)
                } else if (value.startsWith('Two')) {
                    this.arrayTemp.push(value)
                } else if (value.startsWith('Three')) {
                    this.arrayTemp.push(value)
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
        console.log(id);
        const element = this.isMobile
            ? document.getElementById(id) 
            : document.getElementById(id);
        console.log("Element found:", element)
        if (element) {
            element.textContent = `${newValue}%`
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
        console.log(data)

        if ('cards' in data) {
            console.log(data.cards); // Debugging: check the card names
            // Assuming you have 5 cards to display
            const cards = data.cards;

            this.isMobile = window.innerWidth <= 768;

            if (this.iter === 0) {
                if (this.isResult) {
                    this.cardsContainer = this.isMobile 
                        ? document.querySelectorAll('.mobile-only .cards-3 .card')
                        : document.querySelectorAll('.cards-3 .card');
                } else {
                    this.cardsContainer = this.isMobile 
                        ? document.querySelectorAll('.mobile-only .cards-1 .card')
                        : document.querySelectorAll('.cards-1 .card');
                }
            }
            if (this.iter === 1) {
                if (this.isResult) {
                    this.cardsContainer = this.isMobile 
                        ? document.querySelectorAll('.mobile-only .cards-4 .card')
                        : document.querySelectorAll('.cards-4 .card');
                } else {
                    this.cardsContainer = this.isMobile 
                        ? document.querySelectorAll('.mobile-only .cards-2 .card')
                        : document.querySelectorAll('.cards-2 .card');
                }
            }
        
            this.iter += 1;
            
            cards.forEach((card, index) => {
                if (this.cardsContainer[index]) {
                    // Set the background image for each card element
                    this.cardsContainer[index].style.backgroundImage = `url("/static/css/img/${card}.png")`;
                }
            });        
        }  

        if ('type_arrangement' in data) {
            const typeArrangement = data.type_arrangement;
        
            if (this.iter3 === 0) {
                const arrangement1 = this.isMobile
                ? document.querySelectorAll('.mobile-only .arrangement-1')
                : document.querySelector('.arrangement-1');
                arrangement1.textContent = typeArrangement;
                this.iter3 = 1;
            } else if (this.iter3 === 1) {
                const arrangement2 = this.isMobile
                ? document.querySelectorAll('.mobile-only .arrangement-2')
                : document.querySelector('.arrangement-2');
                arrangement2.textContent = typeArrangement;
                this.iter3 = 0;
            }
        }

        if (this.iter == 2) {
            if (!this.isResult) {
                setTimeout(() => {
                    this.elements.nextButton1.disabled = false;
                    this.elements.nextButton2.disabled = true;            
                }, this.executeFunction ? 6500 : 2000);  
            }

            
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
        const player1Area = this.isMobile
            ? document.querySelectorAll('.mobile-only .player1-area')
            : document.querySelectorAll('.player1-area');
        const player2Area = this.isMobile
            ? document.querySelectorAll('.mobile-only .player2-area')
            : document.querySelectorAll('.player2-area');

        // Update the text content for the player areas
        player1Area.textContent = this.player1Name;
        player2Area.textContent = this.player2Name;

        // Optionally, update the player titles as well
        const playerTitles = this.isMobile
         ? document.querySelectorAll('.mobile-only .player-title')
         : document.querySelectorAll('.player-title');

        playerTitles[0].textContent = this.player1Name;
        playerTitles[1].textContent = this.player2Name;
    }

    // Fetch CSRF Token for making POST requests
    getCSRFToken() {
        let token = document.cookie.split(';').find(row => row.startsWith('csrftoken='));
        return token ? token.split('=')[1] : '';
    }

    async waitForWebSocketOpen(socket) {
        return new Promise((resolve, reject) => {
            if (socket.readyState === WebSocket.OPEN) {
                resolve();
            } else {
                socket.onopen = () => resolve();
                socket.onerror = (error) => reject(error);
            }
        });
    }
  
    async startGame() {
        this.elements.nextButton1.disabled = true;
        this.elements.nextButton2.disabled = true;

        await this.stopTask();
    
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("Closing previous WebSocket...");
            this.socket.close();
        }
        this.socket = null;

        console.log('startGame function called');
        fetch('/start_game_view/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({}),
            credentials: 'same-origin'
        })
        .then(response => response.json())  // Read the JSON data once
        .then(async () => {
            // Reinitialize the current instance
            this.reinitializeInstance();

            await this.waitForWebSocketOpen(this.socket);
            
            this.updatePlayerNames();

            // console.log("Socket ready state before sending:", this.socket.readyState);

            // Now the socket is open, send the start_task message
            if (this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({ action: 'close', reason: 'button_click' }));
                console.log("After executing send");
            } else {
                console.error("WebSocket is not open. Current state:", this.socket.readyState);
            }                 
        })
        .catch(error => {
            console.error('Error stopping task:', error);
            alert('An error occurred while stopping the task. Please try again.');
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
    
    async handleBeforeUnload() {
        localStorage.removeItem('pagePreviouslyLoaded');

        console.log("Stopping background task.....");
        await this.stopTask();
        
        this.socket.send(JSON.stringify({ action: 'close', reason: 'on_refresh' }));

        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("Closing WebSocket...");
            this.socket.close();
        }

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
    if (localStorage.getItem('pagePreviouslyLoaded')) {
        // This means the page was previously opened, so we can trigger some actions
        console.log('Page is re-opened or reloaded.');
        // Call any function you need here, similar to `beforeunload` actions
    } else {
        // Set the flag to indicate that the page was loaded
        localStorage.setItem('pagePreviouslyLoaded', 'true');
        console.log('First time loading the page.');
    }
    const isMobile = window.innerWidth <= 768;

    const onePairGame = new OnePairGame(true, isMobile);
    // Simulate some loading process
    const checkLoadingStatus = setInterval(() => {    
        // Check every 100 milliseconds
        if (onePairGame.progress > 0) {
            // Hide the loader once the condition is met
            const loaderContainer = document.getElementById('loaderContainer');
            loaderContainer.style.display = 'none';

            // Make the content visible
            const content = document.getElementById('content');
            content.style.visibility = 'visible';
            // Stop further checks
            clearInterval(checkLoadingStatus);
        }
    }, 100);
});
