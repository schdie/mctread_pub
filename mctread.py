from tabulate import tabulate
import itertools
from itertools import islice
import argparse
import difflib

# arguments
parser = argparse.ArgumentParser(description='Available inputs')
parser.add_argument('-1', dest='file_path1', help='Path to the first input file')
parser.add_argument('-2', dest='file_path2', help='Path to the second input file')
parser.add_argument('-3', dest='file_path3', help='Path to the third input file')
parser.add_argument('-4', dest='file_path4', help='Path to the fourth input file')

args = parser.parse_args()

print('File path 1: ', args.file_path1)
print('File path 2: ', args.file_path2)
print('File path 3: ', args.file_path3)
print('File path 4: ', args.file_path4)

if not args.file_path1:
    print("Usage: readmct.py -1 mctfile1.mct -2 mctfile2.mct -3 mctfile3.mct -4 mctfile4.mct")
    print("You need at least one file path.")
    quit()

# datasets
datasets = [[], [], [], []]
file_paths = [args.file_path1, args.file_path2, args.file_path3, args.file_path4]

# get the all the data sets
for idx, path in enumerate(file_paths):
    if path:
        try:
            with open(path, "r") as file:
                for line in itertools.islice(file, 80):
                    if "+" not in line:
                        datasets[idx].append(line)
        except IOError:
            print(f"Path or filename ({idx+1}) incorrect, quitting...")
            if idx == 0: quit()

# combine every 4 items
combined_datasets = []
for ds in datasets:
    if ds:
        combined = [''.join([ds[i], ds[i+1], ds[i+2], ds[i+3]]).strip() for i in range(0, len(ds), 4)]
        combined_datasets.append(combined)
    else:
        combined_datasets.append([''] * 16)

# pad arrays to match the maximum loop length (default 16 elements)
max_len = max(len(arr) for arr in combined_datasets)
for i in range(4):
    if len(combined_datasets[i]) < max_len:
        combined_datasets[i] += [''] * (max_len - len(combined_datasets[i]))

def highlight_diff(baseline, target):
    """Compares baseline and target character-by-character, highlighting differences in Red."""
    if not target or baseline == target:
        return target
    
    result = []
    # split blocks by newlines to match line alignments accurately
    base_lines = baseline.split('\n')
    target_lines = target.split('\n')
    
    # process line pairings side-by-side
    for b_line, t_line in itertools.zip_longest(base_lines, target_lines, fillvalue=''):
        line_chars = []
        # ndiff mofo!
        diff = difflib.ndiff(b_line, t_line)
        
        for change in diff:
            # '+' indicates character exists in target but not baseline (an addition/change)
            if change.startswith('+ '):
                line_chars.append(f"\033[91m{change[2:]}\033[0m")
            # ' ' indicates character matches perfectly
            elif change.startswith(' '):
                line_chars.append(change[2:])
            # '-' indicates deleted characters from baseline, which we ignore in the target cell
            elif change.startswith('- '):
                pass
                
        result.append(''.join(line_chars))
        
    return '\n'.join(result)

# rows constructor
table_rows = []
for x, (val1, val2, val3, val4) in enumerate(itertools.zip_longest(*combined_datasets, fillvalue='')):
    
    # baseline is treated as a string even if empty
    val1_str = val1 if val1 else ''

    # character-level difference highlighting
    fmt_val2 = highlight_diff(val1_str, val2) if args.file_path2 else val2
    fmt_val3 = highlight_diff(val1_str, val3) if args.file_path3 else val3
    fmt_val4 = highlight_diff(val1_str, val4) if args.file_path4 else val4

    # build the row metadata layout strings
    sb_str = f"{x*4}\n{x*4+1}\n{x*4+2}\n{x*4+3}"
    block_str = "0\n1\n2\n3"
    
    table_rows.append([x, sb_str, block_str, val1, fmt_val2, fmt_val3, fmt_val4])

# add bold titles
table_rows.insert(0, ["\033[1mSector\033[0m", "\033[1mSB\033[0m", "\033[1mBlock\033[0m", "\033[1mDataset 1\033[0m", "\033[1mDataset 2\033[0m", "\033[1mDataset 3\033[0m", "\033[1mDataset 4\033[0m"])

# we are done
table = tabulate(table_rows, headers="firstrow", tablefmt="rounded_grid")
print(table)
