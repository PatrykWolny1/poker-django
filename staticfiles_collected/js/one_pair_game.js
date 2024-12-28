class OnePairGame {
    constructor(executeFunction, isMobile) {
        this.isMobile = isMobile;
        this.executeFunction = executeFunction;
        this.progress = 0;
        this.isStopping = false;
        this.iterations = { iter: 0, iter1: 0, iter2: 0, iter3: 0, iter4: 0 };
        this.arrayTemp = [];
        this.arrayRouteBinTree1 = [];
        this.arrayRouteBinTree2 = [];
        this.cardsContainer = null;
        this.timeoutIds = [];
        this.socket = null;
        this.isResult = false;
        this.socketHandler = null;
        this.blockRefresh = false;

        // Player names
        this.player1Name = document.getElementById("player1").value;
        this.player2Name = document.getElementById("player2").value;

        this.isChances = true;
        this.isProgressGameBorders = false;

        this.elements = new UIElements(isMobile);

        // Adding the two game border containers
        this.progressGameBorders1 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-1') 
            : document.querySelectorAll('.progress-game-border-1');

        this.progressGameBorders2 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-2') 
            : document.querySelectorAll('.progress-game-border-2');
        
        // Bind methods to ensure correct reference to `this`
        this.updatePlayerNames = this.updatePlayerNames.bind(this);
        this.animateBinaryTree = this.animateBinaryTree.bind(this);
        this.resetClasses = this.resetClasses.bind(this);
        this.handleBeforeUnload = this.handleBeforeUnload.bind(this);
        this.startGame = this.startGame.bind(this);
        this.hasRequiredKeys = this.hasRequiredKeys.bind(this);
        this.updateProgress = this.updateProgress.bind(this);
        this.updateBorders = this.updateBorders.bind(this);
        this.processStrategyData = this.processStrategyData.bind(this);
        this.handleBeforeUnload = this.handleBeforeUnload.bind(this)
        
        this.init();
    }

    init() {
        window.addEventListener("beforeunload", this.handleBeforeUnload.bind(this));
        
        window.addEventListener("resize", () => {
            this.isMobile = window.innerWidth <= 768;
            console.log("Viewport resized. Is mobile:", this.isMobile);

            // Update the game border containers upon resizing
            this.updateProgressGameBorders();
        });

        window.addEventListener('click', (event) => this.handleExitStopTask(event, this));

        this.updatePlayerNames();
        this.attachEventListeners();
        this.initializeWebSocket();
  
    }

    attachEventListeners() {
        this.elements.playButton.addEventListener("click", () => {
            this.elements.playButton.disabled = true;
            this.startGame();
            this.elements.playButton.disabled = false;
        });

        this.elements.nextButton1.addEventListener("click", () => {
            this.fetchRedisValue("wait_buffer");
            this.elements.nextButton1.disabled = true;
            this.elements.nextButton2.disabled = false;
        });

        this.elements.nextButton2.addEventListener("click", () => {
            this.fetchRedisValue("wait_buffer");
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
    }

    async initializeWebSocket() {
        this.socketHandler = new WebSocketHandler(this);
        await this.socketHandler.init();
    }

    async startGame() {
        this.elements.nextButton1.disabled = true;
        this.elements.nextButton2.disabled = true;
        await this.stopTask();
        console.log("startGame function called");

        fetch("/start_game_view/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.getCSRFToken(),
            },
            body: JSON.stringify({}),
            credentials: "same-origin",
        })
            .then((response) => response.json())
            .then(async () => {
                this.reinitializeInstance();
                await this.initializeWebSocket();
                this.updatePlayerNames();

                // Now the socket is open, send the start_task message
                if (this.socketHandler.socket.readyState === WebSocket.OPEN) {
                    this.socketHandler.socket.send(JSON.stringify({ action: 'close', reason: 'button_click' }));
                    console.log("After executing send");
                } else {
                    console.error("WebSocket is not open. Current state:", this.socketHandler.socket.readyState);
                }        
            })
            .catch((error) => {
                console.error("Error starting game:", error);
                alert("An error occurred while starting the game. Please try again.");
            });
    }

    reinitializeInstance() {
        console.log("Reinitializing instance...");
        this.resetInstanceVariables();
    }

    // Method to reset instance variables
    resetInstanceVariables() {
        // Reset primary state variables
        this.cards = "";
        this.progress = 0;
        this.progressUpdateThreshold = 500;
        this.lastProgressUpdateTime = Date.now();
        this.isStopping = false;
        this.iterations = { iter: 0, iter1: 0, iter2: 0, iter3: 0, iter4: 0 };
        this.arrayTemp = [];
        this.arrayRouteBinTree1 = [];
        this.arrayRouteBinTree2 = [];
        this.cardsContainer = null;
        this.isProgressGameBorders = false;
        this.isChances = true;
        this.isResult = false;
        this.isName = true;
        this.socket = null;
        this.executeFunction = false;
        this.arrangement_result_off = null;
        this.socketHandler = null;

        // Update player names based on input values
        this.player1Name = document.getElementById('player1').value;
        this.player2Name = document.getElementById('player2').value;

        // Update the progress game borders for mobile and desktop
        this.progressGameBorders1 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-1') 
            : document.querySelectorAll('.progress-game-border-1');

        this.progressGameBorders2 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-2') 
            : document.querySelectorAll('.progress-game-border-2');

        // Clear progress games text content
        const progressGames1 = this.isMobile
            ? this.progressGameBorders1[0]?.querySelectorAll('.mobile-only .progress-game')
            : this.progressGameBorders1[0]?.querySelectorAll('.progress-game');

        if (progressGames1) {
            progressGames1.forEach((progressGame) => {
                progressGame.textContent = null;
            });
        }

        const progressGames2 = this.isMobile
            ? this.progressGameBorders2[0]?.querySelectorAll('.mobile-only .progress-game')
            : this.progressGameBorders2[0]?.querySelectorAll('.progress-game');

        if (progressGames2) {
            progressGames2.forEach((progressGame) => {
                progressGame.textContent = null;
            });
        }

        // Clear arrangement results text content
        const arrangementResult1 = this.isMobile
            ? document.querySelector('.mobile-only .arrangement-result-1')
            : document.querySelector('.arrangement-result-1');
        if (arrangementResult1) {
            arrangementResult1.textContent = null;
        }

        const arrangementResult2 = this.isMobile
            ? document.querySelector('.mobile-only .arrangement-result-2')
            : document.querySelector('.arrangement-result-2');
        if (arrangementResult2) {
            arrangementResult2.textContent = null;
        }

        // Select and clear all the containers for the cards
        const cardContainers = [
            ...document.querySelectorAll('.cards-3'),
            ...document.querySelectorAll('.cards-1'),
            ...document.querySelectorAll('.cards-4'),
            ...document.querySelectorAll('.cards-2')
        ];

        // Loop through each container to reset the card background images
        cardContainers.forEach(container => {
            const cards = container.querySelectorAll('.card');
            cards.forEach(card => {
                card.style.backgroundImage = null; // Remove any background image
            });
        });

        // Reset all classes for result-info elements
        const container = this.isMobile
            ? document.querySelector(".mobile-only .result")
            : document.querySelector(".result");

        if (container) {
            const allClasses = [
                "result-info-1",
                "result-info-2",
            ];
            allClasses.forEach((className) => {
                const element = container.querySelector(`.${className}`);
                if (element) {
                    element.classList.remove("active");
                }
            });
        }

        // Enable the play button to allow the game to start again
        if (this.elements && this.elements.playButton) {
            this.elements.playButton.disabled = false;
        }
        
        this.elements.nextButton1.disabled = false;

        // Bind methods to ensure correct reference to `this`
        this.updatePlayerNames = this.updatePlayerNames.bind(this);
        this.animateBinaryTree = this.animateBinaryTree.bind(this);
        this.resetClasses = this.resetClasses.bind(this);
        this.handleBeforeUnload = this.handleBeforeUnload.bind(this);
        this.hasRequiredKeys = this.hasRequiredKeys.bind(this);
        this.updateProgress = this.updateProgress.bind(this);
        this.updateBorders = this.updateBorders.bind(this);
        this.processStrategyData = this.processStrategyData.bind(this);
                
    }

    updateProgressGameBorders() {
        // Update the references to the game borders after resizing
        this.progressGameBorders1 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-1') 
            : document.querySelectorAll('.progress-game-border-1');

        this.progressGameBorders2 = this.isMobile 
            ? document.querySelectorAll('.mobile-only .progress-game-border-2') 
            : document.querySelectorAll('.progress-game-border-2');
    }

    async handleBeforeUnload() {
        console.log("Page is being reloaded");
        console.log("Stopping background task...");
        
        this.socketHandler.socket.send(JSON.stringify({ action: 'close', reason: 'on_refresh' }));
       
        await this.stopTask();

        if (this.socketHandler.socket && this.socketHandler.socket.readyState === WebSocket.OPEN) {
            console.log("Closing WebSocket...");
            this.socketHandler.socket.close();
        }
    }
    
    async handleExitStopTask(event) {
        const link = event.target.closest('a');
        if (link) {
            const isInternalLink = link.hostname === window.location.hostname;

            if (isInternalLink) {
                // Check if the link is specifically pointing to the home page
                const isHomePageLink = link.pathname === '/' || link.href === window.location.origin + '/';

                if (isHomePageLink) {
                    // User clicked an external link to the home page - stop the task
                    console.log('Home page navigation detected, stopping task.');
                    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                        console.log("Closing previous WebSocket...");
                        this.socketHandler.socket.close();
                    }
                } else {
                    // Internal navigation, do not stop the task
                    console.log('Internal navigation detected, not stopping task.');
                }
            } else {
                // External link, do not stop the task
                console.log('External navigation detected, stopping task.');
                if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                    console.log("Closing previous WebSocket...");
                    this.socketHandler.socket.close();
                }
            }

        }
    }

    async stopTask() {
        fetch("/stop_task_view/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.getCSRFToken(),
            },
            body: JSON.stringify({}),
            credentials: "same-origin",
        })
            .then((response) => response.json())
            .then((data) => {
                console.log(data);
                if (data.status === "Task stopped successfully") {
                    console.log("Task stopped successfully");
                    this.elements.resetProgressBar();
                }
            })
            .catch((error) => {
                console.error("Error stopping task:", error);
                alert("An error occurred while stopping the task. Please try again.");
            });
    }

    getCSRFToken() {
        let token = document.cookie.split(";").find((row) => row.startsWith("csrftoken="));
        return token ? token.split("=")[1] : "";
    }

    fetchRedisValue(key) {
        fetch("/get_redis_value/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": this.getCSRFToken(),
            },
            body: JSON.stringify({ key }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Response from server:", data);
            })
            .catch((error) => console.error("Error fetching value from Redis:", error));
    }

    updatePlayerNames() {
        this.player1Name = document.getElementById("player1").value;
        this.player2Name = document.getElementById("player2").value;

        const player1Area = this.isMobile
            ? document.querySelectorAll(".mobile-only .player1-area")
            : document.querySelectorAll(".player1-area");
        const player2Area = this.isMobile
            ? document.querySelectorAll(".mobile-only .player2-area")
            : document.querySelectorAll(".player2-area");

        player1Area.forEach((area) => (area.textContent = this.player1Name));
        player2Area.forEach((area) => (area.textContent = this.player2Name));

        const playerTitles = this.isMobile
        ? document.querySelectorAll('.mobile-only .player-title')
        : document.querySelectorAll('.player-title');

        playerTitles[0].textContent = this.player1Name;
        playerTitles[1].textContent = this.player2Name;
    }

    updateProgress(newProgress) {
        this.progress = newProgress;
        this.elements.progressBar.style.width = `${this.progress}%`;
        this.elements.progressBar.innerHTML = `${this.progress}%`;
    }

    // Function to add or remove a class from an element
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

    // Function to process strategy data from WebSocket
    processStrategyData(data) {
        console.log("Processing strategy data:", data);

        // Determine keys to update based on whether the view is mobile or desktop
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

        // Iterate over the data object to process the strategy data
        for (const [key, value] of Object.entries(data)) {
            // Handle yes/no and cards_2_3 type keys for binary tree routes
            if (key.includes('yes_no') || key.includes('cards_2_3')) {
                if (value.startsWith('Yes')) {
                    this.arrayTemp.push(value);
                } else if (value.includes('No')) {
                    this.arrayTemp.push(value);
                } else if (value.startsWith('Two')) {
                    this.arrayTemp.push(value);
                } else if (value.startsWith('Three')) {
                    this.arrayTemp.push(value);
                }

                // Manage the iteration and arrayRouteBinTree updates
                if (this.iterations.iter1 === 0 && (this.arrayTemp.length === 2 || this.arrayTemp[0] === 'No')) {
                    this.arrayTemp.unshift("main");
                    this.arrayRouteBinTree1 = this.arrayTemp.slice(); // Shallow copy to store the values
                    console.log(this.arrayTemp, "1");
                    this.arrayTemp = [];
                    this.iterations.iter1 += 1;
                } else if (this.iterations.iter1 === 1 && (this.arrayTemp.length === 2 || this.arrayTemp[0] === 'No')) {
                    this.arrayTemp.unshift("main");
                    this.arrayRouteBinTree2 = this.arrayTemp.slice(); // Shallow copy to store the values
                    console.log(this.arrayTemp, "2");
                    this.arrayTemp = [];
                    this.iterations.iter1 += 1;
                }
            }

            // Update percentage texts in the DOM based on keysToUpdate mapping
            if (key in keysToUpdate) {
                const extractedText = this.extractText(value);
                const rounded = (parseFloat(extractedText) * 100).toFixed(1);
                this.updatePercentage(keysToUpdate[key], rounded);
            } else {
                // If the key does not match expected keys, log for debugging
                this.logStrategyKey(key, value);
            }
        }
    }

    extractText(input) {
        const match = input.match(/^\d+\((.*?)\)$/);
        return match ? match[1] : ''; // Return the captured group or an empty string if no match
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



    updateBorders(progressGames, isFirstSet, data) {
        if (!progressGames) return;

        if ('exchange_cards' in data) {
            const exchangeCardsText = data.exchange_cards === 't' ? 'TAK' : 'NIE';
            if (progressGames[0]) progressGames[0].textContent = `Wymiana kart: ${exchangeCardsText}`;
        }

        if ('amount' in data) {
            const amount = data.amount;
            if (progressGames[3]) progressGames[3].textContent = `Ile kart: ${amount}`;
            this.isProgressGameBorders = !isFirstSet;
        }

        if ('type_arrangement_result' in data) {
            const typeArrangementResult = data.type_arrangement_result;
            const arrangementElement = this.iterations.iter4 === 0 ?
                (this.isMobile ? document.querySelector('.mobile-only .arrangement-result-1') : document.querySelector('.arrangement-result-1')) :
                (this.isMobile ? document.querySelector('.mobile-only .arrangement-result-2') : document.querySelector('.arrangement-result-2'));
            if (arrangementElement) {
                arrangementElement.textContent = typeArrangementResult;

                if (this.iterations.iter4 === 1) {
                    this.arrangement_result_off = true
                }
        
            }
            this.iterations.iter4 = (this.iterations.iter4 + 1) % 2;
        }
    }

    // Function to check if required keys are in the data
    hasRequiredKeys(data) {
        // Define the keys you're expecting in `data`
        const requiredKeys = ['p1_2x_1', 'p1_2x_0', 'p2x', 'p1x', 'yes_no', 'cards_2_3'];
        return requiredKeys.some(key => key in data);  // Returns true if any of the required keys exist in `data`
    }

    // Function to dynamically update the text
    updateProgressGameText(data) {
        if (this.isProgressGameBorders === false && this.progressGameBorders1) {
            const progressGames = this.progressGameBorders1[0].querySelectorAll('.progress-game');
            this.updateBorders(progressGames, false, data);
        } else if (this.isProgressGameBorders === true && this.progressGameBorders2) {
            const progressGames = this.progressGameBorders2[0].querySelectorAll('.progress-game');
            this.updateBorders(progressGames, true, data);
        }
    }

    waitForChances(data, progressGames) {
        if (this.chancesInterval) {
            clearInterval(this.chancesInterval);
        }

        this.chancesInterval = setInterval(() => {
            if ('chances' in data) {
                const chances = data.chances;
                console.log("Chances before: ", chances);

                if (this.isChances) {
                    if (progressGames[1]) {
                        progressGames[1].textContent = `Szansa (2 karty): ${chances}%`;
                        console.log(chances);
                    }
                    this.isChances = false;
                } else {
                    if (progressGames[2]) {
                        progressGames[2].textContent = `Szansa (3 karty): ${chances}%`;
                        console.log(chances);
                    }
                    this.isChances = true;
                }

                const chances_2 = progressGames[1]?.textContent.includes("Szansa (2 karty)");
                const chances_3 = progressGames[2]?.textContent.includes("Szansa (3 karty)");
                if (chances_2 && chances_3) {
                    clearInterval(this.chancesInterval);
                }
            }
        }, 100);
    }

        // Animate the binary tree with the data from the binary tree arrays
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
            
                        // Set appropriate classes based on the element
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
    
            if (this.iterations.iter2 === 0) {
                playerName.textContent = this.player1Name;
                this.iterations.iter2 = 1;
            }
            processArray(animationContainer[0].array, () => {
                if (this.iterations.iter2 === 1) {
                    playerName.textContent = this.player2Name;
                    this.iterations.iter2 = 0;
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
                if (element) {
                    element.classList.remove("active");
                }
            });
        }
}

