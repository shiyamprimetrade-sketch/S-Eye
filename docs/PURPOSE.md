# Purpose: give S an eye

S is the autonomous programming computer. S-Eye is its visual subsystem for
observing another computer while S develops, researches or designs. The goal is
useful visual feedback in a working perception–decision–action loop, rather than
an expanding catalogue of disconnected shape demonstrations.

| Component | Responsibility |
| --- | --- |
| S-Eye | Observe frames, localize supported visual evidence, compare state, record and return signals |
| S | Interpret evidence with its programming/task context and choose the next action |
| S-Tools / host adapter | Supply authorized screenshots and execute authorized mouse/keyboard actions |
| S-Memory integration | Retain/retrieve grounded observations through the defined adapters |

The current integration uses `observe_interface` JSON. A caller can provide a
previous frame, named visual template crops and an optional memory destination.
Responses include source identity, screen dimensions, candidate boxes, change
signals, ambiguity/absence and limitations. A supplied template name is provenance
from S, not a semantic label independently inferred by S-Eye.

Keep this contract small. Add capabilities only when they improve the loop and
can be tested: text reading, unfamiliar control detection, scrolling/viewpoint
correspondence, state history and visual outcome verification. Preserve original
algorithms as measurable comparators and keep explicit uncertainty when evidence
is insufficient. Human review is not required for ordinary engineering progress.

"Works perfectly" is a quality goal, not a measured property. Each claimed feature
needs executable tests, defined supported conditions and reproducible failures.
Synthetic screenshots provide automatic test truth; they do not establish reliable
operation in arbitrary applications. S-Eye does not currently provide complete
OCR/code comprehension, live desktop capture, input automation or general-purpose
human expert vision. Do not advertise those as implemented before evidence exists.
