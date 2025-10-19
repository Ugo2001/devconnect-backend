# ============================================================================
# apps/users/management/commands/create_test_data.py
# ============================================================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile, Follow
from apps.posts.models import Post, Tag, Comment
from apps.snippets.models import Snippet, Language
from faker import Faker
import random

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Generate test data for development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of users to create'
        )
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='Number of posts to create'
        )
        parser.add_argument(
            '--snippets',
            type=int,
            default=15,
            help='Number of snippets to create'
        )
    
    def handle(self, *args, **options):
        users_count = options['users']
        posts_count = options['posts']
        snippets_count = options['snippets']
        
        self.stdout.write('Creating test data...')
        
        # Create users
        users = []
        for i in range(users_count):
            user = User.objects.create_user(
                username=fake.user_name() + str(i),
                email=fake.email(),
                password='testpass123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text(max_nb_chars=200),
                location=fake.city(),
                reputation=random.randint(0, 1000)
            )
            
            # Create profile
            UserProfile.objects.create(
                user=user,
                job_title=fake.job(),
                company=fake.company(),
                skills=['Python', 'Django', 'React', 'PostgreSQL'][:random.randint(2, 4)],
                experience_years=random.randint(1, 10)
            )
            
            users.append(user)
            self.stdout.write(f'Created user: {user.username}')
        
        # Create follows
        for user in users:
            follow_count = random.randint(0, 5)
            potential_follows = [u for u in users if u != user]
            for _ in range(min(follow_count, len(potential_follows))):
                to_follow = random.choice(potential_follows)
                Follow.objects.get_or_create(follower=user, following=to_follow)
                potential_follows.remove(to_follow)
        
        # Create tags
        tag_names = ['python', 'javascript', 'django', 'react', 'tutorial', 
                     'beginner', 'advanced', 'web', 'api', 'database']
        tags = []
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
        
        # Create posts
        for i in range(posts_count):
            author = random.choice(users)
            post = Post.objects.create(
                author=author,
                title=fake.sentence(nb_words=6),
                content=self._generate_markdown_content(),
                status='published',
                views_count=random.randint(0, 1000),
                likes_count=random.randint(0, 100),
                comments_count=random.randint(0, 20)
            )
            
            # Add random tags
            post.tags.set(random.sample(tags, k=random.randint(1, 3)))
            
            self.stdout.write(f'Created post: {post.title}')
            
            # Create comments
            comment_count = random.randint(0, 5)
            for _ in range(comment_count):
                Comment.objects.create(
                    post=post,
                    author=random.choice(users),
                    content=fake.paragraph(nb_sentences=3)
                )
        
        # Ensure languages exist
        if not Language.objects.exists():
            Language.objects.create(name='Python', extension='.py', color='#3776ab')
            Language.objects.create(name='JavaScript', extension='.js', color='#f7df1e')
        
        languages = list(Language.objects.all())
        
        # Create snippets
        for i in range(snippets_count):
            author = random.choice(users)
            snippet = Snippet.objects.create(
                author=author,
                title=fake.sentence(nb_words=4),
                description=fake.text(max_nb_chars=200),
                code=self._generate_code(),
                language=random.choice(languages),
                visibility=random.choice(['public', 'public', 'public', 'unlisted']),
                views_count=random.randint(0, 500),
                likes_count=random.randint(0, 50)
            )
            
            self.stdout.write(f'Created snippet: {snippet.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created:\n'
                f'- {users_count} users\n'
                f'- {posts_count} posts\n'
                f'- {snippets_count} snippets'
            )
        )
    
    def _generate_markdown_content(self):
        """Generate sample markdown content"""
        content = f"# {fake.sentence(nb_words=6)}\n\n"
        content += f"{fake.paragraph(nb_sentences=5)}\n\n"
        content += f"## {fake.sentence(nb_words=4)}\n\n"
        content += f"{fake.paragraph(nb_sentences=4)}\n\n"
        content += "```python\n"
        content += "def example_function():\n"
        content += "    print('Hello, World!')\n"
        content += "```\n\n"
        content += f"{fake.paragraph(nb_sentences=3)}\n"
        return content
    
    def _generate_code(self):
        """Generate sample code"""
        codes = [
            '''def hello_world():
    """A simple hello world function"""
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()''',
            '''function fetchData(url) {
    return fetch(url)
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
}''',
            '''class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

calc = Calculator()
print(calc.add(5, 3))''',
        ]
        return random.choice(codes)
