from ete3 import Tree

# Load tree
tree = Tree("Sciaridae.treefile", format=1)

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
tree.write(format=1, outfile="Sciaridae_ingroup.treefile")
print("\nSaved to: Sciaridae_ingroup.treefile")
