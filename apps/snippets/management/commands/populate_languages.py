from django.core.management.base import BaseCommand
from apps.snippets.models import Language
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Populate database with common programming languages'
    
    def handle(self, *args, **kwargs):
        # Clear existing languages first (optional - uncomment if needed)
        # Language.objects.all().delete()
        # self.stdout.write(self.style.WARNING('Cleared existing languages'))
        
        languages = [
            {'name': 'Python', 'slug': 'python', 'extension': '.py', 'color': '#3776ab'},
            {'name': 'JavaScript', 'slug': 'javascript', 'extension': '.js', 'color': '#f7df1e'},
            {'name': 'TypeScript', 'slug': 'typescript', 'extension': '.ts', 'color': '#3178c6'},
            {'name': 'Java', 'slug': 'java', 'extension': '.java', 'color': '#007396'},
            {'name': 'C++', 'slug': 'cpp', 'extension': '.cpp', 'color': '#00599c'},
            {'name': 'C#', 'slug': 'csharp', 'extension': '.cs', 'color': '#239120'},
            {'name': 'C', 'slug': 'c', 'extension': '.c', 'color': '#555555'},
            {'name': 'Ruby', 'slug': 'ruby', 'extension': '.rb', 'color': '#cc342d'},
            {'name': 'PHP', 'slug': 'php', 'extension': '.php', 'color': '#777bb4'},
            {'name': 'Go', 'slug': 'go', 'extension': '.go', 'color': '#00add8'},
            {'name': 'Rust', 'slug': 'rust', 'extension': '.rs', 'color': '#000000'},
            {'name': 'Swift', 'slug': 'swift', 'extension': '.swift', 'color': '#fa7343'},
            {'name': 'Kotlin', 'slug': 'kotlin', 'extension': '.kt', 'color': '#7f52ff'},
            {'name': 'Scala', 'slug': 'scala', 'extension': '.scala', 'color': '#dc322f'},
            {'name': 'HTML', 'slug': 'html', 'extension': '.html', 'color': '#e34f26'},
            {'name': 'CSS', 'slug': 'css', 'extension': '.css', 'color': '#1572b6'},
            {'name': 'SQL', 'slug': 'sql', 'extension': '.sql', 'color': '#00758f'},
            {'name': 'Shell', 'slug': 'shell', 'extension': '.sh', 'color': '#89e051'},
            {'name': 'R', 'slug': 'r', 'extension': '.r', 'color': '#276dc3'},
            {'name': 'MATLAB', 'slug': 'matlab', 'extension': '.m', 'color': '#e16737'},
            {'name': 'Dart', 'slug': 'dart', 'extension': '.dart', 'color': '#0175c2'},
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for lang_data in languages:
            try:
                # Try to get existing by slug
                try:
                    language = Language.objects.get(slug=lang_data['slug'])
                    # Update existing
                    language.name = lang_data['name']
                    language.extension = lang_data['extension']
                    language.color = lang_data['color']
                    language.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Updated: {language.name}')
                    )
                except Language.DoesNotExist:
                    # Create new
                    language = Language.objects.create(**lang_data)
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Created: {language.name}')
                    )
            except IntegrityError as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Skipped {lang_data["name"]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Total: {created_count} created, {updated_count} updated, {skipped_count} skipped'
            )
        )