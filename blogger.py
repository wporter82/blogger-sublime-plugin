import sublime, sublime_plugin, webbrowser
import sys, os
# make sure we can include extra libraries
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import httplib2
from oauth2client import client
from oauth2client.file import Storage
import markdown

# *****************************************************************************************
# Helper function to post to blogger
# *****************************************************************************************
def post(post_title, post_contents):
	def get_blog_url():
		sublime.active_window().show_input_panel("Paste the blog URL here:", "http://", save_blog_url, None, None)

	def save_blog_url(blog_url):
		settings = sublime.load_settings(settings_file)
		settings.set("blog_url",blog_url)
		sublime.save_settings(settings_file)
		get_blog_info(blog_url)

	def get_blog_info(blog_url):
		credentials = credential_storage.get()
		http_auth = credentials.authorize(httplib2.Http())
		from googleapiclient.discovery import build
		blogger_service = build('blogger','v3',http=http_auth)
		result = blogger_service.blogs().getByUrl(url=blog_url).execute()
		blog_id = result['id']
		post_blog_entry(blog_id, blogger_service)

	def post_blog_entry(blog_id, blogger_service):
		request = blogger_service.posts().insert(blogId=blog_id,body={"title":post_title,"content":post_contents},isDraft=True)
		result = request.execute()
		sublime.status_message("Posted: (" + result['title'] + ") as a draft")
		pass
		
	def save_credentials(code):
		credentials = flow.step2_exchange(code)
		credential_storage.put(credentials)
		blog_url = sublime.load_settings(settings_file).get("blog_url")
		if blog_url == None:
			get_blog_url()
		else:
			get_blog_info(blog_url)

	print(post_title)
	# Load the client_secrets from a file and have Google show a page with the code to paste in Sublime
	secrets_file = os.path.join(os.path.dirname(__file__),"client_secrets.json")
	try:
		flow = client.flow_from_clientsecrets(secrets_file,
						scope='https://www.googleapis.com/auth/blogger',
						redirect_uri='urn:ietf:wg:oauth:2.0:oob')
	except:
		sublime.error_message('API Secrets file not found: ' + secrets_file)
		raise Exception('Blogger Plugin not loaded due to file not found: ' + secrets_file)
	# Use plaintext storage for testing and move to a more secure method later
	credential_storage = Storage(os.path.join(os.path.dirname(__file__),"credentials_file"))
	settings_file = "Blogger.sublime-settings"

	
	credentials = credential_storage.get()
	if credentials == None:
		url = flow.step1_get_authorize_url()
		webbrowser.open(url,new=2,autoraise=True)

		# input as async so don't try to do anything else after this call
		sublime.active_window().show_input_panel("Paste code from Google here:", "", save_credentials, None, None)
	else:
		blog_url = sublime.load_settings(settings_file).get("blog_url")
		if blog_url == None:
			get_blog_url()
		else:
			get_blog_info(blog_url)
	


# *****************************************************************************************
# FORMATTING (custom markdown)
# *****************************************************************************************
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
			self.view.replace(edit, gt, "&gt;")

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

# *****************************************************************************************
# MARKDOWN (using python-markdown library)
# *****************************************************************************************
class BloggerMarkdownCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# Convert markdown code into html
		newHtml = markdown.markdown(self.view.substr(sublime.Region(0, self.view.size())))
		self.view.replace(edit, sublime.Region(0, self.view.size()), newHtml)


# *****************************************************************************************
# POST VIA EMAIL
# *****************************************************************************************
class BloggerPostEmailCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command('blogger_format')
		# Send an email with the formatted post
		# Just append that we sent an email for now, until it is implemented.
		self.view.insert(edit,self.view.size(),"\n\nEmail Sending not enabled yet.")


# *****************************************************************************************
# POST VIA API (without formatting first)
# *****************************************************************************************
class BloggerPostViaApiNoFormatCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		def on_done(post_title):
			post_contents = self.view.substr(sublime.Region(0, self.view.size()))
			post(post_title,post_contents)

		sublime.active_window().show_input_panel("Post Title:", "", on_done, None, None)

# *****************************************************************************************
# POST VIA API (formatting first)
# *****************************************************************************************
class BloggerPostViaApiCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		def on_done(post_title):
			self.view.run_command('blogger_format')
			post_contents = self.view.substr(sublime.Region(0, self.view.size()))
			post(post_title,post_contents)
			
		sublime.active_window().show_input_panel("Post Title:", "", on_done, None, None)
