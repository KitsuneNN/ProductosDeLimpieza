// Aviso sonoro característico del admin (requisito 19.3) — F-T3
// Sintetizado con Web Audio (sin archivos externos).
let contexto: AudioContext | null = null;

export function desbloquearAudio(): void {
  try {
    if (typeof window === "undefined") return;
    if (!contexto) contexto = new AudioContext();
    if (contexto.state === "suspended") void contexto.resume();
  } catch {
    // Audio no disponible en este navegador
  }
}

export function tocarAviso(): void {
  try {
    if (typeof window === "undefined") return;
    if (!contexto) contexto = new AudioContext();
    if (contexto.state === "suspended") void contexto.resume();
    const notas = [880, 1174.66, 1567.98]; // la5, re6, sol6
    notas.forEach((frecuencia, i) => {
      const oscilador = contexto!.createOscillator();
      const ganancia = contexto!.createGain();
      const inicio = contexto!.currentTime + i * 0.16;
      oscilador.type = "sine";
      oscilador.frequency.value = frecuencia;
      ganancia.gain.setValueAtTime(0.0001, inicio);
      ganancia.gain.exponentialRampToValueAtTime(0.35, inicio + 0.02);
      ganancia.gain.exponentialRampToValueAtTime(0.0001, inicio + 0.16);
      oscilador.connect(ganancia);
      ganancia.connect(contexto!.destination);
      oscilador.start(inicio);
      oscilador.stop(inicio + 0.18);
    });
  } catch {
    // sin audio
  }
}
