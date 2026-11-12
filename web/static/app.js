// 808 VAULT // WEB AUDIO ENGINE & DAW MIXER

let audioCtx = null;
let isPlaying = false;
let currentMode = "master"; // 'raw' or 'master'
let playbackStartTime = 0;
let playbackOffset = 0;
let trackDuration = 90; // 90 seconds demo loop
let currentBpm = 140.0;
let animFrameId = null;

// Audio Nodes
let masterGain = null;
let rawFilter = null;
let masteredCompressor = null;
let masterOutput = null;
let oscillatorInterval = null;

// Channel States
const channels = [
  { name: "808 Sub", fader: 0.85, pan: 0, mute: false, solo: false, freq: 55 },
  { name: "Kick", fader: 0.88, pan: 0, mute: false, solo: false, freq: 65 },
  { name: "Snare", fader: 0.78, pan: -0.1, mute: false, solo: false, freq: 220 },
  { name: "Hi-Hats", fader: 0.72, pan: 0.24, mute: false, solo: false, freq: 8000 },
  { name: "Synth", fader: 0.82, pan: -0.3, mute: false, solo: false, freq: 440 },
  { name: "Master", fader: 0.90, pan: 0, mute: false, solo: false, freq: 1000 }
];

// Waveform sample points
let waveformPoints = [15, 30, 65, 80, 95, 60, 45, 85, 100, 80, 40, 70, 90, 75, 55, 85, 65, 35, 95, 80, 50, 70, 85, 60, 40, 90, 75, 45, 65, 85, 95, 70, 50, 80, 100, 85, 45, 75, 60, 30];

document.addEventListener("DOMContentLoaded", () => {
  initUI();
  drawWaveform();
  fetchTracks();
  fetchLicenses();
  setupEventListeners();
  startVUMeterSimulation();
});

function initAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    audioCtx = new AudioContextClass();

    masterGain = audioCtx.createGain();
    masterGain.gain.value = 0.8;

    // Raw mode: low-pass / flat unmastered EQ
    rawFilter = audioCtx.createBiquadFilter();
    rawFilter.type = "lowshelf";
    rawFilter.frequency.value = 400;
    rawFilter.gain.value = -3.0;

    // Mastered mode: Dynamics compressor + high gloss saturation
    masteredCompressor = audioCtx.createDynamicsCompressor();
    masteredCompressor.threshold.setValueAtTime(-18, audioCtx.currentTime);
    masteredCompressor.knee.setValueAtTime(30, audioCtx.currentTime);
    masteredCompressor.ratio.setValueAtTime(4, audioCtx.currentTime);
    masteredCompressor.attack.setValueAtTime(0.003, audioCtx.currentTime);
    masteredCompressor.release.setValueAtTime(0.15, audioCtx.currentTime);

    masterOutput = audioCtx.createGain();
    masterOutput.gain.value = 1.2;

    masterGain.connect(masteredCompressor);
    masteredCompressor.connect(masterOutput);
    masterOutput.connect(audioCtx.destination);
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume();
  }
}

function initUI() {
  const dateInput = document.getElementById("bk-date");
  if (dateInput) {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    dateInput.value = tomorrow.toISOString().split("T")[0];
  }
}

