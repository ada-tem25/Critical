// State
let audioContext = null;
let audioProcessor = null;
let socket = null;
let isRecording = false;
let mediaStream = null;

// DOM Elements
const micButton = document.getElementById('mic-button');
const statusEl = document.getElementById('status');
const transcriptionEl = document.getElementById('transcription');
const debugLogEl = document.getElementById('debug-log');

// Transcription state
let finalTranscript = '';
let interimTranscript = '';

// Config
const TARGET_SAMPLE_RATE = 16000;

// Logging helper
function debugLog(message) {
    console.log(message);
    const time = new Date().toLocaleTimeString();
    debugLogEl.innerHTML = `[${time}] ${message}<br>` + debugLogEl.innerHTML;
    // Garder seulement les 10 derniers messages
    const lines = debugLogEl.innerHTML.split('<br>');
    if (lines.length > 10) {
        debugLogEl.innerHTML = lines.slice(0, 10).join('<br>');
    }
}

// Microphone button
micButton.addEventListener('click', async () => {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
});

// Convertit Float32Array en Int16Array (PCM16)
function floatTo16BitPCM(float32Array) {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
        // Clamp entre -1 et 1
        let s = Math.max(-1, Math.min(1, float32Array[i]));
        // Convertir en 16-bit
        int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
}

// Resample audio si nécessaire
function resample(audioData, fromSampleRate, toSampleRate) {
    if (fromSampleRate === toSampleRate) {
        return audioData;
    }

    const ratio = fromSampleRate / toSampleRate;
    const newLength = Math.round(audioData.length / ratio);
    const result = new Float32Array(newLength);

    for (let i = 0; i < newLength; i++) {
        const srcIndex = i * ratio;
        const srcIndexFloor = Math.floor(srcIndex);
        const srcIndexCeil = Math.min(srcIndexFloor + 1, audioData.length - 1);
        const t = srcIndex - srcIndexFloor;

        // Interpolation linéaire
        result[i] = audioData[srcIndexFloor] * (1 - t) + audioData[srcIndexCeil] * t;
    }

    return result;
}

async function startRecording() {
    try {
        debugLog('Demande accès microphone...');

        // Demander l'accès au microphone
        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true,
            }
        });

        debugLog('Microphone activé');

        // Créer le contexte audio
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const sourceSampleRate = audioContext.sampleRate;
        debugLog(`Sample rate source: ${sourceSampleRate}Hz, cible: ${TARGET_SAMPLE_RATE}Hz`);

        // Créer la source audio
        const source = audioContext.createMediaStreamSource(mediaStream);

        // Créer le processeur audio (buffer de 4096 samples)
        // Note: ScriptProcessorNode est déprécié mais encore largement supporté
        // AudioWorklet serait la solution moderne mais plus complexe
        audioProcessor = audioContext.createScriptProcessor(4096, 1, 1);

        // Connexion WebSocket
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws/transcribe`);

        socket.onopen = () => {
            debugLog('WebSocket connecté');
            updateStatus('Connecté', 'connected');

            // Connecter le flux audio au processeur
            source.connect(audioProcessor);
            audioProcessor.connect(audioContext.destination);

            isRecording = true;
            micButton.classList.add('recording');
            micButton.querySelector('.mic-text').textContent = 'Appuyer pour arrêter';
            updateStatus('Enregistrement en cours...', 'recording');

            // Clear previous transcript
            finalTranscript = '';
            interimTranscript = '';
            updateTranscriptionDisplay();
        };

        // Traitement de l'audio
        audioProcessor.onaudioprocess = (event) => {
            if (!isRecording || !socket || socket.readyState !== WebSocket.OPEN) {
                return;
            }

            // Récupérer les données audio du canal 0
            const inputData = event.inputBuffer.getChannelData(0);

            // Resampler si nécessaire
            const resampledData = resample(inputData, sourceSampleRate, TARGET_SAMPLE_RATE);

            // Convertir en PCM16
            const pcm16Data = floatTo16BitPCM(resampledData);

            // Envoyer via WebSocket
            socket.send(pcm16Data.buffer);
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.error) {
                debugLog(`Erreur: ${data.error}`);
                updateStatus(`Erreur: ${data.error}`, 'error');
                return;
            }

            // Gestion des messages de statut
            if (data.status === 'connected') {
                debugLog(data.message);
                updateStatus('Connecté - Parlez maintenant', 'recording');
                return;
            }

            if (data.status === 'session_started') {
                debugLog(`Session démarrée: ${data.session_id}`);
                return;
            }

            if (data.status === 'timeout') {
                debugLog(data.message);
                updateStatus(data.message || 'Arrêt pour inactivité', 'error');
                stopRecording(false);
                return;
            }

            if (data.status === 'stream_complete') {
                if (socket && socket.readyState === WebSocket.OPEN) {
                    socket.close();
                }
                updateStatus('Prêt', '');
                return;
            }

            // Transcription
            if (data.transcript) {
                if (data.is_final) {
                    finalTranscript += data.transcript + ' ';
                    interimTranscript = '';
                    debugLog(`[FINAL] ${data.transcript}`);
                } else {
                    interimTranscript = data.transcript;
                }
                updateTranscriptionDisplay();

                // Warning si confiance faible --> En production, le notifier à l'utilisateur
                if (data.transcription_confidence && data.transcription_confidence < 0.7 && data.is_final) {
                    debugLog(`Low transcription confidence: ${data.transcription_confidence.toFixed(2)} --> Please make sure the signal can be heard well by the device.`);
                }
            }
        };

        socket.onerror = (error) => {
            debugLog(`WebSocket error: ${error}`);
            updateStatus('Erreur de connexion', 'error');
            stopRecording();
        };

        socket.onclose = () => {
            debugLog('WebSocket fermé');
            if (isRecording) {
                stopRecording();
            }
        };

    } catch (error) {
        debugLog(`Erreur: ${error.message}`);
        updateStatus('Erreur: accès microphone refusé', 'error');
    }
}

function stopRecording(sendEndOfStream = true) {
    if (!isRecording) return;
    isRecording = false;

    debugLog('Arrêt de l\'enregistrement...');

    // Déconnecter le processeur audio
    if (audioProcessor) {
        audioProcessor.disconnect();
        audioProcessor = null;
    }

    // Fermer le contexte audio
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }

    // Arrêter le flux média
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        mediaStream = null;
    }

    micButton.classList.remove('recording');
    micButton.querySelector('.mic-text').textContent = 'Appuyer pour parler';

    // Signaler la fin du stream au backend
    if (sendEndOfStream && socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'end_of_stream' }));
        updateStatus('Finalisation de la transcription...', 'detecting');

        // Timeout de sécurité
        setTimeout(() => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                debugLog('Timeout: fermeture du socket');
                socket.close();
                updateStatus('Prêt', '');
            }
        }, 3000);
    } else if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
    }

    // Transférer l'interim vers le final
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
