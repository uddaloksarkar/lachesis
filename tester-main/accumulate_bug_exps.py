import os
import lzma
import re
from collections import defaultdict
import random

# Directory pattern and regex for filename and file content
dir_prefix = "out-14853391-"
num_dirs = 6
file_pattern = re.compile(r'(\d+_\d+\.\d+_\d+_\d+\.\d+)\.out\.xz')
decision_pattern = re.compile(r'Decision:\s+(accept|reject)', re.IGNORECASE)
calls_pattern = re.compile(r'Number of calls:\s+(\d+)')

# Data structure: {(n,p,n,p): [ (decision, calls), ..., ] for each dir}
results = defaultdict(lambda: [("", "")] * num_dirs)

# Process each directory
for i in range(1, num_dirs + 1):
    dir_name = f"{dir_prefix}{i}"
    if not os.path.isdir(dir_name):
        continue

    for file in os.listdir(dir_name):
        match = file_pattern.match(file)
        if not match:
            continue

        param_key = match.group(1)
        file_path = os.path.join(dir_name, file)

        with lzma.open(file_path, 'rt') as f:
            content = f.read()

            decision_match = decision_pattern.search(content)
            calls_match = calls_pattern.search(content)

            decision = decision_match.group(1) if decision_match else "N/A"
            calls = calls_match.group(1) if calls_match else "N/A"

            result_list = list(results[param_key])
            result_list[i - 1] = (decision, calls)
            results[param_key] = result_list

# Sort keys by first n value in the (n, p, n, p) key
def extract_n_from_key(key):
    parts = key.split('_')
    return int(parts[0])  # First 'n'

sorted_keys = sorted(results, key=extract_n_from_key)

# Generate LaTeX table 
latex = []
latex.append(r"\begin{tabular}{l" + "cc" * num_dirs + "}")
latex.append(r"\toprule")
header = ["(n, p)"]
for i in range(1, num_dirs + 1):
    header.append(f"\\multicolumn{{2}}{{c}}{{{i}}}")
latex.append(" & ".join(header) + r" \\")
subheader = [""] + ["Dec. & Calls" for _ in range(num_dirs)]
latex.append(" & ".join(subheader) + r" \\")
latex.append(r"\midrule")

for key in sorted_keys:
    row = [key.split('_')[0] + r", " + str(float(key.split('_')[1]))]
    for (decision, calls) in results[key]:
        if decision.lower() == "accept":
            row.append(r"\acceptcell")
        elif decision.lower() == "reject":
            row.append(r"\rejectcell")
        else:
            row.append("N/A")
        row.append(calls)
    latex.append(" & ".join(row) + r" \\")

latex.append(r"\bottomrule")
latex.append(r"\end{tabular}")

# Write to file
with open("table.tex", "w") as f:
    f.write("\n".join(latex))


# Generate a shorter LaTeX table 
latex = []
latex.append(r"\begin{tabular}{l" + "cc" * num_dirs + "}")
latex.append(r"\toprule")
header = ["(n, p)"]
for i in range(1, num_dirs + 1):
    header.append(f"\\multicolumn{{2}}{{c}}{{{i}}}")
latex.append(" & ".join(header) + r" \\")
subheader = [""] + ["Dec. & Calls" for _ in range(num_dirs)]
latex.append(" & ".join(subheader) + r" \\")
latex.append(r"\midrule")

random_keys = random.sample(sorted_keys, 10) if len(sorted_keys) > 10 else sorted_keys
for key in random_keys:
    row = [key.split('_')[0] + r", " + str(float(key.split('_')[1]))]
    for (decision, calls) in results[key]:
        if decision.lower() == "accept":
            row.append(r"\acceptcell")
        elif decision.lower() == "reject":
            row.append(r"\rejectcell")
        else:
            row.append("N/A")
        row.append(calls)
    latex.append(" & ".join(row) + r" \\")

latex.append(r"\bottomrule")
latex.append(r"\end{tabular}")

# Write to file
with open("short_table.tex", "w") as f:
    f.write("\n".join(latex))

