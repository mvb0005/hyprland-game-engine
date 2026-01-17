import '../shared/styles.css';
import { ControllerGrid } from './ControllerGrid';
import { Board } from '../shared/types';
import { io, Socket } from 'socket.io-client';

console.log('Controller Initialized');

const app = document.querySelector<HTMLDivElement>('#app');
const socket: Socket = io(import.meta.env.VITE_SERVER_URL || 'http://localhost:3000');

let activeGrid: ControllerGrid | null = null;
let playerName = '';

function renderGame() {
    if(!app) return;
    app.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; height: 100vh; overflow: hidden; background: #11111b;">
            <!-- Header -->
            <div id="word-display" style="height: 120px; width: 100%; display: flex; align-items: center; justify-content: center; background: #1e1e2e; border-bottom: 1px solid #313244; flex-shrink: 0;">
                <span id="current-word" style="font-size: 3rem; font-weight: bold; color: #f9e2af; font-family: monospace; letter-spacing: 0.1em;"></span>
            </div>
            
            <!-- Grid Wrapper (Centers the board) -->
            <div style="flex-grow: 1; width: 100%; display: flex; align-items: center; justify-content: center; padding: 20px; box-sizing: border-box;">
                <div id="grid-container"></div>
            </div>
            
            <!-- Footer/Feedback -->
            <div id="feedback" style="height: 60px; display: flex; align-items: center; justify-content: center; color: #a6e3a1; font-weight: bold; font-size: 1.2rem; flex-shrink: 0;"></div>
        </div>
    `;

    const gridContainer = document.getElementById('grid-container');
    const wordDisplay = document.getElementById('current-word');
    const feedback = document.getElementById('feedback');

    if (gridContainer) {
        activeGrid = new ControllerGrid(gridContainer, 
            (ids) => {
                console.log("Submitted word path:", ids);
                // Convert ["0-0", "0-1"] -> [{x:0, y:0}, {x:0, y:1}]
                const coords = ids.map(id => {
                    const parts = id.split('-');
                    return { x: parseInt(parts[0]), y: parseInt(parts[1]) };
                });
                socket.emit('submit_move', coords);
            },
            (word) => {
                if(wordDisplay) wordDisplay.innerText = word;
            }
        );
    }

    socket.on('move_result', (result: any) => {
        if(feedback) {
            if(result.success) {
                feedback.innerText = `+${result.score} PTS`;
                feedback.style.color = '#a6e3a1'; // Green
                // Clear word on success
                if(wordDisplay) wordDisplay.innerText = "";
                // Reset internal state of grid if needed
                activeGrid?.resetSelection(); 
            } else {
                feedback.innerText = result.message;
                feedback.style.color = '#f38ba8'; // Red
            }
            feedback.style.opacity = '1';
            setTimeout(() => feedback.style.opacity = '0', 1500);
        }
    });

    socket.on('state_update', (state: any) => {
        if (!activeGrid) return;

        const rows = state.grid;
        const height = rows.length;
        const width = rows[0].length;
        
        const cells = rows.map((row: any[], y: number) => 
          row.map((tile: any, x: number) => ({
            id: `${x}-${y}`,
            char: tile.char,
            value: 1, 
            ownerId: tile.ownerId,
            locked: false
          }))
        );

        const board: Board = { width, height, cells };
        activeGrid.render(board);
    });
}

if (app) {
    // Basic Join Screen
  app.innerHTML = `
    <div style="padding: 20px; text-align: center;">
      <h2>Lexigraph</h2>
      <input id="name-input" type="text" placeholder="Your Name" style="padding: 15px; font-size: 1.2rem; width: 80%; border-radius: 8px; border: none; margin-bottom: 20px;" />
      <button id="join-btn" style="padding: 15px 30px; font-size: 1.2rem; background: #89b4fa; border: none; border-radius: 8px; cursor: pointer; color: #1e1e2e; font-weight: bold;">JOIN GAME</button>
    </div>
  `;
  
  document.getElementById('join-btn')?.addEventListener('click', () => {
      const input = document.getElementById('name-input') as HTMLInputElement;
      playerName = input.value || 'Player';
      socket.emit('join_game', playerName);
      renderGame();
  });
}

