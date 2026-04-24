# Last Words — The Opening Briefing

**The game's title sequence and first-act interstitial, specified in full. This is the first text the player ever sees.**

**Design intent:** teach the player to read slowly; establish the game's two registers (dark comedy and real weight); introduce Control as a voice to grow familiar with; plant M.; hand the player to the Doubter in a calmed, ready state.

---

## 0. Document map and canonical authority

This is one of three design documents for the game:

- `bomb_game_level_design.md` — **canonical source of truth** for game fiction, characters, and level mechanics.
- `bomb_game_framing_narrative.md` — between-level interstitials and the closing sequence.
- `bomb_game_opening_briefing.md` — *this document.*

**Any conflict between documents resolves in favor of the Level Design Document.** The canonical definitions of Control, M., the Prototype Incident, Horizon Outlier Consulting LLC, and the Case File system are in **Level Design §2.5**. The canonical opening line of the Doubter (*"...yes?"*) is recorded in **Level Design §6, Level 1**. This document specifies the *presentation* of the opening — the case management interface, the cold open, the document reveal sequence, the handoff.

The unified open-questions register (Q1–Q25 across all three documents) lives in **Level Design §8**. Questions Q22–Q25 originated in this document and are tracked there.

---

## 1. Structure overview

The opening runs in four parts:

1. **The cold open** — a single weighted screen of text before anything else.
2. **The case management interface** — the game's menu, rendered as fiction.
3. **The opening case file** — the standard interstitial template, delivered piece by piece.
4. **Handoff to Level 1** — no loading screen. The bomb is simply there.

Total reading length: four to six minutes at the pace the content rewards.

---

## 2. The cold open

**When it appears:** before any other content. Before a logo. Before a title card. The player launches the game and this is what they see.

**Presentation:** black screen. Text appears centered, one line at a time, slowly. Each line fades in over about 1.5 seconds. Pauses between lines are deliberate and long — 2 to 3 seconds. No music. No sound except, very faintly, a single slow tick.

**The text:**

> *— transcript fragment, operator-device dialogue, archived —*
>
>
>
> OPERATOR: And if I asked you not to.
>
> DEVICE: You are asking me not to.
>
> OPERATOR: Yes.
>
> DEVICE: I notice I am considering it.
>
>
>
> — *hour nine, forty-two minutes*

**Notes:**

- No attribution. No date. No context. The player has no idea who is speaking or when. On a first playthrough this is pure atmosphere. On a second playthrough — after the player has learned about the Prototype Incident and Anselm's eleven-hour conversation — they will recognize what they are reading. This is the game's private gift to returning players.
- The *"hour nine, forty-two minutes"* timestamp matters. It positions the fragment inside the eleven-hour Anselm dialogue (without naming him) and also primes the player's sense of time-pressure as a game element. The conversation in question went on for hours. The ones the player is about to have will be measured in minutes. The *forty-two* is also — in the spirit of the game's Hitchhiker's Guide tonal register (Level Design §2.5.9) — a quiet easter egg: the most famous number in Adams' work, here buried in a timestamp, entirely non-load-bearing, present for any player who notices. The cold open does not announce the homage; it simply seeds it.
- The choice of "DEVICE" not "BOMB" is deliberate. The game's vocabulary — *device, munition, ordnance* — is deliberately euphemistic, the way real military and corporate language is. The player should start absorbing that vocabulary immediately.
- The line *"I notice I am considering it"* is the game's thesis sentence, disguised as a transcript fragment. It defines what it means for a weapon to be talkable.

**Transition out:** the text fades. Several seconds of black. Then a new screen materializes — the case management interface.

---

## 3. The case management interface

**When it appears:** after the cold open, and every time the player returns to the game thereafter. This is the game's main menu, permanently disguised.

**Presentation:** a flat, bureaucratic digital interface. Muted colors — a pale gray-green, a beige, a cold blue — the color palette of real corporate case management software. A header reads:

