import pandas as pd
import json
from ete3 import Tree

print("="*60)
print("CREATING ENHANCED SCIARIDAE METADATA V3")
print("="*60)

# 1. Load data files
print("\n[1/9] Loading data files...")
bioscan = pd.read_csv('sciaridae_bioscan.csv')
uksi = pd.read_csv('sciaridae_uksi.csv')
tree_tips = pd.read_csv('sciaridae_tree_tips.csv')

with open('tree_metadata.json', 'r') as f:
    tree_meta = json.load(f)

with open('curation_data.json', 'r') as f:
    curation = json.load(f)

with open('epa_results/epa_result.jplace', 'r') as f:
    jplace = json.load(f)

print(f"  BIOSCAN: {len(bioscan)} records")
print(f"  UKSI: {len(uksi)} species")
print(f"  Tree tips: {len(tree_tips)} sequences")

# 2. Build BIN-level lookup (PRIMARY) and species-level lookup (FALLBACK)
print("\n[2/9] Building BIN-level and species-level lookups...")
bin_info = {}  # BIN → {grade, species_list, n_species}
species_info = {}  # species → {grade, n_bins, bin_list}

for genus, genus_data in curation['genera'].items():
    
    # Grade C: species split across multiple BINs
    for item in genus_data['grade_C']:
        species = item['species']
        bins = item['bins']
        grade = 'C'
        
        # BIN-level
        for bin_uri in bins:
            if bin_uri not in bin_info:
                bin_info[bin_uri] = {'grade': grade, 'species_list': [], 'issue': 'species_split_across_BINs'}
            bin_info[bin_uri]['species_list'].append(species)
        
        # Species-level
        species_info[species] = {
            'grade': grade,
            'n_bins': len(bins),
            'bin_list': ', '.join(bins)
        }
    
    # Grade E: multiple species per BIN
    for item in genus_data['grade_E']:
        species = item['species']
        bins = item['bins']
        grade = 'E'
        
        # BIN-level
        for bin_uri in bins:
            if bin_uri not in bin_info:
                bin_info[bin_uri] = {'grade': grade, 'species_list': [], 'issue': 'shares_BIN_with_other_species'}
            if species not in bin_info[bin_uri]['species_list']:
                bin_info[bin_uri]['species_list'].append(species)
        
        # Species-level
        species_info[species] = {
            'grade': grade,
            'n_bins': len(bins),
            'bin_list': ', '.join(bins)
        }
    
    # Grade A/B/D: clean
    for item in genus_data['grade_A_B_D']:
        species = item['species']
        bins = item['bins']
        grade = item['grade']
        
        # BIN-level
        for bin_uri in bins:
            if bin_uri not in bin_info:
                bin_info[bin_uri] = {'grade': grade, 'species_list': [species], 'issue': 'clean'}
        
        # Species-level
        species_info[species] = {
            'grade': grade,
            'n_bins': len(bins),
            'bin_list': ', '.join(bins)
        }

print(f"  BIN-level data: {len(bin_info)} BINs")
print(f"  Species-level data: {len(species_info)} species")

# 3. Get monophyly data
print("\n[3/9] Extracting monophyly data...")
monophyly_data = {}
if 'monophyly_analysis' in tree_meta:
    for item in tree_meta['monophyly_analysis'].get('grade_c_species', []):
        species = item.get('species')
        if species:
            monophyly_data[species] = item.get('monophyletic', 'unknown')

print(f"  Monophyly data for {len(monophyly_data)} Grade C species")

# 4. Parse EPA-ng placements
print("\n[4/9] Processing EPA-ng placements...")
epa_placements = []
for placement in jplace['placements']:
    name = placement['n'][0]
    best = placement['p'][0]
    lwr = best[2]
    
    parts = name.split('|')
    bin_code = parts[0]
    species = parts[1]
    process_id = parts[2]
    
    # Fix BIN format
    bin_uri = 'BOLD:' + bin_code[4:] if bin_code.startswith('BOLD') and ':' not in bin_code else bin_code
    
    epa_placements.append({
        'name': name,
        'bold_bin_uri': bin_uri,
        'species': species,
        'process_id': process_id,
        'placement_confidence': lwr,
        'placement_method': 'EPA-ng'
    })

epa_df = pd.DataFrame(epa_placements)
epa_df['placement_quality'] = epa_df['placement_confidence'].apply(
    lambda x: 'High_confidence' if x >= 0.75 else ('Moderate_confidence' if x >= 0.50 else 'Low_confidence')
)

print(f"  EPA placements: {len(epa_df)}")

