import json
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, jsonify
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm, ZooKeeperForm
from .. import db
from ..models import Permission, Role, User, Post, Comment, Dog
from ..decorators import admin_required, permission_required


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           show_followed=show_followed, pagination=pagination)

@main.route('/dog')
def dog():
    
    return render_template('dog.html', dog=dog)




#@main.route('/dog/<username>')
#def dog(username):
#    dog = Dog.query.filter_by(name=name).first_or_404()
#    page = request.args.get('page', 1, type=int)
#    pagination = dog.posts.order_by(Post.timestamp.desc()).paginate(
#        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
#        error_out=False)
#    posts = pagination.items
#    return render_template('dog.html', dog=dog, posts=posts,
#                           pagination=pagination)




@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.dogs = form.dogs.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.dogs.data = current_user.dogs
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.dogs = form.dogs.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.dogs.data = user.dogs
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('Your comment has been published.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/watchZookeeper', methods=['GET', 'POST'])
def watchZookeeper():
	#import test_kafka
	#kafkaStart = startKafka()
	#import sys, os
	#global diskeyStartKafka
	#import kafka
	##print 'going to start zookeepr & kafka now'
	#diskeyStartKafka = os.system('/home/joe/workspace/flasky/kafka-utils/list-topics.sh')
	#flash(diskeyStartKafka)
	#consumer = kafka.KafkaConsumer(bootstrap_servers=['192.168.1.130:9092'])
	#flash(consumer.topics())
	def subfunction():
		return True
        return render_template('watchZookeeper.html')



@main.route('/_kafkaTopics', methods=['GET', 'POST'])
def listKafkaTopics():
    import kafka, sys, os 
    from array import array
    consumer = kafka.KafkaConsumer(bootstrap_servers=['192.168.1.130:9092'])
    kafkaTopics = []
    kafkaRawTopic = consumer.topics()
    kafkaTopics.append(kafkaRawTopic)
    kafkaTopics2 = ["hello mr bubba. this is great!","jeeze bubba"]
    kafkaTopics2.append(kafkaRawTopic)
    kafkaTopics3 = kafkaTopics2[2]
    #kafkaTopics3Encoded = kafkaTopics3.encode('utf-8')
    #firstTopic = kafkaTopics[1]
    #flash(firstTopic)
    #resp = make_response(redirect(url_for('main.watchZookeeper')))
 #   global kafkaTopics3
     
    
    #kafkaTopics3 = os.system('/home/joe/workspace/flasky/kafka-utils/list-topics.sh')
   
    #kafkaTopics4 = kafkaTopics3[0]
    #def subfunction():
#		return True
    #resp = make_response(flash(consumer.topics(0)))
    #resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    #return jsonify(kafkaTopics2)
    #return request.get_json(force=True)
    #return json.dumps({'status':'OK', 'diskeyText' :kafkaTopics2}) 
    return json.dumps({'status':'OK', 'diskeyText' :kafkaTopics2[1]}) 



@main.route('/_StartKafkaProducer', methods=['GET', 'POST'])
def startKafkaProducer():
	import kafka, sys, os, time
	topic = "not a topic"
	#producer = kafka.KafkaProducer(boostrap_servers=['192.168.1.130:9092'])
	
	producer = kafka.KafkaProducer(bootstrap_servers='192.168.1.130:9092')
	topic_name = "cryBert"
	producer_id = "diskeyteststart"
	value_messg = "just sent via kafka, bubba2"
	#producer.send(topic=topic_name, value=value_messg)
	#producer.send(topic=topic_name, value=value_messg, timestamp_ms=time.time())		
	#producer.close()
	message = "Opened a producer"
	
	return json.dumps({'status':'started producer OK', 'producer' :producer_id})
        
