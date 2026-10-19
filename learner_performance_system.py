"""
Learner Performance Tracker
===========================
Reads learner records from a CSV file, works out each learner's mean score and
letter grade, checks bursary qualification and prints a performance report.

OOP ideas used
--------------
* Encapsulation  - hidden score book (__score_book), properties, checked setters
* Abstraction    - LearnerRecord is an abstract class with an abstract method
* Inheritance    - LearnerRecord -> StandardLearner -> BursaryLearner
* Composition    - ClassPerformanceAnalyzer works on the learner objects it is given
* Polymorphism   - summary_line() / build_report() differ for each learner type
* Overriding     - BursaryLearner replaces summary_line() and build_report()
* Overloading    - compute_mean(*scores) accepts a flexible number of scores
"""

import csv
from abc import ABC, abstractmethod

# ----------------------------------------------------------------------
# Settings
# ----------------------------------------------------------------------
SUBJECT_COLUMNS = ("Math", "English", "Science")
BURSARY_CUTOFF = 85          # mean score needed to qualify for a bursary
LOWEST_SCORE = 0
HIGHEST_SCORE = 100


# ======================================================================
# Abstract base class
# ======================================================================
class LearnerRecord(ABC):
    """Abstract parent for all learners. Cannot be created directly."""

    def __init__(self, learner_id, given_name, family_name, course, scores):
        self._learner_id = learner_id        # protected attributes
        self._given_name = given_name
        self._family_name = family_name
        self._course = course

        self.__score_book = {}               # private attribute (name mangled)
        for subject, score in scores.items():
            self.update_score(subject, score)

    # ---------------- read-only properties ----------------
    @property
    def learner_id(self):
        return self._learner_id

    @property
    def display_name(self):
        return f"{self._given_name} {self._family_name}"

    @property
    def course(self):
        return self._course

    @course.setter
    def course(self, new_course):
        if not str(new_course).strip():
            raise ValueError("Course name cannot be blank.")
        self._course = str(new_course).strip()

    # ---------------- controlled access to scores ----------------
    @staticmethod
    def _check_score(score):
        """Return a valid score as a float or raise an error."""
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError(f"Score must be numeric, received {score!r}.")
        if not LOWEST_SCORE <= score <= HIGHEST_SCORE:
            raise ValueError(
                f"Score must be within {LOWEST_SCORE}-{HIGHEST_SCORE}, received {score}.")
        return float(score)

    def update_score(self, subject, score):
        """Add a new subject score or change an existing one."""
        self.__score_book[subject] = self._check_score(score)

    def score_for(self, subject):
        return self.__score_book[subject]

    def all_scores(self):
        """Give back a copy so the private data stays protected."""
        return dict(self.__score_book)

    # ---------------- flexible method (overloading equivalent) ----------------
    def compute_mean(self, *scores):
        """Mean of the given scores.

        compute_mean()               -> mean of this learner's own scores
        compute_mean(70, 80, 90)     -> mean of three scores passed separately
        compute_mean(50, 60, 70, 80) -> mean of any number of scores
        """
        if not scores:
            scores = tuple(self.__score_book.values())
        if not scores:
            raise ValueError("There are no scores to average.")
        checked = [self._check_score(s) for s in scores]
        return sum(checked) / len(checked)

    @property
    def mean_score(self):
        return self.compute_mean()

    def letter_grade(self):
        """Convert the mean score to a letter."""
        mean = self.mean_score
        if mean >= 80:
            return "A"
        elif mean >= 70:
            return "B"
        elif mean >= 60:
            return "C"
        elif mean >= 50:
            return "D"
        return "F"

    # ---------------- abstract method ----------------
    @abstractmethod
    def summary_line(self):
        """Each learner type must describe itself."""

    # ---------------- report for one learner ----------------
    def build_report(self):
        score_text = ", ".join(f"{sub}: {val:.0f}" for sub, val in self.all_scores().items())
        return (
            f"ID: {self.learner_id}   Name: {self.display_name}\n"
            f"Programme: {self.course}\n"
            f"Scores: {score_text}\n"
            f"Mean: {self.mean_score:.2f}   Grade: {self.letter_grade()}\n"
            f"Category: {self.summary_line()}"
        )

    def __str__(self):
        return f"{self.learner_id} {self.display_name} - {self.mean_score:.2f} ({self.letter_grade()})"


# ======================================================================
# Concrete learner types
# ======================================================================
class StandardLearner(LearnerRecord):
    """A learner without a bursary."""

    def summary_line(self):
        return "Standard learner - no bursary"


