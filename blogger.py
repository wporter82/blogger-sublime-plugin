import sublime, sublime_plugin

class BloggerFormatCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# Replace < and > with &lt; and &gt;
		lessThan = self.view.find_all('<')
		lessThan.reverse()
		for lt in lessThan:
			self.view.replace(edit, lt, "&lt;")

		greaterThan = self.view.find_all('>')
		greaterThan.reverse()
		for gt in greaterThan:
			self.view.replace(edit, gt, "&lt;")

		codeTypes = ["java","coldfusion","c","c++","c/c++","python"]
		
		# Add a pre tag around code and output blocks
		preTypes = codeTypes
		preTypes.append("output")
		for preType in preTypes:
			# searchString = '\n' + preType
			codeBlock = self.view.find_all('(?<=' + preType + ':\n)((?!\n\n).|\n)+?(?=\n\n)',sublime.IGNORECASE)
			codeBlock.reverse()
			for block in codeBlock:
				self.view.insert(edit, block.end(),"\n</pre>\n")
				self.view.insert(edit, block.begin(),"<pre>\n")

		# Add code style to code pre tags
		

		# Add <br> to the end of each line
		newLines = self.view.find_all('\n')
		newLines.reverse()
		for line in newLines:
			# Check if the beginning of the line has a <pre> or </pre> tag and
			# skip it since that text is <pre> formatted
			newRegion = sublime.Region(line.begin()-4,line.begin())
			leftOfNewLine = self.view.substr(newRegion)
			# Check to see if the first char of the line is a tab and skip it
			# Get the whole line as a new region
			wholeLine = self.view.line(line)
			# Get just the first char of the line
			beginOfLineRegion = sublime.Region(wholeLine.begin(),wholeLine.begin()+1)
			beginOfLine = self.view.substr(beginOfLineRegion)

			if leftOfNewLine != "pre>" and beginOfLine != '\t':
				self.view.replace(edit, line, "<br>\n")

class BloggerPostEmailCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('blogger_format')
		# Send an email with the formatted post
		self.view.insert(edit,self.view.size(),"\n\nEmail Sent. Blog Post Posted!")