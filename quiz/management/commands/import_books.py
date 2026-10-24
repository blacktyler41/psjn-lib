import csv

from django.core.management.base import BaseCommand, CommandError

from quiz.models import Book

# Words that may be typed in a "category" column  ->  the value stored in the database
CATEGORY_NAMES = {
    'religious': 'religious',
    'science': 'science',
    'sciences': 'science',
    'other': 'other',
    'others': 'other',
}

# For files that have a "subject" column instead: which subjects go where
SCIENCE_SUBJECTS = {'maths', 'math', 'mathematics', 'chemistry', 'physics', 'biology',
                    'computer science', 'ict'}
RELIGIOUS_SUBJECTS = {'religious', 'religion', 'bible'}

# Titles that should be written in capitals
TITLE_FIX = {'ict': 'ICT'}

# A "level" that only means "no level"
NO_LEVEL = ('', '-', '_')


def category_from_subject(subject):
    name = subject.lower()
    if name in RELIGIOUS_SUBJECTS:
        return 'religious'
    if name in SCIENCE_SUBJECTS:
        return 'science'
    return 'other'


class Command(BaseCommand):
    help = ('Add many books from a CSV file. Accepted first lines: '
            'title,link,category   or   title,subject,level,pdf_url')

    def add_arguments(self, parser):
        parser.add_argument('csv_file', help='Path of the CSV file, for example books.csv')

    def handle(self, *args, **options):
        # 1. Open the file ('utf-8-sig' also removes the invisible mark Excel adds at the start)
        try:
            file = open(options['csv_file'], newline='', encoding='utf-8-sig')
        except OSError:
            raise CommandError('Cannot open the file: %s' % options['csv_file'])

        with file:
            # 2. Columns can be separated by a comma, a TAB (what Google Sheets gives when you
            #    copy cells) or a semicolon. Look at the first line to see which one is used.
            first_line = file.readline().strip()     # strip(): ignore stray spaces or tabs at the end
            file.seek(0)
            if '\t' in first_line:
                delimiter = '\t'
            elif first_line.count(';') > first_line.count(','):
                delimiter = ';'
            else:
                delimiter = ','

            reader = csv.DictReader(file, delimiter=delimiter)
            names = [(name or '').strip().lower() for name in (reader.fieldnames or [])]
            reader.fieldnames = names

            # 3. Find out which kind of file this is, from its first line
            if 'title' in names and 'link' in names and 'category' in names:
                kind = 'simple'
            elif 'subject' in names and 'pdf_url' in names:
                kind = 'subjects'
            else:
                raise CommandError('The first line must be  title,link,category  '
                                   'or  title,subject,level,pdf_url')

            # 4. Read every line into a list of books
            books = []
            for line_number, row in enumerate(reader, start=2):
                if kind == 'simple':
                    title = (row.get('title') or '').strip()
                    link = (row.get('link') or '').strip()
                    category = CATEGORY_NAMES.get((row.get('category') or '').strip().lower())
                else:
                    subject = (row.get('subject') or row.get('title') or '').strip()
                    subject = TITLE_FIX.get(subject.lower(), subject)
                    level = (row.get('level') or '').strip()
                    link = (row.get('pdf_url') or '').strip()
                    title = subject if level in NO_LEVEL else '%s %s' % (subject, level)
                    category = category_from_subject(subject) if subject else None

                if not title and not link:
                    continue                      # an empty line: ignore it quietly
                books.append({'line': line_number, 'title': title, 'link': link, 'category': category})

        # 5. In a "subjects" file, books with the same title get numbers: Religious 1, Religious 2 ...
        if kind == 'subjects':
            totals = {}
            for book in books:
                totals[book['title']] = totals.get(book['title'], 0) + 1
            counter = {}
            for book in books:
                if totals[book['title']] > 1:
                    counter[book['title']] = counter.get(book['title'], 0) + 1
                    book['title'] = '%s %s' % (book['title'], counter[book['title']])

        # 6. Check each book, then add it (or update it if its link is already in the library)
        title_limit = Book._meta.get_field('title').max_length
        link_limit = Book._meta.get_field('Drive_link').max_length
        added = 0
        updated = 0
        unchanged = 0
        skipped = 0

        for book in books:
            title, link, category = book['title'], book['link'], book['category']

            problem = None
            if not title:
                problem = 'the title is empty'
            elif len(title) > title_limit:
                problem = 'the title is too long'
            elif not link.lower().startswith(('http://', 'https://')):
                problem = 'the link must start with http:// or https://'
            elif len(link) > link_limit:
                problem = 'the link is too long (maximum %s characters)' % link_limit
            elif category is None:
                problem = 'the category must be religious, science or other'

            if problem:
                skipped += 1
                self.stdout.write(self.style.WARNING('Line %s skipped: %s' % (book['line'], problem)))
                continue

            existing = Book.objects.filter(Drive_link=link).first()
            if existing is None:
                Book.objects.create(title=title, Drive_link=link, category=category)
                added += 1
            elif existing.title != title or existing.category != category:
                existing.title = title
                existing.category = category
                existing.save()
                updated += 1
            else:
                unchanged += 1

        # 7. Tell the user what happened
        self.stdout.write(self.style.SUCCESS(
            'Done: %s added, %s updated, %s already there, %s skipped.' % (added, updated, unchanged, skipped)))
