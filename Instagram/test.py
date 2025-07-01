from instagrapi import Client

cl = Client()
cl.login('enhidna', 'Mytimeisprecious#012345')
hashtag = 'python'

top_medias = cl.hashtag_medias_top(hashtag, amount=10)

print(top_medias)