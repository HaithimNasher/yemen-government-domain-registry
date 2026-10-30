import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUTPUT = DATA / 'governance' / 'university_domain_catalog.json'

# Format: Arabic name | proposed domain | source-list classification
RAW = '''
جامعة صنعاء|sanaa.edu.ye|public_candidate
جامعة عدن|aden.edu.ye|public_candidate
جامعة تعز|taiz.edu.ye|public_candidate
جامعة حضرموت|hadramout.edu.ye|public_candidate
جامعة إب|ibb.edu.ye|public_candidate
جامعة ذمار|dhamar.edu.ye|public_candidate
جامعة الحديدة|hodeidah.edu.ye|public_candidate
جامعة البيضاء|albayda.edu.ye|public_candidate
جامعة عمران|amran.edu.ye|public_candidate
جامعة حجة|hajjah.edu.ye|public_candidate
جامعة صعدة|saada.edu.ye|public_candidate
جامعة 21 سبتمبر للعلوم الطبية والتطبيقية|21september.edu.ye|public_candidate
جامعة إقليم سبأ|saba-region.edu.ye|public_candidate
جامعة سيئون|seiyun.edu.ye|public_candidate
جامعة شبوة|shabwah.edu.ye|public_candidate
جامعة أبين|abyan.edu.ye|public_candidate
جامعة لحج|lahj.edu.ye|public_candidate
جامعة المهرة|almahrah.edu.ye|public_candidate
الأكاديمية العربية للعلوم الإدارية والمالية والمصرفية|arab-academy-finance.edu.ye|private_or_unspecified
جامعة الريان|alrayan.edu.ye|private_or_unspecified
جامعة ابن خلدون|ibn-khaldun.edu.ye|private_or_unspecified
كلية 22 مايو للعلوم الطبية|22may-medical-college.edu.ye|private_or_unspecified
جامعة الإمام الشافعي للعلوم الإسلامية|imam-shafii.edu.ye|private_or_unspecified
جامعة الأحقاف|alahgaff.edu.ye|private_or_unspecified
جامعة الحكمة|alhikma.edu.ye|private_or_unspecified
جامعة العادل|aladel.edu.ye|private_or_unspecified
جامعة العرب|alarab.edu.ye|private_or_unspecified
الجامعة الوطنية|national.edu.ye|private_or_unspecified
جامعة العلوم والتكنولوجيا|ust-yemen.edu.ye|private_or_unspecified
جامعة القرآن الكريم والعلوم الإسلامية|quran-islamic.edu.ye|private_or_unspecified
جامعة الإيمان|aleman.edu.ye|private_or_unspecified
جامعة الوسطية الشرعية للعلوم الإسلامية|wasatiya.edu.ye|private_or_unspecified
كلية ردفان للقرآن وعلومه|radfan-quran-college.edu.ye|private_or_unspecified
جامعة العطاء للعلوم والتكنولوجيا|alataa.edu.ye|private_or_unspecified
جامعة الجند للعلوم والتكنولوجيا|aljund.edu.ye|private_or_unspecified
جامعة خليج عدن الدولية|aden-gulf.edu.ye|private_or_unspecified
جامعة الريادة|alreyada.edu.ye|private_or_unspecified
الجامعة اللبنانية الدولية|lebanese-international-yemen.edu.ye|private_or_unspecified
الجامعة الإسلامية العالمية|international-islamic.edu.ye|private_or_unspecified
جامعة السعيد|alsaeed.edu.ye|private_or_unspecified
جامعة الرواد|alrowad.edu.ye|private_or_unspecified
جامعة الأوائل الحديثة|alawael.edu.ye|private_or_unspecified
جامعة الأرخبيل الدولية|archipelago.edu.ye|private_or_unspecified
الجامعة الحديثة للعلوم والتكنولوجيا|modern-science-tech.edu.ye|private_or_unspecified
جامعة عدن الألمانية الدولية|aden-german.edu.ye|private_or_unspecified
جامعة الخليج العربي|arabian-gulf.edu.ye|private_or_unspecified
جامعة تريم الإسلامية|tarim-islamic.edu.ye|private_or_unspecified
جامعة العلوم الحديثة|modern-sciences.edu.ye|private_or_unspecified
جامعة أهل الحديث|ahl-hadith.edu.ye|private_or_unspecified
الجامعة اليمنية|yemeni.edu.ye|private_or_unspecified
جامعة دار السلام الدولية|dar-alsalam.edu.ye|private_or_unspecified
جامعة المستقبل|future-university-yemen.edu.ye|private_or_unspecified
جامعة الرازي|alrazi.edu.ye|private_or_unspecified
جامعة الناصر|alnasser.edu.ye|private_or_unspecified
الجامعة الإماراتية الدولية|emirati-international.edu.ye|private_or_unspecified
جامعة أزال للتنمية البشرية|azal-human-development.edu.ye|private_or_unspecified
جامعة توتنك الدولية للتكنولوجيا|totenk.edu.ye|private_or_unspecified
جامعة الملكة أروى|queen-arwa.edu.ye|private_or_unspecified
جامعة اليمن|yemen.edu.ye|private_or_unspecified
الجامعة اليمنية الأردنية|yemeni-jordanian.edu.ye|private_or_unspecified
جامعة سبأ|saba.edu.ye|private_or_unspecified
جامعة السعيدة|alsaeeda.edu.ye|private_or_unspecified
جامعة القلم للعلوم الإنسانية والتطبيقية|alqalam.edu.ye|private_or_unspecified
جامعة جينيس للعلوم والتكنولوجيا|genius.edu.ye|private_or_unspecified
جامعة الأندلس للعلوم والتقنية|alandalus.edu.ye|private_or_unspecified
جامعة الاتحاد للعلوم والتكنولوجيا|alittihad.edu.ye|private_or_unspecified
جامعة النخبة الدولية للعلوم والتكنولوجيا|elite-international.edu.ye|private_or_unspecified
جامعة اقرأ للعلوم والتكنولوجيا|iqra.edu.ye|private_or_unspecified
جامعة اليمن والخليج للعلوم والتكنولوجيا|yemen-gulf.edu.ye|private_or_unspecified
جامعة الحضارة|civilization.edu.ye|private_or_unspecified
جامعة الأكاديميين العرب للعلوم والتكنولوجيا|arab-academicians.edu.ye|private_or_unspecified
جامعة الوحدة للعلوم والتكنولوجيا|alwahda.edu.ye|private_or_unspecified
جامعة ابن النفيس|ibn-alnafis.edu.ye|private_or_unspecified
الجامعة الماليزية الدولية - إب|malaysian-international-ibb.edu.ye|private_or_unspecified
جامعة الرشيد الذكية|alrasheed-smart.edu.ye|private_or_unspecified
جامعة الجزيرة|aljazeera.edu.ye|private_or_unspecified
جامعة المعرفة والعلوم الحديثة|knowledge-modern-sciences.edu.ye|private_or_unspecified
جامعة جبلة للعلوم الطبية والصحية|jibla-medical.edu.ye|private_or_unspecified
جامعة آزال للعلوم والتكنولوجيا|azal-science-tech.edu.ye|private_or_unspecified
الجامعة العربية للعلوم والتقنية|arab-science-tech.edu.ye|private_or_unspecified
جامعة دار العلوم الشرعية - الحديدة|dar-aluloom-hodeidah.edu.ye|private_or_unspecified
'''

