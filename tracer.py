import json
import time
import os
from datetime import datetime

class SimpleTracer:
    """
    A simple tracer for logging LLM interactions and agent steps.
    """
    def __init__(self, trace_file="trace.json"):
        self.trace_file = trace_file
        self.traces = []
        # Ensure the directory exists
        os.makedirs(os.path.dirname(trace_file) if os.path.dirname(trace_file) else '.', exist_ok=True)

    def log_event(self, event_type, data):
        """
        Log a single event to the trace.
        
        Args:
            event_type (str): The type of event (e.g., "llm_call", "tool_use").
            data (dict): The data associated with the event.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.traces.append(event)
        # Auto-save for convenience
        self.save()

    def save(self):
        """
        Save the traces to the JSON file.
        """
        with open(self.trace_file, 'w') as f:
            json.dump(self.traces, f, indent=2)

    def load(self):
        """
        Load traces from the file.
        """
        if os.path.exists(self.trace_file):
            with open(self.trace_file, 'r') as f:
                self.traces = json.load(f)
        return self.traces

    def clear(self):
        """Clear existing traces"""
        self.traces = []
        if os.path.exists(self.trace_file):
            os.remove(self.trace_file)