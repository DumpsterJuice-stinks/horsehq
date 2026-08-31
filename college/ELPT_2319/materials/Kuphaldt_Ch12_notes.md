# Kuphaldt Chapter 12 — Programmable Logic Controllers (Study Notes)

Tony R. Kuphaldt, *Lessons In Industrial Instrumentation*, Ch. 12.
More technical/instrumentation-flavored than Petruzella. The course also uses
Kuphaldt Ch 9 for **Exam 02 (Discrete Process Measurement), due 9/7/26**.

Full text: `Kuphaldt_Ch12_text.txt` · PDF: `Kuphaldt_Ch12_PLCs.pdf`

## Framing

> "Every control system may be divided into **three general sections**: **input
> devices (sensors), controllers, and output devices (actuators)**. The input
> devices sense what is happening in the process, the controller decides what to
> do about it, and the output devices manipulate the process."

- A PLC is a **general-purpose** controller — contrast with **PID loop
  controllers**, which are special-purpose devices doing a single control function.
- PLCs were introduced as **electronic replacements for electromechanical relay
  controls**. Benefits: reliability (fewer failures, longer life),
  **re-programmability** (vs. re-wiring), and **networked communication** so
  process conditions can be monitored remotely and by multiple operator stations.
- **PLCs as a rule contain no disk drives, cooling fans, or any other moving
  parts** — an intentional design decision to maximize reliability in harsh
  environments (temperature extremes, vibration, humidity, dust/fibers/fumes).

**Typical input devices:** hand switches, process switches, sensors, analog
transmitters (4–20 mA), thermocouples, thermistors, strain gauges.
**Typical output devices:** electric lamps, solenoids, relay coils, motor
contactors, analog final control elements (throttling control valves,
variable-speed motor drives), audible buzzers.

## Modular ("rack") vs. monolithic ("brick")

| | **Modular / rack** | **Monolithic / brick** |
| --- | --- | --- |
| Build | Rack with plug-in **cards** — processors, I/O points, communication ports | One unit containing all processor, I/O, and comm functions |
| Config | Configurable to the application | Fixed I/O capability |
| Repair | **Replace only the failed card** | **Replace the whole unit** |
| Cost / size | More expensive | Far less expensive, more limited I/O |

## 12.2 I/O capabilities

### Discrete I/O

- A **discrete** data point has only two states, on and off. Process switches,
  pushbuttons, limit switches, proximity switches are discrete sensing devices.
- Inside each discrete input module: **LEDs energized when the sensing device
  turns on**, shining on a **phototransistor**, which activates a **bit** in the
  PLC's memory.
- This **opto-coupled** arrangement isolates the PLC's sensitive computer
  circuitry from transient voltage spikes and other damaging phenomena.
- **Each input channel has its own optocoupler**, writing to its own unique
  memory register bit.
- Discrete input cards typically have **4, 8, 16, or 32 channels**.
- Discrete output modules use the same opto-isolation. Discrete control devices:
  indicator lamps, solenoid valves, motor starters (contactors + overload
  protection).

### Analog I/O

- Early PLCs were **discrete-only** — processor speed and memory were too limited.
- **All PLCs are digital devices at heart**, so translation is required:
  - **Analog input module contains an ADC** (Analog-to-Digital Converter) —
    converts an analog signal into a multi-bit binary word
  - **Analog output module contains a DAC** (Digital-to-Analog Converter)
- Common analog signal types: voltage (0–10 V, 0–5 V), **current (0–20 mA,
  4–20 mA)**, thermocouple (millivoltage), RTD, strain gauge.

### Network I/O

- **Modbus** — "one of the earliest digital protocols developed for PLC
  communication," originally for the **Modicon** brand; adopted by others as a
  **de facto** standard; "remains perhaps the **most universal** digital
  protocol available for industrial digital devices today."
- **Profibus** — originally developed by **Siemens**, also a de facto standard.
- *de facto* = arising from legacy/pre-existence; *de jure* = agreed by
  committee before being built (e.g. FOUNDATION Fieldbus).

## 12.3 Logic programming

### IEC 61131-3 — the five standard languages

1. **Ladder Diagram (LD)** ← the one this course uses
2. **Structured Text (ST)**
3. **Instruction List (IL)**
4. **Function Block Diagram (FBD)**
5. **Sequential Function Chart (SFC)**

