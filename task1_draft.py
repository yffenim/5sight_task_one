import re 
import pymongo 
from dateutil.parser import parse 

### test string
test = """
# FIRST VERSE

I #remember #"you" well in the Chelsea #'Hotel'
You were talking so brave and so sweet
Giving me head on the unmade bed
While the limousines wait in the street

# THE CHORUS

Ah, but #you got away, didn't you, baby?
#"You" just threw it all to the ground #!

# LAST VERSE

I #don't mean to suggest that I loved you the best
I #"can't" keep track of each fallen robin
I remember you well in the Chelsea Hotel
#'That's' all, my little darling, I don't even think of you that often

"""

# helpers
def p(o):
    print(o)

def is_date_or_time(str, fuzzy=True):
    try:
        parse(str, fuzzy=fuzzy)
        return True

    except ValueError:
        return False 


# make string into usable array
def make_posts_arr(str):
	regex_ttl = "(#\s)" 
	posts = re.split(regex_ttl, str)
	
	while "" in posts:
			posts.remove("")

	i = 0
	while i < len(posts):
		if i % 2 != 0:
			posts[i] = posts[i-1] + posts[i]
		i += 1

	while '# ' in posts:
		posts.remove('# ')
	
	return posts 


def make_post_hash(posts):
	hsh = {}
	res = []

	j = 0
	while j < len(posts):
		# get and add the post TITLE to hash
		split_post = posts[j].split("\n\n")
		split_title = split_post[0].strip()
		hsh.update({"title": split_title})
	
		# check if title is a DATE OR TIME and add to hash
		### if we want the # removed from the date ###
		if is_date_or_time(split_title): 
			split_title = split_title.strip("# ")		
			hsh.update({"whence": split_title})

		# add the PARAGRAPHS to hash 
		split_post.remove(split_post[0])
		# remove the empty arr elements
		body = [var for var in split_post if var]
		hsh.update({"paragraphs": body})

		# get the tags
		tags_arr = []
		k = 0
		while k < len(body):	
			words = body[k].split()
			regex_tag = '#\S+' 
			n = 0
			while n < len(words):
				if re.match(regex_tag, words[n]): tags_arr.append(words[n])
				n += 1
			k += 1

		hsh.update({"tags": tags_arr})

		# add hash object to final result
		res.append(hsh.copy())
		j += 1
	return res


def add_to_db(arr):
	mongo_uri = "mongodb://localhost:27017/"  
	client = pymongo.MongoClient(mongo_uri)

	# turns out this does create the db and col
	db = client["task_1"]
	collection = db["dev"]

	collection.insert_many(arr)

posts = make_posts_arr(test)
final_arr = make_post_hash(posts)
add_to_db(final_arr)