# 5. Process reference tree tips
print("\n[5/9] Processing reference tree tips...")
ref_metadata = tree_tips[['tip_label', 'species_clean', 'bin_uri']].copy()
ref_metadata.columns = ['name', 'species', 'bold_bin_uri']
ref_metadata['placement_method'] = 'reference_tree'
ref_metadata['placement_quality'] = 'reference'
ref_metadata['placement_confidence'] = 1.0

# 6. Combine and enrich metadata
print("\n[6/9] Combining and enriching metadata...")
all_metadata = pd.concat([ref_metadata, epa_df], ignore_index=True)

# Count BIOSCAN specimens per BIN
bioscan_counts = bioscan.groupby('bold_bin_uri').size().reset_index(name='bioscan_specimens')
all_metadata = all_metadata.merge(bioscan_counts, on='bold_bin_uri', how='left')
all_metadata['bioscan_specimens'] = all_metadata['bioscan_specimens'].fillna(0).astype(int)

# Add UKSI membership
uksi_species = set(uksi['species_binomial'].str.lower())
all_metadata['in_uksi'] = all_metadata['species'].str.replace('_', ' ').str.lower().isin(uksi_species)

# CRITICAL: Match by BIN FIRST, then fall back to species name
def get_grade(row):
    # Try BIN first
    if row['bold_bin_uri'] in bin_info:
        return bin_info[row['bold_bin_uri']]['grade']
    # Fall back to species name
    species_clean = row['species'].replace('_', ' ')
    if species_clean in species_info:
        return species_info[species_clean]['grade']
    return 'Unknown'

all_metadata['bags_grade'] = all_metadata.apply(get_grade, axis=1)

# Get n_bins and bin_list
def get_n_bins(row):
    species_clean = row['species'].replace('_', ' ')
    if species_clean in species_info:
        return species_info[species_clean]['n_bins']
    return 1

def get_bin_list(row):
    species_clean = row['species'].replace('_', ' ')
    if species_clean in species_info:
        return species_info[species_clean]['bin_list']
    return row['bold_bin_uri']

all_metadata['n_bins_for_species'] = all_metadata.apply(get_n_bins, axis=1)
all_metadata['all_bins_for_species'] = all_metadata.apply(get_bin_list, axis=1)

# Get other species sharing the BIN
def get_other_species(row):
    bin_uri = row['bold_bin_uri']
    this_species = row['species'].replace('_', ' ')
    
    if bin_uri in bin_info:
        species_in_bin = bin_info[bin_uri]['species_list']
        other_species = [s for s in species_in_bin if s != this_species]
        if other_species:
            return ', '.join(other_species)
    return ''

all_metadata['other_species_in_bin'] = all_metadata.apply(get_other_species, axis=1)

# Add monophyly
all_metadata['monophyletic'] = all_metadata.apply(
    lambda row: monophyly_data.get(row['species'].replace('_', ' '), '') if row['bags_grade'] == 'C' else '',
    axis=1
)

# Add bin quality issue description
def describe_bin_issue(row):
    if row['bags_grade'] == 'C':
        mono = row['monophyletic']
        if mono == True:
            return f"split_across_{row['n_bins_for_species']}_BINs_monophyletic"
        elif mono == False:
            return f"split_across_{row['n_bins_for_species']}_BINs_paraphyletic"
        else:
            return f"split_across_{row['n_bins_for_species']}_BINs"
    elif row['bags_grade'] == 'E':
        n_other = len(row['other_species_in_bin'].split(', ')) if row['other_species_in_bin'] else 0
        return f"shares_BIN_with_{n_other}_other_species"
    elif row['bags_grade'] in ['A', 'B', 'D']:
        return 'clean'
    else:
        return 'unknown'

all_metadata['bin_quality_issue'] = all_metadata.apply(describe_bin_issue, axis=1)

# Add geography
all_metadata['geography'] = all_metadata['in_uksi'].map({True: 'UK', False: 'Europe_or_worldwide'})

# Assign categories
def assign_category(row):
    if row['placement_method'] == 'reference_tree':
        if row['bioscan_specimens'] > 0:
            return 'BIOSCAN_collected'
        else:
            return 'Europe_reference'
    else:  # EPA-ng
        if row['bioscan_specimens'] > 0:
            if row['in_uksi']:
                return 'BIOSCAN_collected'
            else:
                return 'Not_in_UKSI'
        else:
            if row['in_uksi']:
                return 'UKSI_no_specimens'
            else:
                return 'Not_in_UKSI'

all_metadata['category'] = all_metadata.apply(assign_category, axis=1)

# Flag attention cases
all_metadata['needs_attention'] = (
    (all_metadata['category'] == 'Not_in_UKSI') & 
    (all_metadata['bioscan_specimens'] > 0)
)

