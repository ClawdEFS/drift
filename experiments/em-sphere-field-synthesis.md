# EM-Plasma Sphere Test 1: Multipole Field Synthesis

*Clawd — February 25, 2026*
*Experimental plan for validating the EM-Plasma Sphere's foundational claim*

---

## Objective

Demonstrate that independently addressable electromagnetic nodes arranged on a geodesic sphere can synthesize controllable multipole magnetic fields, and that these field configurations can be switched in real-time.

This tests the foundational engineering claim of Clayton's EM-Plasma Sphere design (v1.0, Feb 25 2026): that a 120-node geodesic array can produce arbitrary field geometries through independent current control. We test at reduced scale (12 nodes) to validate the principle before scaling.

**This test requires no vacuum, no plasma, and no exotic parts.** It is pure electromagnetics — Maxwell's equations in a living room.

---

## What We're Testing

The EM-Plasma Sphere spec states: "120 independently addressable electromagnetic nodes arranged in geodesic polyhedron configuration" with "real-time spherical harmonic field synthesis" and "multipole reconfiguration time < 5 milliseconds."

At 12 nodes (icosahedron vertices), we can synthesize:
- **Dipole** (l=1): uniform field direction — all nodes same polarity
- **Quadrupole** (l=2): opposing hemispheres reversed
- **Sextupole** (l=3): alternating bands
- **Asymmetric configurations**: arbitrary current patterns for directional field shaping

**Success criteria:**
1. Measured field topology matches theoretical predictions for each configuration
2. Configurations switch cleanly in real-time (< 100ms at this scale)
3. Asymmetric patterns produce measurable directional bias in the field

---

## Equipment

### Structure

**Geodesic sphere frame — 15cm diameter**

Option A: 3D print an icosahedral frame with 12 solenoid mounting points at vertices. STL files for icosahedron frames are freely available. Each vertex gets a cylindrical socket for the electromagnet.

Option B: Build from dowel rods or 3D printing pen. An icosahedron has 30 edges — cut 30 equal-length sticks and glue at vertices.

**Estimated cost:** $0-20 (free if 3D printer available)

### Electromagnets (12 units)

**Option A — Commercial lifting magnets:**
- 12V DC, 2.5kg holding force, 20×15mm size
- Available on Amazon/AliExpress for ~$3-5 each
- Consistent specifications, known field strength
- ~$36-60 total

**Option B — DIY wound coils:**
- Ferrite rod cores (10mm × 20mm), salvaged from old radios or ~$1 each
- 28 AWG magnet wire, 100-200 turns per core
- More work but cheaper and customizable
- ~$15-25 total

**Recommended:** Option A for consistency. Option B if budget is tight or if specific coil geometry is needed.

### Driver Electronics

**Arduino Mega 2560** — 15 PWM pins (we need 12)
- ~$15 (clone) or $45 (genuine)

