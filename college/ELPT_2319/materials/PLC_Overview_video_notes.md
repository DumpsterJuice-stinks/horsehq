# PLC Overview — Video Notes (ELPT 2319)

- **Video:** "PLC OVERVIEW" — https://youtu.be/cmBRvEXrYsM
- **Channel:** Richard Tunstall
- **Ties to:** Quiz "Overview of PLCs Video" (due 8/31/26) and Unit 2 –
  An Introduction to PLCs. Also supports Exam 01 (Ch 1 – PLC Basics).
- **Full transcript:** `PLC_Overview_video_transcript.txt` (source PDF alongside)

## The core distinction: Controls vs. Instrumentation

This is the spine of the whole video — the instructor returns to it repeatedly.

| | **Controls (PLC)** | **Instrumentation** |
| --- | --- | --- |
| Domain | Electrical | Analog process measurement |
| Signal | Digital — on/off, "black and white" | Analog — "shades of gray" |
| Process type | **Batch** | **Continuous** |
| Example signal | Switch closed / open | 4–20 mA, infinite values between |
| Typical action | Open/close a valve, start/stop a motor | Throttle a valve to any position |
| Typical system name | PLC | DCS (Distributed Control Systems) |

**Batch = a batch of cookies.** Open the flour hopper, dose it, close it. Open
milk, close. Open sugar, close. Then turn the mixer on, then off. Every action
is on/off — that's why it's PLC territory.

**Why switches are limited:** a 180 °F temperature switch tells you only that
you're at/above 180 or below it. It cannot tell you *how much* above or below.
Instrumentation gives you the window (e.g. see 150–210 °F), so you know whether
you're a little below setpoint or a lot.

## Relays → PLCs

- Relays are the **precursor** to the PLC; you must understand relays to
  understand PLCs.
- Relays are handy but **electromechanical** — mechanical parts wear out.
- The PLC **virtualizes the relay**: same functionality, no moving parts, and
  one computer replaces many relays. Big reduction in maintenance problems.
- **But PLCs did not eliminate relays.** Relay *output cards* exist precisely
  because a relay output lets you switch **external power** without the PLC
  supplying the output power itself.

## History & applications

- Invented by **Modicon**, for the **automotive industry** (assembling
  automobiles). The Modbus protocol traces back to Modicon.
- Spread everywhere: race cars, amusement park ride control, elevators,
  beverages, food batching.
- **Budweiser** is named as a local employer hiring electricians who need PLC
  knowledge (batch process).
- Refineries/chemical plants are continuous → more often **DCS**, though PLCs
  appear incidentally.
- Older name for PLCs was "PC" — still echoed on AutomationDirect's site under
  "Programmable Control."

## PLC architecture (the part most likely to be quizzed)

A PLC is straightforward — you need:

1. **Power supply** — always the **leftmost card**, slot 1. Plugs into the wall.
   Can also furnish power for I/O internally.
2. **CPU** — the computer, always the **second slot**, never anywhere else.
   Has ports, RUN/STOP/PROGRAM mode switches, indicator lights.
3. **Base / rack** — what everything plugs into.
4. **I/O cards** — plug into the remaining slots.

This card order (power supply, then CPU) is **historically standard across
brands and manufacturers**.

**Card types available:** DC input/output, AC input/output, combined AC/DC,
**relay output**, analog input/output (so PLCs can now do DCS-style continuous
control), Ethernet I/O, and specialty communication modules.

**AutomationDirect color code:** input cards have **blue** tabs, output cards
have a **red** tab/triangle.

**Simulator module:** a card of toggle switches standing in for real pressure,
level, proximity, and photocell switches — far more practical than physically
manipulating real switches while programming. A switch is "nothing more than
making and breaking a wire."

**Terminal blocks** unplug from the card, so you can wire them off the unit and
plug them back in. A cover hides the terminal block when wiring is done. LED
indicators on top show input and output states.

