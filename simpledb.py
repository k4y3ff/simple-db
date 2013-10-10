import sys

class SimpleDB(object):
	
	def __init__(self):
		# Primary key-value store.
		self.master_dict = {}
		
		# "Stack" of KV store versions, used for nested transactions.
		self.dict_stack = []
		
		# Index of current KV store version in dict_stack; set to -1 if current
		# transaction is operating on master_dict.
		self.block_index = -1
		
		# Set of keys that are currently set to None; when any of these keys
		# are retrieved, "NULL" should be returned.
		self.null_keys = set()

	# Starts a new transaction block.
	def begin(self):
		self.block_index += 1
		self.dict_stack.append({})

	# Commits all changes in current transaction blocks to the master_dict.
	def commit(self):
		if self.block_index == -1:
			return "UNNECESSARY COMMIT"
		else:
			for i in range(0, self.block_index + 1):
				for key, value in self.dict_stack[i].items():
					self.master_dict[key] = value
			for i in range(self.block_index, -1, -1):
				del self.dict_stack[i]
			self.block_index = -1

	# Retrieves the value stored under the variable "key". Returns "NULL" if
	# the variable name has not been set.
	def get(self, key):
		if self.block_index == -1:
			if key in self.master_dict:
				if self.master_dict[key] != None:
					return self.master_dict[key]
				else:
					return "NULL"
			return "NULL"
		else:
			for i in range(self.block_index, -1, -1):
				if key in self.dict_stack[i]:
					if self.dict_stack[i] != None:
						return self.dict_stack[i][key]
			if key in self.master_dict:
				if self.master_dict[key] != None:
					return self.master_dict[key]
				else:
					return "NULL"

	# Returns the number of variables equal to "val". Returns 0 if no variables
	# are equal to "val".
	def numequalto(self, val):
		i = 0
		if self.block_index != -1:
			for j in range(self.block_index, -1, -1):
				for key, value in self.dict_stack[j].items():
					if value == val and not key in self.null_keys:
							i += 1
		for key, value in self.master_dict.items():
			if value == val and not key in self.null_keys:
				i += 1
		return i

	# Rolls back all of the commands from the most recent transactional block.
	def rollback(self):
		if self.block_index == -1:
			return "NO TRANSACTION"
		else:
			for key in self.dict_stack[self.block_index].keys():
				if key in self.null_keys:
					self.null_keys.discard(key)
			del self.dict_stack[self.block_index]
			self.block_index -= 1

	# Sets a variable "key" to the value "val".
	def set(self, key, val):
		if self.block_index == -1:
			self.master_dict[key] = val
		else:
			self.dict_stack[self.block_index][key] = val
		self.null_keys.discard(key)

	# Splits a given command "command" into tokens, then calls appropriate
	# data command functions as appropriate.
	def switchboard(self, command):
		command = command.split()
		if command[0].upper() == "BEGIN" and len(command) == 1:
			self.begin()		
		elif command[0].upper() == "COMMIT" and len(command) == 1:
			return self.commit()		
		elif command[0].upper() == "END" and len(command) == 1:
			exit(0)
		elif command[0].upper() == "GET" and len(command) == 2:
			return self.get(command[1])
		elif command[0].upper() == "NUMEQUALTO" and len(command) == 2:
			count = self.numequalto(command[1])
			return count		
		elif command[0].upper() == "ROLLBACK" and len(command) == 1:
			return self.rollback()
		elif command[0].upper() == "SET" and len(command) == 3:
			self.set(command[1], command[2])
		elif command[0].upper() == "UNSET" and len(command) == 2:
			self.unset(command[1])
		else:
			return "INVALID COMMAND"

	# Unsets the variable "key".
	def unset(self, key):
		if self.block_index == -1:
			if key in self.master_dict:
				del self.master_dict[key]
			else:
				return "NULL"
		else:
			self.dict_stack[self.block_index][key] = "NULL"
		self.null_keys.add(key)

if __name__ == "__main__":
	simpledb = SimpleDB()

	# Continuously checks for incoming messages from the CLI, sends them to
	# the switchboard, and stores the database's response.
	while(True):
		return_message = simpledb.switchboard(sys.stdin.readline())

		# If the database returns something other than None (i.e. for 
		# valid "BEGIN", "COMMIT", "ROLLBACK", and "SET" commands), prints
		# prints the return message.
		if return_message != None:
			print return_message