export class AudioController {
    private ctx: AudioContext | null = null;
    private osc: OscillatorNode | null = null;
    private gain: GainNode | null = null;
    private isMuted: boolean = false;

    constructor() {
        // Initialize AudioContext on first user interaction to bypass autoplay policy
        const initAudio = () => {
            if (!this.ctx) {
                this.ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
            }
            window.removeEventListener('pointerdown', initAudio);
            window.removeEventListener('keydown', initAudio);
        };
        window.addEventListener('pointerdown', initAudio);
        window.addEventListener('keydown', initAudio);
    }

    // Pre-defined harmonious chords/scales to choose from
    // We use compact chords (within 1 octave) so the next octave jump is always higher
    private chordScales = [
        [261.63, 329.63, 392.00, 493.88], // C Major 7 (C, E, G, B)
        [220.00, 261.63, 329.63, 392.00], // A Minor 7 (A, C, E, G)
        [293.66, 349.23, 440.00, 523.25], // D Minor 7 (D, F, A, C)
        [349.23, 440.00, 523.25, 659.25], // F Major 7 (F, A, C, E)
        [392.00, 493.88, 587.33, 698.46], // G Major 7 (G, B, D, F#)
    ];
    
    private currentScale: number[] = [];
    private currentNotes: number[] = [];

    playClick(stepIndex: number) {
        if (this.isMuted || !this.ctx) return;
        
        // Reset if starting new word (index 1)
        if (stepIndex === 1) {
            this.currentNotes = [];
            // Pick a random chord scale for this word
            this.currentScale = this.chordScales[Math.floor(Math.random() * this.chordScales.length)];
        }
        // Fallback if somehow empty
        if (this.currentScale.length === 0) this.currentScale = this.chordScales[0];

        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        // Select note from current scale, shifting up octaves if we exceed the scale length
        const len = this.currentScale.length;
        const noteIndex = (stepIndex - 1) % len;
        const octave = Math.floor((stepIndex - 1) / len);
        
        // Frequency doubles every octave
        const baseFreq = this.currentScale[noteIndex];
        const freq = baseFreq * Math.pow(2, octave);
        
        // Store for the final chord
        this.currentNotes.push(freq);

        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        osc.type = 'sine';
        
        // Short pluck
        gain.gain.setValueAtTime(0, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.2, this.ctx.currentTime + 0.01);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.2);

        osc.start(this.ctx.currentTime);
        osc.stop(this.ctx.currentTime + 0.2);
    }

    playSubmitSuccess() {
        if (this.isMuted || !this.ctx || this.currentNotes.length === 0) return;
        
        const now = this.ctx.currentTime;

        // Replay all accumulated notes simultaneously as a chord
        this.currentNotes.forEach((freq) => {
            const osc = this.ctx!.createOscillator();
            const gain = this.ctx!.createGain();
            
            osc.connect(gain);
            gain.connect(this.ctx!.destination);
            
            osc.type = 'sine';
            osc.frequency.value = freq;
            
            // Play simultaneously
            gain.gain.setValueAtTime(0, now);
            gain.gain.linearRampToValueAtTime(0.15 / this.currentNotes.length, now + 0.05); // Normalize volume
            gain.gain.exponentialRampToValueAtTime(0.001, now + 1.5);
            
            osc.start(now);
            osc.stop(now + 1.5);
        });
        
        // Clear for next time
        this.currentNotes = [];
    }
}
