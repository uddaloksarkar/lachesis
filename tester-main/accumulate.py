import os
import re
import matplotlib.pyplot as plt
import lzma

# Use a clean, presentation-friendly style
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.size": 14,
    "font.family": "sans-serif",
    "axes.labelsize": 16,
    "axes.titlesize": 18,
    "legend.fontsize": 14,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
})

def process_logs(log_dir, label):
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
                        results.append((x_value, num_calls, label))
    results.sort(key=lambda x: x[0])
    return results


def plot_results(results, title, show=True):
    label_map = {'baseline': 'Vanilla', 'iTester': 'Instance Dependent'}
    colors = {'Vanilla': '#1f77b4', 'Instance Dependent': '#2ca02c'}  # blue & green

    results = [(x, num_calls, label_map.get(l, l)) for x, num_calls, l in results]
    plotted_labels = set()

    for x_value, num_calls, label in results:
        color = colors[label]
        if label not in plotted_labels:
            plt.scatter(
                x_value, num_calls, 
                color=color, alpha=0.7, edgecolor='black',
                s=80, label=label, linewidth=0.5
            )
            plotted_labels.add(label)
        else:
            plt.scatter(
                x_value, num_calls,
                color=color, alpha=0.7, edgecolor='black',
                s=80, linewidth=0.5
            )

    plt.xlabel("Program Domain Size", labelpad=10)
    plt.ylabel("# Oracle Queries", labelpad=10)
    plt.yscale('log')
    plt.xlim(0, max(x[0] for x in results) + 1)
    plt.grid(True, linestyle='--', linewidth=0.7, alpha=0.6)

    # Legend in a slightly transparent box for presentation
    plt.legend(
        loc="center right",
        frameon=True,
        facecolor='white',
        framealpha=0.9,
        edgecolor='gray'
    )
    plt.title(title, pad=12)
    plt.tight_layout()

    if show:
        plt.show()


if __name__ == "__main__":
    log_dir_1 = "./out-14779807-1"
    log_dir_0 = "./out-14779807-0"

    results_1 = process_logs(log_dir_1, "baseline")
    results_0 = process_logs(log_dir_0, "iTester")

    if results_1 and results_0:
        plt.figure(figsize=(10, 6))
        plot_results(results_1 + results_0, "Instance Dependent Testing on Binomial Sampler", show=False)
        plt.savefig("combined_results_" + log_dir_0.split('-')[1] + ".pdf", bbox_inches="tight")
        plt.show()
