# AutomationDirect PLC Handbook — Chapters 1 & 2 Study Notes

Source: *Practical Guide to Programmable Logic Controllers* (AutomationDirect).
Ties to the **"AutomationDirect PLC Handbook CH 1-2" quiz due 8/31/26**.
Full text: `AutomationDirect_PLC_Handbook_text.txt`

---

## Chapter 1 — What Is a PLC

**Definition:** "miniature industrial computers that contain hardware and
software used to perform control functions."

**Used for:** automation of industrial **electromechanical** processes —
factory assembly lines, **amusement rides**, food processing.

**Designed for:**
- Multiple arrangements of **digital and analog** inputs and outputs
- **Extended temperature ranges**
- **Immunity to electrical noise**
- **Resistance to vibration and impact**

### Two basic sections

> A PLC consists of **two** basic sections: the **CPU** and the **I/O interface
> system**. (Note: two, not three — a likely quiz target.)

**CPU** — controls all system activity through its processor and memory system.
Contains a **microprocessor, memory chip, and other integrated circuits** for
control logic, monitoring, and communications.

**CPU operating modes:**
- **Programming mode** — accepts changes to downloaded logic from a PC
- **Run mode** — executes the program and operates the process

**Memory** stores the program, holds the **status of the I/O**, and provides a
means to **store values**.

**Scan time:** time for one cycle through the program — "in the range of
**1/1000th of a second**" (1 ms), depending on the program. A PLC is a
*dedicated* controller: it runs one program over and over.

### The FOUR basic steps of PLC operation

A continually repeating loop:

| Step | What it does |
| --- | --- |
| **1. Input Scan** | Detects the state of all input devices connected to the PLC |
| **2. Program Scan** | Executes the user-created program logic |
| **3. Output Scan** | Energizes or de-energizes all output devices connected to the PLC |
| **4. Housekeeping** | Communicating with programming devices + performing internal diagnostics |

> The handbook counts **four** steps, including Housekeeping. Some texts list
> only three — go with four for this quiz.

### I/O module types and their devices

| Module | Field devices |
| --- | --- |
| **Discrete input** | Proximity sensors, photoelectric sensors, limit switches, pushbuttons — detect object presence or events |
| **Discrete output** | Motors, lights, solenoid valves — "ON/OFF" loads |
| **Analog input** | Flow, pressure, temperature, and level **transmitters** |
| **Analog output** | Panel meters, **variable frequency drives**, analog flow valves — loads needing a varying control signal |
| **Specialty** | High-speed I/O, motion control, serial or Ethernet communications |

**Greatest benefit of automating with a PLC:** "the ability to **repeat or change
and replicate** the operation or process while **collecting and communicating
vital information**."

**Buying considerations:** cost, power, speed, and communication.

---

## Chapter 2 — History of the PLC

### Key date and person

- **New Year's Day, 1968** — before this the programmable controller did not exist.
- **Dick Morley** — "the undisputed **father of the PLC**." Quote: "The
  programmable controller was **detailed on New Year's Day, 1968**."
- Morley's company at the time: **Bedford and Associates**.
- The customer driving it: **General Motors**, specifically the **Hydra-Matic
  division**.

### Before the PLC — relays only

- **Power relay:** placed between the power source and the motor; energize or
  de-energize it to control whether the motor gets power.
- **Control relay:** controls the relays that control the switch that turns the
  motor on and off.
- A relay works by a **coil** that, when energized, creates a **magnetic force**
  that pulls a switch to ON or OFF. De-energized, the switch releases and returns.

### The problems with relays

- All relays had to be **hardwired in a very specific order**
- **One faulty relay** and the whole system fails
- Troubleshooting took **hours**
- **Coils fail and contacts wear out** → strict maintenance schedules
- Took up **a lot of space**
- To change anything you had to **redo the entire system**

**Tom, a controls designer** (graduated technical college 1970):
- Systems used **50 to well over 100 relays**
- Enclosures typically **six feet wide by four feet high**
- After years of changes the wiring became a **"rat's nest"**

