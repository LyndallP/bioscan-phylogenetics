import pandas as pd

df = pd.read_csv('data/output/sciaridae_taxonium_metadata_FINAL.tsv', sep='\t')

# Try HTML anchor tags (in case Taxonium renders HTML)
def make_html_link(url, text):
    if url == '':
        return ''
    return f'<a href="{url}" target="_blank">{text}</a>'

# Create HTML versions
df['BLAST_link'] = df.apply(lambda x: make_html_link(x['link_BLAST'], 'BLAST') if x['link_BLAST'] else '', axis=1)
df['GBIF_link'] = df.apply(lambda x: make_html_link(x['link_GBIF'], 'GBIF') if x['link_GBIF'] else '', axis=1)
df['BOLD_link'] = df.apply(lambda x: make_html_link(x['link_BOLD'], 'BOLD') if x['link_BOLD'] else '', axis=1)
df['NBN_link'] = df.apply(lambda x: make_html_link(x['link_NBN'], 'NBN') if x['link_NBN'] else '', axis=1)
df['DTOL_link'] = df.apply(lambda x: make_html_link(x['link_DTOL'], 'DTOL') if x['link_DTOL'] else '', axis=1)

df.to_csv('data/output/sciaridae_metadata_html_links.tsv', sep='\t', index=False)
print("Created: sciaridae_metadata_html_links.tsv")
print("Try uploading this version if plain URLs aren't clickable")
