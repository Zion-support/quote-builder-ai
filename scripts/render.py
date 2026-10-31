#!/usr/bin/env python3
"""Generate the five static service cost planning pages from one reviewed locale source."""
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://ziontechgroup.com'
BASE = '/quote-builder-ai/'
LOCALES = json.loads((ROOT / '_data/locales.json').read_text())
RELEASE = 'service-cost-planner-2026-10-31-v1'


def esc(value):
    return html.escape(str(value), quote=True)


def route(locale):
    return BASE if locale == 'en' else BASE + locale + '/'


def links(locale):
    prefix = '/' if locale == 'en' else '/' + locale + '/'
    home = '/' if locale == 'pt' else '/' + locale + '/'
    suffix = '' if locale == 'en' else '-pt-br' if locale == 'pt' else '-' + locale
    return {
        'home': home, 'catalog': prefix + 'apps/', 'discovery': prefix + 'discovery/',
        'network': '/zion-app-network/' if locale == 'en' else '/zion-app-network/home-' + locale + '.html',
        'request': '/zion-app-network/datacenter-service-request-guide-2026' + suffix + '.html',
        'operations': prefix + 'apps/operational-planning-tools.html',
        'finops': prefix + 'apps/finops-scenario-estimator.html'
    }


def render(locale):
    c = LOCALES[locale]
    u = links(locale)
    language_links = ''.join(f'<a href="{route(l)}" lang="{d["lang"]}" hreflang="{d["lang"]}"' + (' aria-current="page"' if l == locale else '') + f'>{esc(d["name"])}</a>' for l, d in LOCALES.items())
    alternates = '\n'.join(f'<link rel="alternate" hreflang="{d["lang"]}" href="{ORIGIN + route(l)}">' for l, d in LOCALES.items())
    navigation = ''.join(f'<a href="{u[k]}">{esc(c[k])}</a>' for k in ('home', 'catalog', 'network', 'discovery'))
    fields = ''.join(f'''<div class="field"><label for="{id}">{esc(label)}</label><input type="text" inputmode="decimal" id="{id}" required maxlength="16" aria-describedby="{id}-help decimal-help {id}-error" autocomplete="off"><span class="help" id="{id}-help">{esc(help_text)}</span><p class="error" id="{id}-error" hidden></p></div>''' for id, label, help_text in c['costs'])
    currency_options = ''.join(f'<option value="{v}"' + (' selected' if v == c['currency'] else '') + f'>{v}</option>' for v in ('USD', 'BRL', 'EUR', 'GBP'))
    metrics = ''.join(f'<div class="metric'+(' highlight' if key == 'price' else '')+f'"><dt>{esc(c[label])}</dt><dd id="{key}-value"></dd></div>' for key, label in [('total','total'),('markup','markupResult'),('floor','floor'),('price','price'),('profit','profit'),('margin','margin')])
    rows = ''.join(f'<tr><th scope="row">{esc(label)}</th><td id="result-{id}"></td></tr>' for id, label, _ in c['costs'])
    steps = ''.join(f'<li><h3>{esc(title)}</h3><p>{esc(body)}</p></li>' for title, body in c['steps'])
    related = ''.join(f'<article class="card"><h3><a href="{u[key]}">{esc(title)}</a></h3><p>{esc(body)}</p></article>' for key, title, body in c['related'])
    runtime_keys = ['intl','costs','steps','sampleNote','stale','emptyResult','formError','zeroError','required','moneyError','markupError','draft','reviewed','draftBody','reviewedBody','total','markupResult','floor','price','profit','margin','resultNotes','summaryHeading','summaryStatus','summaryScope','formula','copied','copyFailed']
    runtime = json.dumps({key:c[key] for key in runtime_keys}, ensure_ascii=False).replace('<','\\u003c')
    structured = json.dumps({'@context':'https://schema.org','@type':'WebPage','name':c['title'],'description':c['description'],'inLanguage':c['lang'],'url':ORIGIN+route(locale)},ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html>
<html lang="{c['lang']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(c['title'])} | Zion Tech Group</title><meta name="description" content="{esc(c['description'])}">
<link rel="canonical" href="{ORIGIN + route(locale)}">
{alternates}
<link rel="alternate" hreflang="x-default" href="{ORIGIN + route('en')}">
<meta property="og:type" content="website"><meta property="og:title" content="{esc(c['title'])}"><meta property="og:description" content="{esc(c['description'])}"><meta property="og:url" content="{ORIGIN + route(locale)}">
<link rel="stylesheet" href="{BASE}assets/quote.css?v=20261031"><script type="application/ld+json">{structured}</script><script src="{BASE}assets/quote.js?v=20261031" defer></script></head>
<body data-release="{RELEASE}" data-locale="{locale}">
<a class="skip" href="#calculator">{esc(c['skip'])}</a>
<header><div class="wrap top"><a class="brand" href="{u['home']}">Zion Tech Group<span>{esc(c['brandSub'])}</span></a><nav aria-label="{esc(c['catalog'])}">{navigation}</nav></div><nav class="wrap languages" aria-label="{esc(c['languages'])}">{language_links}<span>{esc(c['switchNote'])}</span></nav></header>
<main class="wrap" id="main"><section class="hero"><p class="eyebrow">{esc(c['eyebrow'])}</p><h1>{esc(c['h1'])}</h1><p class="lead">{esc(c['lead'])}</p><div class="actions"><a class="button primary" href="#calculator">{esc(c['jump'])}</a><button type="button" id="load-example" disabled>{esc(c['sample'])}</button></div><p class="sample-status help" id="sample-status" role="status"></p><p class="privacy">{esc(c['privacy'])}</p></section>
<noscript><p class="alert">{esc(c['noscript'])}</p></noscript>
<section id="calculator" tabindex="-1" aria-label="{esc(c['title'])}" class="workspace">
<form id="quote-form" class="panel" novalidate autocomplete="off">
<div class="form-section"><h2>{esc(c['formTitle'])}</h2><p class="intro">{esc(c['costInstruction'])}</p><div class="field"><label for="currency">{esc(c['currencyLabel'])}</label><select id="currency" aria-describedby="currency-help currency-error">{currency_options}</select><span class="help" id="currency-help">{esc(c['currencyHelp'])}</span><p class="error" id="currency-error" hidden></p></div><fieldset><legend>{esc(c['costLegend'])}</legend><p class="help" id="decimal-help">{esc(c['decimalHelp'])}</p><div class="cost-grid">{fields}</div></fieldset></div>
<div class="form-section"><h2>{esc(c['markupTitle'])}</h2><div class="field"><label for="markup">{esc(c['markupLabel'])}</label><input type="text" inputmode="decimal" id="markup" value="40" required maxlength="8" aria-describedby="markup-help markup-error" autocomplete="off"><span class="help" id="markup-help">{esc(c['markupHelp'])}</span><p class="error" id="markup-error" hidden></p></div><p class="formula">{esc(c['formula'])}</p></div>
<div class="form-section"><h2>{esc(c['reviewTitle'])}</h2><div class="field"><label for="notes">{esc(c['notesLabel'])}</label><textarea id="notes" rows="3" maxlength="1200" placeholder="{esc(c['notesPlaceholder'])}" aria-describedby="notes-help"></textarea><span class="help" id="notes-help">{esc(c['notesHelp'])}</span></div><label class="check" for="reviewed"><input type="checkbox" id="reviewed" aria-describedby="reviewed-help"><span>{esc(c['reviewLabel'])}</span></label><p class="help" id="reviewed-help">{esc(c['reviewHelp'])}</p></div>
<p id="form-error" class="alert" role="alert" tabindex="-1" hidden></p><div class="actions"><button type="submit" class="primary" id="calculate" disabled>{esc(c['calculate'])}</button><button type="button" id="clear">{esc(c['reset'])}</button></div></form>
<aside class="panel result-shell" aria-labelledby="result-title"><h2 id="result-title" tabindex="-1">{esc(c['resultTitle'])}</h2><p id="result-placeholder" class="result-body" role="status">{esc(c['emptyResult'])}</p><div id="result" hidden><p class="result-state" id="result-state"></p><p class="result-body" id="result-state-body"></p><dl class="metrics">{metrics}</dl><p class="formula">{esc(c['marginHelp'])}</p><details class="breakdown" open><summary>{esc(c['breakdown'])}</summary><table><tbody>{rows}</tbody></table></details><div id="result-notes-wrap" hidden><h3>{esc(c['resultNotes'])}</h3><p class="notes-output" id="result-notes"></p></div><p class="scope">{esc(c['steps'][3][1])}</p><div class="actions"><button type="button" id="copy-result">{esc(c['copy'])}</button><button type="button" id="print-result">{esc(c['print'])}</button></div><p id="copy-status" class="help" role="status"></p></div></aside></section>
<section class="section" aria-labelledby="workflow-title"><h2 id="workflow-title">{esc(c['workflowTitle'])}</h2><ol class="steps">{steps}</ol><div class="example"><h3>{esc(c['exampleTitle'])}</h3><p>{esc(c['exampleText'])}</p></div></section>
<section class="section" aria-labelledby="related-title"><h2 id="related-title">{esc(c['relatedTitle'])}</h2><div class="grid">{related}</div></section></main>
<footer><div class="wrap"><p>{esc(c['footer'])}</p><nav aria-label="{esc(c['catalog'])}">{navigation}<a href="https://github.com/Zion-support/quote-builder-ai">{esc(c['source'])}</a></nav><p>Zion Tech Group · 2026</p></div></footer><script type="application/json" id="quote-copy">{runtime}</script></body></html>
'''


def run(check=False):
    expected = set(LOCALES['en'])
    for locale, content in LOCALES.items():
        if set(content) != expected:
            raise ValueError('Locale keys differ: ' + locale)
    outputs = {}
    for locale in LOCALES:
        path = ROOT / ('index.html' if locale == 'en' else locale + '/index.html')
        outputs[path] = render(locale)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{ORIGIN + route(locale)}</loc></url>\n' for locale in LOCALES) + '</urlset>\n'
    outputs[ROOT/'sitemap.xml'] = sitemap
    stale = []
    for path, content in outputs.items():
        if check:
            if not path.is_file() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        raise SystemExit('Regenerate pages: ' + ', '.join(stale))
    print(('Verified' if check else 'Rendered') + ' five localized pages and their sitemap.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    run(parser.parse_args().check)
