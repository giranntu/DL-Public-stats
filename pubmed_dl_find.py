import urllib.request
import xml.etree.ElementTree as ET
import os, json, csv
from collections import Counter

def get_xml(filename):
  if os.path.isfile(filename):
    pass
  else:
    cnn_terms = ['convolutional network', 'convolutional neural', \
      'convnet']
    rnn_terms = ['recurrent neural network', 'Long short-term']
    gan_terms = ['generative adversarial', 'adversarial network']
    ae_terms = ['autoencoder', 'auto-encoder', 'auto encoder']
    rl_terms = ['deep reinforcement', 'deep re-inforcement']

    dl_terms_ = ['deep learning'] +\
      cnn_terms + rnn_terms + gan_terms + ae_terms + rl_terms

    dl_terms = []
    counter = 0
    for dl_term in dl_terms_:
      if ' ' in dl_term:
        dl_term = dl_term.replace(' ', '+')
      dl_term = '"' + dl_term + '"'
      dl_terms.append(dl_term)
      counter += 1
      if counter < len(dl_terms_):
        dl_terms.append('+OR+')

    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' +\
      ''.join(dl_terms) + \
      '&retmax=900000&tool=dl_search_tool&email=hshin@nvidia.com'

    with urllib.request.urlopen(url) as response, open(filename, 'wb') as outfile:
      data = response.read()
      outfile.write(data)

def parse_xml(filename):
  tree = ET.parse(filename)
  root = tree.getroot()
  xids = []
  for xid in root.iter('Id'):
    xids.append(xid.text)
  return xids

def get_article_metadata(xid):
  url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+\
    xid + '&tool=dl_search_tool&email=hshin@nvidia.com'

  tmp_json_store_dir = 'json_files'
  if not os.path.isdir(tmp_json_store_dir):
    os.makedirs(tmp_json_store_dir)
  filename = os.path.join(tmp_json_store_dir, 'json_meta_' + xid + '.json')
  if not os.path.exists(filename):
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as outfile:
        data = response.read()
        outfile.write(data)
  return filename

def parse_json(filename):
  with open(filename) as f:
    content = f.readlines()
  affilstr = []
  affils = []
  for linei in content:
    line = linei.strip()
    if len(affilstr)<1:
      if line[:9] == 'affil str':
        startp = line.find('"')
        affilstr.append(line[startp+1:])
    else:
      endp = line.find('"')
      if endp<0:
        affilstr.append(line)
      else:
        affilstr.append(line[:endp-1])
        affils.append(' '.join(affilstr))
        affilstr = []

  affils_set = set(affils)
  affils_unique = list(affils_set)

  return affils_unique
  
def main():
  filename = 'pubmed_dl_query_0.xml'
  get_xml(filename)
  xids = parse_xml(filename)

  affils = []
  for xid in xids:
    json_meta_file = get_article_metadata(xid)
    affils += parse_json(json_meta_file)

  with open('pubmed_affil_counts.csv', 'w') as out:
    csv_out = csv.writer(out)
    affil_counts = Counter(affils)
    for affil, count in affil_counts.items():
      csv_out.writerow([affil, count])

if __name__ == "__main__":
  main()
