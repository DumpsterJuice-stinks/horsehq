# Kuphaldt Chapter 9 — Discrete Process Measurement (Study Notes)

**Exam 02 (Ch 9 – Discrete Process Measurement) due 9/7/26.** Also the source
text for the **Discrete Input Measurement Devices Report**, due the same day.

Full text: `Kuphaldt_Ch9_text.txt` · PDF: `Kuphaldt_Ch9_Discrete_Process_Measurement.pdf`

## Core definition

> "The word **discrete** means individual or distinct. In engineering, a
> 'discrete' variable or measurement refers to a **true-or-false condition**.
> Thus, a **discrete sensor is one that is only able to indicate whether the
> measured variable is above or below a specified setpoint**."

- Discrete sensors typically take the form of **switches**, built to "**trip**"
  when the measured quantity exceeds or falls below a specified value.
- Less sophisticated than **continuous sensors** capable of reporting an analog
  value — "but they are quite useful in industry."
- Variables detected: **position, fluid pressure, material level, temperature,
  fluid flow rate**.
- Output is typically electrical — an active voltage signal, or just **resistive
  continuity between two terminals**.

---

## 9.1 "Normal" status of a switch — THE key concept

> "The **'normal' status for a switch is the status its electrical contacts are
> in during a condition of NO PHYSICAL STIMULATION.** Another way to think of
> the 'normal' status is to think in terms of the switch being **at rest**."

- **Electrical switches are ALWAYS drawn in schematic diagrams in their "normal"
  statuses, regardless of their application.**
- **Normally-open (NO) contacts = "form-A" contacts**
- **Normally-closed (NC) contacts = "form-B" contacts**
- A switch providing both NO and NC from a shared common = **"form-C" contact
  set** (incorporates both a form-A and a form-B contact).

### Why "normal" is confusing

Kuphaldt's worked example: a **low coolant flow alarm** using a
**normally-closed** flow switch. Even though it is designated normally-closed,
"it will spend most of its lifetime being **held in the open status** by the
presence of adequate coolant flow." Only when flow drops does it **return to its
'normal' status** and light the lamp.

> "The 'normal' status for this switch (closed) is actually an **abnormal status
> for the process** it operates within."

**Why the convention exists:** "the **manufacturer of the switch has no idea
whatsoever as to your intended use**." A flow switch maker doesn't know if you'll
use it as a low-flow or high-flow detector, so "normal" must rest on a common
criterion unrelated to the application — **the resting status: least or no
stimulation from the process.**

### The "normal" definitions list — memorize this

| Switch type | "Normal" = |
| --- | --- |
| **Limit switch** | Target **not contacting** the switch |
| **Proximity switch** | Target **far away** |
| **Pressure switch** | **Low pressure** (or even a vacuum) |
| **Level switch** | **Low level** (empty) |
| **Temperature switch** | **Low temperature** (cold) |
| **Flow switch** | **Low flow rate** (fluid stopped) |

---

## 9.2 Hand switches

- "A hand switch is exactly what the name implies: an **electrical switch
  actuated by a person's hand motion**."
- Forms: toggle, pushbutton, rotary, pull-chain.
- Industrial pushbutton construction: **button, threaded neck** (inserts through
  a panel hole with a matching nut), **base**, with **NC and NO terminals**.
  The button faces the operator; contacts sit behind the panel.
- When pressed, the downward motion **breaks the bridge between the two NC
  contacts and forms a new bridge between the NO contacts**.
- Schematic symbol: **NC contact set on top, NO contact set below.**
- Connecting two terminals makes it electrically identical to a **form-C** switch.
- Most industrial hand switches are **modular** — contact blocks "stacked" to be
  actuated by the same pushbutton or knob, allowing almost unlimited contacts
  from one actuator. Actuator types (pushbutton, rotary selector, knob,
  keyswitch) are interchangeable with contact modules.

## 9.3 Limit switches

- "A limit switch **detects the physical motion of an object by DIRECT CONTACT**
  with that object."
- Everyday example: the switch detecting an **automobile door** opening, which
  energizes the cabin light.
- **Normal** = not in contact with anything.
- Industrial uses: **robotic control and CNC (Computer Numerical Control)**
  machine tools. Motion-control systems have **"home" positions** where the
  computer assigns position zero — the computer drives each servo until a limit
  switch trips, then resets that axis counter to zero.
