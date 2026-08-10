import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialmedia_backend.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.files import File
from core.models import Profile, Post, Comment, Job, Message, Story

def populate():
    print("Clearing old data...")
    User.objects.exclude(is_superuser=True).delete()
    Job.objects.all().delete()
    Post.objects.all().delete()
    Message.objects.all().delete()
    Story.objects.all().delete()

    base_path = r"C:\Users\hp\.gemini\antigravity-cli\brain\afd6fac6-70f4-4653-9960-4842ec82db64"
    users_data = [
        {"username": "alice_smith", "email": "alice@example.com", "headline": "Senior Frontend Engineer at TechCorp", "exp": "TechCorp (2020-Present)\nWebDev Inc (2018-2020)", "avatar": os.path.join(base_path, "avatar_alice_1786189915081.jpg")},
        {"username": "bob_jones", "email": "bob@example.com", "headline": "Product Manager | Agile Enthusiast", "exp": "StartupXYZ (2021-Present)\nBigBank (2015-2021)", "avatar": os.path.join(base_path, "avatar_bob_1786189932065.jpg")},
        {"username": "carol_white", "email": "carol@example.com", "headline": "Data Scientist @ DataWorks", "exp": "DataWorks (2019-Present)", "avatar": os.path.join(base_path, "avatar_carol_1786189945608.jpg")},
        {"username": "david_brown", "email": "david@example.com", "headline": "Technical Recruiter", "exp": "RecruitMe (2022-Present)", "avatar": os.path.join(base_path, "avatar_david_1786189957353.jpg")}
    ]

    print("Creating users...")
    users = []
    for data in users_data:
        u = User.objects.create_user(username=data['username'], email=data['email'], password='password123')
        # Profile is automatically created by signals if there's a post_save signal.
        # Let's check if it exists, otherwise create it.
        profile, created = Profile.objects.get_or_create(user=u)
        profile.headline = data['headline']
        profile.experience = data['exp']
        profile.education = "University of Technology, B.S. Computer Science"
        profile.skills = "Python, React, Django, SQL"
        
        avatar_path = data.get('avatar')
        if avatar_path and os.path.exists(avatar_path):
            with open(avatar_path, 'rb') as f:
                profile.avatar.save(f"{u.username}_avatar.jpg", File(f), save=False)
        
        profile.save()
        users.append(u)

    print("Creating connections...")
    for u in users:
        profile = u.profile
        others = [other.profile for other in users if other != u]
        # Connect with 2 random people
        to_connect = random.sample(others, 2)
        for other_profile in to_connect:
            profile.connections.add(other_profile)

    print("Creating posts...")
    posts_data = [
        {"content": "Just launched our new React application! So proud of the team. #react #webdev", "image": None},
        {"content": "Attended a great conference on AI today. The future is incredibly exciting.", "image": os.path.join(base_path, "post_image_1_1786189969588.jpg")},
        {"content": "Looking for a Senior Python Developer to join my team. DM me if interested! #hiring #python", "image": None},
        {"content": "Can anyone recommend good resources for learning System Design?", "image": None},
        {"content": "After 5 years at BigBank, I'm thrilled to share that I'm starting a new position!", "image": None},
        {"content": "I can't believe how much WebAssembly is going to change the web. What are your thoughts?", "image": None},
        {"content": "Day 1 of 100 days of code! Started with Python fundamentals.", "image": None},
        {"content": "Does anyone have experience migrating from a monolithic architecture to microservices? I have some questions.", "image": None},
        {"content": "Check out this amazing article on Frontend performance optimization. Highly recommend reading it.", "image": None},
        {"content": "My team is organizing a local hackathon next weekend. Let me know if you want to join!", "image": None},
        {"content": "I finally passed the AWS Certified Solutions Architect exam! The hard work paid off.", "image": None},
        {"content": "Remote work is great, but sometimes I miss the impromptu whiteboard sessions in the office.", "image": None},
        {"content": "If you could only use one programming language for the rest of your life, what would it be and why?", "image": None},
        {"content": "Just finished reading 'Clean Code' by Uncle Bob. It completely changed how I write software.", "image": None},
        {"content": "Are AI assistants going to replace developers, or just make us 10x faster? Let's discuss.", "image": None},
        {"content": "What's the best setup for a home office? I'm looking to upgrade my monitor and chair.", "image": None},
        {"content": "Is it just me, or is CSS getting incredibly powerful lately with flexbox, grid, and new features?", "image": None},
        {"content": "I'm officially stepping down from my role at TechCorp to start my own venture. Wish me luck!", "image": None},
        {"content": "Just discovered a new open-source library that saved me hours of work today.", "image": None},
        {"content": "Does anyone actually enjoy writing tests, or is it just a necessary evil?", "image": None}
    ]
    posts = []
    for data in posts_data:
        author = random.choice(users)
        p = Post.objects.create(author=author, content=data['content'])
        
        img_path = data.get('image')
        if img_path and os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                p.image.save("post_image.jpg", File(f), save=True)
                
        posts.append(p)

    print("Adding likes and comments...")
    comments_data = [
        "Congratulations! That's huge.",
        "Interesting thoughts, I agree.",
        "Sending you a DM right now.",
        "Check out 'Designing Data-Intensive Applications', it's the best book.",
        "Great work team!"
    ]
    for p in posts:
        # Add random likes
        likers = random.sample(users, random.randint(0, 3))
        for liker in likers:
            p.likes.add(liker)
            
        # Add random comments
        for _ in range(random.randint(0, 2)):
            Comment.objects.create(
                post=p,
                author=random.choice(users),
                content=random.choice(comments_data)
            )

    print("Creating jobs...")
    jobs_data = [
        {"title": "Senior Frontend Developer", "company": "TechCorp", "location": "Remote"},
        {"title": "Data Engineer", "company": "DataWorks", "location": "New York, NY"},
        {"title": "Product Designer", "company": "StartupXYZ", "location": "San Francisco, CA"},
    ]
    for job in jobs_data:
        Job.objects.create(
            title=job['title'],
            company=job['company'],
            location=job['location'],
            description="We are looking for an experienced professional to join our fast-growing team. Competitive salary and benefits.",
            posted_by=users[3] # recruiter
        )

    print("Creating stories...")
    story_img_path = os.path.join(base_path, "story_image_1_1786189986172.jpg")
    if os.path.exists(story_img_path):
        author = users[0] # alice
        s = Story.objects.create(author=author)
        with open(story_img_path, 'rb') as f:
            s.image.save("story_image.jpg", File(f), save=True)

    print("Done! Added dummy users, posts, connections, jobs, stories, and comments.")
    print("You can log in with any of these usernames and 'password123'")
    for u in users:
        print(f" - {u.username}")

if __name__ == '__main__':
    populate()
