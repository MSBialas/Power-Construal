#Authored by Mara because ChatGpt sucks 

import numpy as np
import random
from psychopy import visual, event, core, gui
from psychopy import visual, core, event, misc
import random
import csv
import os
from psychopy.hardware import keyboard
from psychopy import core
import math
from collections import defaultdict
import re
from collections import Counter

################ Pop Up Window and Participant Information ############
# Create a pop-up window for entering participant information
dlg = gui.Dlg(title="Participant Information")
dlg.addField("Participant Number:")
dlg.addField("Sex:", choices=["Male", "Female", "Other"])
dlg.addField("Age:")
dlg.addField("Condition:", choices=["A ", "C "])  # <-- new dropdown



participant_info = dlg.show()  # Show the dialog and capture user input

# Check if the user clicked OK or Cancel
if dlg.OK:
    # Extract participant information
    participant_number = participant_info["Participant Number:"]  # First field: Participant Number
    sex = participant_info["Sex:"]  # Second field: Sex
    age = participant_info["Age:"]  # Third field: Age
    condition_choice = participant_info["Condition:"]
    cond_label = "abstract" if condition_choice.upper() == "A" else "concrete"
    
    print("Participant Number:", participant_number)
    print("Sex:", sex)
    print("Age:", age)
    print("Condition Choice:", condition_choice, "->", cond_label)
else:
    print("Participant entry was canceled.")
    core.quit()  # Exit the program if canceled
    
# OUPUT FILE CREATION###########################################################

# Create CSV filename
def increment_filename(base_filename):
    file_count = 0
    filename = f"{base_filename}.csv"
    while os.path.exists(filename):
        file_count += 1
        filename = f"{base_filename}_{file_count}.csv"
    return filename

base_filename_tload = f"results_tload_participant_high_{participant_number}"
base_filename_performance = f"performance_tload_participant_high_{participant_number}"
base_filename_survey = f"survey_results_high_{participant_number}"

# --- Use the increment function to get final filenames ---
csv_filename_tload = increment_filename(base_filename_tload)
csv_filename_performance = increment_filename(base_filename_performance)
csv_filename_survey = increment_filename(base_filename_survey)

