// Refactored code for "OnePairGame" class split into multiple classes for better readability

// Main Game Logic Class
// Main Game Logic Class
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

        // Player names
        this.player1Name = document.getElementById("player1").value;
        this.player2Name = document.getElementById("player2").value;

        this.elements = new UIElements(isMobile);
        this.init();
    }

    init() {
        this.updatePlayerNames();
        this.initializeWebSocket();
        this.attachEventListeners();
        window.addEventListener("beforeunload", this.handleBeforeUnload.bind(this));
        window.addEventListener("resize", () => {
            this.isMobile = window.innerWidth <= 768;
            console.log("Viewport resized. Is mobile:", this.isMobile);
        });
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
        const socketHandler = new WebSocketHandler(this);
        await socketHandler.init();
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
            })
            .catch((error) => {
                console.error("Error starting game:", error);
                alert("An error occurred while starting the game. Please try again.");
            });
    }

    reinitializeInstance() {
        console.log("Reinitializing instance...");
        this.resetInstanceVariables();
        this.initializeWebSocket();
    }

    resetInstanceVariables() {
        this.progress = 0;
        this.isStopping = false;
        this.iterations = { iter: 0, iter1: 0, iter2: 0, iter3: 0, iter4: 0 };
        this.arrayTemp = [];
        this.arrayRouteBinTree1 = [];
        this.arrayRouteBinTree2 = [];
        this.cardsContainer = null;
        this.timeoutIds = [];
        this.elements.reset();
    }

    async handleBeforeUnload() {
        console.log("Stopping background task...");
        await this.stopTask();
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

    waitForSocketOpen() {
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
        console.log(data);

        if ('cards' in data) {
            this.handleCardsData(data.cards);
        }

        if ('type_arrangement' in data) {
            this.handleArrangementData(data.type_arrangement);
        }

        if ('progress' in data) {
            this.gameInstance.updateProgress(data.progress);
        }

        if ('exchange_cards' in data || 'amount' in data || 'type_arrangement_result' in data || 'animate_binary_tree' in data) {
            const progressGames = this.gameInstance.isMobile
                ? document.querySelectorAll('.mobile-only .progress-game-border-1 .progress-game')
                : document.querySelectorAll('.progress-game-border-1 .progress-game');
            this.gameInstance.updateBorders(progressGames, false, data);
        }

        if ('first_second' in data) {
            this.gameInstance.firstSecond = data.first_second;
            if (this.gameInstance.firstSecond === '0') {
                this.gameInstance.toggleClass("result-info-1", "active", 'result');
            } else if (this.gameInstance.firstSecond === '1') {
                this.gameInstance.toggleClass("result-info-2", "active", 'result');
            }
            this.gameInstance.elements.nextButton1.disabled = true;
            this.gameInstance.elements.nextButton2.disabled = true;
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
        this.gameInstance.isMobile = window.innerWidth <= 768;
        const cardSet = this.gameInstance.iterations.iter === 0 ? 1 : 2;
        const cardContainerSelector = this.getCardContainerSelector(cardSet);
        this.gameInstance.cardsContainer = document.querySelectorAll(cardContainerSelector);

        cards.forEach((card, index) => {
            if (this.gameInstance.cardsContainer[index]) {
                this.gameInstance.cardsContainer[index].style.backgroundImage = `url("/static/css/img/${card}.png")`;
            }
        });
        this.gameInstance.iterations.iter = (this.gameInstance.iterations.iter + 1) % 2;
    }

    getCardContainerSelector(set) {
        if (this.gameInstance.isMobile) {
            return set === 1 ? '.mobile-only .cards-1 .card' : '.mobile-only .cards-2 .card';
        } else {
            return set === 1 ? '.cards-1 .card' : '.cards-2 .card';
        }
    }

    handleArrangementData(typeArrangement) {
        const arrangementSelector = this.gameInstance.iterations.iter3 === 0 ? '.arrangement-1' : '.arrangement-2';
        const arrangementElement = this.gameInstance.isMobile ? document.querySelectorAll(`.mobile-only ${arrangementSelector}`) : document.querySelector(arrangementSelector);
        arrangementElement.textContent = typeArrangement;
        this.gameInstance.iterations.iter3 = (this.gameInstance.iterations.iter3 + 1) % 2;
    }
}

// Initialize Game Instance
document.addEventListener("DOMContentLoaded", () => {
    const isMobile = window.innerWidth <= 768;
    const onePairGame = new OnePairGame(true, isMobile);
});