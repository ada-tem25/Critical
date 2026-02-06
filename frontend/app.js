// State
let mediaRecorder = null;
let socket = null;
let isRecording = false;

// DOM Elements
const micButton = document.getElementById('mic-button');
const statusEl = document.getElementById('status');
const transcriptionEl = document.getElementById('transcription');

// Transcription state
let finalTranscript = '';
let interimTranscript = '';

// Microphone button
micButton.addEventListener('click', async () => {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
});

async function startRecording() {
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
            }
        });

        // Connect WebSocket
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/transcribe`);

        socket.onopen = () => {
            console.log('WebSocket connecté');
            updateStatus('Connecté', 'connected');

            // Start MediaRecorder once WebSocket is connected
            // Use webm/opus which browsers support well
            mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
                    socket.send(event.data);
                }
            };

            // Send audio chunks every 250ms
            mediaRecorder.start(250);

            isRecording = true;
            micButton.classList.add('recording');
            micButton.querySelector('.mic-text').textContent = 'Appuyer pour arrêter';
            updateStatus('Enregistrement en cours...', 'recording');

            // Clear previous transcript
            finalTranscript = '';
            interimTranscript = '';
            updateTranscriptionDisplay();
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.error) {
                console.error('Erreur:', data.error);
                updateStatus(`Erreur: ${data.error}`, 'error');
                return;
            }

            // Handle status messages (language detection)
            if (data.status === 'detecting_language') {
                updateStatus('Détection de la langue...', 'detecting');
                return;
            }

            if (data.status === 'language_detected') {
                const langNames = {
                    'fr': 'Français',
                    'en': 'English',
                    'es': 'Español',
                    'de': 'Deutsch',
                    'it': 'Italiano',
                    'pt': 'Português',
                    'nl': 'Nederlands',
                    'ja': '日本語',
                    'zh': '中文',
                    'ko': '한국어',
                };
                const langName = langNames[data.language] || data.language;
                updateStatus(`Langue: ${langName} - Transcription en cours...`, 'recording');
                return;
            }

            if (data.status === 'timeout') {
                updateStatus(data.message || 'Arrêt pour inactivité', 'error');
                // Ne pas envoyer end_of_stream car le backend a initié la fermeture
                stopRecording(false);
                return;
            }

            if (data.status === 'stream_complete') {
                console.log('Stream complet, fermeture du socket');
                if (socket && socket.readyState === WebSocket.OPEN) {
                    socket.close();
                }
                updateStatus('Prêt', '');
                return;
            }

            if (data.transcript) {
                if (data.is_final) {
                    finalTranscript += data.transcript + ' ';
                    interimTranscript = '';
                } else {
                    interimTranscript = data.transcript;
                }
                updateTranscriptionDisplay();

                // Show confidence warning if low
                if (data.confidence && data.confidence < 0.8 && data.is_final) {
                    console.log(`Confiance faible: ${data.confidence.toFixed(2)}`);
                }
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateStatus('Erreur de connexion', 'error');
            stopRecording();
        };

        socket.onclose = () => {
            console.log('WebSocket fermé');
            if (isRecording) {
                stopRecording();
            }
        };

    } catch (error) {
        console.error('Erreur accès microphone:', error);
        updateStatus('Erreur: accès microphone refusé', 'error');
    }
}

function stopRecording(sendEndOfStream = true) {
    if (!isRecording) return;
    isRecording = false;

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }

    micButton.classList.remove('recording');
    micButton.querySelector('.mic-text').textContent = 'Appuyer pour parler';

    // Signaler la fin du stream au backend (sauf si le backend a déjà initié la fermeture)
    if (sendEndOfStream && socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'end_of_stream' }));
        updateStatus('Finalisation de la transcription...', 'detecting');

        // Timeout de sécurité : fermer après 3s si pas de réponse
        setTimeout(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                console.log('Timeout: fermeture du socket');
                socket.close();
                updateStatus('Prêt', '');
            }
        }, 3000);
    } else if (socket && socket.readyState === WebSocket.OPEN) {
        // Backend a initié la fermeture, on ferme proprement le socket
        socket.close();
    }

    // Move any remaining interim to final
    if (interimTranscript) {
        finalTranscript += interimTranscript;
        interimTranscript = '';
        updateTranscriptionDisplay();
    }
}

function updateStatus(text, className) {
    statusEl.textContent = text;
    statusEl.className = 'status';
    if (className) {
        statusEl.classList.add(className);
    }
}

function updateTranscriptionDisplay() {
    if (!finalTranscript && !interimTranscript) {
        transcriptionEl.innerHTML = '<span class="placeholder">La transcription apparaîtra ici...</span>';
        return;
    }

    let html = '';
    if (finalTranscript) {
        html += `<span class="final">${finalTranscript}</span>`;
    }
    if (interimTranscript) {
        html += `<span class="interim">${interimTranscript}</span>`;
    }
    transcriptionEl.innerHTML = html;
}
