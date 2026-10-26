import sys, os, json
from multiprocessing import Pool
from content_courses import VIDEOS as CV
from content_anatomy import VIDEOS as AV
from content_general import VIDEOS as GV
from content_law import VIDEOS as LV
from content_calc import VIDEOS as CC

FIELD_COLOR = {'math': '#0a84ff', 'physics': '#bf5af2', 'cs': '#30d158', 'ee': '#ff9f0a', 'chem': '#ff375f', 'med': '#64d2ff', 'general': '#5e5ce6', 'law': '#c08a2e'}
COURSE = {  # id: (field, english name, hebrew name)
 'calc1': ('math', 'חדו״א 1'), 'calc2': ('math', 'Calculus 2'), 'vector-calc': ('math', 'Vector Calculus'),
 'linalg1': ('math', 'Linear Algebra 1'), 'linalg2': ('math', 'Linear Algebra 2'), 'discrete': ('math', 'Discrete Math'),
 'probability': ('math', 'Probability'), 'ode': ('math', 'Differential Equations'), 'complex': ('math', 'Complex Functions'),
 'physics1': ('physics', 'Physics 1'), 'physics2': ('physics', 'Physics 2'), 'physics3': ('physics', 'Physics 3'), 'quantum': ('physics', 'Quantum Mechanics'),
 'intro-cs': ('cs', 'Intro to Programming'), 'data-structures': ('cs', 'Data Structures'), 'algorithms': ('cs', 'Algorithms'), 'computability': ('cs', 'Computational Models'),
 'circuits': ('ee', 'Electric Circuits'), 'signals': ('ee', 'Signals & Systems'), 'chem': ('chem', 'General Chemistry'), 'anatomy': ('med', 'אנטומיה'), 'fun-facts': ('general', 'עובדות מעניינות'), 'bar-prep': ('law', 'הכנה לבחינת הלשכה'),
}
ALL = CC + CV + AV + GV + LV
for v in ALL:
    f, name = COURSE[v['courseId']]
    v['accent'] = FIELD_COLOR[f]; v['chip'] = name; v['chip2'] = v['topic']

def one(v):
    from render import render
    out = f"out/{v['id']}.mp4"
    if not os.path.exists(out): render(v, out)
    return v['id']

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        from render import still
        from PIL import Image
        ids = sys.argv[2].split(','); t = float(sys.argv[3]) if len(sys.argv) > 3 else 9
        ims = []
        for i in ids:
            v = next(x for x in ALL if x['id'] == i); still(v, t, f'/tmp/st_{i}.png'); ims.append(Image.open(f'/tmp/st_{i}.png').crop((0, 40, 720, 880)))
        c = Image.new('RGB', (720 * len(ims), 840))
        for k, im in enumerate(ims): c.paste(im, (720 * k, 0))
        c.resize((360 * len(ims), 420)).save('/home/claude/preview.png')
    elif sys.argv[1] == 'all':
        os.makedirs('out', exist_ok=True)
        with Pool(2) as p:
            for i in p.imap_unordered(one, ALL): print('done', i, flush=True)
    print(len(ALL), 'videos')
