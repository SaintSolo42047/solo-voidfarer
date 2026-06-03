// Color constants
const BLACK = '#000000';
const WHITE = '#ffffff';
const BLUE = '#6496ff';
const RED = '#ff6464';
const GREEN = '#64ff64';
const GRAY = '#505050';

class Ship {
    constructor(x, y) {
        this.modules = { engine: 1, scanner: 1, shield: 1, weapon: 1, cargo: 1 };
        this.resources = { fuel: 10, oxygen: 10, data: 10 };
        this.action_points = 3;
        this.x = x;
        this.y = y;
        this.thrust = 0;
    }

    draw(ctx) {
        // Ship triangle
        ctx.fillStyle = BLUE;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y - 20);
        ctx.lineTo(this.x - 20, this.y + 20);
        ctx.lineTo(this.x + 20, this.y + 20);
        ctx.closePath();
        ctx.fill();

        // Cockpit
        ctx.fillStyle = WHITE;
        ctx.fillRect(this.x - 8, this.y - 8, 16, 16);

        // Cargo hold
        ctx.fillStyle = GRAY;
        ctx.fillRect(this.x - 15, this.y + 10, 30, 8);

        // Thrust flame
        if (this.thrust > 0) {
            ctx.fillStyle = RED;
            ctx.beginPath();
            ctx.moveTo(this.x - 10, this.y + 20);
            ctx.lineTo(this.x, this.y + 30);
            ctx.lineTo(this.x + 10, this.y + 20);
            ctx.closePath();
            ctx.fill();
        }
    }
}

class Goal {
    constructor(name, difficulty) {
        this.name = name;
        this.difficulty = difficulty;
        this.progress = 0;
    }

    mark(amount) {
        this.progress = Math.min(10, this.progress + amount);
    }
}

class Button {
    constructor(x, y, width, height, text) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.text = text;
        this.hovered = false;
    }

    contains(px, py) {
        return px >= this.x && px <= this.x + this.width &&
               py >= this.y && py <= this.y + this.height;
    }

    draw(ctx) {
        const color = this.hovered ? '#96c8ff' : BLUE;
        ctx.fillStyle = color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
        ctx.strokeStyle = WHITE;
        ctx.lineWidth = 2;
        ctx.strokeRect(this.x, this.y, this.width, this.height);

        // Text
        ctx.fillStyle = WHITE;
        ctx.font = '16px "Courier New"';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this.text, this.x + this.width / 2, this.y + this.height / 2);
    }
}

class Game {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Set canvas size
        this.canvas.width = 1280;
        this.canvas.height = 720;

        this.ship = new Ship(this.canvas.width / 2, this.canvas.height / 2);
        this.goals = [
            new Goal("Reach next sector", "Normal"),
            new Goal("Upgrade scanner", "Easy")
        ];
        this.log = ["Welcome. Tap buttons to play."];
        this.state = "play";
        this.show_tutorial = true;

        // Action buttons
        this.buttons = [
            new Button(this.canvas.width - 200, 50, 180, 50, "Progress"),
            new Button(this.canvas.width - 200, 110, 180, 50, "Travel"),
            new Button(this.canvas.width - 200, 170, 180, 50, "Arrive"),
            new Button(this.canvas.width - 200, 230, 180, 50, "Scavenge"),
            new Button(this.canvas.width - 200, 290, 180, 50, "Explore"),
            new Button(this.canvas.width - 200, 350, 180, 50, "Resources"),
            new Button(this.canvas.width - 200, 410, 180, 50, "Combat"),
            new Button(this.canvas.width - 200, 470, 180, 50, "Status"),
        ];

        // Movement buttons
        this.move_buttons = [
            new Button(this.canvas.width / 2 - 40, 100, 80, 80, "↑"),
            new Button(50, this.canvas.height - 150, 80, 80, "←"),
            new Button(150, this.canvas.height - 150, 80, 80, "↓"),
            new Button(250, this.canvas.height - 150, 80, 80, "→"),
        ];

