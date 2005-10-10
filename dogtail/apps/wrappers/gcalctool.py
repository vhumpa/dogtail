import dogtail.tree

class GCalcTool(dogtail.tree.Application):
	def clickNumeral(self, num):
		self.button('Numeric %s'%num).click()	
	
	def typeNumber(self, num, base):
		digits = []
		while num>0:
			digit = num%base
			digits.insert(0, digit)
			num = num/base
		if len(digits)==0:
			digits=[0]
		# print digits
		for digit in digits:
			self.clickNumeral(digit)
		
	def clearEntry(self):
		self.button('Clear entry').click()

	def doBinaryInfixOp(self, a, b, button):
		self.clearEntry()
		self.typeNumber(a, 10)
		self.button(button).click()
		self.typeNumber(b, 10)
		self.button('Calculate result').click()
		return self.getText()

	def doSum(self, a, b):
		return self.doBinaryInfixOp(a, b, 'Add')

	def doProduct(self, a, b):
		return self.doBinaryInfixOp(a, b, 'Multiply')
		
	def getText(self):
		return self.child(roleName='edit bar').text
