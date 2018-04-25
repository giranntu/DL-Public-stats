from bs4 import BeautifulSoup
import urllib.request
from lxml import html, etree
import requests, operator, sys, pdb


class iclr_company_count_puller(object):

	def __init__(self):
		self.companies = ['nvidia.com', 'google.com', 'fb.com', 'microsoft.com', \
			'intel.com', 'openai.com', 'ibm.com', 'baidu.com', 'adobe.com', \
			'samsung.com', 'nec-labs.com', 'salesforce.com']

		self.company_counts = dict(zip(self.companies, [0]*len(self.companies)))

	def count_companies(self, conflicts):
		for company in self.companies:
			if company in conflicts:
				self.company_counts[company] += 1
				break

	# helper function for ICLR 2017 papers
	def _iclr_2017(self, mirror_url, accepted_titles):
		dl_count = cnn_count = rnn_count = gan_count = ae_count = rl_count = 0

		HtmlFile = open(mirror_url, 'r', \
			encoding='utf-8')
		resp = HtmlFile.read() 
		soup = BeautifulSoup(resp)

		links = []
		for link in soup.find_all('a', href=True):
			hlink = link['href']
			hlink_list = hlink.split('/')
			if hlink_list[3][:5] == 'forum':
				links.append(hlink)

		for link in links:
			url = link
			page = requests.get(url)
			tree = html.fromstring(page.content)

			title = tree.xpath('//h2[contains(@class, "note_content_title citation_title")]/text()')
			if title[0].strip() in accepted_titles:				
				content_field = tree.xpath('//strong[contains(@class, "note-content-field")]/text()')
				content_text = tree.xpath('//span[contains(@class, "note-content-value")]/text()')

				_authorids = content_text[content_field.index('Authorids:')]
				authorids = [aa.strip() for aa in \
					[a.split('@')[1] for a in  _authorids.split(',')]]

				company_counted = []

				for company in self.companies:
					if (company in authorids) and (company not in company_counted):
						self.company_counts[company] += 1
						company_counted.append(company)

	def iclr(self, track):

		if track == 'conference':
			conference_track_accepted = []
			# gathered from http://www.iclr.cc/doku.php?id=iclr2017:conference_posters
			with open('iclr2017_mirror/iclr2017_conference_track_accepted.txt') as f:
			    conference_track_accepted_ = f.readlines()
			for title in conference_track_accepted_:
				conference_track_accepted.append(title.strip())

			# mirror of https://openreview.net/group?id=ICLR.cc/2017/conference
			# - downloaded the .htm file to avoid having to deal with Ajax query
			conf_track_mirror = 'iclr2017_mirror/ICLR2017_conference_OpenReview.htm'
			self._iclr_2017(conf_track_mirror, conference_track_accepted)

		elif track == 'workshop':
			workshop_track_accepted = []
			# gathered from http://www.iclr.cc/doku.php?id=iclr2017:workshop_posters
			with open('iclr2017_mirror/iclr2017_workshop_track_accepted.txt') as f:
			    workshop_track_accepted_ = f.readlines()
			for title in workshop_track_accepted_:
				workshop_track_accepted.append(title.strip())
		
			# mirror of https://openreview.net/group?id=ICLR.cc/2017/workshop
			# - downloaded the .html file to avoid having to deal with Ajax query
			work_track_mirror = 'iclr2017_mirror/ICLR2017_workshop_OpenReview.htm'
			self._iclr_2017(work_track_mirror, workshop_track_accepted)

		else:
			sys.exit('cannot reconize the track name!')

		return self.company_counts


if __name__ == "__main__":
	puller = iclr_company_count_puller()

	print('conference track only:')
	counts = puller.iclr('conference')
	counts_sorted = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
	for count in counts_sorted:
		print(count[0], ':', count[1])

	print()
	print('conference + workshop tracks')
	counts = puller.iclr('workshop')
	counts_sorted = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
	for count in counts_sorted:
		print(count[0], ':', count[1])