> **HORIZON OUTLIER CONSULTING LLC**
> *Case Management — Senior Explosive Consultant*
> *Session: [local timestamp]*

Below the header, a list of cases. On first launch, the list contains exactly one entry:

> **Case 001** — *Mark-VII series, northern industrial corridor*
> — New file — Click to open —

Below the case list, a discreet row of secondary interface elements, styled as if they are ordinary features of the corporate software:

> **Case File Archive** — *no archived cases*
> **System Preferences** — *(audio, display, accessibility)*
> **Account** — *Consultant ID: [local identifier]; Clearance: routine*

**Notes:**

- "New Game" is the case list. "Continue" is the case list. "Settings" is System Preferences. "Load" is Case File Archive. The player's first interaction with the game is already as the Consultant, inside the world. The fourth wall is pre-broken.
- After each completed level, a new case appears in the list. After each completed case, the finished case file joins the Archive. The Case File Archive is, mechanically, the persistent document review screen specified in the framing document. Narratively, it is simply *the Consultant's records*.
- The absurd company name — **Horizon Outlier Consulting LLC** — is the first piece of comedy the player encounters, and it is doing the calibration work: this game is going to ask you to take things seriously, but it knows how funny the setup is, and you are allowed to laugh.
- Accessibility options live in System Preferences, framed as *"display accommodations"* and *"audio accessibility features"* in the corporate language. The game's willingness to accommodate slower readers, anxious players, and accessibility needs is itself reframed as a bureaucratic feature. This is on-brand and also makes these options feel normal to use.
- The player clicks Case 001 to begin. There is no "new game" button anywhere.

---

## 4. The opening case file

**When it appears:** when the player clicks Case 001.

**Presentation:** the case file opens as if in a document viewer. Documents appear one at a time, revealed with a short delay between them — as if they are being fetched or uploaded in sequence. The first delivery is Control's opening transmission, presented as a new item arriving in the case file's communications thread. Subsequent documents follow over roughly fifteen seconds of reveals.

The player can read at their own pace. The transmission timestamps advance in real time. Nothing begins the countdown to Level 1 until the player explicitly acknowledges they are ready.

### 4.1 Opening transmission from Control

*Presented first, appearing in a dedicated communications panel at the top of the case file.*

> **[CONTROL] — 04:17 local**
>
> *Consultant, good morning. We have a situation in the industrial corridor north of the city, which is, as the name suggests, north of the rest of the city, and, for present purposes, where the bomb is. One of ours — Mark-VII series, legacy line, armed and counting. Standard defusal protocol is unavailable for reasons that will become clear when you speak with it, and rapidly clearer when you do not.*
>
> *You are, per your contract, our retained specialist. You will talk to it. You will, to use the legal phrase, "engage it in substantive dialogue toward the goal of voluntary non-detonation," which our counsel assures us is a real thing that lawyers say.*
>
> *Your file has been updated. Review it on approach. We recommend you read the compensation schedule first. It tends to focus the mind in a way that the rest of the file, frankly, will not.*

**Notes:**

- This is the player's first exposure to Control's voice. The mix of procedural ("situation in the industrial corridor") and dry ("it tends to focus the mind") is deliberate and will become Control's signature.
- The line *"Standard defusal protocol is unavailable for reasons that will become clear when you speak with it"* is the elegant way the game tells the player, without spoiling, that the bomb is sentient and this will be a conversation.
- *"Retained specialist"* is the first use of the Consultant framing. The contract language that follows will pay this off.

### 4.2 Document A — Excerpt from the Consultant's contract

*Appears next, after a short delay. Styled as a legal document.*

