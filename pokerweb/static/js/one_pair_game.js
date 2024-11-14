class CardsPermutations {
    connectWebSocket() {
        this.socket = new WebSocket('wss://127.0.0.1:8000/ws/one_pair_game/');
        
        this.socket.onopen = () => console.log("WebSocket connection opened");
        this.socket.onmessage = (event) => this.handleSocketMessage(event);
        this.socket.onclose = () => {
            console.log("WebSocket connection closed");
            this.socket.close();
        };
    }
}