function setupEventListeners() {
  const btnPlay = document.getElementById("btn-play");
  const btnStop = document.getElementById("btn-stop");
  const btnRaw = document.getElementById("btn-mode-raw");
  const btnMaster = document.getElementById("btn-mode-master");

  btnPlay.addEventListener("click", () => {
    initAudioContext();
    startPlayback();
  });

  btnStop.addEventListener("click", () => {
    stopPlayback();
  });

  // Gapless A/B mode toggle
  btnRaw.addEventListener("click", () => {
    switchMonitoringMode("raw");
  });

  btnMaster.addEventListener("click", () => {
    switchMonitoringMode("master");
  });

  // Canvas waveform click for scrubbing
  const canvas = document.getElementById("waveform-canvas");
  canvas.addEventListener("click", (e) => {
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const ratio = clickX / rect.width;
    playbackOffset = ratio * trackDuration;
    if (isPlaying) {
      playbackStartTime = audioCtx.currentTime - playbackOffset;
    }
    updatePlayhead(ratio * 100);
  });

  // Mixer Faders & Mute/Solo
  const strips = document.querySelectorAll(".channel-strip");
  strips.forEach((strip) => {
    const chIndex = parseInt(strip.getAttribute("data-channel"), 10);
    const fader = strip.querySelector(".fader");
    const knob = strip.querySelector(".knob-pan");
    const knobVal = strip.querySelector(".knob-val");
    const btnM = strip.querySelector(".btn-mute");
    const btnS = strip.querySelector(".btn-solo");

    if (fader) {
      fader.addEventListener("input", (e) => {
        channels[chIndex].fader = parseFloat(e.target.value) / 100;
      });
    }

    if (knob && knobVal) {
      knob.addEventListener("input", (e) => {
        const val = parseInt(e.target.value, 10);
        channels[chIndex].pan = val / 50;
        if (val === 0) knobVal.textContent = "C";
        else if (val < 0) knobVal.textContent = Math.abs(val) + "L";
        else knobVal.textContent = val + "R";
      });
    }

    if (btnM) {
      btnM.addEventListener("click", () => {
        channels[chIndex].mute = !channels[chIndex].mute;
        btnM.classList.toggle("active", channels[chIndex].mute);
      });
    }

    if (btnS) {
      btnS.addEventListener("click", () => {
        channels[chIndex].solo = !channels[chIndex].solo;
        btnS.classList.toggle("active", channels[chIndex].solo);
      });
    }
  });

  // Studio booking form
  const bookingForm = document.getElementById("booking-form");
  if (bookingForm) {
    bookingForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        client_name: document.getElementById("bk-name").value,
        client_contact: document.getElementById("bk-contact").value,
        studio_room: document.getElementById("bk-room").value,
        booking_date: document.getElementById("bk-date").value,
        booking_time: document.getElementById("bk-time").value,
        notes: document.getElementById("bk-notes").value
      };

      try {
        const res = await fetch("/api/book-session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        const alertEl = document.getElementById("booking-alert");
        alertEl.textContent = data.message || "Студийная сессия подтверждена!";
        alertEl.className = "booking-alert success";
        bookingForm.reset();
      } catch (err) {
        console.error("Booking failed:", err);
      }
    });
  }

  // Modal close
  document.getElementById("modal-close-btn").addEventListener("click", closeModal);
  document.getElementById("order-modal").addEventListener("click", (e) => {
    if (e.target.id === "order-modal") closeModal();
  });

  // License Order Form
  const orderForm = document.getElementById("license-order-form");
  if (orderForm) {
    orderForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const payload = {
        client_name: document.getElementById("ord-name").value,
        client_contact: document.getElementById("ord-contact").value,
        track_id: document.getElementById("order-track-id").value,
        license_type: document.getElementById("order-license-type").value,
        artist_pseudonym: document.getElementById("ord-pseudonym").value
      };

      try {
        const res = await fetch("/api/order-license", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        const alertEl = document.getElementById("order-alert");
        alertEl.textContent = data.message || "Заказ успешно создан!";
        alertEl.className = "booking-alert success";
        setTimeout(() => closeModal(), 2200);
      } catch (err) {
        console.error("Order failed:", err);
      }
    });
  }
}

// Gapless Switch
function switchMonitoringMode(mode) {
  currentMode = mode;
  document.getElementById("btn-mode-raw").classList.toggle("active", mode === "raw");
  document.getElementById("btn-mode-master").classList.toggle("active", mode === "master");

  const badge = document.getElementById("active-mode-badge");
  if (mode === "raw") {
    badge.textContent = "MODE: RAW UNMIXED DEMO (-3dB)";
    badge.style.color = "#FF6B00";
    if (audioCtx && masterGain) {
      masterGain.disconnect();
      masterGain.connect(rawFilter);
      rawFilter.disconnect();
      rawFilter.connect(masterOutput);
    }
  } else {
    badge.textContent = "MODE: MASTERED HIGH-GLOSS (+4dB)";
    badge.style.color = "#22C55E";
    if (audioCtx && masterGain) {
      masterGain.disconnect();
      masterGain.connect(masteredCompressor);
    }
  }
}

// Playback Logic
function startPlayback() {
  if (isPlaying) return;
  isPlaying = true;
  document.getElementById("btn-play").classList.add("active");
  playbackStartTime = audioCtx.currentTime - playbackOffset;

  // Synthesize rhythmic beat pulse to audio context
  startSynthesizerGroove();

  // Start transport timecode updater
  updateTransportLoop();
}

function stopPlayback() {
  isPlaying = false;
  document.getElementById("btn-play").classList.remove("active");
  if (oscillatorInterval) {
    clearInterval(oscillatorInterval);
    oscillatorInterval = null;
  }
  if (animFrameId) {
    cancelAnimationFrame(animFrameId);
    animFrameId = null;
  }
}