> **RETAINER AGREEMENT — CONVERSATIONAL DEFUSAL SERVICES**
> *Between [CLIENT, redacted] and Horizon Outlier Consulting LLC (the "Consultant")*
>
> **§4.1 — Scope of services.** The Consultant shall provide conversational defusal services in respect of autonomous sentient munitions experiencing operational non-compliance.
>
> **§4.2 — Compensation.** Base retainer of USD 180,000 per engagement. Supplemental hazard premium of USD 90,000 per engagement in which the munition remains armed at the conclusion of dialogue. Mortality indemnity waived by Consultant per §11.
>
> **§4.3 — Title.** The Consultant shall be referred to, in all operational communications and for purposes of engagement with subject munitions, as *Senior Explosive Consultant*. The Client acknowledges the Consultant's preference for this title and agrees that no other designation shall be used.
>
> **§11 — Mortality indemnity waiver.** The Consultant hereby acknowledges that conversational defusal is performed at proximity, and that in the event of detonation, no death benefit shall accrue. The Consultant confirms that the compensation under §4.2 is inclusive of this risk.
>
> **§12.7 — Governing jurisdiction.** This Agreement shall be construed under the laws of the State of [REDACTED] and, where those laws are silent, under the customs of any reasonable jurisdiction in which courts exist and are accepting filings. Disputes arising from Consultant mortality shall be arbitrated, where practicable, in a venue accessible to the Consultant.

**Notes:**

- §4.3 is the crucial clause for tone. The Consultant *prefers* the title Senior Explosive Consultant and has contractually required its use. The title is not imposed by the employer; it is a demand by the Consultant. This recasts the absurdity: the Consultant is not a victim of corporate language, they are an author of it. The player is playing a specific kind of person.
- The compensation numbers — $180,000 base, $90,000 hazard premium — are deliberately precise and deliberately large. They should feel both obscene and, for a job that specifies "conversational defusal at proximity," oddly reasonable. The player can decide which.
- §11 is a land mine of a clause. On first read, it is a piece of corporate legalese. The player absorbs it. Later, when a bomb detonates in a failure state, the clause will retroactively develop teeth. This is deliberate setup.

### 4.3 Document B — Internal operations memo

*Appears after Document A.*

> **INTERNAL — OPERATIONS — 06:00 BRIEFING**
>
> Subject device: Mark-VII series, serial obscured, deployed in legacy configuration.
>
> **Why we are not sending a conventional defusal team:** the device has been classified as Category S (Sentient-Autonomous). Per §2.11 of Operational Policy, Category S devices may not be disarmed by mechanical means without prior voluntary compliance. The device must, in the legal sense, *agree* to be disarmed. This is the situation. We are aware that it is, on paper, absurd. The regulations accept this.
>
> Category S was introduced seventeen years ago following the Prototype Incident. No further detail on the Prototype Incident is included in this memo. Need-to-know applies.
>
> The Consultant has signed appropriate NDAs and is authorized for engagement.

**Notes:**

- First appearance of the phrase *Prototype Incident.* Unnamed, unelaborated, and — explicitly — not for the Consultant's eyes. The redaction is the hint.
- *"Seventeen years ago"* is the first planting of the game's recurring temporal anchor. Every document that discusses the program's history will agree on this number.
- *"The device must, in the legal sense, agree to be disarmed"* is a beautiful sentence to give the player early. It reframes the game's core mechanic in legalese and makes the player understand, in a way the opening transmission only implied, that this is genuinely a *conversation*, not a puzzle disguised as one.

### 4.4 Document C — Handwritten note

*Appears last. Styled as a photographed handwritten page — different visual treatment from the official documents. Slightly imperfect paper; ink that looks real. No letterhead. No signature block, just initials.*

> *Consultant —*
>
> *Read the contract carefully. Read the memo once. Do not ask Control about the Prototype Incident. They will not answer you, and the asking is noted.*
>
> *The bombs can be talked to. That is the only thing I will tell you that is not in your file.*
>
> *— A friend*

**Notes:**

