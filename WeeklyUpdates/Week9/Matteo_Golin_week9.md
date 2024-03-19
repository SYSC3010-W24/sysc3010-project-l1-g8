## Weekly Individual Project Update Report

### Group number: L1-G8

### Student name: Matteo Golin

### Week: 9 (13 Mar - 19 Mar)

---

1. **How many hours did you spend on the project this week? (0-10)**

I spent 8 hours this week.

2. **Give rough breakdown of hours spent on 1-3 of the following:\***
   (meetings, information gathering, design, research, brainstorming, evaluating options, prototyping options, writing/documenting, refactoring, testing, software implementation, hardware implementation)

   1. Creating unit tests for the alarm system and building its circuit: 5 hours
   2. Working on the technical memo: 3 hours

3. **_What did you accomplish this week?_** _(Be specific)_

- I learned how to interact with our passive buzzer component to produce alarm noise
- I modified our state machine pattern to be more easily testable
- I wrote unit tests for the alarm system state machine

4. **_How do you feel about your progress?_** _(brief, free-form reflection)_

- I feel great about my progress this week since our alarm system is working

5. **_What are you planning to do next week_**? _(give specific goals)_

- Next week I'd like to work on integrating the smoke sensor since we now have an ADC

6. **_Is anything blocking you that you need from others?_** _(What do you need from whom)_

- I noticed that the passive buzzer is quite quiet when driven only by the Pi's GPIO pins. I know that a higher voltage
  makes a louder buzz, so I wanted to use a BJT transistor or an op-amp to amplify the voltage signal of the Pi's GPIO
  pin. Unfortunately the maker space had neither so I will need to look elsewhere this week