rows = [line.split('|') for line in RAW.strip().splitlines()]
assert len(rows) == 81, f'Expected 81 records, found {len(rows)}'
assert all(len(row) == 3 for row in rows)

existing_path = DATA / 'universities.json'
existing = json.loads(existing_path.read_text(encoding='utf-8')) if existing_path.exists() else []
assert isinstance(existing, list)

# Only a single, unambiguous exact match is considered linked.
by_name = {}
by_domain = {}
for rec in existing:
    if not isinstance(rec, dict):
        continue
    by_name.setdefault(rec.get('name_ar'), []).append(rec)
    if rec.get('domain'):
        by_domain.setdefault(rec['domain'].lower(), []).append(rec)

catalog = []
seen_names = set()
seen_domains = set()
conflicts = []
for name, domain, classification in rows:
    domain = domain.lower().strip()
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)*', domain):
        raise ValueError(f'Invalid domain: {domain}')
    if not domain.endswith('.edu.ye'):
        raise ValueError(f'Unexpected suffix: {domain}')
    if name in seen_names or domain in seen_domains:
        raise ValueError(f'Duplicate input: {name} / {domain}')
    seen_names.add(name)
    seen_domains.add(domain)

    name_matches = by_name.get(name, [])
    domain_matches = by_domain.get(domain, [])
    linked = name_matches[0] if len(name_matches) == 1 else None
    issues = []
    if len(name_matches) > 1:
        issues.append('duplicate_existing_name')
    if len(domain_matches) > 1:
        issues.append('duplicate_existing_domain')
    if linked and linked.get('domain') and linked['domain'].lower() != domain:
        issues.append('existing_domain_differs')
    if any(rec.get('entity_id') != (linked or {}).get('entity_id') for rec in domain_matches):
        issues.append('domain_assigned_to_other_entity')
    if issues:
        conflicts.append((name, issues))

    catalog.append({
        'name_ar': name,
        'name_en': None,
        'category': 'university' if 'جامعة' in name or name.startswith('الجامعة') else 'higher_education_institution',
        'classification_from_input': classification,
        'classification_verified': False,
        'entity_id': linked.get('entity_id') if linked else None,
        'existing_domain': linked.get('domain') if linked else None,
        'proposed_domain': domain,
        'domain_status': 'proposed',
        'ownership_verified': False,
        'source_url': None,
        'last_verified': None,
        'review_required': bool(issues),
        'review_issues': issues,
    })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
serialized = json.dumps(catalog, ensure_ascii=False, indent=2) + '\n'
if OUTPUT.exists() and OUTPUT.read_text(encoding='utf-8') != serialized:
    raise SystemExit(f'Existing catalog differs: {OUTPUT}. Review before overwriting.')
OUTPUT.write_text(serialized, encoding='utf-8')
print('Institutions:', len(catalog))
print('Linked by exact Arabic name:', sum(bool(x['entity_id']) for x in catalog))
print('New candidates:', sum(not x['entity_id'] for x in catalog))
print('Review conflicts:', len(conflicts))
for name, issues in conflicts:
    print('REVIEW:', name, ', '.join(issues))
print('Catalog:', OUTPUT)