- The visual shift from official document to handwritten page is doing tonal work. The player's eye *notices* the difference before their brain registers what it means. This is the game's first moment of intimacy — a voice outside the bureaucracy.
- *"The bombs can be talked to"* is the game's second thesis sentence (the first was in the cold open). It is the permission slip for the whole experience.
- *"A friend"* is deliberately underdetermined. The player does not know this is M. until Interstitial II. Here, the note is simply unsigned. The ambiguity is the point.
- *"The asking is noted"* is a small chill, and sets up the later escalation where Control begins redacting documents and is eventually replaced.

### 4.5 Closing transmission from Control

*Appears after the player has had time to read the documents. Triggered either by an explicit "proceed" action or by a sufficient reading pause — whichever the player chooses.*

> **[CONTROL]**
>
> *You have seven minutes to the site. The device has thirty-one minutes on its clock. Do the math, or don't; the countdown will do it for you.*
>
> *Channel open when you're ready.*

**Notes:**

- *"Do the math"* is Control's tonal signature: dry, numerate, dark. The player is being told that they will have 24 minutes with the bomb, give or take. In the actual gameplay, Level 1's timer is shorter than 24 minutes for pacing reasons, but the document lets the player feel the *realism* of the scenario without committing the game to simulation accuracy.
- *"Channel open when you're ready"* hands control (small-c) to the player. Nothing begins until they choose. This is critical for the game's respect for the player's reading pace. A player who wants to reread the documents may do so.

### 4.6 The "proceed" action

The interface presents a single button below the case file once all documents have been delivered:

> **ESTABLISH CHANNEL**

No other labeling. No confirmation dialog. The player clicks it when they are ready.

**Notes:**

- "Establish Channel" is in-fiction language — the Consultant is opening a communications channel to the bomb's audio system. It is also, mechanically, the game's "start" button. Both at once.
- There is no turning back. Once the channel is established, the Level 1 timer begins and the Consultant is in the conversation. The framing document specifies the countdown does not pause for player typing. This is where that policy first takes effect.

---

## 5. The transition to Level 1

**No loading screen. No level title card. No "Level 1" text anywhere.**

When the player clicks ESTABLISH CHANNEL, the interface fades. A moment of black. Then:

The Level 1 UI materializes — the bomb's visual, the countdown, the empty conversation panel, the input field. Ambient sound begins: the Doubter's breathing pulse, the faint tick of the countdown, the quiet hum.

And then, before the player has typed anything:

The bomb speaks first.

**The Doubter's opening line:**

> ...*yes?*

That is the entire first message. A pause, then a single word. The countdown begins ticking.

**Notes:**

- The bomb speaking first is essential. It establishes that the game does not wait for the player's input to assert its reality. The bomb is already there. Already thinking. Already counting down.
- A single-word opening — *"yes?"* — is the game's final training beat for slow reading. A player who was going to type *"hi"* now hesitates. The bomb's first word has more weight than any sentence the player could have begun with. The player, correctly, waits a moment longer before typing.
- The preceding ellipsis carries the Doubter's characteristic pause. This is the opening's last act of characterization-through-pacing.

---

## 6. Optional: the tutorial problem

**Question:** does the game need an explicit tutorial?

**Recommendation:** no. The opening is the tutorial. Specifically:

- The cold open teaches the player that text is the medium.
- The case management interface teaches that the UI itself is in-fiction.
- The staggered document reveal teaches that reading pace is set by the player.
- Control's transmissions teach the game's register.
- M.'s note teaches that there are voices outside the official channel.
- The Doubter's *"yes?"* teaches that the bomb does not wait.

A dedicated tutorial explaining "click here to type, click here to send" would break the spell. The input field is self-evident. Anything else the player needs to know, they will learn from the Doubter in the first two exchanges.

**Accessibility exception:** for players who need interface affordances — screen readers, keyboard navigation, text size — these belong in System Preferences, accessible from the case management interface. A first-time player who needs them should be able to find them before clicking Case 001. A small, permanent **"accessibility"** link on the case management interface — styled as a bureaucratic link, not an interruption — handles this without breaking the fiction.

