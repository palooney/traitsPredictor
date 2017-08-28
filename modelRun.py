import os
import pickle
import pandas as pd
import numpy as np
from trainProcess import trainProcess
from scipy.stats import mode
from scipy.stats import describe
class modelRun:
	def __init__(self):
		self.path = "/Users/changye.li/Documents/scripts/traitsPredictor/process/"
		self.root = "/Users/changye.li/Documents/scripts/traitsPredictor/predict/"
		self.label_model = {} ## to store classfication model
		self.modelYes = {} ## to store regression "yes" model
		self.modelNo = {} ## to store regression "no" model
		self.name = [] ## trait names
	## get the list of all docs 
	## output: list that contains testing filenames
	def getDocs(self):
		docs = []
		for r, d ,f in os.walk(self.path):
			for files in f:
				if files.endswith(".csv") and files != "better.csv":
					docs.append(files)
		return docs
	## get trained model
	## output: update dict to store trained model
	def getModel(self):
		m = trainProcess()
		self.name = m.name
		self.label_model = m.trainModelLabel()
		m.saveModel()
		self.modelYes = m.modelYes
		self.modelNo = m.modelNo
	## apply trained model on validation dataset
	## user: user's processed data to scan, gathered from getDocs
	def getTrained(self, user):
		s = self.path + user
		dt = pd.read_csv(s)
		pred = []
		for item in self.name:
			pre = pickle.loads(self.label_model[item]).predict(dt).tolist()
			pred.append(pre)
		pred = np.matrix(np.array(pred))
		mat = pd.concat([dt, pd.DataFrame(pred.transpose())], axis = 1)
		mat.columns = ['anticipation', 'joy', 'negative', 'sadness', 
			'disgust', 'positive', 'anger', 'surprise', 'fear', 'trust',
			'ext', 'neu', 'agr', 'con', 'opn']
		## write to file
		#s1 = self.root + user
		#mat.to_csv(s1, index = False)
		#print "Finish writing to file"
	## apply regression model on classified dataset
	## user: validation user's processed data to scan, gathered from getDocs
	## trait: trait to be regressed
	## statis: predicted label, 1 for yes, N for 0
	def getRegressed(self, user, trait, status):
		s = self.root + user
		df = pd.read_csv(s)
		sample = df[df[trait] == status]
		sample = sample.ix[:, 0:10]
		pre = []
		if(status == 1):
			pre = pickle.loads(self.modelYes[trait]).predict(sample).tolist()
		else:
			pre = pickle.loads(self.modelNo[trait]).predict(sample).tolist()
		return pre
	## get "final" score for each trait for each user
	## a driver function for this class
	def getRated(self):
		self.getModel()
		docs = self.getDocs()
		for files in docs:
			print "processing validation user file: ", files
			self.getTrained(files)
		traits = ['ext', 'neu', 'agr', 'con', 'opn']
		for user in docs:
			print "processing user: ", user
			scores = []
			for each in traits:
				pre1 = self.getRegressed(user, each, 1)
				pre2 = self.getRegressed(user, each, 0)
				s = (np.mean(pre1)*len(pre1) + np.mean(pre2)*len(pre2))/(len(pre1) + len(pre2))
				scores.append(s)
			print scores

x = modelRun()
x.getRated()