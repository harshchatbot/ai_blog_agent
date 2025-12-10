# llm_metrics.py

class LLMMetrics:
    def __init__(self):
        self.call_count = 0

    def register_call(self, label: str = ""):
        """Increment call counter and optionally log a label."""
        self.call_count += 1
        if label:
            print(f"[LLM] Call #{self.call_count} → {label}")
        else:
            print(f"[LLM] Call #{self.call_count}")

    def summary(self) -> str:
        return f"Total LLM calls this run: {self.call_count}"


metrics = LLMMetrics()
