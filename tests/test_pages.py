import importlib.util
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('renderer', ROOT/'scripts/render.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
    def all(self, tag):
        return [a for t, a in self.tags if t == tag]

class Pages(unittest.TestCase):
    def test_complete_static_language_journeys_and_shared_engine(self):
        for locale, c in renderer.LOCALES.items():
            path = ROOT/('index.html' if locale == 'en' else locale+'/index.html')
            source = path.read_text()
            self.assertEqual(source, renderer.render(locale))
            p = Page(source)
            self.assertEqual(p.all('html')[0]['lang'], c['lang'])
            self.assertEqual(len(p.all('h1')), 1)
            self.assertEqual(len(p.all('main')), 1)
            ids = [a['id'] for _,a in p.tags if 'id' in a]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual([a['href'] for a in p.all('link') if a.get('rel')=='canonical'], [renderer.ORIGIN+renderer.route(locale)])
            alternates = {a['hreflang']: a['href'] for a in p.all('link') if a.get('rel')=='alternate'}
            self.assertEqual(len(alternates), 6)
            for target, details in renderer.LOCALES.items():
                self.assertEqual(alternates[details['lang']], renderer.ORIGIN+renderer.route(target))
                self.assertIn(renderer.route(target), [a.get('href') for a in p.all('a')])
            selected = [a for a in p.all('a') if a.get('aria-current')=='page']
            self.assertEqual([a['href'] for a in selected], [renderer.route(locale)])
            self.assertIn(renderer.links(locale)['home'], [a.get('href') for a in p.all('a')])
            for a in p.all('a'):
                if a.get('href','').startswith('#'):
                    self.assertIn(a['href'][1:], ids)
            self.assertEqual([a['src'] for a in p.all('script') if 'src' in a], ['/quote-builder-ai/assets/quote.js?v=20261031'])
            for control in p.all('input')+p.all('textarea')+p.all('select'):
                self.assertIn(control['id'], [a.get('for') for a in p.all('label')])
                for description in control.get('aria-describedby','').split():
                    self.assertIn(description, ids)
                self.assertNotIn('name', control)  # no accidental form transmission
            for id, _, _ in c['costs']:
                control = next(a for a in p.all('input') if a.get('id')==id)
                self.assertNotIn('value', control)  # no assumed supplier rates
            self.assertFalse(p.all('iframe'))
            self.assertIn('disabled', next(a for a in p.all('button') if a['id']=='calculate'))
            self.assertIn('data-release="service-cost-planner-2026-10-31-v1"', source)

    def test_all_copy_keys_match_and_visible_body_is_translated(self):
        base = renderer.LOCALES['en']
        for locale, content in renderer.LOCALES.items():
            self.assertEqual(set(content), set(base))
            self.assertEqual([x[0] for x in content['costs']], ['supplier','labor','equipment','tax','travel','freight','import','other'])
            self.assertEqual(len(content['steps']), 4)
            if locale != 'en':
                for key in ['h1','lead','privacy','formError','reviewed','draft','footer','formula','markupHelp','noscript']:
                    self.assertNotEqual(content[key], base[key])

    def test_same_locale_related_links_and_no_external_runtime(self):
        for locale in renderer.LOCALES:
            p = Page(renderer.render(locale))
            hrefs = {a.get('href') for a in p.all('a')}
            for url in renderer.links(locale).values():
                self.assertIn(url, hrefs)
        runtime = (ROOT/'assets/quote.js').read_text()
        for forbidden in ['fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage', 'innerHTML']:
            self.assertNotIn(forbidden, runtime)

if __name__ == '__main__':
    unittest.main()