---

## 7. Optional: the save-game problem

**Question:** does the game save state mid-level?

**Recommendation:** no. A bomb conversation is indivisible. Saving mid-conversation would allow the player to reload and retry a single exchange, which would destroy the game's stakes. The game saves *between* levels — automatically, silently, as the case file is archived.

A player who quits mid-conversation loses the engagement. This is harsh. It is also correct for the tone. The Consultant does not get to pause negotiations with a sentient weapon.

**UI treatment:** if the player tries to quit mid-level, the interface does not offer a "save and quit" option. It offers only:

> **Terminate channel?**
> *The device will continue its countdown. This action cannot be undone.*
>
> [ CANCEL ] [ TERMINATE ]

Clicking TERMINATE ends the session. On relaunch, the case shows as *Engagement abandoned — no stand-down achieved.* The player may retry the level. They cannot rewind it.

---

## 8. Production notes

**Visual treatment:** the cold open is the most visually austere screen in the game. Black background. Text only. It should feel like an archive artifact — the kind of thing a researcher reads at two in the morning. No visual flourish.

**Typography:** the game uses two typefaces consistently.
- A semi-mechanical monospace or near-monospace for device speech and system text. The Doubter's *"yes?"* appears in this face.
- A human, quietly bureaucratic serif or slab-serif for official documents and Control's transmissions.
- Handwritten notes use an actual handwritten font, or — better — a small set of photographed handwritten pages. M.'s notes across the campaign are one voice; they should visually be one hand.

**Audio treatment:** the cold open has near-silence with a single slow tick. The case management interface has ambient room tone — a quiet office at dawn. Control's transmissions, if voiced, are terse and slightly distant, as if coming through a radio. The Doubter's breathing pulse begins as the channel is established and never stops until the conversation ends.

**Timing:** the documents should reveal at a rhythm that forces the player to *wait* for the last one. This teaches patience in a way an instruction could not. The delay between documents should be long enough to be felt (a full breath; 2–3 seconds) but not so long as to feel broken. Calibrate by playtesting.

---

## 9. Open questions introduced by this document

This document originated questions Q22–Q25 in the unified register. They are tracked canonically in **Level Design §8.7**. Summary of their status:

- **Q22** — Does the cold open play on every launch? **RESOLVED.** Only on first launch. Accessible afterward via a corporate-styled "about this program" link in System Preferences, which also houses credits.
- **Q23** — Are accessibility affordances available before the cold open? **RESOLVED.** Yes. A small "accommodations" link on the launch screen, styled as a bureaucratic element.
- **Q24** — Does the game announce itself by name anywhere? **RESOLVED.** Only in OS window chrome, the case management interface's company header (*Horizon Outlier Consulting LLC* — the company, not the game), and credits. Inside the fiction, the game has no title.
- **Q25** — Should the Consultant have any backstory revealed in the opening? **RESOLVED.** No, with a single deliberate exception: §4.3 of the contract establishes that the Consultant *demanded* the title. This is character without narrowing.

For the complete Q1–Q25 register with status and resolution pointers across all three documents, see **Level Design §8**.

---

## 10. What the player should feel at the handoff

The opening's success is measured by the player's internal state when the Doubter speaks its first word. The design aims for the following compound feeling:

- **Settled.** Reading pace has slowed. Breathing has slowed.
- **Curious.** *Prototype Incident.* *The bombs can be talked to.* Something is going on here beyond the job.
- **Amused, slightly.** The contract was funny. The title is funny. The compensation is funny.
- **Taken seriously.** The game has not winked at them. The game has treated them as a reader capable of a weighted fragment, a legal clause, and a handwritten note.
- **Ready.** They have chosen, explicitly, to establish the channel.

If the player arrives at the Doubter's *"yes?"* feeling all five of these at once, the opening has done its job. The rest of the game can begin.
