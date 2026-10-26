# Clip pipeline

This pipeline renders the 15-second learning clips in `../assets/videos/`. It also generates `../src/data/sample.ts`,
the clip list the app reads.

Each clip has an animated background, a course chip, a title, an animated visual and a short definition, all
burned into the video. The longer explanation, the memory tip and the questions aren't in the video: they go into
`sample.ts` and appear in the app.

## Files

| File | What it does |
|---|---|
| `content_courses.py` | English sample clips for the university courses, plus the shared `Q()` question helper |
| `content_calc.py` | Calculus 1 in Hebrew (40 clips). Based on *Contemporary Calculus I* and *Applied Calculus* |
| `content_anatomy.py` | Anatomy in Hebrew with the Latin term (30 clips, with memory tips) |
| `content_law.py` | Bar exam prep in Hebrew (30 topics, written from the statute texts) |
| `content_general.py` | Fun facts in Hebrew (30 clips, facts only, no questions) |
| `render.py` | Draws every frame with Pillow and encodes it with ffmpeg (720×1280, H.264, 20 fps, 15 s) |
| `calc_scenes.py`, `biz_scenes.py` | Animated math scenes for the calculus clips |
| `body.py` | Human-figure diagram with an animated highlight, used by the anatomy clips |
| `build.py` | Collects all the content files and renders the clips |
| `codegen.py` | Writes `src/data/sample.ts` from the content files |

Each clip has an `id`, such as `d1`, `a12` or `c45`. The id is also the video's file name (`d1.mp4`).

## Adding or changing a clip

Run every command from inside `clip-pipeline/`.

1. Add or edit an entry in the right `content_*.py` file. Give a new clip an id that isn't used yet.
2. Render the clips:
   ```bash
   python build.py all
   ```
   This renders every clip that isn't in `out/` yet. To re-render a clip you changed, delete its file in `out/` first.
3. Copy the new `out/<id>.mp4` to `assets/videos/`.
4. Regenerate the app data:
   ```bash
   python codegen.py
   ```
5. Run the app and check the clip.

`src/data/sample.ts` is generated, so don't edit it by hand. Your changes would be lost the next time `codegen.py` runs.

## Requirements

- Python 3 with **Pillow** (built with libraqm, for Hebrew text) and **NumPy**
- **ffmpeg** on your PATH
- **DejaVu fonts** at `/usr/share/fonts/truetype/dejavu/`

The pipeline is set up for Linux. On Windows, run it inside WSL.

`out/` is git-ignored. Only the copies in `assets/videos/` are committed.
