import webhoseio
import os
import re
def store_article(title,content):
	os.chdir(r'e:\GCSJ\webhoseFacebookNews')
	if len(title) > 100:
		title = title[:100]
	file = title + '.txt'
	file = re.sub(r"[\/\\\:\*\?\"\<\>\|]","",file)
	if os.path.exists(file):
		return
	fp = open(file,'w',encoding='utf-8')
	fp.write(content)
	fp.close()
def parse_output(output):
	for i in range(len(output['posts'])):
		title ,content =  '',''
		try:
			title = output['posts'][i]['title'].lower().strip()
			content = output['posts'][i]['text'].strip()
		except Exception as e:
			continue
		if len(title) > 0 and len(content) > 0:
			store_article(title,content)

webhoseio.config(token="0b31ded8-f4ad-4384-a877-bf133832a373")
query_params = 
{
	"q": "Facebook language:english site_type:news has_video:false",
	"ts": "1509285521532",
	"sort": "relevancy"
}
output = webhoseio.query("filterWebContent", query_params)
resNums = output['totalResults']
curPage = 1
pageNums = resNums // 100
while curPage < pageNums:
	parse_output(output)
	output = webhoseio.get_next()
	curPage += 1