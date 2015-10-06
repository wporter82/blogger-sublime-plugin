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

		# Add a pre tag around code blocks
		codeTypes = ["java","coldfusion","c","c++","c/c++"]
		for codeType in codeTypes:
			# searchString = '\n' + codeType
			codeBlock = self.view.find_all('(?<=' + codeType + ':\n)((?!\n\n).|\n)+?(?=\n\n)',sublime.IGNORECASE)
			codeBlock.reverse()
			for block in codeBlock:
				self.view.insert(edit, block.end(),"\n</pre>\n")
				self.view.insert(edit, block.begin(),"<pre>\n")

		# Add <br> to the end of each line
		newLines = self.view.find_all('\n')
		newLines.reverse()
		for line in newLines:
			# Check if the beginning of the line has a <pre> or </pre> tag and
			# skip it since that text is <pre> formatted
			newRegion = sublime.Region(line.begin()-4,line.begin())
			leftOfNewLine = self.view.substr(newRegion)
			print(leftOfNewLine)
			if leftOfNewLine != "pre>":
				self.view.replace(edit, line, "<br>\n")