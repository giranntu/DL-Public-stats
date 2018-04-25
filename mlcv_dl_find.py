from bs4 import BeautifulSoup
import urllib.request
from lxml import html, etree
import requests
from time import sleep

class mlcv_pub_puller(object):

	def __init__(self):
		self.cnn_terms = ['convolutional network', 'convolutional neural', \
			'CNN', 'convnet']
		self.rnn_terms = ['recurrent network', 'recurrent neural', 'RNN', \
			'LSTM', 'GRU']
		self.gan_terms = ['generative adversarial', 'GAN']
		self.ae_terms = ['autoencoder', 'auto-encoder', 'auto encoder']
		self.rl_terms = ['deep reinforcement', 'deep RL', 'deep re-inforcement']

		self.dl_terms = ['deep', 'neural', 'neural history compressor',\
			'recursive neural networks','recursive networks','Long short-term memory',\
			'deep belief networks','convolutional deep belief networks',\
			'large memory storage networks','retrieval networks','deep boltzmann machines',\
			'stacked denoising','stacked de-noising','deep stacking','tensor deep',\
			'spike-and-slab','compound hierarchical-deep models','deep coding','deep Q',\
			'semantic hashing','neural Turing machines','memory networks','pointer networks',\
			'encoder–decoder networks'] +\
			self.cnn_terms + self.rnn_terms + self.gan_terms + self.ae_terms + self.rl_terms


	def count_terms(self, abstract):
		dl_count = cnn_count = rnn_count = gan_count = ae_count = rl_count = 0
		for cnn_term in self.cnn_terms:
			if cnn_term in abstract:
				cnn_count += 1				
				break

		for rnn_term in self.rnn_terms:
			if rnn_term in abstract:
				rnn_count += 1
				break

		for gan_term in self.gan_terms:
			if gan_term in abstract:
				gan_count += 1
				break

		for ae_term in self.ae_terms:
			if ae_term in abstract:
				ae_count += 1
				break

		for rl_term in self.rl_terms:
			if rl_term in abstract:
				rl_count += 1
				break

		for dl_term in self.dl_terms:
			if dl_term in abstract:
				dl_count += 1
				break

		return dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count


	def nips(self, vol_year):
		dl_count = cnn_count = rnn_count = gan_count = ae_count = rl_count = 0		

		resp = urllib.request.urlopen('https://papers.nips.cc/book/' +\
			'advances-in-neural-information-processing-systems-' + vol_year)
		soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'))

		links = []
		for link in soup.find_all('a', href=True):
		    hlink = link['href']
		    if hlink[1:6] == 'paper':
		    	links.append(hlink)

		_count = 0
		for link in links:
			url = 'https://papers.nips.cc' + link
			page = requests.get(url)
			tree = html.fromstring(page.content)
			
			_abstracts = tree.xpath('//p[contains(@class, "abstract")]/text()')
			abstract = _abstracts[0].lower()
			
			dlc, cnnc, rnnc, ganc, aec, rlc = self.count_terms(abstract)
			
			dl_count += dlc
			cnn_count += cnnc
			rnn_count += rnnc
			gan_count += ganc
			ae_count += aec
			rl_count += rlc

			# NIPS limits number of acess quite strictly, so sleep between retrievals
			_count += 1
			if _count%10 == 0:
				sleep(10)

		total = len(links)
		return total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count


	def icml(self, vol):
		dl_count = cnn_count = rnn_count = gan_count = ae_count = rl_count = 0

		resp = urllib.request.urlopen('http://proceedings.mlr.press/' + vol + '/')
		soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'))

		links = []
		for link in soup.find_all('a', href=True):
			hlink = link['href']
			try:
				hlink_list = hlink.split('/')
				if hlink_list[3] == vol and hlink_list[-1][-4:] == 'html':
					links.append(hlink)
			except:
				pass

		for link in links:
			url = link
			page = requests.get(url)
			tree = html.fromstring(page.content)

			_abstracts = tree.xpath('//div[contains(@class, "abstract")]/text()')
			abstract = _abstracts[0].lower()

			dlc, cnnc, rnnc, ganc, aec, rlc = self.count_terms(abstract)
			
			dl_count += dlc
			cnn_count += cnnc
			rnn_count += rnnc
			gan_count += ganc
			ae_count += aec
			rl_count += rlc

		total = len(links)
		return total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count


	def cvpr(self, year):
		dl_count = cnn_count = rnn_count = gan_count = ae_count = rl_count = 0

		resp = urllib.request.urlopen('http://www.cv-foundation.org/openaccess/CVPR'+\
			year + '.py')
		soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'))

		links = []
		for link in soup.find_all('a', href=True):
			hlink = link['href']
			if hlink[-4:] == 'html':
				links.append(hlink)
		
		for link in links:
			url = 'http://www.cv-foundation.org/openaccess/' + link
			page = requests.get(url)
			tree = html.fromstring(page.content)
			
			_abstracts = tree.xpath('//div[contains(@id, "abstract")]/text()')
			try:
				abstract = _abstracts[0].lower()
			except:
				print(url, ' - Page Not Found!')
		
			dlc, cnnc, rnnc, ganc, aec, rlc = self.count_terms(abstract)
			
			dl_count += dlc
			cnn_count += cnnc
			rnn_count += rnnc
			gan_count += ganc
			ae_count += aec
			rl_count += rlc

		total = len(links)
		return total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count


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
				_abstracts = tree.xpath('//span[contains(@class, "note-content-value")]/text()')
				abstract = _abstracts[0].lower()

				dlc, cnnc, rnnc, ganc, aec, rlc = self.count_terms(abstract)

				dl_count += dlc
				cnn_count += cnnc
				rnn_count += rnnc
				gan_count += ganc
				ae_count += aec
				rl_count += rlc

		return dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count

	# helper function for ICLR papers before 2017
	def _iclr(self, soup, year):
		dl_count = cnn_count = rnn_count = gan_count = ae_count = rl_count = 0

		links = []
		for link in soup.find_all('a', href=True):
			hlink = link['href']
			hlink_list = hlink.split('/')
			if int(year) <= 2015:
				if len(hlink_list)>2 and hlink_list[2] == 'arxiv.org':
					links.append(hlink)
			elif int(year) == 2016:
				if len(hlink_list)>2 and \
					(hlink_list[2] == 'arxiv.org' or hlink_list[2] == 'beta.openreview.net'):
					links.append(hlink)

		for link in links:
			url = link
			page = requests.get(url)
			tree = html.fromstring(page.content)
			
			if 'arxiv.org' in url:
				_abstracts = tree.xpath('//blockquote[contains(@class, "abstract mathjax")]/text()')
				try:
					abstract = _abstracts[1].lower()
				except:
					print(url, _abstracts, '+1 CNN paper, but has PDF link, not arXiv page.')
					cnnc = 1
			elif 'openreview.net' in url:
				_abstracts = tree.xpath('//span[contains(@class, "note-content-value")]/text()')
				abstract = _abstracts[0].lower()

			dlc, cnnc, rnnc, ganc, aec, rlc = self.count_terms(abstract)

			dl_count += dlc
			cnn_count += cnnc
			rnn_count += rnnc
			gan_count += ganc
			ae_count += aec
			rl_count += rlc

		total = len(links)

		return total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count

	def iclr(self, year):
		dl_count = cnn_count = rnn_count = gan_count = ae_count = rl_count = 0

		if int(year)<2017:
			if int(year)>2014:
				resp = urllib.request.urlopen('http://www.iclr.cc/doku.php?id=iclr' +\
					year + ':main')
				soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'))

				total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count = \
					self._iclr(soup, year)
			else:
				resp_c = urllib.request.urlopen('https://sites.google.com/site/'+\
					'representationlearning2014/conference-proceedings')
				resp_w = urllib.request.urlopen('https://sites.google.com/site/'+\
					'representationlearning2014/workshop-proceedings')
				soup_c = BeautifulSoup(resp_c, from_encoding=resp_c.info().get_param('charset'))
				soup_w = BeautifulSoup(resp_w, from_encoding=resp_w.info().get_param('charset'))

				total_c, dl_count_c, cnn_count_c, rnn_count_c, gan_count_c, ae_count_c, rl_count_c = \
					self._iclr(soup_c, year)
				total_w, dl_count_w, cnn_count_w, rnn_count_w, gan_count_w, ae_count_w, rl_count_w = \
					self._iclr(soup_w, year)

				total = total_c + total_w
				dl_count = dl_count_c + dl_count_w
				cnn_count = cnn_count_c + cnn_count_w
				rnn_count = rnn_count_c + rnn_count_w
				gan_count = gan_count_c + gan_count_w
				ae_count = ae_count_c + ae_count_w
				rl_count = rl_count_c + rl_count_w

		else:
			conference_track_accepted = []
			# gathered from http://www.iclr.cc/doku.php?id=iclr2017:conference_posters
			with open('iclr2017_mirror/iclr2017_conference_track_accepted.txt') as f:
			    conference_track_accepted_ = f.readlines()
			for title in conference_track_accepted_:
				conference_track_accepted.append(title.strip())
			workshop_track_accepted = []
			# gathered from http://www.iclr.cc/doku.php?id=iclr2017:workshop_posters
			with open('iclr2017_mirror/iclr2017_workshop_track_accepted.txt') as f:
			    workshop_track_accepted_ = f.readlines()
			for title in workshop_track_accepted_:
				workshop_track_accepted.append(title.strip())
			
			# mirror of https://openreview.net/group?id=ICLR.cc/2017/conference
			# - downloaded the .htm file to avoid having to deal with Ajax query
			conf_track_mirror = 'iclr2017_mirror/ICLR2017_conference_OpenReview.htm'
			dlc, cnnc, rnnc, ganc, aec, rlc = \
				self._iclr_2017(conf_track_mirror, conference_track_accepted)
			dl_count += dlc
			cnn_count += cnnc
			rnn_count += rnnc
			gan_count += ganc
			ae_count += aec
			rl_count += rlc

			# mirror of https://openreview.net/group?id=ICLR.cc/2017/workshop
			# - downloaded the .html file to avoid having to deal with Ajax query
			work_track_mirror = 'iclr2017_mirror/ICLR2017_workshop_OpenReview.htm'
			dlc, cnnc, rnnc, ganc, aec, rlc = \
				self._iclr_2017(work_track_mirror, workshop_track_accepted)
			dl_count += dlc
			cnn_count += cnnc
			rnn_count += rnnc
			gan_count += ganc
			ae_count += aec
			rl_count += rlc

			total = len(conference_track_accepted) + len(workshop_track_accepted)
		return total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count


if __name__ == "__main__":
	puller = mlcv_pub_puller()
	
	# NIPS
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.nips('29-2016')
	print('nips-2016', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.nips('28-2015')
	print('nips-2015', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.nips('27-2014')
	print('nips-2014', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)

	# ICML
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.icml('v48')
	print('icml-2016', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.icml('v37')
	print('icml-2015', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.icml('v32')
	print('icml-2014', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)

	# CVPR
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.cvpr('2016')
	print('cvpr-2016', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)	
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.cvpr('2015')
	print('cvpr-2015', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)	
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.cvpr('2014')
	print('cvpr-2014', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)	

	# ICLR
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.iclr('2017')
	print('iclr-2017', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)	
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.iclr('2016')
	print('iclr-2016', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)	
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.iclr('2015')
	print('iclr-2015', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)	
	total, dl_count, cnn_count, rnn_count, gan_count, ae_count, rl_count =\
		puller.iclr('2014')
	print('iclr-2014', ', total,', total, 'dl,', dl_count, ', cnn,', cnn_count, ', rnn,', rnn_count, \
		', gan,', gan_count, ', ae,', ae_count, ', rl,', rl_count)	