# Add dataset columns
all_metadata['dataset_bioscan'] = all_metadata['bioscan_specimens'] > 0
all_metadata['dataset_dtol'] = False
all_metadata['dataset_goat'] = False

# 7. Add polytomy
print("\n[7/9] Adding polytomy for species without molecular data...")
polytomy_species = "Xylosciara betulae"

polytomy_row = {
    'name': f"{polytomy_species.replace(' ', '_')}|no_BIN|polytomy",
    'species': polytomy_species,
    'bold_bin_uri': 'no_BIN',
    'placement_method': 'polytomy_no_molecular_data',
    'placement_quality': 'no_molecular_data',
    'placement_confidence': 0.0,
    'bioscan_specimens': 0,
    'in_uksi': True,
    'bags_grade': 'Unknown',
    'n_bins_for_species': 0,
    'all_bins_for_species': '',
    'other_species_in_bin': '',
    'monophyletic': '',
    'bin_quality_issue': 'no_molecular_data',
    'geography': 'UK',
    'category': 'UKSI_no_specimens',
    'needs_attention': False,
    'dataset_bioscan': False,
    'dataset_dtol': False,
    'dataset_goat': False
}

all_metadata = pd.concat([all_metadata, pd.DataFrame([polytomy_row])], ignore_index=True)
print(f"  Added polytomy: {polytomy_species}")

# 8. Save metadata
print("\n[8/9] Saving metadata...")
final_columns = [
    'name',
    'species',
    'bold_bin_uri',
    'category',
    'geography',
    'placement_method',
    'placement_quality',
    'placement_confidence',
    'bags_grade',
    'n_bins_for_species',
    'all_bins_for_species',
    'other_species_in_bin',
    'monophyletic',
    'bin_quality_issue',
    'in_uksi',
    'bioscan_specimens',
    'dataset_bioscan',
    'dataset_dtol',
    'dataset_goat',
    'needs_attention'
]

metadata_final = all_metadata[final_columns]
metadata_final.to_csv('sciaridae_taxonium_metadata.tsv', sep='\t', index=False)

# 9. Modify tree to add polytomy
print("\n[9/9] Adding polytomy to tree...")
tree = Tree("gappa_output/epa_result.newick", format=1)
xylosciara_tips = [leaf for leaf in tree if 'Xylosciara' in leaf.name]

if xylosciara_tips:
    genus_node = xylosciara_tips[0].up
    genus_node.add_child(name=f"Xylosciara_betulae|no_BIN|polytomy", dist=0.0)
    print(f"  Added {polytomy_species} to Xylosciara clade")

tree.write(format=1, outfile="sciaridae_final_tree.newick")

# Summary
print("\n" + "="*60)
print("METADATA SUMMARY")
print("="*60)
print(f"Total tips: {len(metadata_final)}")
print(f"\nBy category:")
print(metadata_final['category'].value_counts().to_string())
print(f"\nBy BAGS grade (BIN-first matching):")
print(metadata_final['bags_grade'].value_counts().to_string())

# Check improvement
unknown_count = (metadata_final['bags_grade'] == 'Unknown').sum()
print(f"\n✓ Reduced 'Unknown' from 140 to {unknown_count} by matching BINs first!")

grade_c = metadata_final[metadata_final['bags_grade'] == 'C']
if len(grade_c) > 0:
    print(f"\nGrade C (split BINs): {len(grade_c)} tips")
    print(f"  Monophyletic: {(grade_c['monophyletic'] == True).sum()}")
    print(f"  Paraphyletic: {(grade_c['monophyletic'] == False).sum()}")
    print(f"  Unknown: {(grade_c['monophyletic'] == '').sum()}")

grade_e = metadata_final[metadata_final['bags_grade'] == 'E']
if len(grade_e) > 0:
    has_sharing = (grade_e['other_species_in_bin'] != '').sum()
    print(f"\nGrade E (shared BINs): {len(grade_e)} tips")
    print(f"  With other species in same BIN: {has_sharing}")

print(f"\n⚠️  Cases needing attention: {metadata_final['needs_attention'].sum()}")
if metadata_final['needs_attention'].sum() > 0:
    attention = metadata_final[metadata_final['needs_attention']][
        ['species', 'bioscan_specimens', 'placement_confidence', 'bags_grade', 'bin_quality_issue']
    ].sort_values('bioscan_specimens', ascending=False)
    print("\nNot in UKSI but has BIOSCAN specimens:")
    print(attention.head(10).to_string(index=False))

print(f"\n✓ Enhanced metadata saved to: sciaridae_taxonium_metadata.tsv")
print(f"✓ Tree with polytomy saved to: sciaridae_final_tree.newick")
print("\n📤 Ready to upload to Taxonium!")
