import sys
from ete3 import Tree

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input.treefile> <output.treefile>")
    sys.exit(1)

input_tree = sys.argv[1]
output_tree = sys.argv[2]

# Load tree
tree = Tree(input_tree, format=1)

# Get all tip names
all_tips = [leaf.name for leaf in tree]
print(f"Original tree: {len(all_tips)} tips")

# Find outgroup tips
outgroup_tips = [tip for tip in all_tips if tip.startswith("OUTGROUP")]
print(f"Found {len(outgroup_tips)} outgroup tips to remove:")
for tip in outgroup_tips:
    print(f"  {tip}")

# Remove outgroups
tree.prune([tip for tip in all_tips if not tip.startswith("OUTGROUP")])

print(f"\nPruned tree: {len(tree)} tips")

# Save pruned tree
tree.write(format=1, outfile=output_tree)
print(f"\nSaved to: {output_tree}")