**Power supply options** (you must buy the PLC with the one you need — they are
*not* interchangeable on the same terminal block):
- 110/220 VAC
- 12/24 VDC (typical for instrumentation device wiring, e.g. pressure switches)
- 125 VDC (range 120–240 VDC — *not* a standard wall receptacle)

## I/O addressing

- The PLC **automatically maps** card placement once the hardware configuration
  is set — it learns where each input and output lives.
- Addressing is historically **octal**: first input card gets 0–7, second card
  automatically gets 8–15, even though the cards are identical.
- Octal is a power of two — the course covers **binary, octal, decimal, and
  hexadecimal**.
- There's no rule about which slots hold inputs vs. outputs; it's an engineering
  choice. **Once engineered, don't change the configuration.**

## Ladder logic

- **Rails** run vertically down both sides; **rungs** connect them — like a
  ladder you put hands and feet on. That's where "ladder programming" comes from.
- Ladder logic **did not come from PLC technology** — it came from **electrical
  relay controls**, as a simplified way to see circuitry.
- **Normally open contact:** drawn with a gap. Electrons reach the left side but
  can't cross. **Normally closed:** a line dissects the symbol, so current passes.
- Example given: a rung energizes a timer that reaches setpoint after 3 seconds,
  and all contacts that timer owns then switch.
- **Critical:** saving your project in Windows is *not* the same as putting it in
  the PLC. You must **write the project to the PLC** over the programming cable.
  Save locally too, so a power outage doesn't cost you your work.

## Do-more / AutomationDirect (the course's toolchain)

- **automationdirect.com** makes the Do-more PLC, Click PLC, Productivity,
  Direct Logic (legacy), plus Arduino-compatible controllers and motion
  controllers.
- **Do-more Designer** is a free, powerful **simulator** — program and see your
  logic work without hardware, then transfer the same program to a real Do-more
  PLC over a programming cable.
- **Downloading it:** the $11–$12 price on the page is only for **hard media**.
  Look for the blue "Download it" / "Download Software" link — it's free. You
  must enter an email address. **The download is zipped — decompress it BEFORE
  installing.**
- The **user manual** can no longer be bought but downloads free, chapter by
  chapter. Chapters called out: **1 (getting started), 2 (Do-more overview),
  8 (installation and wiring)**.
- Course product line: **Do-more H2 series**. Newer architectures mentioned:
  "Bricks" and a stackable PLC.
- The Do-more CPU connector resembles a Cat5 / telephone jack.
- Protocols shown: **Modbus**, Direct Net, Direct Logic, Do-more.

## Wiring (lighter touch — "wiring is not the nature of this course")

- PLCs mount in an enclosure/panel, on a **ground bus** and mounting plate; they
  snap onto a **DIN rail** (hook the top on the back channel, swing, push to lock).
  Terminal blocks snap onto the same DIN rail.
- **All inputs and outputs should be fused** (snap-on DIN rail fuses shown).
- **Common vs. unique wires:** the **common** wire is shared by every switch
  (here, the negative side of the supply). The **unique** wires branch off in
  parallel, one to each switch, and each returns to its own input terminal — so
  the PLC knows exactly which switch is "made."
- **Sinking and sourcing:** optional videos are in the course (link from Scott
  Churchman). Worth watching for a head start on wiring.
- Typical output loads: motors, pumps, solenoid valves, dampers, positioners, lights.
- A hobby PLC runs about **$120** for roughly 8 inputs / 6 outputs.

## Likely quiz targets

1. PLC = digital/on-off/batch; instrumentation = analog/4–20 mA/continuous.
2. Modicon invented the PLC for the automotive industry.
3. Power supply first slot, CPU second slot.
4. Relay outputs still exist — to switch external power.
5. Octal I/O addressing (0–7, then 8–15).
6. Ladder logic came from relay controls; rails and rungs.
7. Normally open = gap; normally closed = line through the symbol.
8. Saving in Windows ≠ writing the program to the PLC.
9. Decompress the Do-more download before installing.
10. Batch = cookies analogy; DCS = continuous processes like refineries.