"Not all PLCs support all five language types, but **nearly all of them support
Ladder Diagram (LD)**."

**ISA safety standard 84** classifies industrial programming languages as
Fixed Programming (FPL), **Limited Variability (LVL)**, or **Full Variability
(FVL)**. **Ladder Diagram and Function Block Diagram are "limited variability";
Instruction List and traditional languages (C/C++, FORTRAN, BASIC) are "full
variability"** with more potential for complex errors.

### The fundamental rule of virtual contacts

> "**Each virtual contact shown in the program actuates whenever it reads a '1'
> state in its respective bit and will be at rest whenever it reads a '0'
> state.**"

| Contact type | Bit = 0 | Bit = 1 |
| --- | --- | --- |
| **Normally-open (NO)** | open (normal) | **closed** (actuated) |
| **Normally-closed (NC)** | **closed** (normal) | open (actuated) |

- A **0 bit puts the contact in its "normal" (resting) condition**; a **1 bit
  actuates** it into its non-normal state.
- Analogy: just as a pressure switch is actuated by high pressure, "a PLC's
  virtual contact is actuated by a **high bit condition (1)**."
- **Color highlighting** in programming software: **a colored contact is closed,
  an un-colored contact is open.** The slash marks the *normal* status; the live
  color shows the *conductive* status in real time.

### Memory maps and I/O addressing

- **Discrete I/O channels correspond to individual bits**; **analog I/O channels
  correspond to multi-bit words**.
- Addressing is **not standardized** between manufacturers or even between models
  from the same manufacturer — consult the engineering references.
- Allen-Bradley (Rockwell) was the most common brand in the US at the time of
  writing (2010). Modern A-B PLCs have moved to **tag-name based addressing**.

**Allen-Bradley SLC 500 memory map (data table):**

| File # | File type | Logical address range |
| --- | --- | --- |
| 0 | **Output image** | O:0 to O:30 |
| 1 | **Input image** | I:0 to I:30 |
| 2 | Status | S:0 to S:n |
| 3 | Binary | B3:0 to B3:255 |
| 4 | Timers | T4:0 to T4:255 |
| 5 | Counters | C5:0 to C5:255 |
| 6 | Control | R6:0 to R6:255 |
| 7 | Integer | N7:0 to N7:255 |
| 8 | Floating-point | F8:0 to F8:255 |
| 9 | Network | x9:0 to x9:255 |
| 10–255 | User defined | x10:0 to x255:255 |

- In A-B parlance a **"file" is a block of RAM storing a particular type of
  data** — not a PC-style document file.
- Files **0, 1, and 2 are exclusively reserved** for discrete outputs, discrete
  inputs, and status.
- Address format: file type letter, colon (file separator), element number,
  slash, bit number. Example: **B3:2/0** = first bit of the second element in
  file 3 (Binary).

## 12.4 Ladder Diagram programming

> "**Each contact in a Ladder Diagram PLC program represents the READING of a
> single bit in memory, while each coil represents the WRITING of a single bit
> in memory.**"

Contacts and coils are **discrete programming elements** dealing with Boolean
(1/0, on/off, true/false) states, "intended to mimic the contacts and coils of
electromechanical relays."

- Legacy PLCs: each discrete input channel has a **specific address**.
- Modern PLCs: each channel has a **tag name** created by the programmer.
- Worked example in the chapter: a **redundant flame-sensing system** — three
  sensors, indicate "lit" if **at least two of three** indicate flame
  (2-out-of-3 voting).

Other sections in the chapter: **counters (12.4.2), timers (12.4.3), data
comparison instructions (12.4.4), math instructions (12.4.5), sequencers
(12.4.6)**, then ST/IL/FBD/SFC, **Human-Machine Interfaces (12.9)**, and
"How to teach yourself PLC programming" (12.10).

## 12.11 Review of fundamental principles

- **"Normal" switch status** — the resting condition (minimum stimulus) as
  defined by the manufacturer.
- **"Seal-in" circuit** — "when an electrical relay uses **one of its own switch
  contacts to continue its own coil energization** after the initial triggering
  event has passed."
- **Sourcing versus sinking** — whether the device is outputting (conventional
  flow) current or inputting current. "Relevant to the proper connection of
  discrete DC input and output cards."
