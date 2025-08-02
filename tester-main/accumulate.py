import os
import re
import matplotlib.pyplot as plt
import lzma
from collections import defaultdict

def process_logs(log_dir, label):
    """
    Process all log files in the given directory to extract decision and number of calls.

    Args:
        log_dir (str): Path to the directory containing log files.
        label (str): Label for the log group (e.g., 'baseline' or 'iTester').

    Returns:
        list: A list of tuples (x_value, num_calls, label, decision).
    """
    results = []
    decision_pattern = re.compile(r"Decision:\s*(\w+)")
    calls_pattern = re.compile(r"Number of calls:\s*(\d+)")

    for filename in os.listdir(log_dir):
        if filename.endswith(".out.xz"):
            filepath = os.path.join(log_dir, filename)
            x_value = int(filename.split('_')[0])
            with lzma.open(filepath, "rt") as file:
                content = file.read()
                decision_match = decision_pattern.search(content)
                calls_match = calls_pattern.search(content)

                if decision_match and calls_match:
                    decision = decision_match.group(1)
                    num_calls = int(calls_match.group(1))
                    if not (decision == "reject" and num_calls == 0):
                        results.append((x_value, num_calls, label, decision))
    results.sort(key=lambda x: x[0])
    return results

def plot_results(results, title, show=True):
    """
    Plot the results with color per label and shape per decision.

    Args:
        results (list): A list of tuples (x_value, num_calls, label, decision).
        title (str): Title for the plot.
        show (bool): Whether to display the plot immediately.
    """
    colors = {'baseline': 'blue', 'iTester': 'green'}
    rename = {'iTester': r'$\mathsf{Lachesis}$', 'baseline': r'$\mathsf{CubeProbe}$'}
    markers = {'accept': 'o', 'reject': 'x'}
    dec_rename = {'accept': 'Accept', 'reject': 'Reject'}
    
    agg = defaultdict(list)
    for x_value, num_calls, label, decision in results:
        agg[(x_value, label, decision)].append(num_calls)

    plotted_labels = set()
    for (x_value, label, decision), calls in agg.items():
        avg_calls = sum(calls) / len(calls)
        color = colors[label]
        marker = markers[decision]
        display_label = f"{rename[label]} ({dec_rename[decision]})"
        if display_label not in plotted_labels:
            plt.scatter(x_value, avg_calls, color=color, marker=marker, label=display_label, s=100)
            plotted_labels.add(display_label)
        else:
            plt.scatter(x_value, avg_calls, color=color, marker=marker, s=100)

    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel("Program Domain Size", fontsize=20)
    plt.ylabel(r"#$\mathsf{ICOND}$ Queries", fontsize=20)
    plt.xlim(0, max(x[0] for x in results) + 1)
    plt.yscale('log')
    plt.gcf().set_size_inches(10, 6)
    plt.grid(True)
    plt.legend(loc="center right", fontsize=16)
    # plt.show()

if __name__ == "__main__":
    log_dir_1 = "./out-14971133-1"
    log_dir_0 = "./out-14971133-0"

    results_1 = process_logs(log_dir_1, "iTester")
    results_0 = process_logs(log_dir_0, "baseline")

    if results_1 and results_0:
        plt.figure(figsize=(10, 6))
        plot_results(results_1 + results_0, "Combined Results", show=False)
        plt.savefig("combined_results_" + log_dir_0.split('-')[1] + ".pdf")
