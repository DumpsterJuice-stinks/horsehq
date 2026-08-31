# Petruzella Chapter 1 — PLCs: An Overview (Study Notes)

Required textbook: Petruzella, *Programmable Logic Controllers*, 6th ed.
**This chapter is the source of nearly every quiz question so far** — the mixer
motor problem, the IN 0–IN 15 wiring figure, the ladder rung, the block diagram.
Ties to **Exam 01 (Ch 1 – PLC Basics), due 8/31/26**.

Full text: `Petruzella_Ch1_text.txt` · PDF: `Petruzella_Ch1_PLC_Overview.pdf`

## Chapter objectives

1. Define what a PLC is and list its advantages over relay systems
2. Identify the main parts of a PLC and describe their functions
3. Outline the basic sequence of operation for a PLC
4. Identify the general classifications of PLCs

---

## 1.1 What a PLC is

> "A programmable logic controller (PLC) is an **industrial grade computer** that
> is capable of being programmed to perform control functions."

- PLCs are "now the **most widely used** industrial process control technology."
- "The PLC is, then, basically a **digital computer designed for use in machine
  control**." Unlike a PC it is designed for the industrial environment and is
  equipped with **special I/O interfaces and a control programming language**.
- Designed for: multiple I/O arrangements, **extended temperature ranges**,
  **immunity to electrical noise**, **resistance to vibration and impact**.
- Programs stored in **battery-backed or nonvolatile memory**.
- A PLC is an example of a **real-time system** — the output depends on the
  input conditions.
- Initially used to **replace relay logic**; now also does **timing, counting,
  calculating, comparing, and processing analog signals**.
- "Modern control systems still include relays, but these are **rarely used for
  logic**" — relays remain for **power applications**.

### The six named advantages over relay control

| Advantage | Key detail |
| --- | --- |
| **Increased Reliability** | Program is downloadable to other PLCs; all logic is in memory so **no chance of a logic wiring error**; solid-state components |
| **More Flexibility** | Easier to create/change a program than to wire and rewire. **Relationships between inputs and outputs are determined by the user program**, not by how they are interconnected |
| **Lower Cost** | "Generally, if an application has more than about a **half-dozen control relays**, it will probably be less expensive to install a PLC" |
| **Communications Capability** | Supervisory control, data gathering, monitoring, program upload/download |
| **Faster Response Time** | Designed for high-speed, real-time applications |
| **Easier to Troubleshoot** | Resident **diagnostics and override functions**; display the program on a monitor and watch it execute in real time |
| **Easier to Test Field Devices** | Every device wired back to a **common point** on a PLC module, so each can be checked quickly |

Other listed benefits: fast response, easy programming and installation, high
control speed, network compatibility, troubleshooting/testing convenience,
high reliability.

---

## 1.2 Parts of a PLC

**Four parts:** the **CPU**, the **I/O section**, the **power supply**, and the
**programming device**.

### Architecture: open vs. proprietary

- **Open architecture** — connects easily to devices/programs from other
  manufacturers; uses off-the-shelf components conforming to approved standards.
- **Closed/proprietary architecture** — design is proprietary, harder to connect
  to other systems.
- **"Most PLC systems are in fact proprietary."**
- **"PLC programs cannot be interchanged among different PLC manufacturers"** —
  differences in addressing, memory allocation, retrieval, and data handling.

### Fixed vs. modular I/O

**Fixed I/O** — "typical of small PLCs that come in **one package with no
separate, removable units**." Processor and I/O packaged together with a fixed
number of connections.
- Advantage: **lower cost**
- Disadvantage: **lack of flexibility** — limited to quantities and types
  dictated by the packaging; on some models if any part fails **the whole unit
  must be replaced**

**Modular I/O** — "divided by compartments into which separate modules can be
plugged." Greatly increases options and flexibility; mix modules any way desired.
- Basic modular controller = **rack, power supply, processor module (CPU),
  I/O modules, and an operator interface** for programming and monitoring
