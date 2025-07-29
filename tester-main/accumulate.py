import os
import re
import matplotlib.pyplot as plt
import lzma

def process_logs(log_dir, label):
    """
    Process all log files in the given directory to extract decisions and number of calls.

    Args:
        log_dir (str): Path to the directory containing log files.
        label (str): Label for the log group (e.g., 'logs-1' or 'logs-0').

    Returns:
        list: A list of tuples (x_value, decision, num_calls, label).
    """
    results = []
    decision_pattern = re.compile(r"Decision:\s*(\w+)")
    calls_pattern = re.compile(r"Number of calls:\s*(\d+)")

    for filename in os.listdir(log_dir):
        if filename.endswith(".out.xz"):
            filepath = os.path.join(log_dir, filename)
            x_value = int(filename.split('_')[0])  # Extract the first number from the filename
            with lzma.open(filepath, "rt") as file:  # Decompress and read the file
                content = file.read()
                decision_match = decision_pattern.search(content)
                calls_match = calls_pattern.search(content)

                if decision_match and calls_match:
                    decision = decision_match.group(1)
                    num_calls = int(calls_match.group(1))
                    # Skip if "Decision: reject, Number of calls: 0"
                    if not (decision == "reject" and num_calls == 0):
                        results.append((x_value, decision, num_calls, label))
    # Sort results by x_value
    results.sort(key=lambda x: x[0])
    return results

def plot_results(results, title, show=True):
    """
    Plot the results with different colors for logs-1 and logs-0, and shapes for reject and accept.

    Args:
        results (list): A list of tuples (x_value, decision, num_calls, label).
        title (str): Title for the plot.
        show (bool): Whether to display the plot immediately.
    """
    colors = {'baseline': 'blue', 'iTester': 'green'}
    markers = {'reject': 'x', 'accept': 'o'}
    legend_labels = set()

    for x_value, decision, num_calls, label in results:
        color = colors[label]
        marker = markers['reject' if decision == "reject" else 'accept']
        legend_label = f"{label}-{decision}"
        if legend_label not in legend_labels:
            plt.scatter(x_value, num_calls, marker=marker, color=color, label=legend_label)
            legend_labels.add(legend_label)
        else:
            plt.scatter(x_value, num_calls, marker=marker, color=color)

    # plt.title(title)
    plt.xlabel("Program Domain Size")
    plt.ylabel("#INTCOND Queries")
    plt.xlim(0, max(x[0] for x in results) + 1)
    plt.yscale('log')
    plt.grid(True)
    if show:
        plt.legend(loc="center")
        plt.show()

if __name__ == "__main__":
    log_dir_1 = "./out-14779807-1"  # Update with the correct directory for logs-1
    log_dir_0 = "./out-14779807-0"  # Update with the correct directory for logs-0

    results_1 = process_logs(log_dir_1, "iTester")
    results_0 = process_logs(log_dir_0, "baseline")

    if results_1 and results_0:
        plt.figure(figsize=(10, 6))
        if results_1:
            plot_results(results_1, "Combined Results", show=False)
        if results_0:
            plot_results(results_0, "Combined Results", show=False)
        plt.legend(loc="upper right")
        plt.savefig("combined_results_"+ log_dir_0.split('-')[1] +".pdf")
        plt.show()