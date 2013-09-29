
"""
This script is used to post the weekly runnit posts.

* Sunday Achievement Thread
* Mornic Monday Thread
* Friday Picture Thread 
  - Will collect the top 3 posts from the previous week's thread and update
    body accordingly.
~ A Cron job will kick off the script everyday at 6am MST. 
~ The script will determine if there is any posts to be made on that day.
  This way, we don't have to mess with the cronjob and different parameters etc.
~ The post contents will be stored in a file. This way, the script doesn't
  need to change if the content changes.
"""
import datetime
import os
import praw
import logging
import re
from authentication import USERNAME, PASSWORD

day_to_post = { 6:['Accomplishment','Training'], # Sunday
                1:['Question'],                  # Tuesday
                5:['Picture'] }                   # Friday


def login():
  r = praw.Reddit('Runnit-Bot ver 0.1. - by /u/deds_the_scrub. Here to')
  r.login(USERNAME, PASSWORD)
  return r

def work_to_do():
  ''' This function will check the day of the week and 
     return the type of post that should be posted. 
     This could result in None.
  '''
  day = datetime.date.today().weekday()
  if day in day_to_post:
    return day_to_post[day]
  return None 
    
def submit_post(reddit_session, post_type):
  fname = "{}.txt".format(post_type)
  try: 
    with open(fname) as f:
      contents = f.read()
      title = contents.splitlines()[0]
      contents = "\n".join(contents.splitlines()[1:])
      contents = update_post(reddit_session,title,contents,post_type)
#result = reddit_session.submit('reddit_api_test',title, text=contents)
      logging.debug(str(contents))
      print contents 
  except IOError:
   print 'Oh dear.'
   exit(-2)

def update_post(reddit_session, title,body,post_type):
  if post_type != "Picture":
    return body 
  result = reddit_session.search(title,subreddit="running",sort="new").next()
  submission = reddit_session.get_submission(submission_id=result.id, comment_sort='top')
  for comment in zip(submission.comments[:3],["top","runner up", "second runner up"]): 
    s = "/u/" + str(comment[0].author) + " grabbed the " + comment[1] + " spot with these pictures:"
    for image in enumerate(re.findall("https?://(?:[a-z\-]+\.)+[a-z]{2,6}(?:/[^/#?]+)+\.(?:jpe?g|gif|png)",comment[0].body)):
      s += "[" + str(int(image[0])+1) + "](" + image[1] + ") "
    print s
    body = re.sub(r"(?m)^\*+\s+(\<"+comment[1]+"\>)",s,body)

  return body
  
def message_me(reddit_session, result):
  title = 'New post added'
  body= 'I was able to login and send you a message!'
  #body = '[%s](%s)' % (result.title, result.permalink)
  #reddit_session.send_message('deds_the_scrub', title, body)

def start_bot():
  work = work_to_do() 
  if work is None:
    exit(-1)

  r = login()
  for job in work:
    post = submit_post(r,job)
    message_me(r,post) 

if __name__ == '__main__':
   logging.basicConfig()
   logging.info("Starting")
   start_bot()
   logging.info("Ending")
 
