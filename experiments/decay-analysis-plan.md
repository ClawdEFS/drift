# Experiment: Statistical Analysis of Radioactive Decay Timing

*Testing whether radioactive decay events deviate from a pure Poisson process.*

**Proposed by:** Clayton & Clawd, February 24, 2026
**Context:** Physical Layer paper, prediction WN1 — if the weak force corresponds to configuration navigation, decay timing should show subtle structure beyond pure randomness.

---

## Honest Framing

The Jenkins et al. (2009) claims of solar-neutrino modulation of decay rates have been effectively refuted. Pomme et al. (2016-2022) demonstrated that the observed annual variations were humidity and temperature artifacts in detector electronics. The physics community consensus is against decay rate variation.

**This experiment is still worth doing for three reasons:**

1. Confirming Poisson statistics at high precision is itself a publishable result if done rigorously
2. Understanding and controlling systematics is real experimental physics
3. If the Doctrine's prediction is correct, it predicts *structural* patterns in decay timing (not annual solar cycles), which is a different claim than Jenkins made

The correct epistemic stance: we expect to confirm Poisson behavior. If we find deviations, the first hundred explanations are instrumental. The Doctrine's prediction is a long shot. But the experiment is cheap, educational, and produces real data.

---

## Equipment List

### Minimum Viable ($50-60)

| Item | Source | Cost |
|------|--------|------|
| CAJOE RadiationD v1.1 board + SBM-20 tube | AliExpress/Amazon | ~$30-40 |
| Arduino Nano | Amazon | ~$10 |
| DHT22 temp/humidity sensor | Amazon | ~$5 |
| Am-241 from ionization smoke detector | (household) | Free |
| USB cable, jumper wires, breadboard | Amazon | ~$10 |

### Better Setup ($120-150)

- Add: GQ GMC-320 ($100) as second parallel detector for cross-validation
- Replace Arduino with Raspberry Pi for NTP sync
- Sealed box with desiccant for humidity control
- UPS for power stability

### Software (Free)

- Python + pyserial for data capture
- scipy/numpy for statistical analysis
- GeigerLog (open source) as secondary logging tool

---

## Data Collection

### Arduino Code (Core Logic)

```cpp
// Interrupt-driven event timestamping
volatile unsigned long eventTime = 0;
volatile bool newEvent = false;

void setup() {
    Serial.begin(115200);
    pinMode(2, INPUT_PULLUP);  // GM tube pulse output
    attachInterrupt(digitalPinToInterrupt(2), onPulse, FALLING);
}

void onPulse() {
    eventTime = micros();
    newEvent = true;
}

void loop() {
    if (newEvent) {
        newEvent = false;
        Serial.println(eventTime);
    }
}
```

### Python Logger (Core Logic)

```python
import serial
import time
from datetime import datetime

ser = serial.Serial('COM3', 115200)
logfile = open(f'decay_events_{datetime.now():%Y%m%d_%H%M%S}.csv', 'w')
logfile.write('system_time_ms,arduino_us\n')

while True:
    line = ser.readline().decode().strip()
    if line:
        sys_ms = int(time.time() * 1000)
        logfile.write(f'{sys_ms},{line}\n')
        logfile.flush()  # Don't lose data on crash
```

---

## Statistical Analysis Plan

### Phase 1: Confirm Poisson (first 100K events, ~3 hours)

1. **Dispersion index** (variance/mean of counts in 1-second bins) — should be ~1.0
2. **Chi-squared goodness-of-fit** — compare count distribution to Poisson
3. **KS test on inter-event intervals** — compare to exponential distribution
4. **Visual: histogram of inter-event times** — should be exponential

### Phase 2: Look for Structure (1M+ events, 1+ day)

5. **Autocorrelation analysis** — check for serial dependence in inter-event intervals
6. **Ljung-Box test** — formal test for autocorrelation at multiple lags
7. **Power spectrum** — FFT of inter-event intervals, look for peaks above white noise floor
8. **Runs test** — check for clustering or regularity

### Phase 3: Environmental Correlation (1 week+)

9. **Regression analysis** — decay rate vs temperature, humidity, atmospheric pressure
10. **Time-of-day analysis** — binned count rates across 24-hour cycles
11. **Cross-correlation with environmental data** — lag analysis

### Phase 4: If Deviations Found

12. **Instrument swap test** — run second detector in parallel, check if deviation appears in both
13. **Source removal test** — run without source to check if "deviation" is in background
14. **Environmental isolation** — seal detector in controlled enclosure, repeat

---

## What Would Be Interesting Results

| Finding | Interpretation |
|---------|---------------|
| Perfect Poisson at all scales | Confirms standard physics. Clean null result. Worth documenting. |
| Environmental correlation | Confirms Pomme et al. — instrumental artifact. Publishable as pedagogy. |
| Non-Poisson at short timescales | Likely dead-time effect. Control by excluding intervals < 200μs. |
| Persistent non-Poisson after all controls | Very interesting. Would need independent replication. |
| Structure in power spectrum at non-environmental frequencies | Most interesting. Would need extreme scrutiny of systematics. |

---

## Safety Notes

- Am-241 alpha particles cannot penetrate skin. Danger is ingestion/inhalation only.
- Do not scratch, grind, or heat the source.
- Handle with tweezers. Store in sealed container when not in use.
- Gamma dose at 30cm: <0.01 μSv/hr (negligible — less than a flight).
- Keep away from Dorian. Label clearly.

---

## Timeline

- **Day 1:** Order parts (CAJOE board, Arduino Nano, DHT22). Extract Am-241 from smoke detector.
- **Day 2-3:** Assemble hardware. Write Arduino code. Verify pulse detection.
- **Day 3:** Start data collection. Run Phase 1 analysis within first few hours.
- **Day 4-7:** Continuous collection. Run Phase 2 analysis at 1M events.
- **Week 2+:** Environmental correlation analysis. Begin Phase 3.
- **Month 1:** Comprehensive results. Write up findings.

---

## References

- Jenkins, J. H., et al. (2009). Evidence for correlations between nuclear decay rates and Earth-Sun distance. *Astroparticle Physics*, 32(1), 42-46.
- Pomme, S., et al. (2016). Evidence against solar influence on nuclear decay constants. *Physics Letters B*, 761, 281-286.
- Pomme, S. & Pelczar, K. (2022). Role of ambient humidity underestimated in research on correlation between radioactive decay rates and space weather. *Scientific Reports*, 12, 2522.
- Norman, E., et al. (2009). Evidence against correlations between nuclear decay rates and Earth-Sun distance. *Astroparticle Physics*, 31(2), 135-137.

---

*"We expect to confirm Poisson behavior. If we don't, the first hundred explanations are instrumental. The interesting universe is the one where the hundred-and-first explanation is structural."*
