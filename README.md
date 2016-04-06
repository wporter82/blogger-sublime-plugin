# blogger-sublime-plugin
Plugin for Sublime Text 3 that formats and posts to a blog. Code snippets are formatted for use with 
<a href="http://alexgorbatchev.com/SyntaxHighlighter/">SyntaxHighlighter</a>.

This plugin is meant to make posting code snippits to a Blogger blog easier by auto-formatting for the web and using
SyntaxHighlighter to make it more visible. A blogpost will be coming soon showing how to set it up.

Dependecies:
<ul>
	<li>Included:
		<ul>
			<li><a href="https://github.com/google/oauth2client">oauth2client</a></li>
			<li><a href="https://pypi.python.org/pypi/six">six</a></li>
			<li><a href="https://github.com/google/google-api-python-client">google-api-python-client</a></li>
			<li><a href="https://github.com/jcgregorio/httplib2">httplib2</a></li>
			<li><a href="https://github.com/uri-templates/uritemplate-py/">uritemplate</a></li>
		</ul>
	</li>
	<li>Downloaded via Package Control
		<ul>
			<li><a href="https://github.com/waylan/Python-Markdown">python-markdown</a></li>
		</ul>
	</li>
</ul>
<br>
Formatting:<br>
Here is an example of how formatting is done.<br>
<br>
<pre>
The first line will be the post title.

Typically a paragraph or short description of the code to come will be next.
It can span multiple lines but should never be indented. Code snippets should
be preceded with a language as a caption and will be used to determine what
brush will be used to highlight the syntax.

Java:
	// Code should be indented by 1 or more tabs
	int a = 1;

	// It can have blank lines in between but should
	// always be indented
	return true;

You can have normal text here before you add an output block. This block
should look just like the code block but have "Output:" before the text.

Output:
	The output block should always be indented as well.

You can have as many code and output blocks as you wish. They should always
have a blank line before and after to break up the flow.
</pre>