## Create CSV header #CREATE OUPUT FILE saves in directory
with open(csv_filename_tload, 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Block_Tload","Trial number", "Stimuli", "Correct/Incorrect", "Correct response", "Reaction time", "Stimuli time (STD)", "Performance", "Computer time", "Participant number", "Sex", "Age", "Stimuli Type"])

with open(csv_filename_performance, 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Block_Tload", "performance","stimuli time","computer time" , "pp number", "Sex", "Age"])
   
#Use for Questionnaire Items
with open(csv_filename_survey, 'a', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Participant Number", "Sex", "Age", "Code" , "Rating", "Block Count"])



######################window creation####################
win = visual.Window(size=[800,800], color='white', units='pix', fullscr=False)
# for later win = visual.Window(color='white', units='pix',fullscr=True)
# Hide the mouse cursor
win.mouseVisible = False


###################Initiate Questions for Framing Questions
ABSTRACT_TRUE = [
    "The T-Task is designed to reveal how the human mind processes and organizes information.",
    "The T-Task examines how people move between stable rules and flexible actions.",
    "The T-Task helps explain how humans manage changing and complex environments.",
    "The task offers a perspective on how the mind maintains coherence while adapting to new demands.",
    "The T-Task is based on theories and approaches from Cognitive Psychology."
]
ABSTRACT_FALSE = [
    "The T-Task is intended to study physical states rather than cognitive processes.",
    "The T-Task is design originates outside the study of the human mind.",
    "The T-Task is limited to assessing fixed knowledge rather than adaptive thinking.",
    "The T-Task centers on bodily performance rather than mental organization.",
    "The T-Task is grounded in theories of conditioning instead of cognitive theory."
]

CONCRETE_TRUE = [
    "In the T-Task, letters and numbers are shown one after another in a repeating sequence.",
    "The symbols are displayed for a short, fixed amount of time before the next appears.",
    "The sequence is made of alternating symbols, where a letter always follows a number and vice versa.",
    "The T-Task records both the speed and accuracy of responses.",
    "All key presses are logged to track how participants respond to the changing stream."
]
CONCRETE_FALSE = [
    "The T-Task presents pictures and sounds instead of letters and numbers.",
    "The timing of symbols is random and controlled by the participant.",
    "The T-Task only measures how many trials are completed, not accuracy or speed.",
    "Letters and numbers are shown in random groups instead of a fixed alternation.",
    "Errors are judged only by reaction speed and not by correctness."
]



# you already set these from your dialog:
# participant_number, sex, age, condition_choice ('A' or 'C'), cond_label ('abstract' or 'concrete')

# Track used items so we don't repeat statements until pools are exhausted
used_idxs = {
    "abstract_true": set(),
    "abstract_false": set(),
    "concrete_true": set(),
    "concrete_false": set(),
}

# CSV for TF items, include A/C in filename
csv_filename_tf = f'tf_explanations_{condition_choice}.csv'
if not os.path.exists(csv_filename_tf):
    with open(csv_filename_tf, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([
            "participant","sex","age","block_q",
            "condition_label","statement","ground_truth",
            "chosen_answer","choice_rt","confirm_rt",
            "explanation_text","timestamp"
        ])

def sample_tf_pair(cond_label, used_idxs):
    """Return two items for this block: one true + one false, without replacement across session."""
    if cond_label == "abstract":
        true_pool, false_pool = ABSTRACT_TRUE, ABSTRACT_FALSE
        key_true, key_false = "abstract_true", "abstract_false"
    else:
        true_pool, false_pool = CONCRETE_TRUE, CONCRETE_FALSE
        key_true, key_false = "concrete_true", "concrete_false"

    avail_true = [i for i in range(len(true_pool)) if i not in used_idxs[key_true]]
    avail_false = [i for i in range(len(false_pool)) if i not in used_idxs[key_false]]

    if not avail_true:   # reset if we ever exhaust in-session
        used_idxs[key_true].clear()
        avail_true = list(range(len(true_pool)))
    if not avail_false:
        used_idxs[key_false].clear()
        avail_false = list(range(len(false_pool)))

    i_true = random.choice(avail_true)
    i_false = random.choice(avail_false)
    used_idxs[key_true].add(i_true)
    used_idxs[key_false].add(i_false)

    pair = [
        (true_pool[i_true], "True"),
        (false_pool[i_false], "False")
    ]
    random.shuffle(pair)  # random order within the block
    return pair


def run_true_false_trial(win, statement, ground_truth):
    """
    Shows statement + '← False     → True'. Participant selects with arrows, ENTER to confirm.
    Then keeps statement + chosen answer on screen and collects a brief typed explanation (≤ ~50 words).
    Returns (chosen_answer, choice_rt, confirm_rt, explanation_text).
    """
    event.clearEvents()

    # --- choice phase
    q = visual.TextStim(win, text=statement, color='black', height=28, wrapWidth=1100, pos=(0, 130))
    instr = visual.TextStim(win, text="False ←         → True\nPress ENTER to confirm",
                            color='black', height=22, pos=(0, 40))
    choice_hint = visual.TextStim(win, text="Current selection: (none)",
                                  color='black', height=24, pos=(0, 0))

    selected = None  # "True" or "False"
    t0 = core.getTime()
    choice_rt = None
    confirm_rt = None

    while True:
        choice_hint.text = f"Current selection: {selected if selected else '(none)'}"
        q.draw(); instr.draw(); choice_hint.draw()
        win.flip()

        keys = event.getKeys(timeStamped=True)
        for k, ts in keys:
            if k in ['escape','q']: core.quit()
            if k == 'left':
                if selected is None: choice_rt = ts - t0
                selected = "False"
            elif k == 'right':
                if selected is None: choice_rt = ts - t0
                selected = "True"
            elif k == 'return' and selected is not None:
                confirm_rt = ts - t0
                break
        else:
            continue
        break

    # --- explanation phase
    # Keep question + chosen answer visible. Provide a simple text-entry box.
    chosen_line = visual.TextStim(
        win, text=f"Your answer: {selected} (ground truth: {ground_truth})",
        color='black', height=22, pos=(0, 80)
    )
    prompt = visual.TextStim(
        win,
        text="Briefly explain what the statement means (≤ 50 words):\n(Type; BACKSPACE to edit; ENTER to submit)",
        color='black', height=20, wrapWidth=1100, pos=(0, -40)
    )

    typed = ""
    while True:
        # draw a simple "box"
        box = visual.Rect(win, width=1100, height=120, lineColor='black', pos=(0, -140))
        # content (soft cap)
        display = typed[:800]

        q.draw(); chosen_line.draw(); prompt.draw(); box.draw()
        txt = visual.TextStim(win, text=display, color='black', height=19, wrapWidth=1040, pos=(0, -140))
        txt.draw()
        win.flip()

        keys = event.waitKeys()
        submit = False
        for k in keys:
            if k in ['escape','q']: core.quit()
            elif k == 'return':
                submit = True
            elif k == 'backspace':
                typed = typed[:-1]
            elif k == 'space':
                typed += ' '
            elif len(k) == 1:
                typed += k
        if submit:
            break

    # trim to ~50 words
    words = typed.split()
    if len(words) > 50:
        words = words[:50]
    explanation_text = " ".join(words)

    return selected, choice_rt, confirm_rt, explanation_text


############################################################
# Initialize variables##########################################################
#For Tload Dback Task
fixation_cross = visual.TextStim(win, text=' ', color=(0, 0, 0), height=60, units='pix')  # blank instead of cross

series1         = [ 'L'  'A'  'A'  'R'  'N'  'N'  'R'  'T'  'E'  'E'  'N'  'U'  'N'  'N'  'N'  'P'  'P'  'R'  'E'  'E'  'T'  'U'  'T'  'R'  'R'  'A'  'L'  'L'  'P'  'P' ]
REPONSE_SERIES1 = [ '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1' ]

series2         = [ 'A'  'C'  'C'  'L'  'N'  'R'  'R'  'L'  'E'  'E'  'A'  'P'  'P'  'T'  'N'  'T'  'U'  'T'  'C'  'C'  'R'  'R'  'E'  'L'  'L'  'A'  'A'  'A'  'U'  'U' ]
REPONSE_SERIES2 = [ '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '1'  '0'  '1' ]

series3         = [ 'C'  'R'  'R'  'E'  'E'  'N'  'L'  'L'  'T'  'U'  'R'  'C'  'C'  'E'  'E'  'N'  'U'  'C'  'L'  'L'  'P'  'R'  'R'  'A'  'A'  'T'  'L'  'L'  'P'  'P' ]
REPONSE_SERIES3 = [ '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1' ]

series4         = [ 'N'  'N'  'E'  'L'  'L'  'C'  'U'  'C'  'C'  'R'  'L'  'P'  'P'  'A'  'A'  'N'  'R'  'R'  'L'  'U'  'U'  'L'  'C'  'E'  'C'  'C'  'P'  'P'  'N'  'N' ]
REPONSE_SERIES4 = [ '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '1' ]

series5         = [ 'A'  'T'  'U'  'U'  'R'  'R'  'R'  'C'  'N'  'N'  'L'  'L'  'R'  'E'  'E'  'A'  'T'  'T'  'C'  'C'  'U'  'L'  'U'  'P'  'T'  'R'  'C'  'C'  'P'  'P' ]
REPONSE_SERIES5 = [ '0'  '0'  '0'  '1'  '0'  '1'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '0'  '0'  '0'  '0'  '1'  '0'  '1' ]

series6         = [ 'T'  'T'  'E'  'R'  'R'  'N'  'A'  'C'  'T'  'L'  'L'  'C'  'C'  'E'  'U'  'U'  'L'  'L'  'C'  'R'  'C'  'C'  'T'  'R'  'R'  'A'  'A'  'N'  'A'  'A' ]
REPONSE_SERIES6 = [ '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1' ]

series7         = [ 'L'  'C'  'C'  'E'  'E'  'A'  'C'  'L'  'L'  'U'  'R'  'N'  'N'  'P'  'A'  'T'  'P'  'P'  'C'  'C'  'U'  'U'  'L'  'E'  'R'  'R'  'T'  'T'  'A'  'A' ]
REPONSE_SERIES7 = [ '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '1' ]

series8         = [ 'R'  'R'  'L'  'P'  'P'  'A'  'C'  'C'  'E'  'E'  'C'  'E'  'N'  'N'  'P'  'T'  'T'  'A'  'C'  'U'  'L'  'L'  'U'  'U'  'R'  'T'  'T'  'P'  'R'  'R' ]
REPONSE_SERIES8 = [ '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1' ]

series9         = [ 'U'  'L'  'L'  'A'  'T'  'T'  'E'  'E'  'R'  'R'  'R'  'C'  'C'  'R'  'A'  'U'  'U'  'A'  'A'  'L'  'P'  'P'  'C'  'U'  'R'  'R'  'T'  'E'  'U'  'N' ]
REPONSE_SERIES9 = [ '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '1'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '0' ]

series10        = [ 'C'  'E'  'C'  'C'  'R'  'T'  'A'  'U'  'N'  'N'  'P'  'P'  'A'  'P'  'P'  'U'  'T'  'T'  'R'  'R'  'U'  'U'  'C'  'E'  'E'  'L'  'A'  'A'  'L'  'L' ]
REPONSE_SERIES10= [ '0'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1' ]

series11        = [ 'A'  'L'  'R'  'R'  'T'  'U'  'C'  'U'  'U'  'U'  'U'  'A'  'E'  'A'  'P'  'P'  'R'  'N'  'N'  'L'  'C'  'E'  'E'  'R'  'R'  'L'  'U'  'U'  'E'  'E' ]
REPONSE_SERIES11= [ '0'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '1'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1' ]

series12        = [ 'T'  'C'  'C'  'A'  'A'  'T'  'L'  'L'  'E'  'U'  'P'  'P'  'A'  'A'  'T'  'T'  'N'  'E'  'U'  'U'  'R'  'A'  'C'  'T'  'L'  'L'  'L'  'U'  'P'  'P' ]
REPONSE_SERIES12= [ '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '0'  '1'  '1'  '0'  '0'  '1' ]

series13        = [ 'A'  'A'  'R'  'R'  'T'  'U'  'U'  'E'  'E'  'N'  'P'  'A'  'A'  'A'  'P'  'T'  'T'  'T'  'N'  'N'  'C'  'E'  'N'  'N'  'P'  'L'  'U'  'C'  'C'  'C' ]
REPONSE_SERIES13= [ '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0' ]

series14        = [ 'E'  'E'  'T'  'A'  'U'  'U'  'T'  'R'  'R'  'R'  'L'  'L'  'U'  'E'  'T'  'P'  'P'  'A'  'L'  'P'  'A'  'A'  'C'  'A'  'A'  'C'  'C'  'N'  'R'  'R' ]
REPONSE_SERIES14= [ '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '1'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1' ]

series15        = [ 'U'  'C'  'R'  'R'  'C'  'C'  'L'  'N'  'N'  'U'  'U'  'R'  'A'  'A'  'T'  'L'  'L'  'E'  'U'  'U'  'R'  'A'  'C'  'T'  'T'  'N'  'N'  'U'  'U'  'E' ]
REPONSE_SERIES15= [ '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '1'  '0' ]

series16         = [ 'U'  'T'  'L'  'L'  'A'  'C'  'C'  'A'  'E'  'E'  'R'  'C'  'R'  'R'  'P'  'P'  'N'  'A'  'T'  'T'  'N'  'U'  'U'  'E'  'N'  'N'  'N'  'A'  'C'  'C' ]
REPONSE_SERIES16 = [ '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '1'  '0'  '0'  '1' ]

series17         = [ 'E'  'E'  'U'  'A'  'A'  'R'  'R'  'N'  'P'  'N'  'E'  'E'  'T'  'E'  'T'  'T'  'C'  'A'  'A'  'T'  'C'  'C'  'T'  'R'  'R'  'L'  'E'  'N'  'N'  'L' ]
REPONSE_SERIES17 = [ '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '1' ]

series18         = [ 'T'  'C'  'C'  'T'  'C'  'A'  'E'  'E'  'N'  'N'  'R'  'P'  'P'  'A'  'A'  'U'  'A'  'A'  'C'  'T'  'T'  'L'  'C'  'C'  'E'  'E'  'T'  'C'  'C'  'R' ]
REPONSE_SERIES18 = [ '0'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0' ]

series19         = [ 'N'  'N'  'L'  'A'  'N'  'U'  'U'  'T'  'R'  'R'  'A'  'A'  'R'  'P'  'L'  'T'  'T'  'E'  'A'  'U'  'U'  'N'  'A'  'T'  'T'  'N'  'C'  'C'  'C'  'C' ]
REPONSE_SERIES19 = [ '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '0'  '1'  '1'  '1' ]

series20         = [ 'C'  'T'  'T'  'E'  'R'  'E'  'E'  'U'  'U'  'N'  'P'  'P'  'A'  'C'  'C'  'A'  'T'  'R'  'R'  'N'  'N'  'P'  'U'  'U'  'L'  'L'  'P'  'L'  'L'  'E' ]
REPONSE_SERIES20 = [ '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '1'  '0'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0'  '1'  '0'  '0'  '1'  '0' ]

series_all = series1 + series2 + series3 + series4 + series5 + series6 + series7 + series8 + series9 + series10 + series11 + series12 + series13 + series14 + series15 + series16 + series17 + series18 + series19 + series20
REPONSE_ALL = REPONSE_SERIES1 + REPONSE_SERIES2 + REPONSE_SERIES3 + REPONSE_SERIES4 + REPONSE_SERIES5 + REPONSE_SERIES6 + REPONSE_SERIES7 + REPONSE_SERIES8 + REPONSE_SERIES9 + REPONSE_SERIES10 + REPONSE_SERIES11 + REPONSE_SERIES12 + REPONSE_SERIES13 + REPONSE_SERIES14 + REPONSE_SERIES15 + REPONSE_SERIES16 + REPONSE_SERIES17 + REPONSE_SERIES18 + REPONSE_SERIES19 + REPONSE_SERIES20


#######################General Instructions#######################################
instructions_gen = """
General Instructions\n
In this study, you will complete a roughly 45-minute-long series of tasks. \n
You will complete a task called T-Task, about which we want to ask you some questions. \n
You will be awarded Sona credits and money depending on your performance on the T-Task. \n\n
You will now start a training segment. \n
Press enter to continue"""

# Create text stimulus
instr_text = visual.TextStim(
    win,
    text=instructions_gen,
    color="black",
    height=24,
    wrapWidth=1000,
    alignText="left"
)

# Draw and wait for keypress
instr_text.draw()
win.flip()
event.waitKeys(keyList=["return"])  

###################Specific POWER INSTRUCtions

# ---------------- INSTRUCTIONS SCREEN BASED ON CONDITION ---------------- #
if cond_label == "abstract":
    instructions_text = (
        "T-Task explanation:\n\n"
        "The T-Task is rooted in Cognitive Psychology and is designed as a window into how the human mind processes and organizes information.\n\n"
        "The T-Task examines how individuals transition between maintaining guiding principles and carrying out actions.\n\n"
        "The T-Task creates contexts where individuals have to balance stability with flexibility, remaining sensitive to unfolding structures while adjusting to emerging requirements.\n\n"
        "Through these dynamics, it illuminates how the mind sustains coherence while navigating change.\n\n"
        "Later during the task you will be asked questions about these instructions.\n"
        "Please read carefully until further instructions appear."
    )
else:  # cond_label == "concrete"
    instructions_text = (
        "T-Task explanation:\n\n"
        "The T-Task is a computer-based task where letters and numbers are shown one after another in the center of the screen.\n\n"
        "A letter always appears, followed by a number, then another letter, and so on, creating a continuous stream of alternating symbols.\n\n"
        "Each symbol stays visible for a short, fixed amount of time before the next one appears.\n\n"
        "Throughout the task, the computer records every key press along with how quickly and accurately participants respond to the changing symbols.\n\n"
        "Later during the task you will be asked questions about these instructions.\n"
        "Please read carefully until further instructions appear."
    )

# Record the start time
start_time = t
min_display_time = 240  # 4 minutes (in seconds)

# Show instructions
instr_stim = visual.TextStim(
    win,
    text=instructions_text,
    color='black',
    height=30,
    wrapWidth=1000
)

next_text = visual.TextStim(
    win=win,
    text="You can now move on to the next task.",
    color="white",
    height=0.06,
    wrapWidth=1.2
)

instr_stim.draw()
win.flip()

if t - start_time >= min_display_time:
    next_text.setAutoDraw(True)

# Allow key press to continue only after 4 minutes
if t - start_time >= min_display_time and ('space' in keys or defaultKeyboard.getKeys(keyList=['space'])):
    continueRoutine = False

# Wait for Enter key to continue
event.waitKeys(keyList=['return'])







#First NBACK task
#############################################################################
#                           number training                                 
#############################################################################

## add instruction 

Instruction1_image = visual.ImageStim(win=win, image='inst_num.png',size=(900, 690)) #C:\Users\Gebruiker\Desktop\PsychopyStimuliSP2 current path
Instruction1_image.draw() #size=(150, 150)
win.flip()
event.waitKeys(keyList=['space']) ### might wanna change this to any key
STD = 1.4  # Replace with your desired duration
for j in range(10): #change to 20 later
    keys = event.getKeys()
    if 'q' in keys:
        core.quit()
    if 's' in keys: ###skips the training phase , mainly for our own purposes
        break
    num = 0
    numeros = ['1', '2', '3', '4', '6', '7', '8', '9']
    random.shuffle(numeros)

    text_stim = visual.TextStim(win, text=f'{numeros[0]}', color=(0, 0, 0), height=100)
    text_stim.draw()
    win.flip()

    t = core.getTime()
    while core.getTime() - t < STD:
        keys2 = event.getKeys(['num_2']) ### still need to work out how to make this 2 and 3 rather than letters
        keys3 = event.getKeys(['num_3'])
        if keys2:
            R_NUM = keys2
            core.wait(STD - (core.getTime() - t))
            break
        elif keys3:
            R_NUM = keys3
            core.wait(STD - (core.getTime() - t))
            break
        else:
            R_NUM = '0'
        core.wait(0.001)

    if int(numeros[num]) % 2 == 1:
        if keys3:
            REPONSE_NUM = '1' ## meaning correct
        elif keys2:
            REPONSE_NUM = '0' ## meaning incorrect
        else:
            REPONSE_NUM = '0' #no response is wrong

    elif int(numeros[num]) % 2 == 0:
        if keys2:
            REPONSE_NUM = '1' ## meaning correct
        elif keys3:
            REPONSE_NUM = '0' ## meaning correct
        else:
            REPONSE_NUM = '0' #no response is wrong
            
    if REPONSE_NUM == '0':
        num_stim_wrong = visual.TextStim(win, text=f'{numeros[0]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
        num_stim_wrong.draw()
        win.flip()
        core.wait(0.3)
    fixation_cross.draw()
    win.flip()##
    core.wait(0.2)##
        

#############################################################################
#                           letter training                                 
#############################################################################

## add instruction 

Instruction2_image = visual.ImageStim(win=win, image='inst_letters.png',size=(900, 690)) # current path, need to make sure this works on the lab computers
Instruction2_image.draw() #size=(150, 150)
win.flip()
event.waitKeys(keyList=['space']) ### might wanna change this to any key

R_LETTRE = 99
randorder = np.random.permutation(20)
series = series_all[randorder[0]]
REPONSE_SERIE = REPONSE_ALL[randorder[0]]

STD = 1.4  # Replace with your desired duration
keys = 'a' #####this is to change the s that might have been previously pressed to skip ahead

for j in range(len(series)):
    if 's' in keys:
        break
    keys = event.getKeys()
    if 'q' in keys:
        core.quit()
    if 's' in keys:
        break
    text_stim = visual.TextStim(win, text=f'{series[j]}', color=(0, 0, 0), height=100)
    text_stim.draw()
    win.flip()
    t = core.getTime()

    while core.getTime() - t < STD:
        keys = event.getKeys()
        if 'q' in keys:
            core.quit()
        if 's' in keys:
            break
        if 'space' in keys:
            R_LETTRE = '1'
            core.wait(STD - (core.getTime() - t))
            break
        else:
            R_LETTRE = '0'
        core.wait(0.001)
    if R_LETTRE == REPONSE_SERIE[j]: ####correct or incorrect identification
        REPONSE_LETTRE = '1'
    else:
        REPONSE_LETTRE = '0'
        text_stim_wrong = visual.TextStim(win, text=f'{series[j]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
        text_stim_wrong.draw()
        win.flip()
        core.wait(0.3)
    if R_LETTRE + REPONSE_SERIE[j] == 2: ### This is to essentially indicate the correct key presses. So for example a correct no response is coded as 0 here, and anything wrong is also coded as 0 
        trial = '1'
    else:
        trial = '0'
    fixation_cross.draw() #defined above, we add this just for the time being since we dont have the numbers added yet removed now coz not needed
    win.flip()##
    core.wait(0.2)##
    

#############################################################################
#                           proper training (only stops after 85%performance)                                
#############################################################################

## add instruction 
#instruction_text_85 = visual.TextStim(win, text='Instructions for 85% training - Press Space', pos=(0, 100),color=(0, 0, 0)) #temporary instruction window, will need something different
#instruction_text_85.draw()
#win.flip()
#event.waitKeys(keyList=['space'])

inst_85_p1_image = visual.ImageStim(win=win, image='inst_85_p1.png',size=(900, 690)) 
inst_85_p1_image.draw()
win.flip()
event.waitKeys(keyList=['space']) ### might wanna change this to any key

inst_85_p2_image = visual.ImageStim(win=win, image='inst_85_p2.png',size=(900, 690)) 
inst_85_p2_image.draw()
win.flip()
event.waitKeys(keyList=['space']) ### might wanna change this to any key

inst_85_p3_image = visual.ImageStim(win=win, image='inst_85_p3.png',size=(900, 690)) 
inst_85_p3_image.draw()
win.flip()
event.waitKeys(keyList=['space']) ### might wanna change this to any key


break_text_3 = visual.TextStim(win, text="3...",color=(0, 0, 0), height=100)
break_text_3.draw()
win.flip()
core.wait(1)
break_text_2 = visual.TextStim(win, text="2...",color=(0, 0, 0), height=100)
break_text_2.draw()
win.flip()
core.wait(1)
break_text_1 = visual.TextStim(win, text="1...",color=(0, 0, 0), height=100)
break_text_1.draw()
win.flip()
core.wait(1)  
break_text_GO = visual.TextStim(win, text="GO",color=(0, 0, 0), height=100)
break_text_GO.draw()
win.flip()
core.wait(0.5)

R_LETTRE = 99
performance = 0 ##to initialize the variable fro the while loop
keys = 'a' #####this is to change the s that might have been previously pressed to skip ahead
block_tload='individualization'
training_error_N = 0 
error = 0 
while performance <= 0.85:
    keys = event.getKeys()
    if 'q' in keys:
        core.quit()
    if 's' in keys: ###skips the training phase , mainly for our own purposes
        break
        
    #block_tload += 1 ##to be copy pasted
    computer_time_series = core.getTime() ##to be copy pasted
    randorder = np.random.permutation(20)
    series = series_all[randorder[0]]
    REPONSE_SERIE = REPONSE_ALL[randorder[0]]
    Should_have_pressed_sum = sum(int(num) for num in REPONSE_SERIE)
    Should_not_have_pressed_sum = len(REPONSE_SERIE)-Should_have_pressed_sum
    correctly_pressed_sum = 0
    correctly_ignored_sum = 0
    n_of_numbers_presented = 0 #keeps track of number of digits that are presented
    corect_number_response = 0 #keeps track of number of correctly identified even or uneven
    if 's' in keys:
        break
    STD = 1.4 
    #STD = 0.1
    trial_number = 0 #initializes variable (used in csv file) #to be copy pasted
    for j in range(len(series)):
        trial_number += 1 #incremembst trial number #to be copy pasted
        computer_time_stim = core.getTime() #to be copy pasted
        stimuli = series[j] #### for csv file to save the stimuli # to be copy pasted
        correct_response = REPONSE_SERIE[j] #to be copy pasted 
        correctly_pressed = 0 
        correctly_ignored = 0
        if 's' in keys:
            break
        keys = event.getKeys()
        if 'q' in keys:
            core.quit()
        text_stim = visual.TextStim(win, text=f'{series[j]}', color=(0, 0, 0), height=100)
        text_stim.draw()
        response_clock_tload = core.Clock() #######to determine the start of the visual display so that we can get reaction time of key press
        win.flip()
        t = core.getTime()
        response_time_tload = 0 #to be copy pasted

        while core.getTime() - t < STD:
            keys = event.getKeys()
            if 'q' in keys:
                core.quit()
            if 's' in keys:
                break
            if 'space' in keys:
                R_LETTRE = '1'
                response_time_tload = response_clock_tload.getTime() ######this determines reaction time for space bar press #to be copy pasted
                core.wait(STD - (core.getTime() - t))
                break
            else:
                R_LETTRE = '0'
            core.wait(0.001)
        if R_LETTRE == REPONSE_SERIE[j]: ####correct or incorrect identification
            REPONSE_LETTRE = '1'
            if R_LETTRE == '1':
                correctly_pressed = 1
                correct_incorrect = 'correctly_pressed' ### to be copy pasted
            elif R_LETTRE == '0':
                correctly_ignored = 1
                correct_incorrect = 'correctly_ignored' ### to be copy pasted
        else:
            REPONSE_LETTRE = '0'
            correct_incorrect = 'incorrect' ####to be copy pasted 
            text_stim_wrong = visual.TextStim(win, text=f'{series[j]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
            text_stim_wrong.draw()
            win.flip()
            core.wait(0.3)
        if R_LETTRE + REPONSE_SERIE[j] == 2: ### This is to essentially indicate the correct key presses. So for example a correct no response is coded as 0 here, and anything wrong is also coded as 0 
            trial = '1'
        else:
            trial = '0'
        correctly_pressed_sum = correctly_pressed_sum + correctly_pressed
        correctly_ignored_sum = correctly_ignored_sum + correctly_ignored
        ########trying to save variables in CSV            
        with open(csv_filename_tload, 'a', newline='') as csvfile: ####these lines were copy pasted below
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([block_tload,trial_number, stimuli, correct_incorrect, correct_response, response_time_tload, STD, performance, computer_time_stim, participant_number, sex, age])
#####  the number section
        trial_number += 1 #incremembst trial number #to be copy pasted 
        computer_time_stim = core.getTime() #to be copy pasted 
        num = 0
        n_of_numbers_presented = n_of_numbers_presented + 1 ###this is meant to count the number of numbers presented
        numeros = ['1', '2', '3', '4', '6', '7', '8', '9']
        random.shuffle(numeros)
        stimuli = numeros[0] #to be copy pasted 
        text_stim = visual.TextStim(win, text=f'{numeros[0]}', color=(0, 0, 0), height=100)
        text_stim.draw()
        response_clock_tload = core.Clock() #######to determine the start of the visual display so that we can get reaction time of key press # to be copy pasted 
        response_time_tload = 0 #to be copy pasted
        win.flip()

        t = core.getTime()

        while core.getTime() - t < STD:
            keys2 = event.getKeys(['num_2'])
            keys3 = event.getKeys(['num_3'])
            if keys2:
                R_NUM = keys2
                response_time_tload = response_clock_tload.getTime() ######this determines reaction time for key press #to be copy pasted 
                core.wait(STD - (core.getTime() - t))
                break
            elif keys3:
                R_NUM = keys3
                response_time_tload = response_clock_tload.getTime() ######this determines reaction time for key press#to be copy pasted
                core.wait(STD - (core.getTime() - t))
                break
            else:
                R_NUM = '0'
            core.wait(0.001)
        if int(numeros[num]) % 2 == 1:
            correct_response = 3 #to be copy pasted 
            if keys3:
                REPONSE_NUM = '1' ## meaning correct
                correct_incorrect = 'correct' # to be copy pasted 
            elif keys2:
                REPONSE_NUM = '0' ## meaning incorrect
                correct_incorrect = 'incorrect' # to be copy pasted 
            else:
                REPONSE_NUM = '0' #no response is wrong
                correct_incorrect = 'no_press' #to be copy pasted 

        elif int(numeros[num]) % 2 == 0:
            correct_response = 2  # to be copy pasted 
            if keys2:
                REPONSE_NUM = '1' ## meaning correct
                correct_incorrect = 'correct' #to be copy pasted 
            elif keys3:
                REPONSE_NUM = '0' ## meaning correct
                correct_incorrect = 'incorrect' #to be copy pasted 
            else:
                REPONSE_NUM = '0' #no response is wrong
                correct_incorrect = 'no_press' # to be copy pasted 
                
        if REPONSE_NUM == '0':
            num_stim_wrong = visual.TextStim(win, text=f'{numeros[0]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
            num_stim_wrong.draw()
            win.flip()
            core.wait(0.3)
        elif REPONSE_NUM == '1':
            corect_number_response = corect_number_response + 1
            
########trying to save variables in CSV            
        with open(csv_filename_tload, 'a', newline='') as csvfile: ##### to be copy pasted 
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([block_tload,trial_number, stimuli, correct_incorrect,correct_response, response_time_tload, STD, performance,computer_time_stim, participant_number, sex, age])
            #
    correctly_pressed_proportion = correctly_pressed_sum/Should_have_pressed_sum
    correctly_ignored_proportion = correctly_ignored_sum/Should_not_have_pressed_sum
    letter_id_performance = correctly_pressed_proportion*0.65 + correctly_ignored_proportion* 0.35
    number_id_performace = corect_number_response/n_of_numbers_presented #calculates the average identification rate of even or uneven
    performance = letter_id_performance*0.65 + number_id_performace *0.35
    #block_tload = '85% training'
    ######add here variables for csv file with only performance ### need to add teh code 
    with open(csv_filename_performance, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([block_tload, performance, STD, computer_time_series, participant_number, sex, age])
    if performance <= 0.85:
        training_error_N += 1
    if training_error_N >= 5:
        error = 1 
        break 
    if performance <= 0.85:
        if 's' not in keys:
            break_text.draw()
            win.flip()
            core.wait(12)
            break_text_3 = visual.TextStim(win, text="3...",color=(0, 0, 0), height=100)
            break_text_3.draw()
            win.flip()
            core.wait(1)
            break_text_2 = visual.TextStim(win, text="2...",color=(0, 0, 0), height=100)
            break_text_2.draw()
            win.flip()
            core.wait(1)
            break_text_1 = visual.TextStim(win, text="1...",color=(0, 0, 0), height=100)
            break_text_1.draw()
            win.flip()
            core.wait(1)  
            break_text_GO = visual.TextStim(win, text="GO",color=(0, 0, 0), height=100)
            break_text_GO.draw()
            win.flip()
            core.wait(0.5)
    if training_error_N >= 5:
        error = 2 
        break 
            
        

#############################################################################
#                           Individualiziation                                
#############################################################################

## add instruction 

#fast_as_possible = visual.TextStim(win, text='Now try to be as accurate as possible to work out how fast you can do this \n Press Space', pos=(0, 100),color=(0, 0, 0))
#fast_as_possible.draw()
#win.flip()
#event.waitKeys(keyList=['space'])

inst_indiv_image = visual.ImageStim(win=win, image='inst_indiv.png',size=(900, 690)) 
inst_indiv_image.draw()
win.flip()
event.waitKeys(keyList=['space']) ### might wanna change this to any key

R_LETTRE = 99
STD = 1.3
if performance <= 0.85:
    STD = 1.2
keys = 'a' #####this is to change the s that might have been previously pressed to skip ahead

skipped = False

while performance >= 0.01:
    block_tload = 'Inidivdualization'
        
    computer_time_series = core.getTime() ##to be copy pasted
    randorder = np.random.permutation(20)
    series = series_all[randorder[0]]
    REPONSE_SERIE = REPONSE_ALL[randorder[0]]
    Should_have_pressed_sum = sum(int(num) for num in REPONSE_SERIE)
    Should_not_have_pressed_sum = len(REPONSE_SERIE)-Should_have_pressed_sum
    correctly_pressed_sum = 0
    correctly_ignored_sum = 0
    n_of_numbers_presented = 0 #keeps track of number of digits that are presented
    corect_number_response = 0 #keeps track of number of correctly identified even or uneven
    if 's' in keys:
        break
    trial_number = 0 #initializes variable (used in csv file) #to be copy pasted
    for j in range(len(series)):
        trial_number += 1 #incremembst trial number #to be copy pasted
        computer_time_stim = core.getTime() #to be copy pasted
        stimuli = series[j] #### for csv file to save the stimuli # to be copy pasted
        correct_response = REPONSE_SERIE[j] #to be copy pasted 
        correctly_pressed = 0 
        correctly_ignored = 0
        keys = event.getKeys()
        if 'q' in keys:
            core.quit()
        if 's' in keys:
            skipped = True
            break
        text_stim = visual.TextStim(win, text=f'{series[j]}', color=(0, 0, 0), height=100)
        text_stim.draw()
        response_clock_tload = core.Clock() #######to determine the start of the visual display so that we can get reaction time of key press
        win.flip()
        t = core.getTime()
        response_time_tload = 0 #to be copy pasted

        while core.getTime() - t < STD:
            keys = event.getKeys()
            if 'q' in keys:
                core.quit()
            if 's' in keys:
                break
            if 'space' in keys:
                R_LETTRE = '1'
                response_time_tload = response_clock_tload.getTime() ######this determines reaction time for space bar press #to be copy pasted
                core.wait(STD - (core.getTime() - t))
                break
            else:
                R_LETTRE = '0'
            core.wait(0.001)
        if R_LETTRE == REPONSE_SERIE[j]: ####correct or incorrect identification
            REPONSE_LETTRE = '1'
            if R_LETTRE == '1':
                correctly_pressed = 1
                correct_incorrect = 'correctly_pressed' ### to be copy pasted
            elif R_LETTRE == '0':
                correctly_ignored = 1
                correct_incorrect = 'correctly_ignored' ### to be copy pasted
        else:
            REPONSE_LETTRE = '0'
            correct_incorrect = 'incorrect' ####to be copy pasted 
            text_stim_wrong = visual.TextStim(win, text=f'{series[j]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
            text_stim_wrong.draw()
            win.flip()
            core.wait(0.3)
        if R_LETTRE + REPONSE_SERIE[j] == 2: ### This is to essentially indicate the correct key presses. So for example a correct no response is coded as 0 here, and anything wrong is also coded as 0 
            trial = '1'
        else:
            trial = '0'
        correctly_pressed_sum = correctly_pressed_sum + correctly_pressed
        correctly_ignored_sum = correctly_ignored_sum + correctly_ignored
        with open(csv_filename_tload, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([block_tload, trial_number, stimuli, correct_incorrect, correct_response, response_time_tload, STD, performance, computer_time_stim, participant_number, sex, age])

#####  the number section
        trial_number += 1 #incremembst trial number #to be copy pasted 
        computer_time_stim = core.getTime() #to be copy pasted 

        num = 0
        n_of_numbers_presented = n_of_numbers_presented + 1 ###this is meant to count the number of numbers presented
        numeros = ['1', '2', '3', '4', '6', '7', '8', '9']
        random.shuffle(numeros)
        stimuli = numeros[0] #to be copy pasted 
        text_stim = visual.TextStim(win, text=f'{numeros[0]}', color=(0, 0, 0), height=100)
        text_stim.draw()
        response_clock_tload = core.Clock() #######to determine the start of the visual display so that we can get reaction time of key press # to be copy pasted 
        response_time_tload = 0 #to be copy pasted
        win.flip()
        t = core.getTime()

        while core.getTime() - t < STD:
            keys2 = event.getKeys(['num_2'])
            keys3 = event.getKeys(['num_3'])
            if keys2:
                R_NUM = keys2
                response_time_tload = response_clock_tload.getTime() ######this determines reaction time for key press #to be copy pasted 
                core.wait(STD - (core.getTime() - t))
                break
            elif keys3:
                R_NUM = keys3
                response_time_tload = response_clock_tload.getTime() ######this determines reaction time for key press#to be copy pasted
                core.wait(STD - (core.getTime() - t))
                break
            else:
                R_NUM = '0'
            core.wait(0.001)

        if int(numeros[num]) % 2 == 1:
            correct_response = 3 #to be copy pasted 
            if keys3:
                REPONSE_NUM = '1' ## meaning correct
                correct_incorrect = 'correct' # to be copy pasted 
            elif keys2:
                REPONSE_NUM = '0' ## meaning incorrect
                correct_incorrect = 'incorrect' # to be copy pasted 
            else:
                REPONSE_NUM = '0' #no response is wrong
                correct_incorrect = 'no_press' #to be copy pasted 

        elif int(numeros[num]) % 2 == 0:
            correct_response = 2 
            if keys2:
                REPONSE_NUM = '1' ## meaning correct
                correct_incorrect = 'correct' #to be copy pasted 
            elif keys3:
                REPONSE_NUM = '0' ## meaning correct
                correct_incorrect = 'incorrect' #to be copy pasted 
            else:
                REPONSE_NUM = '0' #no response is wrong
                correct_incorrect = 'no_press' #to be copy pasted 

                
        if REPONSE_NUM == '0':
            num_stim_wrong = visual.TextStim(win, text=f'{numeros[0]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
            num_stim_wrong.draw()
            win.flip()
            core.wait(0.3)
        elif REPONSE_NUM == '1':
            corect_number_response = corect_number_response + 1
        with open(csv_filename_tload, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([block_tload, trial_number, stimuli, correct_incorrect,correct_response, response_time_tload, STD, performance, computer_time_stim, participant_number, sex, age])
    
    if not skipped:
        correctly_pressed_proportion = correctly_pressed_sum/Should_have_pressed_sum
        correctly_ignored_proportion = correctly_ignored_sum/Should_not_have_pressed_sum
        letter_id_performance = correctly_pressed_proportion*0.65 + correctly_ignored_proportion* 0.35
        number_id_performace = corect_number_response/n_of_numbers_presented #calculates the average identification rate of even or uneven
        performance = letter_id_performance*0.65 + number_id_performace *0.35
        
        ######add here variables for csv file with only performance ### need to add teh code 
        with open(csv_filename_performance, 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([block_tload, performance, STD, computer_time_series, participant_number, sex, age])


        if performance <= 0.85:
            error = error + 1
            if error < 2: 
                break_text.draw()
                win.flip()
                core.wait(12)
                break_text_3 = visual.TextStim(win, text="3...",color=(0, 0, 0), height=100)
                break_text_3.draw()
                win.flip()
                core.wait(1)
                break_text_2 = visual.TextStim(win, text="2...",color=(0, 0, 0), height=100)
                break_text_2.draw()
                win.flip()
                core.wait(1)
                break_text_1 = visual.TextStim(win, text="1...",color=(0, 0, 0), height=100)
                break_text_1.draw()
                win.flip()
                core.wait(1)  
                break_text_GO = visual.TextStim(win, text="GO",color=(0, 0, 0), height=100)
                break_text_GO.draw()
                win.flip()
                core.wait(0.5)
            #event.waitKeys(keyList=['space'])#### will be removed i think , we used to have this but not anymore 
        else: ###### we wanna make it so that if performance is above 96 then -0.3 and if 92 -0.2
            if performance > 0.95:
                STD = STD - 0.1
            STD = STD - 0.1
            error = 0
            break_text.draw()
            win.flip()
            core.wait(12)
            break_text_3 = visual.TextStim(win, text="3...",color=(0, 0, 0), height=100)
            break_text_3.draw()
            win.flip()
            core.wait(1)
            break_text_2 = visual.TextStim(win, text="2...",color=(0, 0, 0), height=100)
            break_text_2.draw()
            win.flip()
            core.wait(1)
            break_text_1 = visual.TextStim(win, text="1...",color=(0, 0, 0), height=100)
            break_text_1.draw()
            win.flip()
            core.wait(1)  
            break_text_GO = visual.TextStim(win, text="GO",color=(0, 0, 0), height=100)
            break_text_GO.draw()
            win.flip()
            core.wait(0.5)
            ####event.waitKeys(keyList=['space']) #maxWait=30 ###can be deleted now 
        if error >= 2:
            STD = STD + 0.1
            break
        

# --- Continuation instructions after break ---
continue_text = visual.TextStim(
    win,
    text="The break is over.\n\nPress SPACE to continue with the task.",
    color='black',
    height=32,
    wrapWidth=900,
    pos=(0, 0)
)

continue_text.draw()
win.flip()
event.waitKeys(keyList=['space'])

  

## ---------------- Questionnaire 1 ----------------

def show_likert_scale_confirm(win, question, options):
    # Horizontal positions in pixels, spread across screen width (e.g., -400 to 400)
    positions = list(np.linspace(-800, 800, len(options)))
    key_labels = [str(i) for i in range(len(options))]
    selected_index = None

    # Question and instruction text
    question_text = visual.TextStim(
        win,
        text=question,
        pos=(0, 250),  # near top of screen
        height=40,
        wrapWidth=900,
        color='black'
    )

    instructions_text = visual.TextStim(
        win,
        text="Press a number key to select a response. \n Press a different number key to change your answer. \nPress Enter to confirm.",
        pos=(0, -250),  # near bottom of screen
        height=20,
        color='gray',
        wrapWidth=900
    )

    while True:
        question_text.draw()
        instructions_text.draw()

        # Draw response options
        for i, (label, key, x) in enumerate(zip(options, key_labels, positions)):
            if selected_index == i:
                color = 'red'
                size = 30  # selected size
            else:
                color = 'black'
                size = 24  # default size

            scale_label = visual.TextStim(
                win,
                text=label,
                pos=(x, -100),  # answer labels
                height=size,
                color=color,
                wrapWidth=300
            )

            key_label = visual.TextStim(
                win,
                text=f"({key})",
                pos=(x, -140),  # keys below label
                height=30,
                color=color
            )

            scale_label.draw()
            key_label.draw()

        win.flip()

        keys = event.waitKeys()
        for key in keys:
            if key in ['q']:
                win.close()
                core.quit()

            if key.startswith('num_'):
                key = key[-1]  # convert numpad input

            if key in key_labels:
                selected_index = int(key)
            
            elif key == 's':  # Skip the entire segment
                response = 'skipped'
                return response
                
            elif key in ['return', 'num_enter'] and selected_index is not None:
                return selected_index

    return response
def show_number_input_confirm(win, question, min_val=0, max_val=100, allow_decimal=True):
    """Numeric text entry with Enter confirm, backspace edit, 'q' quit, 's' skip.
       Returns a float (or int if whole number), or the string 'skipped' if skipped.
    """
    typed = ""
    confirmed = False
    feedback_timer = 0.0  # seconds left to show feedback
    clock = core.Clock()

    question_text = visual.TextStim(
        win, text=question, pos=(0, 250), height=40, wrapWidth=900, color='black'
    )
    instructions_text = visual.TextStim(
        win,
        text=f"Type a number between {min_val} and {max_val}. "
             "Use BACKSPACE to correct. Press ENTER to confirm.\n"
             "Press 's' to skip this question.",
        pos=(0, -250), height=20, color='gray', wrapWidth=900
    )
    input_display = visual.TextStim(
        win, text="", pos=(0, -50), height=60, color='blue'
    )
    feedback_text = visual.TextStim(
        win, text="", pos=(0, -120), height=28, color='red'
    )

    def _normalize_key(k):
        # map numpad keys like 'num_1' -> '1', 'num_period' -> '.'
        if k.startswith('num_'):
            tail = k[4:]
            return '.' if tail in ('period', 'decimal') else tail
        return k

    while not confirmed:
        # Draw UI
        question_text.draw()
        instructions_text.draw()
        input_display.text = typed if typed != "" else "—"
        input_display.draw()

        # Show feedback briefly
        if feedback_timer > 0:
            feedback_text.draw()
            feedback_timer -= clock.getTime()
        clock.reset()
        win.flip()

        keys = event.waitKeys()
        for key in keys:
            key = _normalize_key(key)

            if key == 'q':
                win.close(); core.quit()

            if key == 's':
                return 'skipped'

            if key in ('return', 'enter'):
                if typed != "":
                    # validate range & format
                    try:
                        val = float(typed)
                        if min_val <= val <= max_val:
                            # cast to int if whole number
                            if val.is_integer():
                                return int(val)
                            else:
                                return val
                        else:
                            feedback_text.text = f"Please enter a value between {min_val} and {max_val}."
                            feedback_timer = 1.0
                    except ValueError:
                        feedback_text.text = "Invalid number. Please type digits (and a decimal point if needed)."
                        feedback_timer = 1.0
                else:
                    feedback_text.text = "Please type a value first."
                    feedback_timer = 0.8

            elif key == 'backspace':
                typed = typed[:-1]

            elif key in ('.', 'period'):
                if allow_decimal and '.' not in typed:
                    typed += '.'

            elif key.isdigit():
                typed += key

            # ignore all other keys

    # Fallback (should never hit because we return on confirm/skip)
    return None


block_q = 1
questionnaire_results = []

# Define VASF and emotional items in separate blocks
vasf_questions = [
     #("PM1", "How much do you feel in charge right now?"), #after power
     # Fatigue VAS-F
    ("FAT1", "How tired do you feel right now?"),
    ("FAT2", "How fatigued do you feel right now?"),
    ("FAT3", "How exhausted do you feel right now?"),
    ("FAT4", "How effortful does concentrating feel right now?"),
]

accu_questions = [
     #("PM1", "How much do you feel in charge right now?"), #after power
     # Fatigue VAS-F
    ("ACC1", "What accuracy would you give yourself? (0-100, choose in steps of 10)"),
    ("ACC2", "What accuracy level would you give the other person? (0-100, choose in steps of 10)"),
]


#I think, open questions only needs to happen after in loop, power q only needs to happen after power and then in loop
emo_questions = [
    # Boredom / Task Switching / Flow
    ("BOR1", "How much do you wish you were doing something else?"),
    ("BOR2", "How much do you feel you are wasting time that would be better spent on something else?"),
    ("BOR3", "Did you lose awareness of yourself as separate from the activity?"),
    ("BOR4", "How much do you want to quit right now?"),
    ("BOR5", "How meaningful does the task feel to you?"),
    
    # Effort
    
    ("EFF1", "How effortful was the task for you?"),
    ("EFF2", "How much effort did you put into the task?")
    ("EFF3", "Please rate your mental effort required to complete this task.") #in tload loop
    ("EFF4", "How did this effort feel?") #in tload loop
]


questions_open = [
    ("TIME1", "How long do you think the T-Task Block lasted in Seconds? \n
    "Please type below and confirm by pressing enter."), #in tload loop
]

questions_open2 = [
    ("TIME2", "Did you experience time passing differently?") #in tload loop
]

power_question = [
     ("PM1", "How much do you feel in charge right now?"), #after power
]



#write outputs to file
    
##########################
# VASF Scale (0–9)
##########################

vasf_options = [f"{i} = Not at all" if i == 0 else f"{i} = Very much" if i == 9 else str(i) for i in range(10)]
open2_options = [f"{i} = Slower" if i == 0 else f"{i} = Faster" if i == 9 else str(i) for i in range(10)]
power_options = [f"{i} = Not at all" if i == 0 else f"{i} = Very much" if i == 9 else str(i) for i in range(10)]
accu_options = [f"{i}% = Not at all accurate" if i == 0 else f"{i}% = Perfectly accurate" if i == 100 else f"{i}%"for i in range(0, 101, 5)]
emo_options = [
    "Strongly Disagree",
    "Disagree",
    "Somewhat Disagree",
    "Neutral",
    "Somewhat Agree",
    "Agree",
    "Strongly Agree"
]


for code, prompt in vasf_questions:
    win.flip()  # blank screen
    core.wait(0.01)
    rating = show_likert_scale_confirm(
        win=win,
        question=prompt,
        options=vasf_options
    )
    questionnaire_results.append((code, rating))


  

# ------------ SAVE RESULTS Questionnaires ------------- # I need to later make sure the questionnaires create new files each time or keep writing in one file
with open(csv_filename_survey, 'a', newline='') as questionnaire_file:
    csv_writer = csv.writer(questionnaire_file)
    for code, rating in questionnaire_results:
        csv_writer.writerow([participant_number, sex, age, code, rating, block_q])
              

# End Screen
end_questionnaire_text = visual.TextStim(
    win,
    text="Thank you!\nPress SPACE to continue to the next task.",
    color='black',
    height=65,
    pos=(0, 0),
    units='pix'
)

end_questionnaire_text.draw()
win.flip()
event.waitKeys(keyList=['space'])


############################################################
############Power Manipulation + Question about Power ##############
############################################################

instructions_text = visual.TextStim(
    win=win,
    text=(
        "You will now get the chance to double your reward.\n\n"
        "This will work like this:\n"
        "You will be paired with another participant. You will be leader or follower.\n\n"
        "If you are Leader, you decide for yourself and for the other how accurate you and they "
        "will have to score on the T-task to double your reward. You can choose between 10% to 100%.\n\n"
        "If you are follower, you don’t decide. Your leader will have decided for you.\n\n"
        "In the next screen, you will learn whether you were drawn to be leader or follower."
    ),
    pos=(0, 0),           # centered on screen
    height=24,            # 24 pixels per line (adjust for readability)
    wrapWidth=1000,       # line breaks at ~1000 pixels width
    color='white',
    alignText='center',   # center the text block
    units='pix'
)


instructions_text.draw()
win.flip()
event.waitKeys(keyList=['return'])  # wait for space to continue


for code, prompt in question_power:
        win.flip()  # blank screen
        core.wait(0.01)
        rating = show_likert_scale_confirm(
            win=win,
            question=prompt,
            options=power_options
        )
        questionnaire_results.append((code, rating)) 



for code, prompt in accu_questions:
        win.flip()  # blank screen
        core.wait(0.01)
        rating = show_likert_scale_confirm(
            win=win,
            question=prompt,
            options=accu_options
        )
        questionnaire_results.append((code, rating)) 

    with open(csv_filename_survey, 'a', newline='') as questionnaire_file:
        csv_writer = csv.writer(questionnaire_file)
        for code, rating in questionnaire_results:
            csv_writer.writerow([participant_number, sex, age, code, rating, block_q])

############################################################
############Loop repeating 5 min Tload + Questionnaires +SPD
############################################################




blocksmid = 3
block_num = 0

item_number = 0 ##### we want this to go all the way up to 16 and be the number of rows in our survey csv file. 
block_tload = 0 #these are not rechnically needed
win.mouseVisible = False

for i in range (blocksmid):
    
    Tload_Start_text = visual.TextStim(
        win,
        text="You will now continue to the Numbers and Letters task.\n\n"
             "Press Space to start the task.",
        color='black',
        height=40,
        wrapWidth=1000,
        pos=(0, 0)
    )
    Tload_Start_text.draw()
    win.flip()
    event.waitKeys(keyList=['space'])
    
    block_num +=1
    block_tload += 1 #might not need these later


    next_block = visual.TextStim(win, text=f'The Number and Letter task will start in:', pos=(0, 80), color=(0, 0, 0), height=30)
    break_text_3 = visual.TextStim(win, text="3...",pos=(0, -80), color=(0, 0, 0), height=100)
    break_text_3.draw()
    next_block.draw()
    win.flip()
    core.wait(1)
    break_text_2 = visual.TextStim(win, text="2...",pos=(0, -80),color=(0, 0, 0), height=100)
    break_text_2.draw()
    next_block.draw()
    win.flip()
    core.wait(1)
    break_text_1 = visual.TextStim(win, text="1...",pos=(0, -80),color=(0, 0, 0), height=100)
    break_text_1.draw()
    next_block.draw()
    win.flip()
    core.wait(1)  
    break_text_GO = visual.TextStim(win, text="GO",color=(0, 0, 0), height=100)
    break_text_GO.draw()
    win.flip()
    core.wait(0.5)
        
    
    R_LETTRE = 99
    
    block_duration = 10 #300  # 5 minutes
    block_clock = core.Clock()
    event.clearEvents(eventType='keyboard')


    while block_clock.getTime() < block_duration:
        #block_tload = block_tload + 1
        computer_time_series = core.getTime() ##to be copy pasted
        
        keys = event.getKeys()
        if 'q' in keys:
            core.quit()
        if 's' in keys:
            break
        
        #randorder = np.random.permutation(20)
        randorder = np.random.permutation(len(series_all)) 
        for idx in randorder:
            if block_clock.getTime() >= block_duration:
                break
            series = series_all[idx]
            REPONSE_SERIE = REPONSE_ALL[idx]
            
            
            series = series_all[randorder[0]]
            REPONSE_SERIE = REPONSE_ALL[randorder[0]]
            Should_have_pressed_sum = sum(int(num) for num in REPONSE_SERIE)
            Should_not_have_pressed_sum = len(REPONSE_SERIE)-Should_have_pressed_sum
            correctly_pressed_sum = 0
            correctly_ignored_sum = 0
            n_of_numbers_presented = 0 #keeps track of number of digits that are presented
            corect_number_response = 0 #keeps track of number of correctly identified even or uneven
            trial_number = 0 #initializes variable (used in csv file) #to be copy pasted
            
            for j in range(len(series)):
                if block_clock.getTime() >= block_duration:
                    break
                    
                trial_number += 1 #incremembst trial number #to be copy pasted
                
                
                computer_time_stim = core.getTime() #to be copy pasted
                
                stimuli = series[j] #### for csv file to save the stimuli # to be copy pasted
                correct_response = REPONSE_SERIE[j] #to be copy pasted 
                correctly_pressed = 0 
                correctly_ignored = 0

                text_stim = visual.TextStim(win, text=f'{series[j]}', color=(0, 0, 0), height=100)
                text_stim.draw()
                win.flip()
                t = core.getTime()
                response_clock_tload = core.Clock()
                response_time_tload = 0 #to be copy pasted
        
                while core.getTime() - t < STD:
                    keys = event.getKeys()
                    if 'q' in keys:
                        core.quit()
                    if 'space' in keys:
                        R_LETTRE = '1'
                        response_time_tload = response_clock_tload.getTime() ######this determines reaction time for space bar press #to be copy pasted
                        core.wait(STD - (core.getTime() - t))
                        break
                    else:
                        R_LETTRE = '0'
                    core.wait(0.001)
                if R_LETTRE == REPONSE_SERIE[j]: ####correct or incorrect identification
                    REPONSE_LETTRE = '1'
                    if R_LETTRE == '1':
                        correctly_pressed = 1
                        correct_incorrect = 'correctly_pressed' ### to be copy pasted
                    elif R_LETTRE == '0':
                        correctly_ignored = 1
                        correct_incorrect = 'correctly_ignored' ### to be copy pasted
                else:
                    REPONSE_LETTRE = '0'
                    correct_incorrect = 'incorrect' ####to be copy pasted 
                    text_stim_wrong = visual.TextStim(win, text=f'{series[j]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
                    text_stim_wrong.draw()
                    win.flip()
                    core.wait(0.3)
                if R_LETTRE + REPONSE_SERIE[j] == 2: ### This is to essentially indicate the correct key presses. So for example a correct no response is coded as 0 here, and anything wrong is also coded as 0 
                    trial = '1'
                else:
                    trial = '0'
                correctly_pressed_sum = correctly_pressed_sum + correctly_pressed
                correctly_ignored_sum = correctly_ignored_sum + correctly_ignored
                with open(csv_filename_tload, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow([block_tload, trial_number, stimuli, correct_incorrect, correct_response, response_time_tload, STD, performance, computer_time_stim, participant_number, sex, age, "letter"])

        #####  the number section
                trial_number += 1 #incremembst trial number #to be copy pasted 
                computer_time_stim = core.getTime() #to be copy pasted 
                num = 0
                n_of_numbers_presented = n_of_numbers_presented + 1 ###this is meant to count the number of numbers presented
                numeros = ['1', '2', '3', '4', '6', '7', '8', '9']
                random.shuffle(numeros)
                stimuli = numeros[0] #to be copy pasted 
        
                text_stim = visual.TextStim(win, text=f'{numeros[0]}', color=(0, 0, 0), height=100)
                text_stim.draw()
                response_clock_tload = core.Clock() #######to determine the start of the visual display so that we can get reaction time of key press # to be copy pasted 
                response_time_tload = 0 #to be copy pasted
                win.flip()
                t = core.getTime()
        
                while core.getTime() - t < STD:
                    keys2 = event.getKeys(['num_2'])
                    keys3 = event.getKeys(['num_3'])
                    if keys2:
                        R_NUM = keys2
                        response_time_tload = response_clock_tload.getTime() ######this determines reaction time for key press #to be copy pasted 
                        core.wait(STD - (core.getTime() - t))
                        break
                    elif keys3:
                        R_NUM = keys3
                        response_time_tload = response_clock_tload.getTime() ######this determines reaction time for key press#to be copy pasted
                        core.wait(STD - (core.getTime() - t))
                        break
                    else:
                        R_NUM = '0'
                    core.wait(0.001)
                if int(numeros[num]) % 2 == 1:
                    correct_response = 3 #to be copy pasted 
                    if keys3:
                        REPONSE_NUM = '1' ## meaning correct
                        correct_incorrect = 'correct' # to be copy pasted 
                    elif keys2:
                        REPONSE_NUM = '0' ## meaning incorrect
                        correct_incorrect = 'incorrect' # to be copy pasted 
                    else:
                        REPONSE_NUM = '0' #no response is wrong
                        correct_incorrect = 'no_press' #to be copy pasted 
        
        
                elif int(numeros[num]) % 2 == 0:
                    correct_response = 2 
                    if keys2:
                        REPONSE_NUM = '1' ## meaning correct
                        correct_incorrect = 'correct' #to be copy pasted 
                    elif keys3:
                        REPONSE_NUM = '0' ## meaning correct
                        correct_incorrect = 'incorrect' #to be copy pasted 
                    else:
                        REPONSE_NUM = '0' #no response is wrong
                        correct_incorrect = 'no_press' #to be copy pasted 
        
                        
                if REPONSE_NUM == '0':
                    num_stim_wrong = visual.TextStim(win, text=f'{numeros[0]}', color=(1, 0, 0), height=100) ####this is added for ease of understanding can be removed
                    num_stim_wrong.draw()
                    win.flip()
                    core.wait(0.3)
                elif REPONSE_NUM == '1':
                    corect_number_response = corect_number_response + 1
                
                
                
                
                with open(csv_filename_tload, 'a', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow([block_tload,trial_number, stimuli, correct_incorrect,correct_response, response_time_tload, STD, performance, computer_time_stim,participant_number, sex, age, "number"])
            
            correctly_pressed_proportion = correctly_pressed_sum/Should_have_pressed_sum
            correctly_ignored_proportion = correctly_ignored_sum/Should_not_have_pressed_sum
            letter_id_performance = correctly_pressed_proportion*0.65 + correctly_ignored_proportion* 0.35
            number_id_performace = corect_number_response/n_of_numbers_presented #calculates the average identification rate of even or uneven
            performance = letter_id_performance*0.65 + number_id_performace *0.35
            
            ######add here variables for csv file with only performance ### need to add teh code 
            with open(csv_filename_performance, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([block_tload, performance, STD, computer_time_series,participant_number, sex, age])


    ###########Starting Questionnaire######################################

    toquestcon = visual.TextStim(
        win,
        text=(
            "You will now be asked a few questions.\n\n"
            "Please select an answer by pressing a number,\n"
            "and confirm your choice by pressing the SPACE key.\n\n"
            "Press SPACE to continue."
        ),
        color='black',
        height=32,
        wrapWidth=900,
        pos=(0, 0)
    )
    toquestcon.draw()
    win.flip()
    event.waitKeys(keyList=['space'])  # restrict to space to make intention clear




    # === INSERT QUESTIONNAIRE AFTER EACH BLOCK ===
    questionnaire_results = []
    block_q = block_q+1

    for code, prompt in vasf_questions:
        win.flip()  # blank screen
        core.wait(0.01)
        rating = show_likert_scale_confirm(
            win=win,
            question=prompt,
            options=vasf_options
        )
        questionnaire_results.append((code, rating))
        
    for code, prompt in emo_questions:
        win.flip()  # blank screen
        core.wait(0.01)
        rating = show_likert_scale_confirm(
            win=win,
            question=prompt,
            options=emo_options
        )
        questionnaire_results.append((code, rating))
        
       for code, prompt in questions_open2:
        win.flip()  # blank screen
        core.wait(0.01)
        rating = show_likert_scale_confirm(
            win=win,
            question=prompt,
            options=open2_options
        )
        questionnaire_results.append((code, rating)) 
        
        for code, prompt in question_power:
        win.flip()  # blank screen
        core.wait(0.01)
        rating = show_likert_scale_confirm(
            win=win,
            question=prompt,
            options=power_options
        )
        questionnaire_results.append((code, rating)) 
    
        
        for code, prompt in questions_open:
            win.flip(); core.wait(0.01)
            val = show_number_input_confirm(
                win=win,
                question=prompt,
                min_val=0,
                max_val=100,
                allow_decimal=True
            )
        questionnaire_results.append((code, val))

        

    with open(csv_filename_survey, 'a', newline='') as questionnaire_file:
        csv_writer = csv.writer(questionnaire_file)
        for code, rating in questionnaire_results:
            csv_writer.writerow([participant_number, sex, age, code, rating, block_q])

    # === AFTER emo_questions loop, BEFORE writing questionnaire_results to your CSV ===
    pair = sample_tf_pair(cond_label, used_idxs)  # cond_label is "abstract" or "concrete" from the dialog

    for stmt_text, truth_label in pair:
        chosen_answer, choice_rt, confirm_rt, explanation_text = run_true_false_trial(
            win=win,
            statement=stmt_text,
            ground_truth=truth_label
        )
        # Log immediately
        with open(csv_filename_tf, 'a', newline='') as f:
            w = csv.writer(f)
            w.writerow([
                participant_number, sex, age, block_q,
                cond_label, stmt_text, truth_label,
                chosen_answer, choice_rt, confirm_rt,
                explanation_text, core.getTime()
            ])



# End screen
end_txt2 = visual.TextStim(
    win,
    text=f"Thank you for participating!\n\nYou finished the study .",
    color='black',
    height=50
)

end_txt2.draw()
win.flip()
event.waitKeys()
win.close()
core.quit()