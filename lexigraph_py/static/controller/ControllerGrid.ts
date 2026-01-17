import { Board } from '../shared/types';
import { AudioController } from './AudioController';

export class ControllerGrid {
    private container: HTMLElement;
    private cells: Map<string, { el: HTMLElement, x: number, y: number, char: string }> = new Map();
    private isDragging: boolean = false;
    private selectedPath: string[] = []; // List of cell IDs
    private onWordSubmit: (wordIds: string[]) => void;
    private onSelectionChange: (word: string) => void;
    private audio: AudioController;

    constructor(container: HTMLElement, onWordSubmit: (ids: string[]) => void, onSelectionChange: (word: string) => void) {
        this.container = container;
        this.onWordSubmit = onWordSubmit;
        this.onSelectionChange = onSelectionChange;
        this.audio = new AudioController();
        
        // Bind event listeners globally for drag behavior
        window.addEventListener('pointerup', this.handlePointerUp.bind(this));
        window.addEventListener('pointermove', this.handleGlobalPointerMove.bind(this));
    }

    render(board: Board) {
        this.container.innerHTML = '';
        this.cells.clear();
        
        // CSS Grid Layout
        this.container.style.display = 'grid';
        this.container.style.gridTemplateColumns = `repeat(${board.width}, 1fr)`;
        this.container.style.gap = '8px';
        this.container.style.padding = '10px';
        this.container.style.width = '100%';
        this.container.style.maxWidth = '400px'; // Limit max size
        this.container.style.aspectRatio = '1/1'; // Force square aspect ratio
        this.container.style.touchAction = 'none'; // Prevent scrolling
        this.container.style.userSelect = 'none';
        this.container.style.webkitUserSelect = 'none';

        board.cells.forEach((row, y) => {
            row.forEach((cell, x) => {
                const el = document.createElement('div');
                el.className = 'grid-cell';
                el.dataset.id = cell.id;
                el.textContent = cell.char;
                
                // Base Styles
                el.style.display = 'flex';
                el.style.justifyContent = 'center';
                el.style.alignItems = 'center';
                el.style.fontSize = '2rem';
                el.style.fontWeight = 'bold';
                el.style.borderRadius = '8px';
                el.style.userSelect = 'none';
                el.style.webkitUserSelect = 'none';
                el.style.cursor = 'pointer';
                el.style.background = '#313244';
                el.style.color = '#cdd6f4';

                // We attach pointerdown to start the gesture from a valid cell
                el.addEventListener('pointerdown', (e) => this.handlePointerDown(e, cell.id));

                this.container.appendChild(el);
                this.cells.set(cell.id, { el, x, y, char: cell.char });
            });
        });
    }

    private handlePointerDown(e: PointerEvent, id: string) {
        this.isDragging = true;
        this.selectedPath = [id];
        this.updateVisuals();
        
        // Check compatibility (iOS Safari doesn't support navigator.vibrate)
        if (navigator.vibrate) {
            navigator.vibrate(20);
        }
        
        this.audio.playClick(1);
        
        // Important: Release capture so global pointermove works freely
        (e.target as HTMLElement).releasePointerCapture(e.pointerId); 
    }

    private handleGlobalPointerMove(e: PointerEvent) {
        if (!this.isDragging) return;

        // Find element under pointer
        const target = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement;
        if (!target) return;

        // Check if it's one of our cells
        const id = target.dataset.id;
        if (!id || !this.cells.has(id)) return;

        // Hit Detection Refinement:
        // Only select if we are "deep" enough into the cell (inner 75%)
        // This prevents clipping corners when moving diagonally
        const rect = target.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        // Calculate distance from center normalized to size (0 to 1)
        // We use a box check rather than circle for grid feel
        const relativeX = Math.abs(e.clientX - centerX) / (rect.width / 2);
        const relativeY = Math.abs(e.clientY - centerY) / (rect.height / 2);

        // If we are on the edge (outer 25%), ignore this hit
        if (relativeX > 0.75 || relativeY > 0.75) return;

        this.processMoveTo(id);
    }

    private processMoveTo(id: string) {
        const lastId = this.selectedPath[this.selectedPath.length - 1];
        
        // Case 1: Same cell, do nothing
        if (id === lastId) return;

        // Case 2: Backtracking (User moves back to previous cell)
        if (this.selectedPath.length > 1 && id === this.selectedPath[this.selectedPath.length - 2]) {
             this.selectedPath.pop();
             this.updateVisuals();
             if (navigator.vibrate) navigator.vibrate(10);
             return;
        }

        // Case 3: Already selected elsewhere (Invalid loop)
        if (this.selectedPath.includes(id)) return;

        // Case 4: Valid move?
        if (this.isAdjacent(lastId, id)) {
            this.selectedPath.push(id);
            this.updateVisuals();
            if (navigator.vibrate) navigator.vibrate(20);
            this.audio.playClick(this.selectedPath.length);
        }
    }

    private isAdjacent(id1: string, id2: string): boolean {
        const c1 = this.cells.get(id1);
        const c2 = this.cells.get(id2);
        if (!c1 || !c2) return false;

        const dx = Math.abs(c1.x - c2.x);
        const dy = Math.abs(c1.y - c2.y);

        return dx <= 1 && dy <= 1 && !(dx === 0 && dy === 0);
    }

    private handlePointerUp() {
        if (!this.isDragging) return;
        this.isDragging = false;
        
        if (this.selectedPath.length >= 3) {
            this.onWordSubmit(this.selectedPath);
            this.audio.playSubmitSuccess();
        }
        
        this.selectedPath = [];
        this.updateVisuals();
    }

    public resetSelection() {
        this.selectedPath = [];
        this.updateVisuals();
    }

    private updateVisuals() {
        let currentWord = "";
        
        // 1. Reset everything first
        this.cells.forEach((data, id) => {
             // Check if this cell WAS selected but is NO LONGER selected
             const wasSelected = data.el.classList.contains('selected');
             const isNowSelected = this.selectedPath.includes(id);

             if (wasSelected && !isNowSelected) {
                 data.el.classList.remove('selected');
                 data.el.classList.add('deselected');
                 // Cleanup animation class
                 setTimeout(() => data.el.classList.remove('deselected'), 300);
             } else if (!wasSelected && !isNowSelected) {
                 // Ensure clean state for unvisited cells
                 data.el.classList.remove('selected', 'deselected');
                 data.el.style.transform = '';
                 data.el.style.background = '#313244';
                 data.el.style.color = '#cdd6f4';
             }
        });

        // 2. Apply Selected State
        this.selectedPath.forEach((id) => {
            const data = this.cells.get(id);
            if (data) {
                // Remove deselected if it was there (e.g. rapid re-select)
                data.el.classList.remove('deselected');
                
                // Only add selected if not already there to avoid restarting animation loop if using simple classes
                if (!data.el.classList.contains('selected')) {
                    data.el.classList.add('selected');
                }
                
                currentWord += data.char;
            }
        });
        
        this.onSelectionChange(currentWord);
    }
}
