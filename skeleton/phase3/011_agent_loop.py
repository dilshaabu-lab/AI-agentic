import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient
from utils.tools import web_search, calculator
from utils.tracer import SimpleTracer


def agent_loop(question, max_iterations=5):

    trace_path = os.path.join(
        os.path.dirname(__file__),
        "../../data/traces/agent_loop_tracing.json"
    )

    tracer = SimpleTracer(trace_path)
    tracer.clear()

    client = LLMClient()

    prompt = f"""
Answer the question using tools: [WEB_SEARCH, CALCULATOR].
Format:
Question: {question}
Thought: ...
Action: TOOL_NAME
Action Input: INPUT
Observation: RESULT
...
Final Answer: RESULT

Begin!
Question: {question}
"""

    history = prompt

    # -------- start trace --------
    tracer.log_event("start", {
        "question": question,
        "max_iterations": max_iterations
    })

    # BUG: while True with no step limit — can run forever if LLM never says "Final Answer:"
    # while True:
    #     print("\n--- Iteration (no bound) ---")

    #     # 1. Generate
    #     response = client.get_completion(history, stop=["Observation:"])
    #     print(f"LLM: {response}")
    #     history += response

    #     # 2. Check for Final Answer
    #     if "Final Answer:" in response:
    #         return response.split("Final Answer:")[-1].strip()

    #     # 3. Parse Action
    #     action_match = re.search(r"Action: (.*)", response)
    #     input_match = re.search(r"Action Input: (.*)", response)

    #     if action_match and input_match:
    #         tool = action_match.group(1).strip()
    #         arg = input_match.group(1).strip()

    #         # 4. Execute
    #         observation = f"Error: Tool {tool} not found"
    #         if tool == "WEB_SEARCH":
    #             observation = web_search(arg)
    #         elif tool == "CALCULATOR":
    #             observation = calculator(arg)

    #         print(f"Observation: {observation}")

    #         # 5. Update History
    #         history += f"\nObservation: {observation}\n"
    #     else:
    #         print("No action detected. Ending.")
    #         break

    # return "No answer found."


# =============================================================================
# FIX (uncomment and apply to prevent infinite loop):
# =============================================================================
#
# 1. Replace the unbounded loop with a bounded one and track the step count:

    for i in range(max_iterations):
        print(f"\n--- Iteration {i+1} ---")

        response = client.get_completion(history)
        print(f"LLM: {response}")

        history += response

        step_trace = {
            "step": i + 1,
            "llm_output": response,
            "parsed_action": None,
            "observation": None
        }

        # -------- Final answer check --------
        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[-1].strip()

            tracer.log_event("step", step_trace)

            tracer.log_event("end", {
                "stop_reason": "final_answer_detected",
                "final_answer": final_answer
            })

            return final_answer

        # -------- Parse Action --------
        action_match = re.search(r"Action:\s*(.*)", response)
        input_match = re.search(r"Action Input:\s*(.*)", response)

        if action_match and input_match:
            tool = action_match.group(1).strip()
            arg = input_match.group(1).strip()

            observation = f"Error: Tool {tool} not found"

            if tool == "WEB_SEARCH":
                observation = web_search(arg)
            elif tool == "CALCULATOR":
                observation = calculator(arg)

            print(f"Observation: {observation}")

            step_trace["parsed_action"] = {
                "tool": tool,
                "input": arg
            }
            step_trace["observation"] = observation

            history += f"\nObservation: {observation}\n"

            tracer.log_event("step", step_trace)

        else:
            print("No action detected. Ending.")

            tracer.log_event("step", step_trace)

            tracer.log_event("end", {
                "stop_reason": "no_action_detected"
            })

            return "No answer found."

    # -------- max iterations reached --------
    tracer.log_event("end", {
        "stop_reason": "max_iterations_reached"
    })

    return "No answer found."


if __name__ == "__main__":
    print(agent_loop("what is 100*24"))




# import sys
# import os
# import re

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# from utils.llm_client import LLMClient
# from utils.tools import web_search, calculator
# from utils.tracer import SimpleTracer


# def agent_loop(question, max_iterations=5):

#     trace_path = os.path.join(
#         os.path.dirname(__file__),
#         "../../data/traces/agent_loop_tracing.json"
#     )

#     tracer = SimpleTracer(trace_path)
#     tracer.clear()

#     client = LLMClient()

#     prompt = f"""
# Answer the question using tools: [WEB_SEARCH, CALCULATOR].
# Format:
# Question: {question}
# Thought: ...
# Action: TOOL_NAME
# Action Input: INPUT
# Observation: RESULT
# ...
# Final Answer: RESULT

# Begin!
# Question: {question}
# """

#     history = prompt

#     # -------- start trace --------
#     tracer.log_event("start", {
#         "question": question,
#         "max_iterations": max_iterations
#     })

#     for i in range(max_iterations):
#         print(f"\n--- Iteration {i+1} ---")

#         response = client.get_completion(history)
#         print(f"LLM: {response}")

#         history += response

#         step_trace = {
#             "step": i + 1,
#             "llm_output": response,
#             "parsed_action": None,
#             "observation": None
#         }

#         # -------- Final answer check --------
#         if "Final Answer:" in response:
#             final_answer = response.split("Final Answer:")[-1].strip()

#             tracer.log_event("step", step_trace)

#             tracer.log_event("end", {
#                 "stop_reason": "final_answer_detected",
#                 "final_answer": final_answer
#             })

#             return final_answer

#         # -------- Parse Action --------
#         action_match = re.search(r"Action:\s*(.*)", response)
#         input_match = re.search(r"Action Input:\s*(.*)", response)

#         if action_match and input_match:
#             tool = action_match.group(1).strip()
#             arg = input_match.group(1).strip()

#             observation = f"Error: Tool {tool} not found"

#             if tool == "WEB_SEARCH":
#                 observation = web_search(arg)
#             elif tool == "CALCULATOR":
#                 observation = calculator(arg)

#             print(f"Observation: {observation}")

#             step_trace["parsed_action"] = {
#                 "tool": tool,
#                 "input": arg
#             }
#             step_trace["observation"] = observation

#             history += f"\nObservation: {observation}\n"

#             tracer.log_event("step", step_trace)

#         else:
#             print("No action detected. Ending.")

#             tracer.log_event("step", step_trace)

#             tracer.log_event("end", {
#                 "stop_reason": "no_action_detected"
#             })

#             return "No answer found."

#     # -------- max iterations reached --------
#     tracer.log_event("end", {
#         "stop_reason": "max_iterations_reached"
#     })

#     return "No answer found."


# if __name__ == "__main__":
#     print(agent_loop("what is 100*5"))