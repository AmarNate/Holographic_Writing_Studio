import asyncio, json, sys, subprocess, time, os
from playwright.async_api import async_playwright

PORT = 8765
BASE = f"http://127.0.0.1:{PORT}"
OUT = "shots"
os.makedirs(OUT, exist_ok=True)
results = []
def rec(name, ok, note=""):
    results.append((name, "PASS" if ok else "FAIL", note))
    print(("PASS " if ok else "FAIL ") + name + ("  - " + note if note else ""))

async def ev(page, js):
    return await page.evaluate(js)

async def main():
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--autoplay-policy=no-user-gesture-required"])
        ctx = await br.new_context(viewport={"width": 1904, "height": 901})
        errors = []
        page = await ctx.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        answers = []
        async def ans(dg):
            if answers: await dg.accept(answers.pop(0))
            else: await dg.accept()
        page.on("dialog", lambda dg: asyncio.ensure_future(ans(dg)))

        # --- 1. a1.8: make the state he has now (22hrs essay + a new essay made in a1.8)
        await page.goto(BASE + "/a18.html"); await page.wait_for_timeout(600)
        await page.click("#btnNewDoc")
        await page.fill("#newDocTitle", "NeuroToxic Highjack & Neural Web Uplink")
        await page.fill("#newDocSub", "Personal Essay")
        await page.click("#btnConfirmNewDoc"); await page.wait_for_timeout(300)
        await page.screenshot(path=f"{OUT}/a18_new_cover_pc.png")
        vault18 = await ev(page, "localStorage.getItem('nate_writing_studio_vault_v1')")
        v = json.loads(vault18)
        newid = v["activeDocId"]
        rec("a1.8 new essay inherited the 22hrs link (the reported problem)", v["docs"][newid].get("reelUrl","").startswith("https://www.instagram.com/reel/DgB"))

        # --- 2. open a1.9 on the same vault
        await page.goto(BASE + "/index.html"); await page.wait_for_timeout(700)
        d = await ev(page, """(() => { const v = JSON.parse(localStorage.getItem('nate_writing_studio_vault_v1')); const a = v.docs[v.activeDocId];
          return { id: v.activeDocId, reel: a.reelUrl, song: a.song, fix: v.fixA19, words: Object.keys(v.docs).length }; })()""")
        rec("a1.9 opens the same vault, both essays kept", d["words"] == 2)
        rec("NeuroToxic essay drops the inherited 22hrs link", d["reel"] == "")
        st = await ev(page, """({ dome: document.getElementById('domeTrackLabel').textContent,
            time: document.getElementById('domeTimecode').textContent,
            live: document.getElementById('domeLiveLyric').textContent,
            frameEmpty: document.querySelector('.cover-hero-frame').classList.contains('is-empty'),
            heroSrc: document.getElementById('coverHeroImg').getAttribute('src'),
            linkHidden: document.getElementById('coverReelLink').classList.contains('is-none'),
            linkBtn: document.getElementById('btnEditReelUrl').textContent,
            noteShown: getComputedStyle(document.querySelector('.cover-empty-note')).display })""")
        rec("new essay: player says No song yet", st["dome"] == "No song yet", st["dome"])
        rec("new essay: no 2:45 length", st["time"] == "0:00 / -:--", st["time"])
        rec("new essay: no 22hrs lyric on the dome", "22 hours" not in st["live"], st["live"])
        rec("new essay: cover is a quiet empty frame", st["frameEmpty"] and not st["heroSrc"] and st["noteShown"] == "block")
        rec("new essay: no link shown, button says Add Link", st["linkHidden"] and st["linkBtn"] == "Add Link")
        await page.screenshot(path=f"{OUT}/a19_new_cover_pc.png")

        # chamber view: art strip hidden
        await page.click("#btnNextChamber"); await page.wait_for_timeout(200)
        strip = await ev(page, "getComputedStyle(document.getElementById('visualAnchorCard')).display")
        rec("new essay chamber: no 22hrs art strip", strip == "none", strip)
        await page.screenshot(path=f"{OUT}/a19_new_chamber_pc.png")

        # lyrics drawer empty
        await page.click("#btnToggleLyrics"); await page.wait_for_timeout(150)
        lt = await ev(page, "document.getElementById('lyricsContainer').textContent.trim()")
        head = await ev(page, "document.getElementById('lyricsHeadLabel').textContent")
        rec("new essay lyrics drawer: empty note, no 22hrs lines", lt.startswith("No lyrics") and "22" not in head, head)
        await page.screenshot(path=f"{OUT}/a19_new_lyrics_empty_pc.png")

        # paste plain lyrics, save
        await page.click("#btnEditLyrics")
        await page.fill("#lyricsEditText", "first test line\nsecond test line\n0:20 third line already timed")
        await page.screenshot(path=f"{OUT}/a19_lyrics_edit_pc.png")
        await page.click("#btnLyricsSave"); await page.wait_for_timeout(150)
        ly = await ev(page, "JSON.parse(localStorage.getItem('nate_writing_studio_vault_v1')).docs[JSON.parse(localStorage.getItem('nate_writing_studio_vault_v1')).activeDocId].song.lyrics")
        rec("lyrics saved per essay, timed and untimed lines read right", ly == [{"t":"","line":"first test line"},{"t":"","line":"second test line"},{"t":"0:20","line":"third line already timed"}], json.dumps(ly))

        # load MP3: song gets the file's name
        await page.set_input_files("#audioFileInput", "test-song.mp3"); await page.wait_for_timeout(800)
        title = await ev(page, "document.getElementById('domeTrackLabel').textContent")
        rec("Load MP3 names this essay's song", title == "test-song", title)

        # tap to time
        await page.click("#btnEditLyrics")
        await page.click("#btnLyricsTap"); await page.wait_for_timeout(300)
        tapping = await ev(page, "document.getElementById('lyricsDrawer').classList.contains('is-tapping')")
        rec("Tap to time opens with the song playing", tapping)
        await page.screenshot(path=f"{OUT}/a19_tap_pc.png")
        await ev(page, "document.getElementById('trackPlayer').currentTime = 3")
        await page.click("#btnTapMark")
        await ev(page, "document.getElementById('trackPlayer').currentTime = 7.4")
        await page.click("#btnTapMark")
        await ev(page, "document.getElementById('trackPlayer').currentTime = 12")
        await page.click("#btnTapMark")
        status = await ev(page, "document.getElementById('tapStatus').textContent")
        await page.click("#btnTapDone"); await page.wait_for_timeout(150)
        ly = await ev(page, "(() => { const v = JSON.parse(localStorage.getItem('nate_writing_studio_vault_v1')); return v.docs[v.activeDocId].song.lyrics.map(x => x.t); })()")
        rec("Mark writes each line's time", ly == ["0:03", "0:07", "0:12"], json.dumps(ly) + " / " + status)
        await ev(page, "document.getElementById('trackPlayer').currentTime = 8; document.getElementById('trackPlayer').dispatchEvent(new Event('timeupdate'))")
        await page.wait_for_timeout(100)
        live = await ev(page, "document.getElementById('domeLiveLyric').textContent")
        rec("dome follows the timed lyrics", live == '[0:07] "second test line"', live)
        await page.screenshot(path=f"{OUT}/a19_lyrics_timed_pc.png")
        await page.click("#btnCloseLyrics")

        # cue from a lyric line goes into the chamber
        await page.click("#domeLiveLyric"); await page.wait_for_timeout(100)
        cue = await ev(page, "document.getElementById('writingSurface').innerHTML")
        rec("cue chip from this essay's song", "second test line" in cue and "22 hours" not in cue)

        # edit link: address then words (dialogs answered with defaults => set below)
        answers.extend(["https://example.com/neuro", "NeuroToxic reel"])
        await page.click("#btnPrevChamber"); await page.wait_for_timeout(150)
        await page.click("#btnEditReelUrl"); await page.wait_for_timeout(300)
        lk = await ev(page, "({ href: document.getElementById('coverReelLink').getAttribute('href'), label: document.getElementById('coverReelLabel').textContent, hidden: document.getElementById('coverReelLink').classList.contains('is-none') })")
        rec("Edit Link sets this essay's own address and words", lk["href"] == "https://example.com/neuro" and "NeuroToxic reel" in lk["label"] and not lk["hidden"], json.dumps(lk))

        # cover art swap still per essay
        await page.set_input_files("#coverArtFileInput", "shots/a18_new_cover_pc.png"); await page.wait_for_timeout(500)
        fe = await ev(page, "document.querySelector('.cover-hero-frame').classList.contains('is-empty')")
        rec("Change Cover Art fills the empty frame", not fe)
        await page.screenshot(path=f"{OUT}/a19_new_cover_withart_pc.png")

        # switch back to 22hrs: everything 22hrs, player stopped
        await page.click("#btnSwitchPiece"); await page.wait_for_timeout(150)
        await page.click(".piece-card-btn >> nth=0"); await page.wait_for_timeout(300)
        st2 = await ev(page, """({ dome: document.getElementById('domeTrackLabel').textContent, time: document.getElementById('domeTimecode').textContent,
           src: document.getElementById('trackPlayer').getAttribute('src'), live: document.getElementById('domeLiveLyric').textContent,
           link: document.getElementById('coverReelLabel').textContent, href: document.getElementById('coverReelLink').getAttribute('href'),
           empty: document.querySelector('.cover-hero-frame').classList.contains('is-empty'), n: document.querySelectorAll('.lyric-line-btn').length,
           title: document.getElementById('coverMainTitle').textContent })""")
        rec("22hrs essay: KAIA - 22hrs, 2:45, its 35 lyric lines", st2["dome"] == "KAIA - 22hrs" and st2["time"] == "0:00 / 2:45" and st2["n"] == 35, json.dumps({k: st2[k] for k in ['dome','time','n']}))
        rec("22hrs essay: its reel link and label unchanged", "KAIA - 22hrs (Fan-made Visualizer) · Watch Reel (@IZ.NENAD.AN)" in st2["link"] and st2["href"].startswith("https://www.instagram.com/reel/DgB"))
        rec("22hrs essay: its art", not st2["empty"])
        rec("switching essays stops the other essay's MP3", not st2["src"])
        await page.screenshot(path=f"{OUT}/a19_22hrs_cover_pc.png")

        # new piece made in a1.9
        await page.click("#btnNewDoc")
        await page.fill("#newDocTitle", "Fresh Test Piece")
        await page.click("#btnConfirmNewDoc"); await page.wait_for_timeout(300)
        st3 = await ev(page, "({ dome: document.getElementById('domeTrackLabel').textContent, empty: document.querySelector('.cover-hero-frame').classList.contains('is-empty'), link: document.getElementById('coverReelLink').classList.contains('is-none') })")
        rec("a piece made in a1.9 starts blank (song, art, link)", st3["dome"] == "No song yet" and st3["empty"] and st3["link"], json.dumps(st3))

        # exports for a blank piece carry no 22hrs
        html = await ev(page, "buildHolographicExportDocument(getActiveDoc(), false)")
        md_ok = await ev(page, """(() => { let got=''; const orig = window.downloadBlob; window.downloadBlob = (n,c)=>{got=c}; exportActiveDoc('md'); window.downloadBlob = orig; return got; })()""")
        rec("HTML export of a blank piece: no 22hrs art, label or link", "22hrs" not in html and "DgB-TvyIf9D" not in html)
        rec("Markdown export of a blank piece: no 22hrs link", "22hrs" not in md_ok and "DgB-TvyIf9D" not in md_ok)
        html22 = await ev(page, "buildHolographicExportDocument(vault.docs['essay-22hrs'], false)")
        rec("HTML export of the 22hrs essay keeps its art and link", "DgB-TvyIf9D" in html22 and "KAIA - 22hrs (Fan-made Visualizer)" in html22 and "data:image/jpeg" in html22)

        # full essay view of new doc
        await page.click("#btnModeFull"); await page.wait_for_timeout(150)
        fv = await ev(page, "document.getElementById('fullEssayView').innerHTML")
        rec("Full Essay view of a blank piece: no 22hrs link", "22hrs" not in fv)
        await page.click("#btnModeSingle")

        # every button: click each one and look for page errors
        ids = await ev(page, "Array.from(document.querySelectorAll('button[id]')).map(b=>b.id)")
        clicked = 0
        for i in ids:
            if i in ("btnExpPdf",): continue
            try:
                await ev(page, f"(() => {{ const b = document.getElementById('{i}'); if (b && !b.disabled) b.click(); }})()")
                clicked += 1
                await page.keyboard.press("Escape")
            except Exception as e:
                errors.append(f"{i}: {e}")
        await page.wait_for_timeout(300)
        rec(f"every button pressed ({clicked}), zero page errors", not errors, "; ".join(errors[:5]))

        # --- phone (iPhone 16 Pro, Chrome)
        ph = await br.new_context(viewport={"width": 402, "height": 874}, device_scale_factor=3, is_mobile=True, has_touch=True)
        pp = await ph.new_page(); perr = []
        pp.on("pageerror", lambda e: perr.append(str(e)))
        pp.on("dialog", lambda dg: asyncio.ensure_future(dg.accept()))
        await pp.goto(BASE + "/index.html"); await pp.wait_for_timeout(300)
        await pp.evaluate("v => localStorage.setItem('nate_writing_studio_vault_v1', v)", vault18)
        await pp.reload(); await pp.wait_for_timeout(700)
        await pp.screenshot(path=f"{OUT}/a19_new_cover_phone.png")
        await pp.click("#btnToggleLyrics"); await pp.wait_for_timeout(200)
        await pp.click("#btnEditLyrics"); await pp.fill("#lyricsEditText", "first test line\nsecond test line")
        await pp.screenshot(path=f"{OUT}/a19_lyrics_edit_phone.png")
        await pp.click("#btnLyricsSave")
        await pp.set_input_files("#audioFileInput", "test-song.mp3"); await pp.wait_for_timeout(500)
        await pp.click("#btnEditLyrics"); await pp.click("#btnLyricsTap"); await pp.wait_for_timeout(300)
        await pp.screenshot(path=f"{OUT}/a19_tap_phone.png")
        await pp.click("#btnTapDone"); await pp.click("#btnCloseLyrics")
        await pp.evaluate("selectSection(flattenSections(getActiveDoc())[1].subId)"); await pp.wait_for_timeout(200)
        await pp.screenshot(path=f"{OUT}/a19_new_chamber_phone.png")
        # 22hrs essay on phone
        await pp.evaluate("vault.activeDocId='essay-22hrs'; vault.activeSectionId='cover-main'; renderChapterTree(); setViewMode('single')"); await pp.wait_for_timeout(300)
        await pp.screenshot(path=f"{OUT}/a19_22hrs_cover_phone.png")
        rec("phone: zero page errors", not perr, "; ".join(perr[:3]))

        # a1.8 phone reference of the same new essay
        p18 = await ph.new_page()
        await p18.goto(BASE + "/a18.html"); await p18.evaluate("v => localStorage.setItem('nate_writing_studio_vault_v1', v)", vault18)
        await p18.reload(); await p18.wait_for_timeout(700)
        await p18.screenshot(path=f"{OUT}/a18_new_cover_phone.png")
        await br.close()
    srv.terminate()
    fails = [r for r in results if r[1] == "FAIL"]
    print(f"\n{len(results)-len(fails)} PASS / {len(fails)} FAIL")
    json.dump(results, open("check_results.json", "w"), indent=1)

asyncio.run(main())