- Typical design: a **roller-tipped lever** contacting the moving part.
- Most share a **"common" terminal** between NC and NO — a **form-C** set, with
  **NO / NC / C** screw terminals.

## 9.4 Proximity switches

- "A proximity switch is one detecting the **proximity (closeness)** of some
  object. By definition, these switches are **NON-CONTACT SENSORS**, using
  magnetic, electric, or optical means."
- **Normal** = distant from any detectable object.
- Advantage over limit switches: **never wear out from repeated physical
  contact**.
- "**Most proximity switches are ACTIVE in design**" — they incorporate a
  **powered electronic circuit**.

| Type | Senses | How |
| --- | --- | --- |
| **Inductive** | **Metallic** objects | High-frequency **magnetic** field |
| **Capacitive** | **Non-metallic** objects | High-frequency **electric** field |
| **Optical** | Interruption of a **light beam** | — |
| **Ultrasonic** | Dense matter | **Reflection of sound waves** |

- **Symbol:** same as a mechanical limit switch **but enclosed by a diamond
  shape**, indicating a powered (active) device.
- Many prox switches don't provide **"dry contact"** outputs — instead their
  output elements are **transistors configured either to SOURCE or SINK
  current**. Sourcing/sinking is best understood using **conventional flow**,
  not electron flow.

## 9.5 Pressure switches

- "A pressure switch is one detecting the presence of **fluid pressure**."
- Sensing elements: **diaphragms or bellows**, whose motion actuates the contacts.
- **Normal** = minimum pressure; any pressure **below the trip threshold**.
- Legacy design: a **bourdon tube** as sensing element with a **glass bulb
  partially filled with mercury** as the switching element — flexing tilts the
  bulb so mercury falls against electrodes. Sold widely under the brand
  **"Mercoid."**

## 9.6 Level switches

- "A level switch is one detecting the level of **liquid or solid (granules or
  powder)** in a vessel."
- Often use **floats** as the sensing element.
- **Normal** = minimum level (empty); any level below the trip threshold.
- The **schematic symbol is based on the float mechanism** — a round "ball" float
  drawn as the actuating element.
- Example: **Magnetrol** float switches sensing water level in a boiler steam
  drum. Mechanism uses a **mercury tilt bulb**, tilted by a magnet's attraction
  to a **steel rod** lifted by the float.

## 9.7 Temperature switches

- "A temperature switch is one detecting the temperature of some substance."
- Sensing elements: **bimetallic strips**, or a **metal bulb filled with fluid
  that expands with temperature**, pressing on a diaphragm or bellows.
- Note: "This latter temperature switch design is **really a pressure switch**,
  whose pressure is a direct function of process temperature."
- **Normal** = minimum temperature (cold).
- Example manufacturer named: **Ashcroft**.

## 9.8 Flow switches

- "A flow switch is one detecting the flow of some fluid through a pipe."
- Often use **"paddles"** as the sensing element — a paddle in the fluid stream
  generates a mechanical force that actuates the switch.
- **Normal** = minimum flow (no fluid moving).

---

## Deadband / hysteresis — appears in both 9.7 and 9.8

> "Like all other process switches, temperature switches exhibit a certain amount
> of **deadband** in their switching action."

- A temperature switch tripping at **300 °F rising will NOT reset at 300 °F
  falling** — more likely around **295 °F**.
- A flow switch tripping at **15 GPM rising** would likely reset near **14 GPM**.
- Also called **differential**.
- With mechanical designs some deadband is **inevitable due to friction**, but
  "process switch deadband is actually a **useful characteristic** as it helps
  **avoid repeated 'nuisance' alarms**" when the process variable hovers right
  at the trip point.

## 9.9 Review of fundamental principles

- **"Normal" switch status** — the resting condition (minimum stimulus), as
  defined by the manufacturer.
- **Sourcing versus sinking** — whether the device outputs (conventional flow)
  or inputs current. Especially relevant to proximity switches.
- **Deadband and hysteresis** — the difference in response with the independent
  variable increasing versus decreasing; usually caused by friction. "The value
  at which a switch changes state when its stimulus **increases** is not the same
  value it changes state when its stimulus **decreases**."