### GM's four requirements for a "standard machine controller"

1. A **solid-state** system that was **flexible like a computer** but **priced
   competitively** with a like-kind relay logic system.
2. **Easily maintained and programmed** in line with the already accepted
   **relay ladder logic** way of doing things.
3. Had to work in an **industrial environment** — dirt, moisture,
   electromagnetism, vibration.
4. Had to be **modular** in form, for easy exchange of components and
   **expandability**.

### Why ladder logic

Programming had to be understood by **maintenance electricians and plant
engineers**. In relay logic drawn as a ladder:
- **Left rail = control power hot wire**
- **Right rail = control power neutral**
- Contacts, pushbuttons, selector switches, limit switches, relay coils, motor
  starter coils, and solenoid valves in logical order form the **rungs**

### The first machines

- Initial machine (**never delivered**): only **125 words of memory**, and far
  too slow.
- **Relay response times are on the order of 1/60th of a second** — the first
  design couldn't match it.
- Memory expanded to **1K**, then to **4K**. "At 4K, it stood the test of time."

### Modicon

- Morley spun off a new company named **Modicon**.
- **Modicon 084** — named because it was **prototype #84**. This is what was
  presented to GM. Sold with very limited success: "Our sales in the first four
  years were **abysmal**."
- **Modicon 184** — the real success. Designed by **Michael Greenberg**, with
  **Lee Rousseau** (president and marketer). Morley objected to it and was
  "dead wrong." The 184 — *not* the 084 — is what made Modicon and the PLC
  industry take off.

### Evolution of PLC capability

**First PLCs could do:** input/output signals, relay coil/contact internal
logic, **timers and counters**.

Timers and counters used **word-size internal registers**, which soon enabled
simple **four-function math**.

**Later additions:** one-shots, analog I/O, enhanced timers and counters,
floating point math, drum sequencers, math functions, and built-in **PID
(Proportional-Integral-Derivative)** — a huge advantage in the process industry.
Then fill-in-the-blank data boxes, and **Tag Names** replacing non-descriptive
labels (importable/exportable to other devices to eliminate hand-entry errors).

### Programming devices — the progression

**Dedicated but suitcase-sized** → **handheld** → **proprietary software running
on a personal computer**.

- **AutomationDirect's DirectSOFT**, developed by **Host Engineering**, was the
  **first Windows-based PLC programming software package**.
- A PC talking to a PLC allowed not just programming but easier **testing and
  troubleshooting**.

### Communications — the progression

**MODBUS protocol over RS-232 serial** → RS-485, DeviceNet, Profibus and other
serial architectures → **Ethernet and EtherNet/IP** (IP = Industrial Protocol),
most recently and most popular.

Serial comms also let PLCs be networked with other PLCs, motor drives, and
**HMIs**.

---

## Likely quiz targets

1. A PLC has **two** basic sections: CPU and I/O interface system.
2. **Four** operating steps: Input Scan, Program Scan, Output Scan, **Housekeeping**.
3. Scan time ≈ **1/1000th of a second**.
4. CPU modes: **programming** and **run**.
5. **Dick Morley** = father of the PLC; **New Year's Day 1968**.
6. **General Motors / Hydra-Matic** issued the requirement; **Bedford and
   Associates** responded.
7. **Modicon 084** = prototype #84, poor sales. **Modicon 184** = the success.
8. First machine had **125 words** of memory; grew to **1K** then **4K**.
9. Relay response time = **1/60th of a second**.
10. GM's four requirements: solid-state/competitively priced, ladder-logic
    programmable, industrial-environment tough, **modular**.
11. **DirectSOFT** (Host Engineering) = first **Windows-based** PLC programming
    software.
12. Communications began with **MODBUS over RS-232**.
13. Relay enclosures were ~**6 ft × 4 ft**, holding **50–100+** relays.
14. Analog **outputs** drive panel meters, **VFDs**, analog flow valves.
15. Greatest benefit: **repeat/change/replicate** the process while collecting
    and communicating information.