function startSynthesizerGroove() {
  if (oscillatorInterval) clearInterval(oscillatorInterval);

  // Play an 808 sub kick and hi-hat beat pulse
  const stepTime = (60 / currentBpm) / 2 * 1000;
  let step = 0;

  oscillatorInterval = setInterval(() => {
    if (!isPlaying || !audioCtx) return;

    const time = audioCtx.currentTime;

    // Kick / 808 on steps 0, 4, 6
    if (step % 8 === 0 || step % 8 === 6) {
      if (!channels[0].mute && channels[0].fader > 0.05) {
        triggerSub808(time, 50 * (currentMode === "master" ? 1.1 : 0.9));
      }
    }

    // Snare on steps 4, 12
    if (step % 8 === 4) {
      if (!channels[2].mute && channels[2].fader > 0.05) {
        triggerSnare(time);
      }
    }

    // Hi-hats on all even steps
    if (step % 2 === 0) {
      if (!channels[3].mute && channels[3].fader > 0.05) {
        triggerHat(time);
      }
    }

    step = (step + 1) % 16;
  }, stepTime);
}

function triggerSub808(time, freq) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = "sine";
  osc.frequency.setValueAtTime(freq, time);
  osc.frequency.exponentialRampToValueAtTime(30, time + 0.35);

  const vol = channels[0].fader * (currentMode === "master" ? 0.9 : 0.5);
  gain.gain.setValueAtTime(vol, time);
  gain.gain.exponentialRampToValueAtTime(0.001, time + 0.4);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(time);
  osc.stop(time + 0.45);
}

function triggerSnare(time) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = "triangle";
  osc.frequency.setValueAtTime(180, time);

  const vol = channels[2].fader * (currentMode === "master" ? 0.5 : 0.3);
  gain.gain.setValueAtTime(vol, time);
  gain.gain.exponentialRampToValueAtTime(0.001, time + 0.18);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(time);
  osc.stop(time + 0.2);
}

function triggerHat(time) {
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.type = "sawtooth";
  osc.frequency.setValueAtTime(7000, time);

  const vol = channels[3].fader * (currentMode === "master" ? 0.25 : 0.15);
  gain.gain.setValueAtTime(vol, time);
  gain.gain.exponentialRampToValueAtTime(0.001, time + 0.06);

  osc.connect(gain);
  gain.connect(masterGain);
  osc.start(time);
  osc.stop(time + 0.07);
}

function updateTransportLoop() {
  if (!isPlaying) return;

  const currentSec = (audioCtx.currentTime - playbackStartTime) % trackDuration;
  playbackOffset = currentSec;

  // Format timecode MM:SS:MS
  const mins = Math.floor(currentSec / 60);
  const secs = Math.floor(currentSec % 60);
  const ms = Math.floor((currentSec % 1) * 100);

  const formatted = 
    String(mins).padStart(2, "0") + ":" +
    String(secs).padStart(2, "0") + ":" +
    String(ms).padStart(2, "0");

  const timecodeEl = document.getElementById("timecode-val");
  if (timecodeEl) timecodeEl.textContent = formatted;

  const pct = (currentSec / trackDuration) * 100;
  updatePlayhead(pct);

  animFrameId = requestAnimationFrame(updateTransportLoop);
}

function updatePlayhead(pct) {
  const playhead = document.getElementById("playhead");
  if (playhead) {
    playhead.style.left = pct + "%";
  }
}