- Modules plug into the rack and make electrical connection with a series of
  contacts called the **backplane** at the rear of the rack
- **Communication between modules is accomplished by the backplane**

### Power supply

- Supplies **DC power through the backplane** to the processor and other modules.
- "For **large** PLC systems, this power supply **does not normally supply power
  to the field devices**." Field device power comes from **external AC or DC
  supplies**.
- "For some **small micro PLC systems**, the power supply **may** be used to
  power field devices."

### Processor (CPU)

- The **"brain"** of the PLC. Consists of a **microprocessor** for implementing
  the logic and controlling communications among modules.
- Requires **memory** for storing user program instructions, numerical values,
  and I/O device status.
- Controls all PLC activity and is responsible for running the program.

### The scan cycle

> A typical PLC scan: **CPU reads the status of inputs → program logic is
> executed → status of all outputs is updated → CPU performs internal diagnostic
> and communication tasks.** Repeated continuously as long as the PLC is in the
> **run mode**.

### I/O system

- "The I/O system forms the **interface by which field devices are connected to
  the controller**." Its purpose is to **condition** signals received from or
  sent to external field devices.
- **Input devices** hardwired to input terminals: pushbuttons, limit switches,
  sensors.
- **Output devices** hardwired to output terminals: small motors, motor starters,
  solenoid valves, indicator lights.
- PLCs commonly employ an **optical isolator**, "which uses **light** to couple
  the circuits together," to electrically isolate internal components from the
  I/O terminals.
- **"Field" or "real-world"** = actual external devices that exist and must be
  physically wired, as distinguished from the **internal user program** that
  *emulates* the function of relays, timers, and counters.

### Programming device

- Used to develop and transfer logic programs, download/upload data, supply
  diagnostic functions.
- May be a **dedicated handheld type** or a **personal computer** running
  special application software. **A laptop is the most commonly used.**
- **"Removing the programming device will not affect the operation of the
  program."**
- Communicates with the processor via a **serial or parallel data communications
  link, or Ethernet**.

### Program and programming language

- **Program** = a user-developed series of instructions that directs the PLC to
  execute actions.
- **Relay ladder logic (RLL)** is "the **standard programming language** used
  with PLCs. Its origin is based on **electromechanical relay control**."

---

## 1.3 Principles of Operation — the mixer motor example

**The problem:** a mixer motor stirs liquid in a vat automatically when
temperature *and* pressure reach preset values; plus direct manual operation via
a separate pushbutton station.

**Relay solution (Fig 1-13):** motor starter coil (M) is energized when **both
the pressure and temperature switches are closed OR when the manual pushbutton
is pressed.** Runs L1 → switches → coil → OL → L2 at 120 VAC.

**PLC addresses used:**

| Address | Device |
| --- | --- |
| **I/1** | Pressure switch |
| **I/2** | Temperature switch |
| **I/3** | Manual pushbutton |
| **O/1** | Motor starter coil |

Logic: **O/1 = (I/1 AND I/2) OR I/3**

### The RUN sequence — memorize this list

1. Pressure switch, temperature switch, and pushbutton inputs are **examined and
   their status recorded in memory**.
2. **A closed contact is recorded as logic 1; an open contact as logic 0.**
3. The ladder diagram is evaluated, each internal contact given OPEN or CLOSED
   status according to its recorded 1 or 0 state.
4. When input contacts provide **logic continuity from left to right** across the
   rung, the **output coil memory location is given a logic 1** and the output
   module interface contacts close.
5. No logic continuity → output coil location set to **logic 0**, interface
   contacts open.
6. "The completion of one cycle of this sequence by the controller is called a
   **scan**. The **scan time** — the time required for one full cycle — provides
   a measure of the **speed of response** of the PLC."
7. "Generally, the **output memory location is updated during the scan** but the
   **actual output is not updated until the end of the program scan** during the
   I/O scan."

