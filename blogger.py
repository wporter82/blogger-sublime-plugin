import sublime, sublime_plugin, webbrowser
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import httplib2
from oauth2client import client
from oauth2client.file import Storage


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

		codeTypes = ["java","js","coldfusion","cpp","c","csharp","html","css","python","vb","powershell","ruby","bash","shell","sql"]

		# Add a pre tag around code and output blocks
		preTypes = codeTypes[:] # Copy the array into a new variable
		preTypes.append("output")
		for preType in preTypes:
			# searchString = '\n' + preType
			codeBlock = self.view.find_all('(?<=' + preType + ':\n)((?!\n\n(?!\t)).|\n)+?(?=\n\n(?!\t))',sublime.IGNORECASE)
			codeBlock.reverse()
			for block in codeBlock:
				self.view.insert(edit, block.end(),"\n</pre>\n")
				self.view.insert(edit, block.begin(),"<pre>\n")

		# Add code style to code pre tags
		for codeType in codeTypes:
			preTags = self.view.find_all(codeType + ':\n<pre>',sublime.IGNORECASE)
			preTags.reverse()
			for tag in preTags:
				self.view.insert(edit,tag.end()-1," class=\"brush: " + codeType + "\"")

		# Add <br> to the end of each line except for certain cases
		newLines = self.view.find_all('\n')
		newLines.reverse()
		for line in newLines:
			# Get the whole line as a new region
			wholeLine = self.view.line(line)
			previousLine = self.view.line(line.begin()-1)
			nextLine = self.view.line(line.end()+1)

			# Check to see if the first char of the line is a tab and skip it
			# Get just the first char of the line
			beginOfLine = self.view.substr(sublime.Region(wholeLine.begin(),wholeLine.begin()+1))
			beginOfPrevLine = self.view.substr(sublime.Region(previousLine.begin(),previousLine.begin()+1))
			beginOfNextLine = self.view.substr(sublime.Region(nextLine.begin(),nextLine.begin()+1))

			#Get the first 4 chars of the line to check for the <pre> tag
			first4chars = self.view.substr(sublime.Region(wholeLine.begin(),wholeLine.begin()+4))

			if beginOfLine != '\t' and first4chars != '<pre' and first4chars != '</pr' and beginOfPrevLine != '\t' and beginOfNextLine != '\t':
				self.view.replace(edit, line, "<br>\n")

class BloggerPostEmailCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('blogger_format')
		# Send an email with the formatted post
		# Just append that we sent an email for now, until it is implemented.
		self.view.insert(edit,self.view.size(),"\n\nEmail Sent. Blog Post Posted!")

class BloggerAuthenticateCommand(sublime_plugin.TextCommand):
	# Load the client_secrets from a file and have Google show a page with the code to paste.
	flow = client.flow_from_clientsecrets('client_secrets.json',
						scope='https://www.googleapis.com/auth/blogger',
						redirect_uri='urn:ietf:wg:oauth:2.0:oob')
	# Use plaintext storage for now and move to a more secure method later
	storage = Storage(os.path.join(os.path.dirname(__file__),"credentials_file"))

	def run(self, edit):
		credentials = self.storage.get()
		if credentials == None:
			url = self.flow.step1_get_authorize_url()
			webbrowser.open(url,new=2,autoraise=True)

			# input as async so don't try to do anything else after this call
			sublime.active_window().show_input_panel("Paste code from Google here:", "", self.save_credentials, None, None)
		else:
			self.use_credentials(credentials)
	
	def save_credentials(self, code):
		credentials = self.flow.step2_exchange(code)
		self.storage.put(credentials)
		self.use_credentials(credentials)

	def use_credentials(self, credentials):
		http_auth = credentials.authorize(httplib2.Http())
		# from apiclient.discovery import build
		print(credentials)