// Waveform Canvas Rendering
function drawWaveform() {
  const canvas = document.getElementById("waveform-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;

  ctx.fillStyle = "#0B0C0E";
  ctx.fillRect(0, 0, w, h);

  // Center line
  ctx.strokeStyle = "#1A1C23";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(0, h / 2);
  ctx.lineTo(w, h / 2);
  ctx.stroke();

  // Draw audio peaks
  const barCount = 120;
  const barWidth = w / barCount;

  for (let i = 0; i < barCount; i++) {
    const val = waveformPoints[i % waveformPoints.length];
    const barHeight = (val / 100) * (h * 0.85);

    // Gradient styling: cyan to orange
    const grad = ctx.createLinearGradient(0, (h - barHeight) / 2, 0, (h + barHeight) / 2);
    grad.addColorStop(0, "#00E5FF");
    grad.addColorStop(0.5, "#3B82F6");
    grad.addColorStop(1, "#FF6B00");

    ctx.fillStyle = grad;
    ctx.fillRect(i * barWidth + 2, (h - barHeight) / 2, barWidth - 3, barHeight);
  }
}

// LED VU Meters Simulator
function startVUMeterSimulation() {
  setInterval(() => {
    const strips = document.querySelectorAll(".channel-strip");
    strips.forEach((strip) => {
      const chIndex = parseInt(strip.getAttribute("data-channel"), 10);
      const ch = channels[chIndex];
      const leds = strip.querySelectorAll(".vu-led");

      if (!isPlaying || ch.mute) {
        leds.forEach(led => led.classList.remove("lit"));
        return;
      }

      // Calculate dynamic level
      const baseSignal = ch.fader * (currentMode === "master" ? 1.15 : 0.85);
      const jitter = (Math.random() * 0.35);
      const signal = Math.min(1.0, baseSignal * (0.7 + jitter));
      const activeCount = Math.floor(signal * leds.length);

      leds.forEach((led, idx) => {
        // VU meters light from bottom up
        const revIdx = leds.length - 1 - idx;
        if (revIdx < activeCount) {
          led.classList.add("lit");
        } else {
          led.classList.remove("lit");
        }
      });
    });
  }, 80);
}

// Fetch API
async function fetchTracks() {
  try {
    const res = await fetch("/api/tracks");
    const data = await res.json();
    renderTracks(data.tracks || []);
  } catch (err) {
    console.error("Tracks load error:", err);
  }
}

function renderTracks(tracks) {
  const container = document.getElementById("track-list");
  if (!container) return;

  container.innerHTML = tracks.map(t => `
    <div class="track-item">
      <div class="track-meta">
        <h4>${t.title}</h4>
        <div class="track-sub">${t.key} // ${t.bpm} BPM // ${t.tags.join(", ")}</div>
      </div>
      <div class="track-actions">
        <button class="track-load-btn" onclick="selectTrack('${t.id}', '${t.title}', ${t.bpm})">LOAD TO CONSOLE</button>
        <button class="track-load-btn" style="color: #FF6B00;" onclick="openOrderModal('${t.id}', '${t.title}', 'WAV Lease', ${t.price_lease})">${t.price_lease} ₽</button>
      </div>
    </div>
  `).join("");
}

window.selectTrack = function(id, title, bpm) {
  document.getElementById("current-track-title").textContent = title + " // " + bpm + " BPM";
  document.getElementById("bpm-val").textContent = bpm.toFixed(1);
  currentBpm = bpm;
  playbackOffset = 0;
  if (isPlaying) {
    playbackStartTime = audioCtx.currentTime;
    startSynthesizerGroove();
  }
};

async function fetchLicenses() {
  try {
    const res = await fetch("/api/licenses");
    const data = await res.json();
    renderLicenses(data.licenses || []);
  } catch (err) {
    console.error("Licenses load error:", err);
  }
}

function renderLicenses(licenses) {
  const container = document.getElementById("license-grid");
  if (!container) return;

  container.innerHTML = licenses.map(l => `
    <div class="license-card">
      <div class="lic-name">${l.type}</div>
      <div class="lic-price">${l.price.toLocaleString("ru-RU")} ₽</div>
      <div class="lic-features">
        • ${l.format}<br>
        • ${l.distribution_limit}<br>
        • ${l.commercial_use ? "Commercial Rights: YES" : "Non-commercial only"}<br>
        • Stems: ${l.stems_included ? "INCLUDED" : "Stereo Only"}
      </div>
      <button class="lic-buy-btn" onclick="openOrderModal('trk-01', 'Sub Zero 808', '${l.type}', ${l.price})">SELECT LICENSE ➔</button>
    </div>
  `).join("");
}

// Modal handling
window.openOrderModal = function(trackId, trackTitle, licenseType, price) {
  document.getElementById("order-track-id").value = trackId;
  document.getElementById("order-license-type").value = licenseType;
  document.getElementById("modal-license-title").textContent = "BUY: " + licenseType.toUpperCase();
  document.getElementById("modal-summary-text").textContent = `Selected Track: "${trackTitle}" (${licenseType})`;
  document.getElementById("order-total-price").textContent = price.toLocaleString("ru-RU") + " ₽";
  document.getElementById("order-alert").classList.add("hidden");
  document.getElementById("order-modal").classList.remove("hidden");
};

function closeModal() {
  document.getElementById("order-modal").classList.add("hidden");
}
