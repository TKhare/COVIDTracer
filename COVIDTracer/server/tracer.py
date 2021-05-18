import sys, csv 

class Tracer: 
	def __init__(self, num):
		self.num = 0
		with open('./csvs/num.csv') as csv6_file:
			csv6_reader = csv.reader(csv6_file, delimiter=',')
			line_count = 0
			for row in csv6_reader:
				if(len(row) >= 2):
					self.num = int(row[0])

		self.UNVISITED = -1 
		self.VISITED = 1
		self.CC = []
		self.dfs_num = {}
		self.AdjList = {}
		self.accounts = {} 
		self.interactions = {}
		self.update()

	def getAccounts(self):
		return self.accounts 
	def update(self):
		self.num = 0
		with open('./csvs/num.csv') as csv6_file:
			csv6_reader = csv.reader(csv6_file, delimiter=',')
			line_count = 0
			for row in csv6_reader:
				if(len(row) == 2):
					self.num = int(row[0])
		self.accounts = {} 
		with open('./csvs/accounts.csv') as csv_file:

			csv_reader = csv.reader(csv_file, delimiter=',')
			line_count = 0
			for row in csv_reader:
				if len(row) >= 3:
					self.accounts[row[0]] = {'name' : row[1], 'covid' : row[2]} #FORMAT: ID, Bluetooth IP, Account Name, Has Covid 
					self.AdjList[row[0]] = []
					self.dfs_num[row[0]] = self.UNVISITED
					#print("ip:", row[0], "  name:", self.accounts[row[0]]['name'],"  covid:", self.accounts[row[0]]['covid'])
					line_count += 1

			#print(f'Processed {line_count} lines.')

		self.interactions = {}
		with open('./csvs/interactions.csv') as csv_file2:
			csv_reader2 = csv.reader(csv_file2, delimiter=',')
			line_count = 0
			for row in csv_reader2:
				if len(row) >= 7:
					self.interactions[line_count] = {'id1' : row[0], 'id2' : row[1], 'coordN' : row[2], 'coordW' : row[3], 'day' : row[4], 'month' : row[5], 'year' : row[6]} #FORMAT: ID1, ID2, coordN, coordW, day, month, year
					#print("id1:", self.interactions[line_count]['id1'],"  id2:", self.interactions[line_count]['id2'],"   coordN:", self.interactions[line_count]['coordN'],"  coordW:", self.interactions[line_count]['coordW'], "  day:", self.interactions[line_count]['day'],  "  month:", self.interactions[line_count]['month'],  "  year:", self.interactions[line_count]['year'])
					line_count += 1
			#print(f'Processed {line_count} lines.')
	def getInteractions(self): 
		return self.interactions

	def addAccount(self, accountIP, accountName, hasCovid): #writes a new account to ./csvs/accounts.csv, reloads graph to account for change
		with open('./csvs/accounts.csv', mode='w') as csv_file3:
			csv_writer = csv.writer(csv_file3, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for key in self.accounts:
				#print("name:", self.accounts[key]['name'],"  covid:", self.accounts[key]['covid'])
				csv_writer.writerow([key, self.accounts[key]['name'], self.accounts[key]['covid']])
			csv_writer.writerow([accountIP, accountName, hasCovid])
		self.num+=1
		with open('./csvs/num.csv', mode='w') as csv_file7:
			csv_writer7 = csv.writer(csv_file7, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			csv_writer7.writerow([self.num, 0])

	def addInteraction(self, accountID_1, accountID_2, coordN, coordW, day, month, year): #writes a new interaction to ./csvs/interactions.csv, reloads graph to account for change
		with open('./csvs/interactions.csv', mode='w') as csv_file4:
			csv_writer2 = csv.writer(csv_file4, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for key in self.interactions:
				csv_writer2.writerow([self.interactions[key]['id1'], self.interactions[key]['id2'],self.interactions[key]['coordN'], self.interactions[key]['coordW'],self.interactions[key]['day'], self.interactions[key]['month'], self.interactions[key]['year']])
			csv_writer2.writerow([accountID_1, accountID_2, coordN, coordW, day, month, year])

	def loadGraph(self):
		self.update()
		#print(self.AdjList)
		for key in self.interactions: 
			thisGuy = self.interactions[key]['id1']
			thisList = self.AdjList[thisGuy]
			thisList.append([self.interactions[key]['id2'], self.interactions[key]['coordN'], self.interactions[key]['coordW'], self.interactions[key]['day'], self.interactions[key]['month'], self.interactions[key]['year']])
			self.AdjList[thisGuy] = thisList
			thisGuy2 = self.interactions[key]['id2']
			thisList = self.AdjList[thisGuy2]
			thisList.append([self.interactions[key]['id1'], self.interactions[key]['coordN'], self.interactions[key]['coordW'], self.interactions[key]['day'], self.interactions[key]['month'], self.interactions[key]['year']])
			self.AdjList[thisGuy2] = thisList
		# for key in self.AdjList: 
			#print("Key:",key,"    List:",self.AdjList[key])

	def dfs(self, IP): 
		self.CC.append(IP)
		self.dfs_num[IP] = self.VISITED
		for neighbor in self.AdjList[IP]:
			if(self.dfs_num[neighbor[0]] == self.UNVISITED):
				self.dfs(neighbor[0])


	def getConnections(self,IP): #returns connected component with user's account IP
		self.loadGraph()
		self.CC = []
		self.connectedInteractions = []
		self.dfs(IP)
		#print("CC:",self.CC)
		for key in self.interactions: 
			if self.interactions[key]['id1'] in self.CC and self.interactions[key]['id2'] in self.CC: 
				thisInteraction = [self.interactions[key]['id1'], self.interactions[key]['id2'], self.interactions[key]['coordN'], self.interactions[key]['coordW'], self.interactions[key]['day'], self.interactions[key]['month'], self.interactions[key]['year']]
				#print(thisInteraction)
				self.connectedInteractions.append(thisInteraction)

		#CC has the IPs of the connected component, connectedInteractions holds all the interactions between two people who are both in the connected component (to be used for building the user's personalized map)
												  # connectedInteractions format: id1, id2, coordN, coordW, day, month, year
		return [self.CC,self.connectedInteractions]