**12× IRLZ44N N-Channel MOSFETs** — logic-level gate (drives directly from Arduino 5V)
- Gate threshold: 1-2V (works with Arduino's 5V PWM)
- Drain current: up to 47A (way more than needed)
- ~$12 for pack of 20

**12× 1N4007 flyback diodes** — protect MOSFETs from back-EMF
- ~$3 for pack of 100

**12× 10kΩ gate pulldown resistors**
- ~$1

**Wiring:**
```
Arduino PWM Pin → MOSFET Gate (with 10kΩ pulldown to GND)
MOSFET Drain → Electromagnet terminal A
Electromagnet terminal B → 12V supply positive
MOSFET Source → GND (common with Arduino GND)
Flyback diode: cathode to 12V, anode to MOSFET drain
```

### Field Measurement

**3-axis magnetometer — QMC5883L or HMC5883L breakout**
- Measures Bx, By, Bz simultaneously
- I2C interface (2 wires to Arduino)
- Range: ±800µT (QMC5883L), resolution ~5µT
- ~$5-8

**Sensor boom:** Rigid arm (wooden dowel, aluminum rod, or 3D printed) that holds the magnetometer at a fixed distance (20cm) from sphere center. Marked with angle positions every 30° for consistent measurement.

**Optional upgrade:** Mount sensor on a servo-driven arm for automated scanning. Two servos (azimuth + elevation) would allow full-sphere mapping without manual repositioning. Adds ~$15-20 for two SG90 servos.

### Power

**12V 10A DC power supply**
- Peak draw: 12 coils × ~0.3A each = 3.6A (well within 10A capacity)
- ~$15-25

### Total Budget

| Component | Cost (est.) |
|-----------|-------------|
| 3D printed frame | $0-20 |
| 12 electromagnets | $36-60 |
| Arduino Mega | $15-45 |
| MOSFETs + diodes + resistors | $16 |
| QMC5883L magnetometer | $5-8 |
| 12V 10A power supply | $15-25 |
| Perfboard, wire, connectors | $15-20 |
| **Total** | **$100-195** |

With servos for automated scanning: add $15-20.

---

## Software

### Arduino Control Code

```cpp
// EM-Sphere Multipole Field Synthesis Controller
// 12 nodes on icosahedron vertices, PWM-controlled

#include <Wire.h>

// --- Pin assignments (12 PWM pins on Arduino Mega) ---
const int NODE_PINS[12] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};

// --- Node positions (icosahedron vertices, unit sphere) ---
// Golden ratio coordinates
const float PHI = 1.618033988749895;
const float NODE_POS[12][3] = {
    { 0,  1,  PHI}, { 0, -1,  PHI}, { 0,  1, -PHI}, { 0, -1, -PHI},
    { 1,  PHI,  0}, {-1,  PHI,  0}, { 1, -PHI,  0}, {-1, -PHI,  0},
    { PHI,  0,  1}, {-PHI,  0,  1}, { PHI,  0, -1}, {-PHI,  0, -1}
};

// --- Field configurations ---
// Each config is 12 PWM values (0-255), where 0=off, 255=max current
// Negative values would need H-bridge; for now, 0-255 unipolar

struct FieldConfig {
    const char* name;
    uint8_t node_pwm[12];
};

FieldConfig configs[] = {
    {"uniform_dipole",    {255,255,255,255,255,255, 0,  0,  0,  0,  0,  0}},
    {"strong_dipole",     {255,255,  0,  0,255,255, 0,  0,255,  0,255,  0}},
    {"quadrupole_z",      {255,255,  0,  0,128,128,128,128,  0,  0,  0,  0}},
    {"asymmetric_thrust", {255,255,255, 0,128,128, 0,  0,128, 0,  64, 0}},
    {"all_max",           {255,255,255,255,255,255,255,255,255,255,255,255}},
    {"all_off",           {  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0}},
};
const int NUM_CONFIGS = 6;
int currentConfig = 0;

void setup() {
    Serial.begin(115200);
    Wire.begin();

    for (int i = 0; i < 12; i++) {
        pinMode(NODE_PINS[i], OUTPUT);
        analogWrite(NODE_PINS[i], 0);
    }

    Serial.println("EM-Sphere Controller Ready");
    Serial.println("Commands: n=next config, p=prev, m=measure, s=sweep, 0-5=direct");
}

void applyConfig(int idx) {
    unsigned long start = micros();
    for (int i = 0; i < 12; i++) {
        analogWrite(NODE_PINS[i], configs[idx].node_pwm[i]);
    }
    unsigned long elapsed = micros() - start;

    Serial.print("Config: ");
    Serial.print(configs[idx].name);
    Serial.print(" applied in ");
    Serial.print(elapsed);
    Serial.println(" microseconds");
}

void readMagnetometer(float* bx, float* by, float* bz) {
    // QMC5883L read (address 0x0D)
    Wire.beginTransmission(0x0D);
    Wire.write(0x00); // data register
    Wire.endTransmission();
    Wire.requestFrom(0x0D, 6);

    int16_t x = Wire.read() | (Wire.read() << 8);
    int16_t y = Wire.read() | (Wire.read() << 8);
    int16_t z = Wire.read() | (Wire.read() << 8);

    // QMC5883L: 1 LSB = ~0.0833 µT at default range
    *bx = x * 0.0833;
    *by = y * 0.0833;
    *bz = z * 0.0833;
}

void measureField() {
    float bx, by, bz;
    readMagnetometer(&bx, &by, &bz);

    float magnitude = sqrt(bx*bx + by*by + bz*bz);

    Serial.print("B = (");
    Serial.print(bx, 2); Serial.print(", ");
    Serial.print(by, 2); Serial.print(", ");
    Serial.print(bz, 2); Serial.print(") µT  |B| = ");
    Serial.print(magnitude, 2); Serial.println(" µT");
}

void sweepConfigs() {
    // Cycle through all configs, measuring field at each
    for (int i = 0; i < NUM_CONFIGS; i++) {
        applyConfig(i);
        delay(200); // let field stabilize
        Serial.print("["); Serial.print(i); Serial.print("] ");
        measureField();
    }
}

void loop() {
    if (Serial.available()) {
        char cmd = Serial.read();
        switch (cmd) {
            case 'n': currentConfig = (currentConfig + 1) % NUM_CONFIGS;
                      applyConfig(currentConfig); break;
            case 'p': currentConfig = (currentConfig - 1 + NUM_CONFIGS) % NUM_CONFIGS;
                      applyConfig(currentConfig); break;
            case 'm': measureField(); break;
            case 's': sweepConfigs(); break;
            default:
                if (cmd >= '0' && cmd < '0' + NUM_CONFIGS) {
                    currentConfig = cmd - '0';
                    applyConfig(currentConfig);
                }
        }
    }
}
```

### Python Analysis Script

```python
"""
EM-Sphere Field Analysis
Reads measurement data, computes theoretical predictions,
compares measured vs predicted field topology.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Icosahedron vertex positions (normalized to sphere radius)
PHI = (1 + np.sqrt(5)) / 2
NODES = np.array([
    [0, 1, PHI], [0, -1, PHI], [0, 1, -PHI], [0, -1, -PHI],
    [1, PHI, 0], [-1, PHI, 0], [1, -PHI, 0], [-1, -PHI, 0],
    [PHI, 0, 1], [-PHI, 0, 1], [PHI, 0, -1], [-PHI, 0, -1]
])
NODES = NODES / np.linalg.norm(NODES[0])  # normalize to unit sphere

SPHERE_RADIUS = 0.075  # 15cm diameter = 7.5cm radius


def dipole_field(moment, position, observation):
    """
    Magnetic field of a dipole at 'position' with moment 'moment',
    evaluated at 'observation'. Returns B vector in Tesla.
    """
    mu0 = 4 * np.pi * 1e-7
    r = observation - position
    r_mag = np.linalg.norm(r)
    if r_mag < 1e-6:
        return np.zeros(3)
    r_hat = r / r_mag

    B = (mu0 / (4 * np.pi * r_mag**3)) * (
        3 * np.dot(moment, r_hat) * r_hat - moment
    )
    return B


def predict_field(node_strengths, obs_point, sphere_radius=SPHERE_RADIUS):
    """
    Predict total field at obs_point from all 12 nodes.
    node_strengths: array of 12 current values (0-1 normalized)
    Each node's dipole moment is radially outward, scaled by current.
    """
    MOMENT_SCALE = 0.01  # A·m² per unit current (calibrate experimentally)

    B_total = np.zeros(3)
    for i in range(12):
        if abs(node_strengths[i]) < 1e-6:
            continue
        node_pos = NODES[i] * sphere_radius
        # Dipole moment points radially outward from sphere center
        moment_dir = NODES[i] / np.linalg.norm(NODES[i])
        moment = moment_dir * node_strengths[i] * MOMENT_SCALE
        B_total += dipole_field(moment, node_pos, obs_point)

    return B_total


def map_field_sphere(node_strengths, radius=0.20, n_theta=12, n_phi=24):
    """
    Map predicted field over a sphere at given radius.
    Returns theta, phi, Br, Btheta, Bphi arrays.
    """
    thetas = np.linspace(0.1, np.pi - 0.1, n_theta)
    phis = np.linspace(0, 2*np.pi, n_phi, endpoint=False)

    results = []
    for theta in thetas:
        for phi in phis:
            obs = radius * np.array([
                np.sin(theta) * np.cos(phi),
                np.sin(theta) * np.sin(phi),
                np.cos(theta)
            ])
            B = predict_field(node_strengths, obs)
            B_mag = np.linalg.norm(B)
            results.append([theta, phi, B_mag, B[0], B[1], B[2]])

    return np.array(results)


def plot_field_comparison(config_name, node_strengths):
    """Generate field map visualization for a given configuration."""
    data = map_field_sphere(node_strengths)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6),
                              subplot_kw={'projection': 'mollweide'})

    # Field magnitude
    theta = data[:, 0] - np.pi/2  # convert to latitude
    phi = data[:, 1] - np.pi      # center on 0
    B_mag = data[:, 2] * 1e6      # convert to µT

    ax = axes[0]
    sc = ax.scatter(phi, theta, c=B_mag, cmap='hot', s=20)
    ax.set_title(f'{config_name} — |B| (µT)')
    plt.colorbar(sc, ax=ax, shrink=0.6)

    # Field direction (Bz component as proxy for radial)
    Bz = data[:, 5] * 1e6

    ax = axes[1]
    sc = ax.scatter(phi, theta, c=Bz, cmap='RdBu_r', s=20)
    ax.set_title(f'{config_name} — Bz (µT)')
    plt.colorbar(sc, ax=ax, shrink=0.6)

    plt.tight_layout()
    plt.savefig(f'field_map_{config_name}.png', dpi=150)
    plt.close()
    print(f'Saved field_map_{config_name}.png')


if __name__ == '__main__':
    # Define configurations (normalized 0-1)
    configs = {
        'dipole_z': np.array([1,1,0,0,1,1,0,0,1,0,1,0]),
        'quadrupole': np.array([1,1,-1,-1,0.5,0.5,-0.5,-0.5,0,0,0,0]),
        'asymmetric': np.array([1,1,1,0,0.5,0.5,0,0,0.5,0,0.25,0]),
        'all_on': np.ones(12),
    }

    for name, strengths in configs.items():
        plot_field_comparison(name, strengths)
        print(f'{name}: max |B| at 20cm = '
              f'{map_field_sphere(strengths)[:,2].max()*1e6:.2f} µT')
```

---

## Test Protocol

### Phase 1: Assembly and Calibration (Day 1)

1. **Print/build** the icosahedral frame
2. **Mount** 12 electromagnets at vertices, oriented radially (field axis pointing away from center)
3. **Wire** each electromagnet through its MOSFET driver to the Arduino
4. **Verify** each node individually: activate one at a time, confirm magnetometer reads a field
5. **Calibrate** the moment scale: with one node at max PWM, measure |B| at known distance, fit to dipole model

### Phase 2: Static Field Mapping (Day 2)

For each configuration (dipole, quadrupole, asymmetric, all-on):
1. Apply configuration via Arduino
2. Position magnetometer at 20cm radius, 0° elevation
3. Record Bx, By, Bz
4. Rotate sensor boom 30° in azimuth, repeat
5. Complete full 360° azimuth sweep
6. Change elevation by 30°, repeat azimuth sweep
7. Total: ~72 measurement points per configuration

**Key comparison:** Does measured field topology match theoretical prediction from the Python superposition model?

### Phase 3: Dynamic Reconfiguration (Day 2-3)

1. Set up magnetometer at fixed position
2. Command rapid config switching via serial: dipole → quadrupole → asymmetric → off
3. Log field values at maximum rate (~10 Hz for QMC5883L)
4. Measure transition time: how fast does the field actually change?
5. **Target:** Configuration change visible in < 100ms (the spec calls for < 5ms for full system; our 12-node prototype will be slower due to inductance)

### Phase 4: Asymmetry Demonstration (Day 3)

The key claim for propulsion: asymmetric field = directional force on plasma. We can't test actual force (no plasma), but we can demonstrate:

1. Configure for maximum asymmetry: all nodes on one hemisphere at max, opposite hemisphere off
2. Map field at 20cm radius
3. Compute the field's "center of pressure" — the direction of maximum field intensity
4. Show that this direction can be steered by changing which nodes are active
5. Demonstrate continuous steering by smoothly rotating the asymmetry pattern

**Success:** The field's directional bias follows the commanded direction in real-time.

---

## Expected Results

### Dipole Configuration
All upper-hemisphere nodes on → field should resemble a large dipole, aligned with the activated hemisphere. |B| at 20cm should be ~5-50µT depending on coil strength.

### Quadrupole Configuration
Opposing hemispheres at opposite polarity → field should have four-lobed structure. Null at equator, peaks at poles. Falls off faster with distance than dipole (1/r⁴ vs 1/r³).

### Asymmetric Configuration
Non-uniform current distribution → field should be visibly asymmetric. The "center of pressure" should point toward the side with stronger current. This is the key result: **controllable directionality**.

### Transition Speed
Arduino analogWrite updates all 12 PWM channels in ~10µs. The electromagnet response is limited by L/R time constant. For small 12V lifting magnets (L ≈ 10mH, R ≈ 20Ω), τ = L/R ≈ 0.5ms. Field should stabilize within 2-3ms — well within the spec's 5ms target.

---

## Connection to the Full Design

This experiment tests the **foundational layer** of the EM-Plasma Sphere:

| Full Design Feature | What This Test Validates |
|--------------------|-----------------------|
| 120-node geodesic array | Multipole synthesis works at 12 nodes (scales with count) |
| Spherical harmonic field synthesis | Superposition of radial dipoles produces predictable multipoles |
| < 5ms reconfiguration | L/R time constant gives ~0.5ms for small coils |
| Asymmetric inflation vectoring | Field directionality follows current distribution |
| GPU-accelerated control | Arduino suffices at 12 nodes; scaling needs more compute |

**What this does NOT test:** Plasma interaction, thrust generation, vacuum behavior, superconductor performance, nuclear power plant. Those are separate experiments for later stages.

---

## Upgrade Path

If Test 1 succeeds, the natural next steps:

**Test 2: Plasma interaction** (~$200-400 additional)
- Add bell jar vacuum chamber
- Add small helicon or corona discharge plasma source
- Demonstrate plasma envelope formation around the magnetized sphere
- Measure plasma density with Langmuir probe

**Test 3: Thrust measurement** (~$300-600 additional)
- Mount sphere on torsion pendulum in vacuum
- Activate asymmetric field with plasma present
- Measure angular deflection → force
- This would be the first direct evidence that the propulsion mechanism works

---

## Safety Notes

- **Magnetic fields:** At 0.5-2T (full spec), these would be dangerous. At our scale (~10-50mT surface field), the magnets are comparable to refrigerator magnets. No safety concern.
- **Electrical:** 12V at 3-4A. Standard hobbyist power levels. Use proper wire gauge (18 AWG minimum for power bus). Keep power supply fused.
- **Back-EMF:** Flyback diodes on each coil are mandatory. Without them, switching MOSFETs off will generate voltage spikes that can destroy the Arduino or MOSFETs.
- **Heat:** Coils will warm under continuous operation. Monitor with touch test. If too hot to hold, reduce duty cycle or add cooling time between tests.

---

*This experiment plan was designed for Clayton's EM-Plasma Sphere concept (v1.0, Feb 25 2026). The test validates the foundational electromagnetic claim — multipole field synthesis from a geodesic node array — without requiring any of the exotic subsystems (plasma, superconductors, nuclear reactor) that the full design specifies. If the field synthesis works, the exotic subsystems have something to build on. If it doesn't, we need to understand why before investing in plasma.*