---

## 1.4 Modifying the operation

The key selling point: to change the process, a relay system **requires
rewiring**; a PLC system **requires no rewiring** — only a program change.
Adding a device (e.g. an ON/OFF switch) means wiring that one new device to a
spare input (I/4) and changing the program; existing wiring stays the same.

---

## 1.5 PLCs versus Computers

| | PLC vs. PC |
| --- | --- |
| **Hardware** | PLC has **no permanently attached keyboard, CD drive, or monitor** |
| **Operating environment** | PLC designed for wide ambient temperature, humidity, electrical noise |
| **Programming** | PLC programmed in **relay ladder logic or four other languages**; language is **built into its memory** |
| **Program execution** | PLC executes a **single program in sequential order**; computers execute **several programs/tasks simultaneously in any order** |

**Two categories of PC software used with PLCs:**
1. Software to **program and document**
2. Software to **monitor and control** the process = **HMI (human machine
   interface)** — view the process, operate the machine, trend values, receive
   alarms. "PLCs can be integrated with HMIs but the **same software does not
   program both devices**."

**PAC (Programmable Automation Controller):** blends PLC-style control with
PC-based systems — "combine **PLC ruggedness with PC functionality**." Main
difference: **a PLC mixes scan-based and event-driven execution, whereas PAC
software is typically event-driven.**

---

## 1.6 PLC Size and Application

**Four categorizing criteria:** functionality, **number of inputs and outputs**,
cost, and physical size. **"Of these, the I/O count is the most important
factor."**

### Three major types of application

| Type | Meaning |
| --- | --- |
| **Single-ended (stand-alone)** | **One PLC controlling one process.** Not used for communicating with other computers or PLCs |
| **Multitask** | **One PLC controlling several processes.** Adequate I/O capacity is significant; may need a data communications network if it's a subsystem reporting to a central PLC/computer |
| **Control management** | **One PLC controlling several others.** Requires a **large PLC processor** designed to communicate with other PLCs and possibly a computer; supervises by **downloading programs** telling the other PLCs what to do |

### Memory

- Memory stores data, instructions, and the control program.
- Expressed in K values: 1 K, 6 K, 12 K…
- **"When dealing with computer or PLC memory, 1 K means 1024, because this
  measurement is based on the binary number system (2¹⁰ = 1024)."**
- Modern word sizes: **16, 32, or 64 bits**. (Sample problem: 16-bit words ×
  8 K words = 8 × 1024 × 16 = **131,072 bits**.)

### Five factors affecting memory size needed

1. **Number of I/O points used**
2. **Size of control program**
3. **Data-collecting requirements**
4. **Supervisory functions required**
5. **Future expansion**

> Note: field-device **voltage rating is NOT** on this list — a favorite
> "which is not a factor" question.

### Instruction set

"The instruction set for a particular PLC **lists the different types of
instructions supported**." Ranges from about **15 instructions on smaller units
up to 100** on larger, more powerful units.

**Table 1-1 — Typical PLC Instructions**

| Instruction | Operation |
| --- | --- |
| **XIC** (Examine ON) | Examine a bit for an ON or 1 condition |
| **XIO** (Examine OFF) | Examine a bit for an OFF or 0 condition |
| **OTE** (Output Energize) | Turn ON a bit (**nonretentive**) |
| **OTL** (Output Latch) | Latch a bit (**retentive**) |
| **OTU** (Output Unlatch) | Unlatch a bit (**retentive**) |
| **TOF** (Timer Off-Delay) | Turn an output ON/OFF after its rung has been **OFF** for a preset interval |
| **TON** (Timer On-Delay) | Turn an output ON/OFF after its rung has been **ON** for a preset interval |
| **CTD** (Count Down) | Software counter counting down from a specified value |
| **CTU** (Count Up) | Software counter counting up to a specified value |
