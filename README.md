class Student:
    """Represents one student and their exam scores."""

    def __init__(self, name: str, reg_number: str, scores: list[float]):
        self.name = name
        self.reg_number = reg_number
        self.scores = scores

    def calculate_average(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores) / len(self.scores)

    def classify_result(self) -> str:
        average = self.calculate_average()
        if average >= 80:
            return "Distinction"
        elif average >= 70:
            return "Credit"
        elif average >= 50:
            return "Pass"
        else:
            return "Fail"

    def __str__(self) -> str:
        avg = self.calculate_average()
        result = self.classify_result()
        return (f"{self.reg_number} | {self.name:<20} "
                f"| Average: {avg:6.2f} | Result: {result}")