// Class for Handling UI Elements
class UIElements {
    constructor(isMobile) {
        this.isMobile = isMobile;
        this.playButton = document.getElementById("playButton");
        this.nextButton1 = isMobile ? document.getElementById("nextButton1Mobile") : document.getElementById("nextButton1");
        this.nextButton2 = isMobile ? document.getElementById("nextButton2Mobile") : document.getElementById("nextButton2");
        this.progressBar = document.getElementById("progressBar");
    }

    reset() {
        this.progressBar.style.width = "0%";
        this.progressBar.innerHTML = "0%";
    }

    resetProgressBar() {
        this.progressBar.style.width = "0%";
        this.progressBar.innerHTML = "0%";
    }
}

// Class for Handling WebSocket Connections
class WebSocketHandler {
    constructor(gameInstance) {
        this.gameInstance = gameInstance;
        this.socket = null;
    }

    async init() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            console.log("Closing previous WebSocket...");
            this.socket.close();
        }
        this.socket = this.createWebSocket();
        console.log(this.socket)
        await this.waitForSocketOpen();
        this.setupSocketHandlers();
    }

    createWebSocket() {
        if (window.env.IS_DEV.includes("yes")) {
            return new WebSocket("wss://127.0.0.1:8000/ws/op_game/");
        } else {
            return new WebSocket("wss://pokersimulation.onrender.com/ws/op_game/");
        }
    }

    async waitForSocketOpen() {
        return new Promise((resolve, reject) => {
            if (this.socket.readyState === WebSocket.OPEN) {
                resolve();
            } else {
                this.socket.onopen = () => resolve();
                this.socket.onerror = (error) => reject(error);
            }
        });
    }

    setupSocketHandlers() {
        this.socket.onmessage = (event) => this.handleSocketMessage(event);
        this.socket.onerror = (error) => console.error('WebSocket error:', error);
        this.socket.onclose = () => console.log('WebSocket connection closed');
    }

    handleSocketMessage(event) {
        const data = JSON.parse(event.data);
        console.log("Received data:", data);

        if ('cards' in data) {
            this.handleCardsData(data.cards);
        }

        if ('exchange_cards' in data || 'amount' in data || 'type_arrangement_result' in data || 'chances' in data) {
            // Determine which game border set to update based on `isProgressGameBorders`
            const progressGames = this.gameInstance.isProgressGameBorders === false 
                ? this.gameInstance.progressGameBorders1[0].querySelectorAll('.progress-game')
                : this.gameInstance.progressGameBorders2[0].querySelectorAll('.progress-game');
            
            this.gameInstance.updateBorders(progressGames, this.gameInstance.isProgressGameBorders, data);

            // Specifically handle chances data for dynamic updates
            if ('chances' in data) {
                this.gameInstance.waitForChances(data, progressGames);
            }
        }

        if ('progress' in data) {
            this.gameInstance.updateProgress(data.progress);
        }

        if ('type_arrangement' in data) {
            this.handleArrangementData(data.type_arrangement);
        }


        if ('first_second' in data) {
            this.gameInstance.firstSecond = data.first_second;
            if (this.gameInstance.firstSecond === '0') {
                this.gameInstance.toggleClass("result-info-1", "active", 'result');
            } else if (this.gameInstance.firstSecond === '1') {
                this.gameInstance.toggleClass("result-info-2", "active", 'result');
                this.gameInstance.elements.nextButton1.disabled = true;
                this.gameInstance.elements.nextButton2.disabled = true;
            }

        }

        if ('strategy_one' in data || 'strategy_two' in data) {
            this.gameInstance.processStrategyData(data);
        }

        if (this.gameInstance.hasRequiredKeys(data)) {
            this.gameInstance.processStrategyData(data);
        }

        if (this.gameInstance.iterations.iter1 === 2) {
            this.gameInstance.animateBinaryTree();
        }
    }

    handleCardsData(cards) {
        console.log("Handling cards:", cards);

        // Determine if the view is mobile
        this.gameInstance.isMobile = window.innerWidth <= 768;

        // Determine which set of cards container to use based on iteration and result status
        let cardsContainerSelector = "";
        if (this.gameInstance.iterations.iter === 0) {
            if (this.gameInstance.isResult) {
                cardsContainerSelector = this.gameInstance.isMobile 
                    ? '.mobile-only .cards-3 .card'
                    : '.cards-3 .card';
            } else {
                cardsContainerSelector = this.gameInstance.isMobile 
                    ? '.mobile-only .cards-1 .card'
                    : '.cards-1 .card';
            }
        } else if (this.gameInstance.iterations.iter === 1) {
            if (this.gameInstance.isResult) {
                cardsContainerSelector = this.gameInstance.isMobile 
                    ? '.mobile-only .cards-4 .card'
                    : '.cards-4 .card';
            } else {
                cardsContainerSelector = this.gameInstance.isMobile 
                    ? '.mobile-only .cards-2 .card'
                    : '.cards-2 .card';
                
                this.gameInstance.isResult = true;

            }
        }

        // Select the card container elements
        this.gameInstance.cardsContainer = document.querySelectorAll(cardsContainerSelector);

        // Debugging: Log the container elements
        console.log("Selected cards container:", cardsContainerSelector);
        console.log("Found card elements:", this.gameInstance.cardsContainer);

        // Update iteration state
        this.gameInstance.iterations.iter = (this.gameInstance.iterations.iter + 1) % 2;

        // Update the card containers with the card images if elements are found
        if (this.gameInstance.cardsContainer.length === 0) {
            console.warn("No card container elements found for selector:", cardsContainerSelector);
        } else {
            cards.forEach((card, index) => {
                if (this.gameInstance.cardsContainer[index]) {
                    // Set the background image for each card element
                    this.gameInstance.cardsContainer[index].style.backgroundImage = `url("/static/css/img/${card}.png")`;
                    console.log(`Card ${index + 1} updated with image: /static/css/img/${card}.png`);

                    // Force a repaint to ensure the image is updated in the DOM
                    this.gameInstance.cardsContainer[index].style.display = 'none';
                    setTimeout(() => {
                        this.gameInstance.cardsContainer[index].style.display = 'block';
                    }, 10);
                } else {
                    console.warn(`Card container not found for index ${index}`);
                }
            });
        }

        // Additional logic to handle the iteration state and set result flag
        if (this.gameInstance.iterations.iter === 2) {
            if (!this.gameInstance.isResult) {
                setTimeout(() => {
                    this.gameInstance.elements.nextButton1.disabled = false;
                    this.gameInstance.elements.nextButton2.disabled = true;            
                }, this.gameInstance.executeFunction ? 6500 : 2000);  
            }

            // Reset iter and set isResult to true for the next iteration
            this.gameInstance.iterations.iter = 0;
            this.gameInstance.isResult = true;
        }
    }

    handleArrangementData(typeArrangement) {
        const arrangementSelector = this.gameInstance.iterations.iter3 === 0 ? '.arrangement-1' : '.arrangement-2';
        let arrangementElement;
    
        if (this.gameInstance.isMobile) {
            // Use querySelectorAll for mobile and ensure we set textContent for each matching element
            const arrangementElements = document.querySelectorAll(`.mobile-only ${arrangementSelector}`);
            if (arrangementElements.length > 0) {
                arrangementElements.forEach(element => {
                    element.textContent = typeArrangement;
                });
            } else {
                console.warn(`Mobile arrangement element with selector '.mobile-only ${arrangementSelector}' not found.`);
            }
        } else {
            // Use querySelector for desktop
            arrangementElement = document.querySelector(arrangementSelector);
            if (arrangementElement) {
                arrangementElement.textContent = typeArrangement;
            } else {
                console.warn(`Desktop arrangement element with selector '${arrangementSelector}' not found.`);
            }
        }
    
        // Update the iteration counter
        this.gameInstance.iterations.iter3 = (this.gameInstance.iterations.iter3 + 1) % 2;
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
        onePairGame.blockRefresh = true;   
        // Check every 100 milliseconds
        if (onePairGame.progress > 0) {
            // Hide the loader once the condition is met
            const loaderContainer = document.getElementById('loaderContainer');
            if (loaderContainer) loaderContainer.style.display = 'none';

            // Make the content visible
            const content = document.getElementById('content');
            if (content) content.style.visibility = 'visible';

            // Stop further checks
            clearInterval(checkLoadingStatus);
        }
    }, 100);
});