        // Event listeners
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));

        // Start game loop
        this.run();
    }

    addLog(text) {
        this.log.push(text);
        if (this.log.length > 8) {
            this.log.shift();
        }
    }

    roll2d20(advantage = false) {
        const dice = [];
        const count = advantage ? 3 : 2;
        for (let i = 0; i < count; i++) {
            dice.push(Math.floor(Math.random() * 20) + 1);
        }
        
        let result = dice;
        if (advantage) {
            result = dice.sort((a, b) => a - b).slice(0, 2);
        }
        
        const successes = result.filter(d => d <= 10).length;
        return { successes, dice: result };
    }

    getMousePos(e) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }

    getTouchPos(touch) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        return {
            x: (touch.clientX - rect.left) * scaleX,
            y: (touch.clientY - rect.top) * scaleY
        };
    }

    handleMouseMove(e) {
        const pos = this.getMousePos(e);
        this.updateButtonHovers(pos);
    }

    handleTouchMove(e) {
        e.preventDefault();
        if (e.touches.length > 0) {
            const pos = this.getTouchPos(e.touches[0]);
            this.updateButtonHovers(pos);
        }
    }

    updateButtonHovers(pos) {
        this.buttons.forEach(btn => {
            btn.hovered = btn.contains(pos.x, pos.y);
        });
        this.move_buttons.forEach(btn => {
            btn.hovered = btn.contains(pos.x, pos.y);
        });
    }

    handleClick(e) {
        const pos = this.getMousePos(e);
        this.processClick(pos);
    }

    handleTouchStart(e) {
        e.preventDefault();
        if (e.touches.length > 0) {
            const pos = this.getTouchPos(e.touches[0]);
            this.processClick(pos);
        }
    }

    processClick(pos) {
        // Movement buttons
        if (this.move_buttons[0].contains(pos.x, pos.y)) { // Up
            this.ship.y -= 10;
            this.ship.thrust = 5;
        } else if (this.move_buttons[1].contains(pos.x, pos.y)) { // Left
            this.ship.x -= 10;
        } else if (this.move_buttons[2].contains(pos.x, pos.y)) { // Down
            this.ship.y += 10;
            this.ship.thrust = 5;
        } else if (this.move_buttons[3].contains(pos.x, pos.y)) { // Right
            this.ship.x += 10;
        }

        // Action buttons
        for (const btn of this.buttons) {
            if (btn.contains(pos.x, pos.y)) {
                this.handleButton(btn.text);
            }
        }

        // Tutorial close
        if (this.show_tutorial && pos.x >= this.canvas.width / 2 - 50 &&
            pos.x <= this.canvas.width / 2 + 50 &&
            pos.y >= this.canvas.height - 150 &&
            pos.y <= this.canvas.height - 100) {
            this.show_tutorial = false;
        }
    }

    handleButton(btnText) {
        if (btnText === "Progress") {
            const result = this.roll2d20();
            this.addLog(`Progress roll ${result.dice} -> ${result.successes} successes`);
            this.goals[0].mark(result.successes);
        } else if (btnText === "Travel") {
            this.addLog("Engaging FTL drive...");
            this.ship.resources.fuel -= 2;
        } else if (btnText === "Arrive") {
            this.addLog("Exiting jump space. Scanning sector...");
        } else if (btnText === "Scavenge") {
            const result = this.roll2d20();
            this.addLog(`Scavenging: ${result.successes} items found`);
            this.ship.resources.data += result.successes;
        } else if (btnText === "Explore") {
            this.addLog("Deploying probes...");
            this.ship.resources.oxygen -= 1;
        } else if (btnText === "Resources") {
            this.addLog(`Fuel: ${this.ship.resources.fuel} | O2: ${this.ship.resources.oxygen} | Data: ${this.ship.resources.data}`);
        } else if (btnText === "Combat") {
            const result = this.roll2d20(true);
            this.addLog(`Combat roll: ${result.successes} hits!`);
        } else if (btnText === "Status") {
            this.addLog("All systems operational.");
        }
    }

    drawStarfield() {
        for (let i = 0; i < 80; i++) {
            const x = Math.random() * this.canvas.width;
            const y = Math.random() * this.canvas.height;
            this.ctx.fillStyle = WHITE;
            this.ctx.fillRect(x, y, 1, 1);
        }

        // Hyperspace line
        this.ctx.strokeStyle = 'rgb(50, 0, 100)';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(200, 100);
        this.ctx.lineTo(400, 300);
        this.ctx.stroke();
    }

    drawTutorial() {
        // Semi-transparent overlay
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        this.ctx.fillRect(100, 100, this.canvas.width - 200, this.canvas.height - 200);

        // Border
        this.ctx.strokeStyle = GREEN;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(100, 100, this.canvas.width - 200, this.canvas.height - 200);

        // Title
        this.ctx.fillStyle = GREEN;
        this.ctx.font = 'bold 32px "Courier New"';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('TUTORIAL - Solo Voidfarer', this.canvas.width / 2, 150);

        // Tutorial text
        const lines = [
            "Tap arrow buttons to move ship",
            "Tap sidebar buttons for Moves",
            "Progress bars fill as you complete missions",
            "Resources deplete on Travel and Explore",
            "NPCs use Perilous Void tables for dialog"
        ];

        this.ctx.fillStyle = WHITE;
        this.ctx.font = '16px "Courier New"';
        this.ctx.textAlign = 'left';
        lines.forEach((line, i) => {
            this.ctx.fillText(line, 150, 220 + i * 30);
        });

        // Close button
        const closeBtn = new Button(this.canvas.width / 2 - 50, this.canvas.height - 150, 100, 50, "Close");
        closeBtn.draw(this.ctx);
    }

    drawUI() {
        // Sidebar buttons
        this.buttons.forEach(btn => btn.draw(this.ctx));

        // Movement buttons
        this.move_buttons.forEach(btn => btn.draw(this.ctx));

        // Ship
        this.ship.draw(this.ctx);

        // Log
        this.ctx.fillStyle = WHITE;
        this.ctx.font = '14px "Courier New"';
        this.ctx.textAlign = 'left';
        this.log.slice(-5).forEach((line, i) => {
            this.ctx.fillText(line, 20, this.canvas.height - 150 + i * 25);
        });
    }

    run = () => {
        // Clear canvas
        this.ctx.fillStyle = BLACK;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Starfield
        this.drawStarfield();

        // Draw UI
        this.drawUI();

        // Draw tutorial if needed
        if (this.show_tutorial) {
            this.drawTutorial();
        }

        // Update thrust
        this.ship.thrust = Math.max(0, this.ship.thrust - 1);

        // Continue loop
        requestAnimationFrame(this.run);
    }
}

// Start game when page loads
window.addEventListener('DOMContentLoaded', () => {
    new Game('gameCanvas');
});