@main.route('/_StartKafkaConsumer', methods=['GET', 'POST'])
def startKafkaConsumer():
	import kafka, array
	from kafka import KafkaConsumer
	#topic = "cryBert"
	#messages = "yo"
	numberOfMessages = 5
	consumer = kafka.KafkaConsumer("cryBert", group_id='diskeyGroup', bootstrap_servers='192.168.1.130:9092' , enable_auto_commit=True)	
	#consumer = kafka.KafkaConsumer("cryBert", group_id='diskeyGroup', bootstrap_servers='192.168.1.130:9092',value_deserializer=lambda m: json.loads(m.decode('ascii')))
	print 'started a consumer'
	#consumer = kafka.KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('ascii')))
	consumer.subscribe(topics=('cryBert'), pattern=None, listener=None)
	print 'subscribed to these topic(s):'	
	print consumer.topics()
 	#consumer = KafkaConsumer(value_deserializer=lambda m: json.loads(m.decode('ascii')))
	print 'deserialized consumer'
	numberOfMessages = numberOfMessages + 1
	print numberOfMessages
	print consumer.partitions_for_topic('cryBert') 
	print consumer.assignment()
	consumer.poll()	
	consumer.seek_to_end()	
	consumer.poll()	
	lastMesssage = 'made it to the end'
	print lastMesssage
	
	print	consumer.subscription()
	messages = ["hi nice bear"]
 	
	  
	consumer.poll()
	consumer.seek_to_beginning()
	for message in consumer:
	    # message value and key are raw bytes -- decode if necessary!
	    # e.g., for unicode: `message.value.decode('utf-8')`
            print len(messages) 
	    messages.append(message.value)
	    #if len(messages	
	    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
		                                  message.offset, message.key,
		                                  message.value))
	    print "wahoo no indent issue"
	    if len(messages) == 2:
	    	consumer.unsubscribe()
	    	print 'unsubscribed from consumer'
	    	return json.dumps({'status': 'success', 'consumer':messages})
	#consumer.unsubscribe()	
	#print 'Closed a consumer'
	consumer.unsubscribe()
	consumer.close()
	#return json.dumps({'status': 'success', 'numberOfMessages':numberOfMessages})
	return json.dumps({'status': 'success', 'consumer':messages})

@main.route('/_getMessage', methods=['GET', 'POST'])
def getMessage():
	import kafka, array, time
	from kafka.errors import (
	    KafkaError,
	    KafkaTimeoutError
	)	
	messages = []
	consumer = kafka.KafkaConsumer('cryBert', bootstrap_servers=['192.168.1.130:9092'], group_id='diskeygroup', enable_auto_commit=True )
	#dummy poll
	consumer.poll(timeout_ms=100, max_records=None)
	#go to end of the stream
	consumer.seek_to_beginning()
	numOfEntries = 0
	numOfMessages = len(messages) 
	#start iterate
	print 'about to start loop'
	for message in consumer:
	    print 'made it into the loop'
	    try: 
		print 'i tried once again'	    	
		print(message.offset)
	    	messages.append(message.value)
		numOfEntries = numOfEntries + 1
		numOfMessages = len(messages)
		print numOfEntries
		print numOfMessages
		if numOfMessages < numOfEntries:
			print numOfEntries
			print numOfMessages
			return json.dumps({'status': 'success', 'consumer':messages})	
	    except KafkaError as kafka_error:
	    	print 'some kafka error'
		return json.dumps({'status': 'success', 'consumer':messages})	
	    except Exception:
		return json.dumps({'status': 'success', 'consumer':messages})
		print 'empty value here'
	    print 'made it to the bottom of the loop'
	print 'I got out of the loop' 
	#consumer.close()
	return json.dumps({'status': 'success', 'consumer':messages})


@main.route('/_StopKafkaConsumer', methods=['GET', 'POST'])
def stopKafkaConsumer():
	import kafka
	topic = "cryBert"
	consumer = kafka.KafkaConsumer(bootstrap_servers='192.168.1.130:9092')
	consumer.unsubscribe()		
	consumer.close()
	return json.dumps({'status': 'OK','topic': topic})

@main.route('/_SendKafkaMessage', methods=['GET', 'POST'])
def sendKafkaMessage():
	import kafka, time
	producer_id = "diskeytestsend"
	producer = kafka.KafkaProducer(bootstrap_servers='192.168.1.130:9092')
	value_messg = "just sent via kafka, bubba232457"
	topic_name = "cryBert"	
	producer.send(topic=topic_name, value=value_messg)		
	sendProducerMessage = "Sent a message over the wire"
	producer.flush()
	producer.close() 	
	return json.dumps({'status': 'OK sending this message: ','sendProducerMsg': sendProducerMessage})



@main.route('/_StopKafkaProducer', methods=['GET', 'POST'])
def stopKafkaProducer():
	import kafka
	producer_id = "diskeyteststop"
	producer = kafka.KafkaProducer(bootstrap_servers='192.168.1.130:9092')
	producer.flush()	
	producer.close()
	return json.dumps({'status': 'OK stop producer','producer': producer_id})


from query_service import QueryService
from flask_restful import Api, Resource, reqparse
from flask import Flask, render_template, send_from_directory

api = Api(main)
api.add_resource(QueryService, '/news_urls')


@main.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response



@main.route("/NLP-Demo")
def nlpDemo():
    return render_template("nlp-demo.html")



#@main.route('/publicScripts/', methods=['GET', 'POST'])
#def runSomeScript():
#    return render_template('watchZookeeper.html')


#@main.route('/watchZookeeper2', methods=['GET', 'POST'])
#def watchZookeeper2():
#        flash('Hello mr dinghey todays date is Nov17, like seriously')
#        return render_template('watchZookeeper.html')

#@main.route('test_kafka')
#def test_kafa():
	
#	return 