class BursaryLearner(StandardLearner):
    """A learner who has a bursary attached to their record."""

    def __init__(self, learner_id, given_name, family_name, course, scores, bursary_amount=0):
        super().__init__(learner_id, given_name, family_name, course, scores)
        self.bursary_amount = bursary_amount

    @property
    def bursary_amount(self):
        return self._bursary_amount

    @bursary_amount.setter
    def bursary_amount(self, value):
        if value < 0:
            raise ValueError("Bursary amount cannot be negative.")
        self._bursary_amount = value

    def qualifies(self):
        """True if the mean score reaches the bursary cut-off."""
        return self.mean_score >= BURSARY_CUTOFF

    # Overridden behaviour
    def summary_line(self):
        verdict = "QUALIFIES" if self.qualifies() else "does NOT qualify"
        return f"Bursary learner - {verdict} (KES {self.bursary_amount:,.0f})"

    def build_report(self):
        text = super().build_report()
        return text + f"\nBursary status: {'Qualified' if self.qualifies() else 'Not qualified'}"


# ======================================================================
# Analyzer (composition)
# ======================================================================
class ClassPerformanceAnalyzer:
    """Works out class statistics from a collection of learner objects."""

    def __init__(self, learners):
        if not learners:
            raise ValueError("Provide at least one learner.")
        self._learners = list(learners)

    def top_learner(self):
        return max(self._learners, key=lambda l: l.mean_score)

    def bottom_learner(self):
        return min(self._learners, key=lambda l: l.mean_score)

    def class_mean(self):
        return sum(l.mean_score for l in self._learners) / len(self._learners)

    def qualified_learners(self):
        return [l for l in self._learners
                if isinstance(l, BursaryLearner) and l.qualifies()]

    def build_report(self):
        border = "#" * 62
        lines = [border, "LEARNER PERFORMANCE REPORT".center(62), border]
        for learner in self._learners:
            lines.append(learner.build_report())      # polymorphic call
            lines.append("." * 62)

        top, bottom = self.top_learner(), self.bottom_learner()
        winners = self.qualified_learners()
        lines += [
            "CLASS SUMMARY".center(62),
            border,
            f"Number of learners : {len(self._learners)}",
            f"Highest mean       : {top.mean_score:.2f} - {top.display_name}",
            f"Lowest mean        : {bottom.mean_score:.2f} - {bottom.display_name}",
            f"Class mean         : {self.class_mean():.2f}",
            f"Bursary qualifiers : {len(winners)} "
            f"({', '.join(w.display_name for w in winners) or 'none'})",
            border,
        ]
        return "\n".join(lines)


# ======================================================================
# CSV loading
# ======================================================================
def read_learners(file_name):
    """Create learner objects from the CSV file."""
    learners = []
    with open(file_name, newline="", encoding="utf-8") as handle:
        for line_no, row in enumerate(csv.DictReader(handle), start=2):
            try:
                scores = {sub: float(row[sub]) for sub in SUBJECT_COLUMNS}
                bursary = float(row.get("BursaryAmount") or 0)
                core = (row["StudentID"], row["FName"], row["LName"], row["Programme"], scores)
                if bursary > 0:
                    learners.append(BursaryLearner(*core, bursary_amount=bursary))
                else:
                    learners.append(StandardLearner(*core))
            except (KeyError, ValueError, TypeError) as err:
                print(f"Ignoring CSV line {line_no}: {err}")
    return learners


# ======================================================================
# Demonstrations
# ======================================================================
def show_polymorphism(learners):
    print("\nPOLYMORPHISM - one method name, different results")
    print("-" * 62)
    for learner in learners:
        print(f"{type(learner).__name__:<16} {learner.display_name:<16} {learner.summary_line()}")


def show_flexible_method(learner):
    print("\nFLEXIBLE METHOD - compute_mean()")
    print("-" * 62)
    print("No arguments       :", f"{learner.compute_mean():.2f}")
    print("Three scores       :", f"{learner.compute_mean(60, 75, 90):.2f}")
    print("Six scores         :", f"{learner.compute_mean(50, 60, 70, 80, 90, 100):.2f}")
    try:
        learner.compute_mean(80, -5)
    except ValueError as err:
        print("Out of range       :", err)
    try:
        learner.compute_mean(80, None)
    except TypeError as err:
        print("Wrong data type    :", err)


def main():
    learners = read_learners("learners.csv")
    analyzer = ClassPerformanceAnalyzer(learners)

    report = analyzer.build_report()
    print(report)

    show_polymorphism(learners)
    show_flexible_method(learners[0])

    with open("learner_report.txt", "w", encoding="utf-8") as out_file:
        out_file.write(report)
    print("\nReport saved to learner_report.txt")


if __name__ == "__main__":
    main()
